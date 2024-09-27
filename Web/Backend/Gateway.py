from json import dumps, loads

def Load_Json(filepath: str) -> dict|list:
    with open(filepath, "r") as file:
        return loads(file.read())
