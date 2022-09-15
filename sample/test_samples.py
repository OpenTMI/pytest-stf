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


def test_client(appium_client):
    # allocated phone with adb+appium server + appium client (WebDriver)
    client, appium, adb, phone = appium_client

    # adb: AdbServer instance, that is already connected
    # appium: AppiumServer instance that provide server address for appium client
    #
    client: WebDriver
    test_url = 'https://google.com'

    client.get(test_url)
    url = client.current_url
    assert url == test_url, 'Wrong URL'
