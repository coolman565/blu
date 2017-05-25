import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from database import Sqlite


class MediaType(enum.Enum):
    SERIES = 'SERIES'
    MOVIE = 'MOVIE'


class Media(Sqlite.base):
    __tablename__ = 'medias'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    type = Column(String)
    media_type = Column(Enum(MediaType), nullable=False)
    discs = relationship("Disc", backref='medias')

    __mapper_args__ = {
        'polymorphic_identity': 'medias',
        'polymorphic_on': type
    }
