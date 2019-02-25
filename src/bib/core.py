"""
Public code
"""
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import pkg_resources

class BibRepo(object):
    """
    每一个索引仓库 ，称为一个BibRepo

    """
    version = "1"

    def __init__(self, root):
        self.root = root

    @classmethod
    def create_bib_repo(cls, repo_path):
        pass

    @classmethod
    def get_bib_repo(cls, cur_dir):
        cur_dir_b = cur_dir.split(os.sep)
        while cur_dir_b:
            db_path = f"{os.sep.join(cur_dir_b)}{os.sep}.bib{os.sep}index.db"
            if os.path.exists(db_path):
                return cls(os.sep.join(cur_dir_b))
            else:
                cur_dir_b.pop()


    def get_db_path(self):
        return f"{self.root}/.bib/index.db"

    def open_db(self):
        db_path = self.get_db_path()
        if not os.path.exists(db_path):
            engine = create_engine(f'sqlite://{db_path}', echo=True)
            Base.metadata.create_all(engine)
        else:
            engine = create_engine(f'sqlite://{db_path}', echo=True)
        self.Session = sessionmaker(bind=engine)


