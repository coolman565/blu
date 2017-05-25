from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.domain.media import Media


class Series(Media):
    __tablename__ = 'series'

    id = Column(Integer, ForeignKey('medias.id'), primary_key=True)
    season = Column(Integer)
    episodes = relationship("Episode", backref='series')

    __mapper_args__ = {
        'polymorphic_identity': 'series'
    }
