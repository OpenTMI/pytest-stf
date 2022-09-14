from time import sleep
from appium import webdriver
from appium.options.android import UiAutomator2Options

def test_adb(phone_with_adb):
    phone, adb = phone_with_adb
    print(phone)
    sleep(100)


def test_appium(appium_server):
    appium, adb, phone = appium_server
    print(phone)
    #print(adb._execute('devices'))
    print(f'wd_hub: {appium.get_wd_hub_uri()}')


    options = UiAutomator2Options()
    options.platform_name = phone['platform']
    options.platform_Version = phone['version']
    #options.udid = phone['serial']
    options.set_capability("browser_name", "Browser")
    driver = webdriver.Remote(appium.get_wd_hub_uri(), options=options)

    print(driver)

    driver.quit()

