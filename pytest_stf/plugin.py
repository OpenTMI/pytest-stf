import os
import pytest
from stf_appium_client.StfClient import StfClient
from stf_appium_client.tools import parse_requirements
from stf_appium_client.AdbServer import AdbServer
from stf_appium_client.AppiumServer import AppiumServer
from stf_appium_client.AppiumClient import AppiumClient
from appium.webdriver.webdriver import WebDriver


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
    group.addoption(
        "--appium_capabilities",
        help="Appium capabilities"
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
        yield adb, allocated_phone


@pytest.fixture(name='appium_args', scope='session')
def fixture_appium_args():
    # overridable list of appium server args
    return []

@pytest.fixture(name="appium_server", scope="session")
def fixture_appium_server(phone_with_adb, appium_args):
    """
    Allocate required phone, create ADB tunnel to phone via STF and start appium server for tests.
    Yields tuple (appium: Appium, adb: AdbServer, device: dict )
    """
    adb, phone = phone_with_adb
    with AppiumServer(appium_args) as appium:
        yield appium, adb, phone


@pytest.fixture(name='capabilities', scope='session')
def fixture_capabilities(pytestconfig, allocated_phone):
    kwargs = {
        "desired_capabilities": {
            'platformName': allocated_phone['platform']
        }
    }
    extra_capabilities = pytestconfig.getoption('appium_capabilities')
    if extra_capabilities:
        extra_capabilities = parse_requirements(extra_capabilities)
        kwargs['desired_capabilities'].update(extra_capabilities)
    yield kwargs


@pytest.fixture(name="appium_client", scope="session")
def fixture_appium_client(appium_server, capabilities):
    appium, adb, phone = appium_server
    client = AppiumClient(command_executor=appium.get_api_path(), **capabilities)
    with client as driver:
        driver: WebDriver
        yield driver, appium, adb, phone
