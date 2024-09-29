from json import dumps, loads
from pandas import DataFrame, read_json
from random import choice

def Report_Listing(listNumber: str) -> None:
    with open(r"Web\Backend\Reports.json", "r") as file:
        data: dict[str, int] = loads(file.read())

    if listNumber in data:
        data[listNumber] += 1
    else:
        data[listNumber] = 1

    with open(r"Web\Backend\Reports.json", "w") as file:
        file.write(dumps(data))

def Get_Reports() -> dict[str, int]:
    with open(r"Web\Backend\Reports.json", "r") as file:
        return loads(file.read())


def Load_Json(filepath: str) -> dict|list:
    with open(filepath, "r") as file:
        return loads(file.read())
    
def Update_Listings(data: DataFrame) -> None:
    with open(r"Web\Backend\Rental_Data.json", "w") as file:
        file.write(data.to_json(orient="records", date_format="iso"))
    print("Listings Updated!")

def Get_Listings(sIndex: int = 0, eIndex: int = 10, cityName: str = None, buildingType: str = None, bedrooms: int = None) -> DataFrame:
    rentalData: DataFrame = read_json(r"Web\Backend\Rental_Data.json")

    # clamp
    if sIndex < 0:
        sIndex = 0
    if eIndex > len(rentalData) or eIndex < 0:
        eIndex = len(rentalData) - 1

    if cityName is not None:
        rentalData = rentalData[rentalData["City"] == cityName]

    if buildingType is not None:
        rentalData = rentalData[rentalData["Building Type"] == buildingType]

    if bedrooms is not None:
        rentalData = rentalData[rentalData["Bedrooms Total"] == bedrooms]
    if bedrooms == 5:
        rentalData = rentalData[rentalData["Bedrooms Total"] >= 5]

    return rentalData[sIndex:eIndex]

def Get_Cities() -> list[str]:
    cities: list[str] = Load_Json(r"Web\Backend\Cities.json")
    return cities

def Get_Building_Types() -> list[str]:
    types: list[str] = Load_Json(r"Web\Backend\Types.json")
    return types

def Get_Random_Image() -> str:
    import os
    imageDir: str = r"Web\Backend\Images"
    imageFiles: list[str] = os.listdir(imageDir)
    imagePaths: list[str] = [
        os.path.join(imageDir, imageFile) for imageFile in imageFiles
    ]

    return choice(imagePaths)
