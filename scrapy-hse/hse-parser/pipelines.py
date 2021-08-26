from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from hse_parser.models import (
    Article,
    Meta,
    Rubric,
    Tag,
    Hyperlink,
    Person,
    db_connect,
    create_table,
)


class EmptyArticlesPipeline:
    def process_item(self, item, spider):
        if item.get("text") is None:
            raise DropItem(f"Unfilled article found: {item.get('title')}")
        else:
            return item


class DuplicatesPipeline:
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        exist_article = (
            session.query(Article).filter_by(title=item.get("title")).first()
        )
        session.close()
        if exist_article is not None:
            raise DropItem(f"Duplicate article found: {item.get('title')}")
        else:
            return item


class SaveNewsPipeline:
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        article = Article()
        meta = Meta()
        rubric = Rubric()

        article.title = item.get("title")
        article.description = item.get("description")
        article.text = item.get("text")

        meta.date = item.get("date")
        meta.link = item.get("link")
        # meta.views = item.get("visitors")

        rubric.name = item.get("rubric")

        exist_meta = session.query(Meta).filter_by(link=meta.link).first()
        if exist_meta is not None:
            article.meta = exist_meta
        else:
            article.meta = meta

        exist_rubric = session.query(Rubric).filter_by(name=rubric.name).first()
        if exist_rubric is not None:
            meta.rubric = exist_rubric
        else:
            meta.rubric = rubric

        if "tags" in item:
            for tags_name in item.get("tags"):
                tag = Tag(name=tags_name)
                exist_tag = session.query(Tag).filter_by(name=tags_name).first()
                if exist_tag is not None:
                    tag = exist_tag
                meta.tags.append(tag)

        if "persons" in item:
            pack = item["persons"]
            for name, link, img in pack:
                person = Person(name=name, link=link, img=img)
                exist_person = (
                    session.query(Person)
                    .filter_by(name=name, link=link, img=img)
                    .first()
                )
                if exist_person is not None:
                    person = exist_person
                meta.persons.append(person)

        if "hyperlinks" in item:
            for link in item.get("hyperlinks"):
                hyperlink = Hyperlink(hyperlink=link)
                exist_link = session.query(Hyperlink).filter_by(hyperlink=link).first()
                if exist_link is not None:
                    hyperlink = exist_link
                meta.hyperlinks.append(hyperlink)

        try:
            session.add(article)
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

        return item
