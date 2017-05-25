from sqlalchemy import Column, Integer, ForeignKey, String

from database.domain.title import Title


class Movie(Title):
    __tablename__ = 'movies'

    id = Column(Integer, ForeignKey('titles.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'movies'
    }