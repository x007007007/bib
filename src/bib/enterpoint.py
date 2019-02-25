import os

from . import core


def bib():
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    print(bib_repo)