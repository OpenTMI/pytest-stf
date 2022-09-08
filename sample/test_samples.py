def test_create(selected_phone):
    device, adb, appium = selected_phone
    print(device)
    print(f'wd_hub: {appium.get_wd_hub_uri()}')
