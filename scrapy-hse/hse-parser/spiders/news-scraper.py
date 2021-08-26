# import re
# import time
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import Rule
from hse_parser.items import NewsItem


class NewsSpider(scrapy.Spider):
    name = "news"

    allowed_domains = ["hse.ru"]
    start_urls = ["https://www.hse.ru/news"]

    rules = [
        Rule(LinkExtractor(allow=(r"/page[0-9]+",)), callback="parse", follow=True)
    ]

    def parse(self, response):
        news = response.css(".post")
        for article in news:
            loader = ItemLoader(item=NewsItem(), selector=article)
            loader.add_css("title", "h2 a::text")
            loader.add_css("description", "p:nth-child(2)::text")
            loader.add_css("link", "h2 a::attr(href)")
            loader.add_css("rubric", "span::text")
            loader.add_css("tags", ".tag::text")
            loader.add_css("date", ".post-meta__date *::text")

            news_item = loader.load_item()

            report_url = article.css("h2 a::attr(href)").get()

            yield response.follow(
                report_url, self.parse_report, cb_kwargs={"news_item": news_item}
            )
            # report_url": report_url

            next_page = response.css(".pages__page_active + a::attr(href)").get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse_report(self, response, news_item):  # report_url
        loader = ItemLoader(item=news_item, response=response)

        loader.add_css(
            "text", ".builder--text, .big.page-edi p::text, .big.page-edi a::text"
        )
        loader.add_css(
            "hyperlinks", "div.builder--text a::attr(href), .with-indent a::attr(href)"
        )
        loader.add_css(
            "persons",
            ".b-peoples a::attr(href), div.last_child.with-indent_left100 a::attr(href), "
            "div.last_child.with-indent_left100 a::text, .b-peoples span.b::text, "
            "div.articleMeta img::attr(src)",
        )
        yield loader.load_item()

        # The following code is for extracting number of post views,
        # but scraping the counter's page is restricted,
        # it is only accessible when disobeying the robots.txt
        # if re.search(r"(?<=/)\d+|null(?=\.html)", report_url) is not None:
        #     post_id = re.search(r"(?<=/)\d+|null(?=\.html)", report_url).group()
        #     unix_time = str(int(time.time()))
        #     js_link = f"https://www.hse.ru/n/api/counter/news?id={post_id}&_={unix_time}"
        #     js_request = scrapy.Request(url=js_link, cookies={"cookies": "tracking=ZEsUBGBsYV0C32tWA4UDAg=="},
        #                                 callback=self.parse_visitors, cb_kwargs={"news_item": news_item})
        #     yield js_request

    # def parse_visitors(self, response, news_item):
    #     loader = ItemLoader(item=news_item, response=response)
    #     loader.add_css("visitors", "body")
    #     yield loader.load_item()
