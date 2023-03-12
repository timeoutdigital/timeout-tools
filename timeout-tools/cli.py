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

    parser_init = subparsers.add_parser(
        'pyenv-install',
        help='install pyenv',
    )
    parser_init.set_defaults(func=pyenv_install)

    args = parser.parse_args()
    if len(vars(args)) == 1:
        parser.print_help()
        sys.exit(0)
    args.func(args)


def pyenv_install(args):
    home_directory = os.path.expanduser('~')
    res = subprocess.run(
        f'ls -d {home_directory}/.pyenv',
        capture_output=True,
        shell=True,
    )
    if res.returncode == 0:
        print("$HOME/.pyenv already exists")
        sys.exit(1)

    if platform.system() == 'Linux':
        res = subprocess.run(
            'curl -s https://pyenv.run | bash',
            capture_output=True,
            shell=True,
        )
    elif platform.system() == 'macOS':
        res = subprocess.run(
            'brew install pyenv && brew install pyenv-virtualenv',
            capture_output=True,
            shell=True,
        )
    if res.returncode == 0:
        res = subprocess.run(
            f'grep "TIMEOUT-TOOLS PYENV" {home_directory}/.bashrc',
            capture_output=True,
            shell=True,
        )
        if res.returncode == 0:
            print("pyenv already configured in .bashrc\n")
            sys.exit(1)
        with open(f'{home_directory}/.bashrc', 'a') as bashrc:
            bashrc.write('\n## TIMEOUT-TOOLS PYENV\n')
            bashrc.write('export PATH="$HOME/.pyenv/bin:$PATH"\n')
            bashrc.write('eval "$(pyenv init --path)"\n')
            bashrc.write('eval "$(pyenv virtualenv-init -)"\n')



if __name__ == '__main__':
    main()
