import os
import pytest
from stf_appium_client import StfClient
from stf_appium_client.tools import parse_requirements
from stf_appium_client.AdbServer import AdbServer
from stf_appium_client.Appium import Appium


def pytest_addoption(parser):
    """
    add option hook
    :param parser: argparser
    :return: None
    """
    group = parser.getgroup("openstf")
    group.addoption(
        "--stf_host",
        default=os.environ.get('OPENSTF_HOST', None),
        help="Openstf host",
    )
    group.addoption(
        "--stf_token",
        default=os.environ.get('OPENSTF_TOKEN', None),
        help="Openstf access token",
    )
    group.addoption(
        "--phone_requirements",
        help="Phone requirements",
    )
    group.addoption(
        "--stf_allocation_timeout",
        default=10,
        help="Allocation timeout",
    )


def pytest_configure(config):
    """
    configure hook
    :param config: unused
    :return: None
    """
    host = config.getoption("stf_host")
    token = config.getoption("stf_token")
    if host and token:
        config._openstf = StfClient(host)  # pylint: disable=protected-access
        config._openstf.connect(token)  # pylint: disable=protected-access


def pytest_unconfigure(config):
    """
    unconfigure hook
    :param config: unused
    :return: None
    """
    openstf = getattr(config, "_openstf", None)
    if openstf:
        del config._openstf  # pylint: disable=protected-access


@pytest.fixture(name="selected_phone", scope="session")
def fixture_selected_phone(pytestconfig):
    """
    Allocate required phone, create ADB tunnel to phone via STF and start appium server for tests.
    Yields tuple (device: dict, adb: AdbServer, appium: Appium)
    """
    assert hasattr(pytestconfig, '_openstf'), 'stf_host or stf_token missing'

    stf = pytestconfig._openstf  # pylint: disable=protected-access
    stf  # type=StfClient
    requirements = pytestconfig.getoption('phone_requirements')
    timeout = pytestconfig.getoption('stf_allocation_timeout')
    assert requirements, 'phone_requirements required'
    requirements = parse_requirements(requirements)

    with stf.allocation_context(requirements, timeout_seconds=timeout) as device:
        with AdbServer(device['remote_adb_url']) as adb:
            with Appium() as appium:
                yield device, adb, appium
