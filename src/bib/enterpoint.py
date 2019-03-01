import os
import argparse
from six import with_metaclass

from . import core


class Command(object):
    _sub_command = []

    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='bib')
        self._subparsers = self._parser.add_subparsers()
        self.init_sub_command()

    def init_sub_command(self):
        for sub_cmd_cls in self._sub_command:
            sub_cmd = sub_cmd_cls()  # type: SubCommandBase
            parser = self._subparsers.add_parser(sub_cmd.name, help=sub_cmd.help_text)
            parser.set_defaults(func=sub_cmd.handle)
            sub_cmd.set_parser(parser)

    def execute(self):
        args = self._parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            self._parser.print_help()


class CommandMeta(type):
    def __new__(self, cls, bases, attr):
        is_cmd = cls.endswith('Command')
        if 'name' not in attr:
            attr['name'] = cls[:-7].lower()
        sub_command = type.__new__(self, cls, bases, attr)
        if is_cmd:
            Command._sub_command.append(sub_command)
        return sub_command


class SubCommandBase(with_metaclass(CommandMeta)):
    help_text = ''

    def set_parser(self, parser):
        pass

    def handle(self, args):
        pass



class RepoCommandMixin(object):
    @property
    def repo(self):
        self._repo = core.BibRepo.get_bib_repo(os.curdir)
        return self._repo


class InitCommand(SubCommandBase):
    help_text = "init bib repo"
    def set_parser(self, parser):
        parser.add_argument('path', nargs="*", default=".")

    def handle(self, args):
        repo_path = os.path.abspath(os.path.join(os.curdir, args.path))
        bib_repo = core.BibRepo.create_bib_repo(repo_path)


class StatusCommand(SubCommandBase, RepoCommandMixin):
    help_text = 'show repo state'

    def handle(self, args):
        res = self.repo.status()
        print(f"we have {res['index_count']} resources, "
              f"{res['unique_count']} are unique, "
              f"{res['unindex_count']} untracked")


class AddCommand(SubCommandBase, RepoCommandMixin):
    help_text = 'add file into index'

    def set_parser(self, parser):
        parser.add_argument('match_pattern', nargs="+")

    def handle(self, args):
        self.repo.add_resource(*args.match_pattern)


class RemoveCommand(SubCommandBase, RepoCommandMixin):
    def set_parser(self, parser):
        parser.add_argument('match_pattern', nargs="+")

    def handle(self, args):
        self.repo.remove_resource(*args.match_pattern)


class CheckCommand(SubCommandBase, RepoCommandMixin):
    def set_parser(self, parser):
        parser.add_argument('match_pattern', nargs="+")

    def handle(self, args):
        res = self.repo.check_files(*args.match_pattern)
        print(res)

class ScanCommand(SubCommandBase, RepoCommandMixin):
    help_text = 'scan folder, automatic add, remote by rule'

    def handle(self, args):
        self.repo.scan()


def bib():
    command = Command()
    command.execute()
