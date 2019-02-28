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

    parser_cmd_remove = subparsers.add_parser(
        'rm', help='remove file index from index'
    )
    parser_cmd_remove.add_argument('match_pattern', nargs="+")
    parser_cmd_remove.set_defaults(func=cmd_rm)

    parser_cmd_status = subparsers.add_parser(
        'status', help="show datebase status"
    )
    parser_cmd_status.set_defaults(func=cmd_status)

    parser_cmd_check = subparsers.add_parser(
        'check', help='check file hash'
    )
    parser_cmd_check.add_argument('match_pattern', nargs="+")
    parser_cmd_check.set_defaults(func=cmd_check)

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

def cmd_rm(args):
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    bib_repo.remove_resource(*args.match_pattern)


def cmd_status(args):
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    res = bib_repo.status()
    print(f"we have {res['index_count']} resources, "
          f"{res['unique_count']} are unique, "
          f"{res['unindex_count']} untracked")

def cmd_check(args):
    bib_repo = core.BibRepo.get_bib_repo(os.curdir)
    res = bib_repo.check_files(*args.match_pattern)
    print(res)


def bib():
    parser = parse_arg()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

