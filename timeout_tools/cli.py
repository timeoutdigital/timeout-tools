import argparse
import logging
import os
import platform
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

    parser_uv_install = subparsers.add_parser(
        'uv-install',
        help='install uv',
    )
    parser_uv_install.set_defaults(func=uv_install)

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


def uv_install(args):
    home_directory = os.path.expanduser('~')
    ret, out = run('which uv')
    if ret == 0:
        print("UV is already installed")
        sys.exit(0)
    
    if platform.system() == 'Linux':
        ret, out = run('curl -LsSf https://astral.sh/uv/install.sh | sh')
    elif platform.system() == 'Darwin':
        # try brew first
        ret, out = run('which brew')
        if ret == 0:
            ret, out = run('brew install uv')
        else:
            ret, out = run('curl -LsSf https://astral.sh/uv/install.sh | sh')
    else:
        print(f'{platform.system()} unknown system')
        sys.exit(1)
    
    if ret == 0:
        print('UV installed successfully')
        print('You may need to restart your shell')
    else:
        print('Failed to install UV')
        print(out)
        sys.exit(1)


def python_setup_func(args):
    if not args.python_version:
        args.python_version = load_python_version()
    python_setup(args.app, args.branch, args.python_version)


def python_setup(app, branch, python_version):
    # install the Python version if needed
    print(f'- Installing Python {python_version}', end='', flush=True)
    ret, out = run(f'uv python install {python_version}')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')
    
    print(f'- Creating virtual environment', end='', flush=True)
    ret, out = run(f'uv venv --python {python_version}')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')
    
    # try installing requirements using uv pip sync
    print('- Installing requirements.txt', end='', flush=True)
    ret, out = run('uv pip sync requirements.txt')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')

    # install the dev requirements if they exist
    ret, out = run('ls requirements-dev.txt')
    if ret == 0:
        print('- Installing requirements-dev.txt', end='', flush=True)
        ret, out = run('uv pip install -r requirements-dev.txt')
        if ret != 0:
            print(' ❌')
            print(out)
            sys.exit(1)
        print(' ✅')

    # pre-commit
    print('- Installing pre-commit', end='', flush=True)
    ret, out = run('uv pip install pre-commit')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')
    
    # pre-commit install
    print('- Running `pre-commit install`', end='', flush=True)
    ret, out = run('uv run pre-commit install')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')


def python_remove(args):
    print('- Deleting `.venv` virtualenv', end='', flush=True)
    ret, out = run('rm -rf .venv')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')
    
    ret, out = run('ls .python-version')
    if ret == 0:
        print('- Deleting `.python-version`', end='', flush=True)
        ret, out = run('rm .python-version')
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
        logging.debug('"PYTHON_VERSION" file not found')
        return False


if __name__ == '__main__':
    main()
