"""
Public code
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, aliased
from .models import Base, FilePath, FileHash
from .stream_engine import (
    FileStreamAnalysis,
    AnalysisMd5,
    AnalysisEd2k,
    AnalysisSha1,
    AnalysisSize,
    AnalysisMine,
)
from .scan_rule import RuleEngine


class BaseBibRepo(object):
    """
    每一个索引仓库 ，称为一个BibRepo

    """
    version = "1"

    def __init__(self, root):
        self.root = root
        self._init_analysis_factor()

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
        cur_dir_b = os.path.abspath(cur_dir).split(os.sep)
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
            engine = create_engine(db_uri)
            Base.metadata.create_all(engine)
        else:
            engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=engine)
        return self.Session


    def _init_analysis_factor(self):
        fsa = FileStreamAnalysis()
        fsa.register(AnalysisSize())
        fsa.register(AnalysisSha1())
        fsa.register(AnalysisEd2k())
        fsa.register(AnalysisMd5())
        fsa.register(AnalysisMine())
        self.fsa = fsa

    def analysis_file(self, file_path: str):
        with open(file_path, "rb") as fp:
            return self.fsa.executor(fp)




class BibRepo(BaseBibRepo):
    @staticmethod
    def get_or_create(session, table, default=None, **kwargs):
        is_created = False
        if default is None:
            default = {}
        obj = session.query(table).filter_by(
            **kwargs
        ).one_or_none()
        if not obj:
            is_created = True
            n_value = {}
            n_value.update(default)
            n_value.update(kwargs)
            obj = table(**n_value)
            session.add(obj)
        session.commit()
        return obj, is_created

    def get_seesion(self):
        return self.open_db()()

    def add_resource(self, *file_paths):
        session = self.get_seesion()

        for exist_file_path in (p for p in file_paths if os.path.exists(p) and os.path.isfile(p)):
            repo_rel_path = self.get_repo_path(exist_file_path)

            fpo, is_created = self.get_or_create(session, FilePath,
                path=repo_rel_path
            )

            res = self.analysis_file(exist_file_path)

            fho, is_created = self.get_or_create(session, FileHash,
                md5=res['md5'],
                size=res['size'],
                ed2k=res['ed2k'],
                sha1=res['sha1']
            )
            if fpo not in fho.file_paths:
                fho.file_paths.append(fpo)

        session.commit()

    def remove_resource(self, *file_paths):
        session = self.open_db()()
        FilePathAF = aliased(FilePath)

        for file_path in file_paths:
            repo_rel_path = self.get_repo_path(file_path)
            if session.query(FilePath).join(
                FilePathAF,
                FilePath.file_hash_id == FilePathAF.file_hash_id
            ).filter(
                FilePathAF.path == repo_rel_path,
            ).filter(
                FilePath.path != repo_rel_path
            ).count() == 0:  # without other ref
                fp_o = session.query(FilePath).filter_by(
                    path=repo_rel_path
                ).one_or_none()
                if fp_o:
                    session.query(FileHash).filter_by(
                        id=fp_o.file_hash_id
                    ).delete()
                    session.commit()
            session.query(FilePath).filter_by(
                path=repo_rel_path
            ).delete()
            session.commit()
        session.commit()

    def check_files(self, *file_paths):
        session = self.get_seesion()
        not_in_db = []
        check_pass = []
        check_fail = []
        for file_path in file_paths:
            repo_rel_path = self.get_repo_path(file_path)
            fpo = session.query(FilePath).filter_by(
                path=repo_rel_path
            ).one_or_none()
            if fpo is None:
                not_in_db.append(file_path)
            else:
                res = self.analysis_file(file_path)
                if (res['md5'] == fpo.file_hash.md5
                    and res['sha1'] == fpo.file_hash.sha1
                    and res['size'] == fpo.file_hash.size
                    and res['ed2k'] == fpo.file_hash.ed2k):
                    check_pass.append(file_path)
                else:
                    check_fail.append(file_path)

        return {
            'untracked': not_in_db,
            'fail': check_fail,
            'pass': check_pass
        }

    def status(self):
        """
        show database summary
        :return:
        """
        session = self.get_seesion()
        res = {}

        res['index_count'] = session.query(FilePath).join(
            FileHash
        ).count()
        res['unindex_count'] = session.query(FilePath).count() - res['index_count']
        res['unique_count'] = session.query(FilePath).join(
            FileHash
        ).group_by(FilePath.file_hash_id).count()
        return res


    def scan(self):
        session = self.get_seesion()
        rule = RuleEngine(os.path.join(self.root, ".bib", "bib.yml"))
        for root, dir, files in os.walk(self.root):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)
                repo_path = self.get_repo_path(file_path)
                if rule.could_index(repo_path, file_size):
                    print(f"match {repo_path}")
        print(rule)
