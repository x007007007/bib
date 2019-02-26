import os
import argparse
import glob


from . import core


def parse_arg():
    parser = argparse.ArgumentParser(prog='bib')

    subparsers = parser.add_subparsers()

    parsers_init = subparsers.add_parser('init', help='show repo state')
    parsers_init.add_argument('path', nargs="*", default=".")
    parsers_init.set_defaults(func=init)

    parsers_state = subparsers.add_parser('state', help='show repo state')
    parsers_state.set_defaults(func=state)

    parser_cmd_add = subparsers.add_parser('add', help='add file into index')
    parser_cmd_add.add_argument('match_pattern', nargs="+")
    parser_cmd_add.set_defaults(func=cmd_add)

    return parser

def init(args):
    repo_path = os.path.abspath(os.path.join(os.curdir, args.path))
    bib_repo = core.BibRepo.create_bib_repo(repo_path)

def state(args):
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    print(bib_repo)

def cmd_add(args):
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    bib_repo.add_resource(*args.match_pattern)

def bib():
    parser = parse_arg()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

