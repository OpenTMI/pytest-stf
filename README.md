[![pytest-stf](https://github.com/OpenTMI/pytest-stf/actions/workflows/test.yml/badge.svg)](https://github.com/OpenTMI/pytest-stf/actions/workflows/test.yml) [![PyPI version](https://badge.fury.io/py/pytest-stf.svg)](https://pypi.org/project/pytest-stf/)


## pytest plugin for OpenSTF

Plugin for simplify [OpenSTF](https://github.com/DeviceFarmer/stf) usage with pytest 
framework by providing simple fixture that do all primitive tasks for appium based tests.

Target is to easily scale up tests in CI environment where external stf service is used to 
provide android phones.

Plugin based on [stf-appium-python-client](https://github.com/OpenTMI/stf-appium-python-client)


## pytest arguments
```
openstf:
  --stf_host=STF_HOST   Openstf host
  --stf_token=STF_TOKEN
                        Openstf access token
  --phone_requirements=PHONE_REQUIREMENTS
                        Phone requirements
  --stf_allocation_timeout=STF_ALLOCATION_TIMEOUT
                        Allocation timeout (how long time plugin waits for device)
```


## Fixture `selected_phone`

is `session` scoped fixture that find out suitable android phone based on cli arguments, 
prepare remote adb connection and starts appium server that tests could utilize eventually.

**NOTE:** `appium` need to be installed separately! (`npm i appium`) .

**NOTE:** only one phone is handled by this fixture.

## Usage example

Test script: sample.py

```python

from appium.webdriver.webdriver import WebDriver


def test_create(appium_client):
    client, appium, adb, phone = appium_client
    # device is dictionary of device metadata
    # adb: AdbServer instance, that is already connected
    # appium: AppiumServer instance that provide server address for appium client
    print(phone)
    print(f'wd_hub: {appium.get_api_path()}')
    
    client: WebDriver
    client, *_ = appium_client
    URL = 'https://google.com'
    client.get(URL)
    url = client.current_url
    assert url == URL, 'Wrong URL'
```

Execution
```
> pytest sample/test_samples.py --stf_host localhost --stf_token $TOKEN --phone_requirements platform=Android
```


See more examples from [sample/test_samples.py](sample/test_samples.py).

custom capabilities:
```
> pytest --appium_capabilities cab=val1&cab=val2
```
