def make_device_info_str(device_info: dict) -> str:
    device_info_str = ""
    for key, value in device_info.items():
        device_info_str += f"{key}:{value}||"
    return device_info_str


def parse_device_info(device_info_str: str) -> dict:
    device_info = {}
    device_info_list = device_info_str.split("||")
    for device_info_item in device_info_list:
        key, value = device_info_item.split(":")
        device_info[key] = value
    return device_info
