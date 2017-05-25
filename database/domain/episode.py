from sqlalchemy import Column, Integer, ForeignKey

from database.domain.title import Title


class Episode(Title):
    __tablename__ = 'episodes'

    id = Column(Integer, ForeignKey('titles.id'), primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id'))
    number = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'episodes'
    }
