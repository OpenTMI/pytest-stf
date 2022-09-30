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
        help="OpenSTF host",
    )
    group.addoption(
        "--stf_token",
        default=os.environ.get('OPENSTF_TOKEN', None),
        help="OpenSTF access token",
    )
    group.addoption(
        "--phone_requirements",
        help="Phone requirements",
    )
    group.addoption(
        "--stf_allocation_timeout",
        default=StfClient.DEFAULT_ALLOCATION_TIMEOUT_SECONDS,
        help="Maximum time in seconds after which STF releases allocated devices",
    )
    group.addoption(
        "--appium_server",
        default='http://localhost:4723',
        help="Appium server API URL"
    )
    group.addoption(
        "--appium_capabilities",
        help="Appium capabilities"
    )
    group.addoption(
        "--appium_logs",
        help="Appium server log file path"
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
        # set allocation resource list file to None when using OpenSTF
        if not config.option.allocation_requirements:
            config.option.allocation_resource_list_file = None


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
def fixture_allocated_phone(pytestconfig, lockable):
    """
    1) Allocate a required phone via STF or lockable
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
    requirements = pytestconfig.getoption('phone_requirements')
    assert requirements, 'phone_requirements required'
    assert 'platform' in requirements, 'platform required'

    allocation_timeout = pytestconfig.getoption('allocation_timeout')

    if hasattr(pytestconfig, '_openstf'):
        stf = pytestconfig._openstf  # pylint: disable=protected-access
        stf  # type=StfClient
        timeout = pytestconfig.getoption('stf_allocation_timeout')
        requirements = parse_requirements(requirements)

        with stf.allocation_context(requirements,
                                    wait_timeout=allocation_timeout,
                                    timeout_seconds=timeout) as device:
            yield device
    else:
        with lockable.auto_lock(requirements, allocation_timeout) as device:
            yield device


@pytest.fixture(name='phone_with_adb', scope="session")
def fixture_phone_with_adb(pytestconfig, allocated_phone):
    """
    1) Allocate a required phone via STF or lockable
    2) Create an ADB tunnel to phone if using STF
    Yields tuple (adb: AdbServer, device: dict)
    """
    if hasattr(pytestconfig, '_openstf'):
        with AdbServer(allocated_phone['remote_adb_url']) as adb:
            yield adb, allocated_phone
    else:
        yield None, allocated_phone


@pytest.fixture(name='appium_args', scope='session')
def fixture_appium_args(pytestconfig):
    # overridable list of appium server args
    args = []
    logs_file = pytestconfig.getoption('appium_logs')
    if logs_file:
        args.extend(['--log', logs_file])
    return args


@pytest.fixture(name="appium_server", scope="session")
def fixture_appium_server(pytestconfig, phone_with_adb, appium_args):
    """
    1) Allocate a required phone via STF or lockable
    2) Create an ADB tunnel to phone if using STF
    3) Start Appium server or use remote one if requested
    Yields tuple (appium: AppiumServer|RemoteAppiumServer, adb: AdbServer, device: dict )
    """
    adb, phone = phone_with_adb
    if adb:
        with AppiumServer(appium_args) as appium:
            yield appium, adb, phone
    else:
        appium_api_path = phone.get(
            'appium_server') or pytestconfig.getoption('appium_server')

        class RemoteAppiumServer:
            def get_api_path(self):
                return appium_api_path
        yield RemoteAppiumServer(), adb, phone


@pytest.fixture(name='capabilities', scope='session')
def fixture_capabilities(pytestconfig, allocated_phone):
    """
    Arguments passed to Appium client which tests can override with own fixture.
    By default simply contains a desired capability for device platform.
    Yields appium webdriver kwargs as dict.
    """
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
    """
    1) Allocate a required phone via STF or lockable
    2) Create an ADB tunnel to phone if using STF
    3) Start Appium server or use remote one if requested
    4) Start Appium webdriver client
    Yields tuple (driver: WebDriver, appium: AppiumServer|RemoteAppiumServer, adb: AdbServer, device: dict)
    """
    appium, adb, phone = appium_server
    client = AppiumClient(
        command_executor=appium.get_api_path(), **capabilities)
    with client as driver:
        driver: WebDriver
        yield driver, appium, adb, phone
