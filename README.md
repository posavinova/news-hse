# An extensive tool for obtaining and proceeding HSE news 
> ![HSE logo](https://www.hse.ru/data/2020/11/16/1367273515/HSE_University_blue.png) 
>
> © HSE University
## Setup
Tested with Python 3.9 via virtual environment:
```shell
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Crawling & Scraping

The official website: *https://www.hse.ru/news/*

Start the spider from its root directory with the following command:
```shell
$ scrapy crawl news
```

Comand for saving scraped data to a file:
```shell
$ scrapy crawl news -o file_name.csv # file_name.json
```
CSS-selectors are used for extracting data from web-pages.

Sample log:

![log1](/images/log1.png)
![log1](/images/log2.png)

### *Optional*
*A part of the spider's code may be uncommented with the spider settings "ROBOTSTXT_OBEY" set to False for getting number of post views (wheather use it or not is up to you, but it's actually disallowed by hse robots.txt).*

## Database storing

PostgreSQL + SQLAlchemy are used in this project. 

The database is designed in a way that the tables have one-to many and many-to-many relations.

Here's the DB schema:
![log1](https://raw.github.com/posavinova/news-hse/main/images/news_hse.png)

Configure your database settings in a separate file (secrets.py):
```python
postgresql = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}".format(
    dialect="xxxx",
    driver="xxxx",
    user="xxxx",
    password="xxxx",
    host="xxxx",
    port="xxxx",
    db_name="xxxx",
)
```
Apart from saving scraped items to the DB, pipelines take care of dropping duplicates and posts without any text.

## Building social network

The data set I use is a CSV spreadsheet with 558 scraped posts.
![log1](https://raw.github.com/posavinova/news-hse/main/images/news_table.png)

To create a social graph within a list of people, mentioned in HSE news posts, we'll use spaCy for NER and NetworkX to bind nodes and edges.
![log1](https://raw.github.com/posavinova/news-hse/main/images/graph.png)
Display top-mentioned names:

```
Top 10 mentioned people:
('Ярослав Кузьминов', 62)
('Ярослав Кузьминова', 26)
('Исак Фрумин', 16)
('Сергей Рощин', 14)
('Лилия Овчаров', 14)
('Алексей Иванов', 13)
('Владимир Путин', 13)
('Леонид Гохберг', 12)
('Исиэз Ниу', 11)
('Валерий Касамара', 11)
```

## Issues
For any reference follow:
* __Scrapy__ - https://docs.scrapy.org/
* __SQLAlchemy__ - https://docs.sqlalchemy.org/
* __spaCy__ - https://spacy.io/usage/spacy-101
* __NetworkX__ - https://networkx.org/
