import argparse
import logging
import os
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Timeout Tools',
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
    )

    subparsers = parser.add_subparsers(
        title="commands",
    )

    parser_python_setup = subparsers.add_parser(
        'python-setup',
        help='setup repos python environment',
    )
    parser_python_setup.add_argument(
        '-a',
        '--app',
        required=False
    )
    parser_python_setup.add_argument(
        '-b',
        '--branch',
        required=False
    )
    parser_python_setup.add_argument(
        '-p',
        '--python-version',
        required=False
    )
    parser_python_setup.set_defaults(func=python_setup_func)

    parser_python_remove = subparsers.add_parser(
        'python-remove',
        help='delete python environment',
    )
    parser_python_remove.add_argument(
        '-a',
        '--app',
        required=False
    )
    parser_python_remove.add_argument(
        '-b',
        '--branch',
        required=False
    )
    parser_python_remove.add_argument(
        '-p',
        '--python-version',
        required=False
    )
    parser_python_remove.set_defaults(func=python_remove)

    parser_ws = subparsers.add_parser(
        'ws',
        help='create ws',
    )
    parser_ws.add_argument(
        'app',
    )
    parser_ws.add_argument(
        'ticket',
    )
    parser_ws.add_argument(
        '-p',
        '--python-version',
        required=False
    )
    parser_ws.set_defaults(func=ws)

    args = parser.parse_args()
    if len(vars(args)) == 1:
        parser.print_help()
        sys.exit(0)

    if 'branch' in args and not args.branch:
        res, out = run('git rev-parse --abbrev-ref HEAD')
        args.branch = out.rstrip()
    if 'app' in args and not args.app:
        res, out = run('git config --get remote.origin.url')
        args.app = re.match(r'.*/([\w|-]+)', out).group(1)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    args.func(args)


def run(cmd):
    logging.debug(f'RUNNING: "{cmd}"')
    res = subprocess.run(
        cmd,
        capture_output=True,
        shell=True,
    )
    logging.debug(res)

    if res.returncode == 0:
        return (res.returncode, res.stdout.decode())
    else:
        return (res.returncode, res.stderr.decode())


def python_setup_func(args):
    if not args.python_version:
        args.python_version = load_python_version()
    python_setup(args.app, args.branch, args.python_version)


def python_setup(app, branch, python_version):
    if os.path.exists('PYTHON_VERSION'):
        req_python_setup(app, branch, python_version)
    else:
        pypro_python_setup(app, branch, python_version)

    print('- Running `pre-commit install`', end='', flush=True)
    ret, out = run('pre-commit install')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    else:
        print(' ✅')


def req_python_setup(app, branch, python_version):
    print('- Creating venv', end='', flush=True)
    ret, out = run(f'uv venv --python {python_version} --clear')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    else:
        print(' ✅')

    print('- Installing requirements.txt', end='', flush=True)
    ret, out = run('uv pip install -r requirements.txt')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    else:
        print(' ✅')

    ret, out = run('ls requirements-dev.txt')
    if ret == 0:
        print('- Installing requirements-dev.txt', end='', flush=True)
        ret, out = run('uv pip install -r requirements-dev.txt')
        if ret != 0:
            print(' ❌')
            print(out)
            sys.exit(1)
        else:
            print(' ✅')


def pypro_python_setup(app, branch, python_version):
    pass


def python_remove(args):
    ret, out = run('cat .python-version')
    if ret != 0:
        print(out)
        sys.exit(1)
    pyenv_name = out.rstrip()

    print('- Deleting `.python-version`', end='', flush=True)
    ret, out = run('rm .python-version')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')

    print(f'- Deleting `{pyenv_name}` virtualenv', end='', flush=True)
    ret, out = run(f'pyenv virtualenv-delete -f {pyenv_name}')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')


def ws(args):
    ws = f'{args.ticket}--{args.app}'

    print(f'- Cloning `{args.app}` into `{ws}`', end='', flush=True)
    ret, out = run(f'git clone git@github.com:timeoutdigital/{args.app}.git {ws}')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')

    print(f'- Branch `{args.ticket}`', end='', flush=True)
    ret, out = run(f'cd {ws} && git checkout {args.ticket}')
    if ret == 0:
        print(' checked out ✅')
    else:
        ret, out = run(f'cd {ws} && git checkout -b {args.ticket}')
        if ret != 0:
            print(' failed ❌')
            print(out)
            sys.exit(1)
        print('created ✅')

    py_ver = load_python_version(ws)
    if py_ver:
        python_setup(args.app, args.ticket, py_ver)

    print(f'Complete, you can now `cd {ws}`\n')


def load_python_version(ws=None):
    if ws:
        os.chdir(ws)
    try:
        with open('PYTHON_VERSION', 'r') as pv:
            return pv.read().rstrip()
    except FileNotFoundError:
        logging.debug('"PYTHON_VERSION" file not found, trying ".python-version"')
        try:
            with open('.python-version', 'r') as pv:
                return pv.read().rstrip()
        except FileNotFoundError:
            logging.debug('".python-version" file not found')
            return False


if __name__ == '__main__':
    main()
