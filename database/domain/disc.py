from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Sqlite


class Disc(Sqlite.base):
    __tablename__ = 'discs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    drive = Column(String)
    drive_name = Column(String)
    disc_id = Column(Integer)
    title = Column(String)
    rip_dir = Column(String)
    titles = relationship("Title", backref='discs')
    media_id = Column(Integer, ForeignKey('medias.id'))
    source = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'discs'
    }
