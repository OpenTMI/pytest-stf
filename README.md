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
def test_create(selected_phone):
    device, adb, appium = selected_phone
    # device is dictionary of device metadata
    # adb: AdbServer instance, that is already connected
    # appium: AppiumServer instance that provide server address for appium client
    print(device)
    print(f'wd_hub: {appium.get_wd_hub_uri()}')
    
```

Execution
```
> pytest sample/test_samples.py --stf_host localhost --stf_token $TOKEN --phone_requirements platform=Android
```
