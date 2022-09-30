from unittest import mock
import pytest
from pytest import Pytester


@pytest.fixture()
def example_stf(pytester):
    pytester.makefile(".py", test_sample="""
        def test_create(appium_client):
            driver, appium, adb, phone = appium_client
            assert phone == {"platform": "Android", "remote_adb_url": "localhost"}
            assert adb.port == 5037
            assert appium.port > 0
    """)


@pytest.fixture()
def example_local(pytester):
    pytester.makefile(".py", test_sample="""
        def test_create(appium_client):
            driver, appium, adb, phone = appium_client
            assert phone == {"platform": "Android"}
            assert adb is None
    """)


def test_plugin_stf(pytester: Pytester, example_stf):
    """Make sure the plugin works with STF"""
    # run all tests with pytest
    with mock.patch('stf_appium_client.StfClient.StfClient.connect') as connect, \
         mock.patch('stf_appium_client.StfClient.StfClient.allocation_context') as allocation_context, \
         mock.patch('stf_appium_client.AdbServer.AdbServer.connect') as adb_start, \
         mock.patch('stf_appium_client.AppiumServer.AppiumServer.start') as appium_server_start, \
         mock.patch('stf_appium_client.AppiumServer.AppiumServer.stop') as appium_server_stop, \
         mock.patch('stf_appium_client.AppiumServer.AppiumServer.get_api_path'), \
         mock.patch('stf_appium_client.AppiumClient.AppiumClient.start') as appium_client_start, \
         mock.patch('stf_appium_client.AppiumClient.AppiumClient.stop') as appium_client_stop:

        allocation_context.return_value.__enter__.return_value = {
            "platform": "Android",
            "remote_adb_url": "localhost"}
        result = pytester.runpytest('--stf_host=.', '--stf_token=abc', '--phone_requirements=platform=Android')

    connect.assert_called_once_with('abc')
    allocation_context.assert_called_once_with({'platform': 'Android'}, timeout_seconds=1000)
    adb_start.assert_called_once_with()
    appium_server_start.assert_called_once_with()
    appium_server_stop.assert_called_once_with()
    appium_client_start.assert_called_once_with()
    appium_client_stop.assert_called_once_with()

    # check that all test passed
    result.assert_outcomes(passed=1)


def test_plugin_local(pytester: Pytester, example_local):
    """Make sure the plugin works with a local device"""
    # run all tests with pytest
    with mock.patch('lockable.lockable.create_provider'), \
         mock.patch('pytest_lockable.plugin.Lockable.auto_lock') as auto_lock, \
         mock.patch('stf_appium_client.AppiumClient.AppiumClient.start') as appium_client_start, \
         mock.patch('stf_appium_client.AppiumClient.AppiumClient.stop') as appium_client_stop:

        auto_lock.return_value.__enter__.return_value = {
            "platform": "Android"
        }
        result = pytester.runpytest('--phone_requirements=platform=Android')
        print(result)

    auto_lock.assert_called_once_with('platform=Android', 10)
    appium_client_start.assert_called_once_with()
    appium_client_stop.assert_called_once_with()

    # check that all test passed
    result.assert_outcomes(passed=1)
