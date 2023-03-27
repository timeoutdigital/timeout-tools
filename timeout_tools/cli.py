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


def pyenv_install(args):
    home_directory = os.path.expanduser('~')
    ret, out = run(f'ls -d {home_directory}/.pyenv')
    if ret == 0:
        logging.debug("$HOME/.pyenv already exists")
        sys.exit(1)
    shell_rc = '.bashrc'
    if platform.system() == 'Linux':
        ret, out = run('curl -s https://pyenv.run | bash')
    elif platform.system() == 'Darwin':
        shell_rc = '.zshrc'
        ret, out = run('brew install pkg-config openssl@1.1 xz gdbm tcl-tk')
        ret, out = run('brew install pyenv')
        ret, out = run('brew install pyenv-virtualenv')
    else:
        print(f'{platform.system()} unknown system')
        sys.exit(1)
    if ret == 0:
        ret, out = run(f'grep "TIMEOUT-TOOLS START" {home_directory}/{shell_rc}')
        if ret == 0:
            logging.debug("pyenv already configured in .bashrc\n")
            sys.exit(1)
        with open(f'{home_directory}/{shell_rc}', 'a') as shellrc:
            shellrc.write('\n## TIMEOUT-TOOLS START\n')
            #  shellrc.write('export PYENV_VIRTUALENV_DISABLE_PROMPT=1\n')
            shellrc.write('export PATH="$HOME/.pyenv/bin:$PATH"\n')
            shellrc.write('eval "$(pyenv init --path)"\n')
            shellrc.write('eval "$(pyenv virtualenv-init -)"\n')
            shellrc.write('\n## TIMEOUT-TOOLS END\n')
        run(f'. {home_directory}/{shell_rc}')


def python_setup_func(args):
    if not args.python_version:
        args.python_version = load_python_version()
    python_setup(args.app, args.branch, args.python_version)


def python_setup(app, branch, python_version):
    pyenv_name = f'{app}-{python_version}'
    print(f'- Creating virtualenv `{pyenv_name}`', end='', flush=True)
    run(f'pyenv install -s {python_version}')
    ret, out = run(f'pyenv virtualenv {python_version} {pyenv_name}')
    if ret != 0:
        if 'already exists' in out:
            print(' (already exists) ✅')
        else:
            print(' ❌')
            print(out)
            sys.exit(1)
    else:
        print(' ✅')
    run(f'echo {pyenv_name} > .python-version')

    init_active = f'eval "$(pyenv init -)" && pyenv activate {pyenv_name}'
    print('- Upgrading pip', end='', flush=True)
    ret, out = run(f'{init_active} && pip install -U pip')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')

    print('- Installing requirements.txt', end='', flush=True)
    ret, out = run(f'{init_active} && pip install -r requirements.txt')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')

    ret, out = run('ls requirements-dev.txt')
    if ret == 0:
        print('- Installing requirements-dev.txt', end='', flush=True)
        ret, out = run(f'{init_active} && pip install -r requirements-dev.txt')
        if ret != 0:
            print(' ❌')
            print(out)
            sys.exit(1)
        print(' ✅')

    print('- Running `pre-commit install`', end='', flush=True)
    ret, out = run(f'{init_active} && pre-commit install')
    if ret != 0:
        print(' ❌')
        print(out)
        sys.exit(1)
    print(' ✅')


def python_remove(args):
    pyenv_name = f'{args.app}-{args.branch}'
    run('rm .python-version')
    run(f'pyenv virtualenv-delete -f {pyenv_name}')


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
