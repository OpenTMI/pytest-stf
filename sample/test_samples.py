import pytest
from appium.webdriver.webdriver import WebDriver

from stf_appium_client import AppiumServer, AdbServer


def test_allocated_phone(allocated_phone: dict):
    # allocated_phone is dictionary of phone metadata
    print(allocated_phone)


def test_adb(phone_with_adb):
    # allocated phone with adb proxy
    adb, phone = phone_with_adb
    adb: AdbServer
    response = adb._execute('shell getprop ro.build.version.release', 10)
    assert response.stdout == phone.get('version'), 'Wrong Android version'


def test_appium(appium_server):
    # allocated phone with adb and appium server
    appium, adb, phone = appium_server
    appium: AppiumServer
    print(f'wd_hub: {appium.get_api_path()}')


@pytest.fixture(scope='session')
def fixture_capabilities(pytestconfig):
    values = pytestconfig.getoption('appium_capabilities')


@pytest.fixture(name='appium_args', scope='session')
def fixture_appium_args():
    # overridable list of appium server args
    # https://appium.io/docs/en/writing-running-appium/server-args/
    return []


@pytest.fixture(name='capabilities', scope='session')
def fixture_capabilities(pytestconfig, allocated_phone):
    # Allows to overwrite WebDriver arguments
    # Under the hoods these are used like `WebDriver(**kwargs)`
    kwargs = {
        "desired_capabilities": {
            'platformName': allocated_phone['platform'],
            #'udid': '', #allocated_phone['serial'],
            'automationName': 'UiAutomator2',
            'browserName': 'Chrome',
        }
    }
    yield kwargs


def test_client(appium_client):
    # allocated phone with adb+appium server + appium client (WebDriver)
    driver, appium, adb, phone = appium_client

    # adb: AdbServer instance, that is already connected
    # appium: AppiumServer instance that provide server address for appium client
    #
    driver: WebDriver
    test_url = 'https://google.com'

    driver.get(test_url)
    url = driver.current_url
    assert url == test_url, 'Wrong URL'
