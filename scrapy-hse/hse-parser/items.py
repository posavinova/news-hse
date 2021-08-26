import re
import dateparser
from bs4 import BeautifulSoup
from itemloaders.processors import Join, MapCompose, TakeFirst, Compose
from scrapy.item import Item, Field


def convert_date(date):
    date = dateparser.parse(date)
    return date


def normalize_link(link):
    if "https://" in link:
        link = link
    else:
        link = "https://www.hse.ru" + link
    return link


def normalize_text(text):
    soup = BeautifulSoup(text, "lxml")

    if remove_sign := soup.select("div.photo-caption.darkgrey.smaller"):
        for i in remove_sign:
            i.decompose()

    if remove_button := soup.select("a.button"):
        for p in remove_button:
            p.decompose()

    if remove_promo := soup.select("p.promo-section"):
        for p in remove_promo:
            p.decompose()

    text = soup.get_text().replace("\n", " ")
    if "\xa0" in text:
        text = text.replace("\xa0", " ")
    return text


# def filter_views(visitors):
#     if visitors is not None:
#         if re.search(r"\d+", visitors) is not None:
#             visitors = int(re.search(r"\d+", visitors).group())
#         else:
#             visitors = 0
#     return visitors


def remove_duplicates(data_list):
    data = set(data_list)
    data = list(data)
    return data


def match_people(people):
    seq = []
    idx: int = 0
    while idx < len(people):
        if not re.search(r"/cimage|[а-я]", people[idx]):
            if re.search(r"/mirror", people[idx + 1]):
                seq.append((people[idx + 2], people[idx], people[idx + 1]))
                idx += 3
            else:
                seq.append((people[idx + 1], people[idx], None))
                idx += 2
        elif re.search(r"/mirror", people[idx]):
            if not re.search(r"/cimage|[а-я]", people[idx + 1]):
                seq.append((people[idx + 2], people[idx + 1], people[idx]))
                idx += 3
            else:
                seq.append((people[idx + 1], None, people[idx]))
                idx += 2
        else:
            seq.append((people[idx], None, None))
            idx += 1
    persons_list = [list(elem) for elem in seq]
    for seq in persons_list:
        if seq[1] is not None:
            if "hse" in seq[1]:
                seq[1] = "https:" + seq[1]
            else:
                seq[1] = "https://www.hse.ru" + seq[1]
        if seq[2] is not None:
            seq[2] = "https://www.hse.ru" + seq[2]
    seq = [tuple(elem) for elem in persons_list]
    return seq


class NewsItem(Item):
    title = Field(output_processor=TakeFirst())
    description = Field(output_processor=TakeFirst())
    link = Field(
        input_processor=MapCompose(normalize_link), output_processor=TakeFirst()
    )
    hyperlinks = Field(input_processor=Compose(remove_duplicates))
    rubric = Field(output_processor=TakeFirst())
    tags = Field()
    date = Field(input_processor=MapCompose(convert_date), output_processor=TakeFirst())
    text = Field(input_processor=MapCompose(normalize_text), output_processor=Join())
    persons = Field(
        input_processor=Compose(match_people),
    )
    # visitors = Field(
    #     input_processor=MapCompose(filter_views),
    #     output_processor=TakeFirst()
    # )
