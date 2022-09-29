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
                        Maximum time in seconds after which STF releases allocated devices
  --appium_server=APPIUM_SERVER
                        Appium server API URL
  --appium_capabilities=APPIUM_CAPABILITIES
                        Appium capabilities
  --appium_logs=APPIUM_LOGS
                        Appium server log file path
```

## Fixtures

### `allocated_phone`

- Session scoped
- Find and allocate a phone based on `--phone_requirements` cli argument from STF or using pytest-lockable

**NOTE:** only one phone is handled by this fixture.

### `phone_with_adb`

- Session scoped
- Depends on `allocated_phone`
- Create ADB tunnel to phone if using STF

**NOTE:** `Android SDK` (commandline tools, platform tools and build tools) need to be installed separately!

### `appium_server`

- Session scoped
- Depends on `phone_with_adb`
- Start Appium server or alternatively use remote one passed via `--appium_server` cli argument or `appium_server` lockable resource property

**NOTE:** `appium` need to be installed separately! (`npm i appium`) .

### `appium_client`

- Session scoped
- Depends on `appium_server`
- Start Appium webdriver client

### `capabilities`

- Session scoped
- Returns arguments passed to Appium webdriver
- Tests can override this fixture in order to pass custom arguments

### `appium_args`

- Session scoped
- Returns arguments passed to Appium server
- Tests can override this fixture in order to pass custom arguments

## Usage example

*sample.py:*

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

Execution:
```
> pytest sample/test_samples.py --stf_host localhost --stf_token $TOKEN --phone_requirements platform=Android
```


See more examples from [sample/test_samples.py](sample/test_samples.py).

Custom capabilities:
```
> pytest --appium_capabilities cab=val1&cab=val2
```

### Usage with local devices

Testing with a local device you can omit `--stf_host` and `--stf_token` cli arguments and use lockable resources file (defaults to `resources.json`).

`resources.json` example:
```
[
  {
    "id": "1",
    "type": "Phone",
    "platform": "Android",
    "online": true,
    "hostname": <HOSTNAME>,
    "version": "12",
    "appium_server": "http://localhost:4723"
  }
]
```

Execution:
```
> pytest sample/test_samples.py --phone_requirements platform=Android
```

**NOTE:** Appium server need to be run separately! (`appium -a 127.0.0.1`)
