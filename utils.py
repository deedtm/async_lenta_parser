import json


def save_to_json(filename: str, value: dict | list):
    with open(f"{filename}.json", 'w') as f:
        json.dump(value, f, ensure_ascii=False, indent=4)
        