from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Binary, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()



class FilePath(Base):
    __tablename__ = 'file_path'
    path = Column(String)
    file_hash_id = Column(Integer, ForeignKey('parent.id'))


class FileHash(Base):
    __tablename__ = 'file_hash'
    id = Column(Integer, primary_key=True)

    md5 = Column(Binary(length=128))
    sha1 = Column(Binary(length=160))
    size = Column(Integer)

    file_path = relationship("FilePath")