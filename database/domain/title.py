import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float

from database import Sqlite


class Status(enum.Enum):
    SCANNED = 0
    RIPPED = 10
    COMPRESSED = 100


class Title(Sqlite.base):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key=True)
    bytes = Column(Integer)
    duration = Column(Integer)
    file_name = Column(String)
    f_name = Column(String)
    frame_rate = Column(Float)
    lang = Column(String)
    lang_code = Column(String)
    stream_id = Column(Integer)
    title = Column(String)
    title_id = Column(String)
    type = Column(String)
    disc_id = Column(Integer, ForeignKey('discs.id'))
    status = Column(Enum(Status))
    raw_file = Column(String)
    compressed_file = Column(String)
    video_size = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'titles',
        'polymorphic_on': type
    }
