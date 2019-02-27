from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Binary, ForeignKey
from sqlalchemy.orm import relationship
import binascii

Base = declarative_base()



class FilePath(Base):
    __tablename__ = 'file_path'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    file_hash_id = Column(Integer, ForeignKey('file_hash.id'), nullable=True)


class FileHash(Base):
    __tablename__ = 'file_hash'

    id = Column(Integer, primary_key=True)
    md5 = Column(String(length=32))
    sha1 = Column(String(length=40))
    ed2k = Column(String(length=32))
    size = Column(Integer)

    file_paths = relationship("FilePath",  cascade="save-update, merge, delete")

    def __str__(self):
        return f"<FileHash:{binascii.b2a_hex(self.md5)}>"