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
        default=1000,
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


@pytest.fixture(name='allocated_phone', scope="session")
def fixture_allocated_phone(pytestconfig):
    """
    Allocate required phone via STF.
    Yields device details as dict.
    e.g.
    {
        "abi": "arm64-v8a",
        "airplaneMode": false,
        "battery": {...},
        "browser": {...},
        "cpuPlatform": "...",
        "manufacturer": "...",
        "marketName": "Pixel 4",
        "model": "Pixel 4",
        "network": {...},
        "platform": "Android",
        "sdk": "32",
        "serial": "...",
        "version": "12",
        ...
    }
    """
    assert hasattr(pytestconfig, '_openstf'), 'stf_host or stf_token missing'

    stf = pytestconfig._openstf  # pylint: disable=protected-access
    stf  # type=StfClient
    requirements = pytestconfig.getoption('phone_requirements')
    timeout = pytestconfig.getoption('stf_allocation_timeout')
    assert requirements, 'phone_requirements required'
    requirements = parse_requirements(requirements)

    with stf.allocation_context(requirements, timeout_seconds=timeout) as device:
        yield device


@pytest.fixture(name='phone_with_adb', scope="session")
def fixture_phone_with_adb(allocated_phone):
    """
    Allocate required phone and create ADB tunnel to phone via STF.
    Yields tuple (adb: AdbServer, device: dict)
    """
    with AdbServer(allocated_phone['remote_adb_url']) as adb:
        yield allocated_phone, adb


@pytest.fixture(name="appium_server", scope="session")
def fixture_appium_server(phone_with_adb):
    """
    Allocate required phone, create ADB tunnel to phone via STF and start appium server for tests.
    Yields tuple (appium: Appium, adb: AdbServer, device: dict )
    """
    phone, adb = phone_with_adb
    with Appium() as appium:
        yield appium, adb, phone


@pytest.fixture(name='capabilities')
def fixture_capabilities(pytestconfig, allocated_phone):
    capabilities = {
        "platformName": allocated_phone['platform'],
        'udid': allocated_phone['serial'],
    }
    yield capabilities

@pytest.fixture(name="appium_client", scope="session")
def fixture_appium_client(appium_server, capabilities):
    yield appium, adb, phone


@pytest.fixture(name="selected_phone", scope="session")
def fixture_selected_phone(appium_server):
    """
    Alternative for appium_server -fixture except tuple is in different order:
    (device, adb, appium)
    """
    appium, adb, device = appium_server
    yield device, adb, appium
