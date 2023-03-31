from unittest import mock

import pytest

from ..cli import (PyEnvFailure, check_python_version_available,
                   check_python_version_installed, install_python_version)


def test_check_python_version_installed_success():
    mock_run = mock.Mock()
    mock_run.return_value = (
        0,
        '   3.7.9\n   3.10.10\n   3.10.11'
    )

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '3.10.10'
        try:
            check_python_version_installed(python_version)
        except Exception:
            pytest.fail(f'Error checking version installed {python_version}')

        mock_run.assert_called_with('pyenv versions --bare --skip-aliases')


def test_check_python_version_installed_cmd_exception():

    mock_run = mock.Mock()
    mock_run.return_value = (1, "")

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '3.10.10'
        with pytest.raises(PyEnvFailure) as e:
            check_python_version_installed(python_version)
        assert e.value.args[0]['message'] == 'Failed to run'

        mock_run.assert_called_with('pyenv versions --bare --skip-aliases')


def test_check_python_version_available_success():
    mock_run = mock.Mock()
    mock_run.return_value = (
        0,
        '   3.7.9\n   3.10.10\n   3.10.11'
    )

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '3.10.10'
        try:
            check_python_version_available(python_version)
        except Exception:
            pytest.fail(f'Error checking {python_version}')

        mock_run.assert_called_with('pyenv install --list')


def test_check_python_version_available_cmd_exception():

    mock_run = mock.Mock()
    mock_run.return_value = (1, "")

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '3.10.10'
        with pytest.raises(PyEnvFailure) as e:
            check_python_version_available(python_version)
        assert e.value.args[0]['message'] == 'Failed to run'

        mock_run.assert_called_with('pyenv install --list')


def test_check_python_version_available_version_missing_exception():

    mock_run = mock.Mock()
    mock_run.return_value = (
        0,
        '   3.7.9\n   3.10.10\n   3.10.11'
    )

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '0.0.0'
        with pytest.raises(PyEnvFailure) as e:
            check_python_version_available(python_version)
        assert e.value.args[0]['message'] == 'Pyenv requires update'

        mock_run.assert_called_with('pyenv install --list')


def test_install_python_version_success():

    mock_run = mock.Mock()
    mock_run.return_value = (0, "")

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '3.10.10'
        try:
            install_python_version(python_version)
        except Exception:
            pytest.fail(f'Error installing {python_version}')

        mock_run.assert_called_with(f'pyenv install {python_version}')


def test_install_python_version_exception():

    mock_run = mock.Mock()
    mock_run.return_value = (1, "")

    with mock.patch('timeout_tools.cli.run', mock_run):
        python_version = '0.0.0'
        with pytest.raises(BaseException) as e:
            install_python_version(python_version)
        assert str(e.value) == f'Failed to install python version {python_version}'

        mock_run.assert_called_with(f'pyenv install {python_version}')
