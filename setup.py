from setuptools import setup

setup(
    name='timeout-tools',
    version='0.1',
    description='Tools for devs',
    author='Keith Harvey',
    author_email='sysadmin@timeout.com',
    packages=['timeout-tools'],
    install_requires=[
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'timeout-tools = timeout-tools.cli:main'
        ]
    },
)
