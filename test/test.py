from unittest import mock
import pytest
from pytest import Pytester


@pytest.fixture()
def example(pytester):
    pytester.makefile(".py", test_sample="""
        def test_create(selected_phone):
            device, adb, appium = selected_phone
            assert device == {"platform": "Android", "remote_adb_url": "localhost"}
            assert adb.port == 5037
            assert appium.port > 0
    """)


def test_plugin(pytester: Pytester, example):
    """Make sure that our plugin works."""
    # run all tests with pytest
    with mock.patch('stf_appium_client.StfClient.connect') as connect, \
         mock.patch('stf_appium_client.StfClient.allocation_context') as allocation_context, \
         mock.patch('stf_appium_client.AdbServer.connect') as adb_start, \
         mock.patch('stf_appium_client.Appium.start') as appium_start, \
         mock.patch('stf_appium_client.Appium.stop') as appium_stop, \
         mock.patch('stf_appium_client.Appium.get_wd_hub_uri'):

        allocation_context.return_value.__enter__.return_value = {
            "platform": "Android",
            "remote_adb_url": "localhost"}
        result = pytester.runpytest('--stf_host=.', '--stf_token=abc', '--phone_requirements=platform=Android')

    connect.assert_called_once_with('abc')
    allocation_context.assert_called_once_with({'platform': 'Android'}, timeout_seconds=10)
    adb_start.assert_called_once_with()
    appium_start.assert_called_once_with()
    appium_stop.assert_called_once_with()

    # check that all test passed
    result.assert_outcomes(passed=1)
