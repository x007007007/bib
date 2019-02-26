"""
Public code
"""
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, FilePath, FileHash
import pkg_resources
from .stream_engine import FileStreamAnalysis, AnalysisMd5, AnalysisEd2k, AnalysisSha1, AnalysisSize



class BibRepo(object):
    """
    每一个索引仓库 ，称为一个BibRepo

    """
    version = "1"

    def __init__(self, root):
        self.root = root

    @classmethod
    def create_bib_repo(cls, repo_path):
        repo_meta_path = os.path.join(repo_path, ".bib")
        if not os.path.exists(repo_meta_path):
            os.mkdir(repo_meta_path)
        with open(os.path.join(repo_path, ".bib", "bib.ini"), "w") as fp:
            pass
        repo = cls(repo_path)
        repo.open_db()
        return repo

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

    def get_repo_path(self, sys_path):
        abs_sys_path = os.path.abspath(sys_path)
        abs_root_path = os.path.abspath(self.root)
        if abs_sys_path.startswith(abs_root_path):
            return abs_sys_path[len(abs_root_path):]
        else:
            raise FileExistsError("Out of repo")

    def open_db(self):
        db_path = self.get_db_path()
        db_uri = f'sqlite:///{db_path}'

        if not os.path.exists(db_path):
            engine = create_engine(db_uri, echo=True)
            Base.metadata.create_all(engine)
        else:
            engine = create_engine(db_uri, echo=True)
        self.Session = sessionmaker(bind=engine)
        return self.Session


    def add_resource(self, *file_paths):
        exist_file_paths = (p for p in file_paths if os.path.exists(p) and os.path.isfile(p))
        repo_paths = (self.get_repo_path(p) for p in exist_file_paths)
        session = self.open_db()()

        session.add_all([
            FilePath(path=repo_path) for repo_path in repo_paths
        ])
        session.commit()
        fsa = FileStreamAnalysis()
        fsa.register(AnalysisSize())
        fsa.register(AnalysisSha1())
        fsa.register(AnalysisEd2k())
        fsa.register(AnalysisMd5())

        for exist_file_path in exist_file_paths:
            repo_path = self.get_repo_path(p)
            with open(exist_file_path) as fp:
                res = fsa.executor(fp)
                print(repo_path, res)
