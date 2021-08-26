from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, DateTime, Text
from scrapy.utils.project import get_project_settings

Base = declarative_base()

metadata = MetaData()


def db_connect():
    return create_engine(
        get_project_settings().get("CONNECTION_STRING"), client_encoding="utf-8"
    )


def create_table(engine):
    Base.metadata.create_all(bind=engine)


meta_tag = Table(
    "meta_tag",
    Base.metadata,
    Column("meta_id", Integer, ForeignKey("meta.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

meta_hyperlink = Table(
    "meta_hyperlink",
    Base.metadata,
    Column("meta_id", Integer, ForeignKey("meta.id")),
    Column("hyperlinks_id", Integer, ForeignKey("hyperlinks.id")),
)

meta_persons = Table(
    "meta_persons",
    Base.metadata,
    Column("meta_id", Integer, ForeignKey("meta.id")),
    Column("persons_id", Integer, ForeignKey("persons.id")),
)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, ForeignKey("meta.id"), primary_key=True)
    title = Column("title", String(200), nullable=False)
    description = Column("description", String(1000))
    text = Column("text", Text())

    meta = relationship("Meta", backref="articles")


class Meta(Base):
    __tablename__ = "meta"

    id = Column(Integer, primary_key=True)
    link = Column("link", String(200), unique=True)
    date = Column("date", DateTime, nullable=False)
    # views = Column("views", Integer)
    rubric_id = Column(Integer, ForeignKey("rubrics.id"))

    rubric = relationship("Rubric", backref="meta")

    hyperlinks = relationship(
        "Hyperlink", secondary="meta_hyperlink", lazy="dynamic", backref="meta"
    )

    tags = relationship("Tag", secondary="meta_tag", lazy="dynamic", backref="meta")

    persons = relationship(
        "Person", secondary="meta_persons", lazy="dynamic", backref="meta"
    )


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(50), unique=True, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(50), unique=True)


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(50))
    link = Column("link", String(200), unique=True)
    img = Column("img", String(200), unique=True)


class Hyperlink(Base):
    __tablename__ = "hyperlinks"

    id = Column(Integer, primary_key=True)
    hyperlink = Column("hyperlink", String(500), unique=True)
