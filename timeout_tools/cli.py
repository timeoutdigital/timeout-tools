import argparse
import os
import platform
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

    parser_pyenv_install = subparsers.add_parser(
        'pyenv-install',
        help='install pyenv',
    )
    parser_pyenv_install.set_defaults(func=pyenv_install)

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
    parser_python_setup.set_defaults(func=python_setup)

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
        args.app = out.split('/')[1].split('.')[0]

    args.func(args)


def run(cmd):
    print(f'RUNNING: "{cmd}"')
    res = subprocess.run(
        cmd,
        capture_output=True,
        shell=True,
    )
    if res.stderr:
        print(res.stderr.decode())

    return (res.returncode, res.stdout.decode())


def pyenv_install(args):
    home_directory = os.path.expanduser('~')
    ret, out = run(f'ls -d {home_directory}/.pyenv')
    if ret == 0:
        print("$HOME/.pyenv already exists")
        sys.exit(1)
    if platform.system() == 'Linux':
        ret, out = run('curl -s https://pyenv.run | bash')
    elif platform.system() == 'macOS':
        ret, out = run('brew install pyenv && brew install pyenv-virtualenv')
    if ret == 0:
        ret, out = run(f'grep "TIMEOUT-TOOLS PYENV" {home_directory}/.bashrc')
        if ret == 0:
            print("pyenv already configured in .bashrc\n")
            sys.exit(1)
        with open(f'{home_directory}/.bashrc', 'a') as bashrc:
            bashrc.write('\n## TIMEOUT-TOOLS PYENV\n')
            bashrc.write('export PATH="$HOME/.pyenv/bin:$PATH"\n')
            bashrc.write('eval "$(pyenv init --path)"\n')
            bashrc.write('eval "$(pyenv virtualenv-init -)"\n')
        run(f'. {home_directory}/.bashrc')


def python_setup_func(args):
    if not args.python_version:
        args.python_version = load_python_version()
    python_setup(args.app, args.branch, args.python_version)


def python_setup(app, branch, python_version, ws=None):
    if ws:
        os.chdir(ws)
    pyenv_name = f'{app}-{branch}'
    run(f'pyenv install -s {python_version}')
    run(f'pyenv virtualenv {python_version} {pyenv_name}')
    run(f'echo {pyenv_name} > .python-version')
    run(f'eval "$(pyenv init -)" && \
            pyenv activate {pyenv_name} && \
            pip install -U pip && \
            pip install -r requirements.txt && \
            pre-commit install')


def python_remove(args):
    pyenv_name = f'{args.app}-{args.branch}'
    run('rm .python-version')
    run(f'pyenv virtualenv-delete -f {pyenv_name}')


def ws(args):
    ws = f'{args.ticket}--{args.app}'
    ret, out = run(f'git clone git@github.com:timeoutdigital/{args.app}.git {ws} && \
        cd {ws} && \
        git checkout -b {args.ticket}')
    if ret != 0:
        sys.exit(1)

    py_ver = load_python_version(ws)
    if py_ver:
        python_setup(args.app, args.ticket, py_ver, ws=f'{args.ticket}--{args.app}')


def load_python_version(ws=None):
    print(run('ls && pwd'))
    if ws:
        os.chdir(ws)
    try:
        with open('PYTHON_VERSION', 'r') as pv:
            return pv.read().rstrip()
    except FileNotFoundError:
        print('"PYTHON_VERSION" file not found')
        return False


if __name__ == '__main__':
    main()
