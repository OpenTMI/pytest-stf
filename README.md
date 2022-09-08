## pytest plugin for OpenSTF

Plugin to simplify STF usage with pytest framework by providing simple fixture that do 
all primitive tasks for appium based tests.

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
                        Allocation timeout
```

## Usage example

Test script: sample.py
```python
def test_create(selected_phone):
    device, adb, appium = selected_phone
    print(device)
    print(f'wd_hub: {appium.get_wd_hub_uri()}')
    
```

Execution
```
pytest sample.py --stf_host localhost --stf_token $TOKEN --phone_requirements platform=Android
```
