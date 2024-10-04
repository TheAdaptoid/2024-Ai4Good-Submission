from pandas import read_json, DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import SelectKBest, f_regression
from numpy import ndarray
from statistics import mean, stdev, NormalDist
from pickle import dump, load
from os import path, makedirs
from json import dumps, loads
from datetime import date, timedelta, datetime
from Common import CONFIDENCE_INTERVAL

MODEL_DIR: str = r"Web\Backend\Models"
FEATURE_DIR: str = r"Web\Backend\Features"
DISTRIBUTION_DIR: str = r"Web\Backend\Distributions"
MOVE_IN_DIR: str = r"Web\Backend\Move_In"

ROOT_DATE: date = date(2024, 7, 31)

def Save_Model(segment: str, model: LinearRegression) -> None:
    filePath: str = f"{MODEL_DIR}/{segment}.pkl"

    if not path.exists(MODEL_DIR):
        makedirs(MODEL_DIR)

    file = open(filePath, "wb")
    dump(model, file)

def Load_Model(segment: str) -> LinearRegression | None:
    filePath: str = f"{MODEL_DIR}/{segment}.pkl"

    try:
        file = open(filePath, "rb")
        return load(file)
    except FileNotFoundError:
        return None
    
def Save_Features(segment: str, features: list[str]) -> None:
    filePath: str = f"{FEATURE_DIR}/{segment}.json"

    if not path.exists(FEATURE_DIR):
        makedirs(FEATURE_DIR)

    with open(filePath, "w") as file:
        file.write(dumps(features))

def Load_Features(segment: str) -> list[str] | None:
    filePath: str = f"{FEATURE_DIR}/{segment}.json"

    try:
        with open(filePath, "r") as file:
            return loads(file.read())
    except FileNotFoundError:
        return None
    
def Save_Dist(segment: str, distribution: dict[str, list[float]|float]) -> None:
    filePath: str = f"{DISTRIBUTION_DIR}/{segment}.json"

    if not path.exists(DISTRIBUTION_DIR):
        makedirs(DISTRIBUTION_DIR)

    with open(filePath, "w") as file:
        file.write(dumps(distribution))

def Load_Dist(segment: str) -> dict[str, list[float]|float] | None:
    filePath: str = f"{DISTRIBUTION_DIR}/{segment}.json"

    try:
        with open(filePath, "r") as file:
            return loads(file.read())
    except FileNotFoundError:
        return None
    
def Save_Move_In(segment, moveInData: dict[str, list[float] | float]) -> None:
    filePath: str = f"{MOVE_IN_DIR}/{segment}.json"

    if not path.exists(MOVE_IN_DIR):
        makedirs(MOVE_IN_DIR)

    with open(filePath, "w") as file:
        file.write(dumps(moveInData))

def Load_Move_In(segment: str) -> dict[str, list[float] | float] | None:
    filePath: str = f"{MOVE_IN_DIR}/{segment}.json"

    try:
        with open(filePath, "r") as file:
            return loads(file.read())
    except FileNotFoundError:
        return None

def Prepare_Data() -> dict[str, DataFrame]:
    # Load data
    data: DataFrame = read_json(r"Web\Backend\Rental_Data.json").sample(frac=0.8)

    # Create market segmentations
    segments: dict[str, DataFrame] = {
        buildingType: data[data["Building Type"] == buildingType] for buildingType in data["Building Type"].unique()
    }

    return segments

def Train_Linear_Model(data: DataFrame) -> tuple[LinearRegression, list[str], float]:
    inputFeatures: DataFrame = data[[
        "Zip Code", "Living Area", "Bedrooms Total", "Bathrooms Full", "Bathrooms Total", "Bathrooms Half",
        "Garage Spaces", "Waterfront YN", "Days on Market", "Year Built", "List Price"
    ]].dropna()
    target: list[float] = list(inputFeatures["List Price"])
    inputFeatures = inputFeatures.drop(columns=["List Price"])

    # Select best features
    selector: SelectKBest = SelectKBest(score_func=f_regression, k=5)
    selector.fit(inputFeatures, target)
    outputFeatures: list[str] = list(selector.get_feature_names_out())

    # Train model
    model: LinearRegression = LinearRegression()
    model.fit(inputFeatures[outputFeatures], target)

    # Calculate R-Squared
    rScore: float = model.score(inputFeatures[outputFeatures], target)

    return model, outputFeatures, rScore

def Calculate_Price_Distribution(data: DataFrame, model: LinearRegression, features: list[str]) -> dict[str, float]:
    # Use selected features
    selectedFeatures: DataFrame = data[features]

    # Predict prices
    expectedPrices: ndarray = model.predict(selectedFeatures)
    differences: ndarray = expectedPrices - data["List Price"]

    # Calculate statistics
    return {
        "Mean": mean(differences),
        "Stdev": stdev(differences),
    }

def Calculate_Timing_Distribution(data: DataFrame) -> dict[str, float]:
    moveInWindows: list[int] = []
    selectedFeatures: DataFrame = data[[
        'Days on Market', 'Availability Date'
    ]].dropna()

    for index, row in selectedFeatures.iterrows():
        # Calculate the listing date
        listingDate: date = ROOT_DATE - timedelta(days=row["Days on Market"])

        # Calculate the move in date
        moveInDate: date = datetime.fromisoformat((row["Availability Date"])).date()

        # Calculate the move in window
        moveInWindow: int = (moveInDate - listingDate).days
        if moveInWindow > 0:
            moveInWindows.append(moveInWindow)

    # Calculate statistics
    return {
        "Mean": mean(moveInWindows),
        "Stdev": stdev(moveInWindows),
    }

def Process_Segment(segmentName: str, segmentData: DataFrame) -> None:
    # Train pricing model
    linearModel, selectedFeatures, rScore = Train_Linear_Model(segmentData)
    priceDist: dict[str, float] = Calculate_Price_Distribution(segmentData, linearModel, selectedFeatures)
    priceDist["R-Squared"] = rScore

    # Save Linear Model
    Save_Model(segmentName, linearModel)
    Save_Features(segmentName, selectedFeatures)
    Save_Dist(segmentName, priceDist)

    # Train timing model
    timingDist: dict[str, float] = Calculate_Timing_Distribution(segmentData)
    Save_Move_In(segmentName, timingDist)

def Get_Fraud_Counts() -> dict[str, int]:
    data: DataFrame = read_json(r"Web\Backend\Rental_Data.json")

    counter = 0
    for index, row in data.iterrows():
        if row["Price Fraud"] < CONFIDENCE_INTERVAL and row["Time Fraud"] < CONFIDENCE_INTERVAL:
            counter += 1

    return {
        "Price": data[data["Price Fraud"] < CONFIDENCE_INTERVAL].shape[0],
        "Time": data[data["Time Fraud"] < CONFIDENCE_INTERVAL].shape[0],
        "Total": counter
    }

def Detect_Price_Fraud(listingData: DataFrame) -> float:
    if listingData.dropna().shape[0] == 0:
        return 1
    
    buildingType: str = listingData["Building Type"].values[0]

    # Load data
    model: LinearRegression = Load_Model(buildingType)
    features: list[str] = Load_Features(buildingType)
    distribution: dict[str, float] = Load_Dist(buildingType)

    # Calculate expected price
    expectedPrice: float = model.predict(listingData[features])[0]

    # Calculate Z Score
    mean: float = distribution["Mean"]
    stdev: float = distribution["Stdev"]
    zScore: float = ((expectedPrice - listingData["List Price"].values[0]) - mean) / stdev
    percentile: float = NormalDist().cdf(zScore)

    return percentile if expectedPrice < listingData["List Price"].values[0] else 1

def Detect_Time_Fraud(listingData: DataFrame) -> float:
    relevantData: DataFrame = listingData[[
        'Days on Market', 'Availability Date'
    ]].dropna()
    if relevantData.shape[0] == 0:
        return 1

    # Load data
    distribution: dict[str, float] = Load_Move_In(listingData["Building Type"].values[0])

    # Calculate Listing Date
    listingDate: date = ROOT_DATE - timedelta(days=relevantData["Days on Market"].values[0])

    # Calculate Move In Date
    moveInDate: date = datetime.fromisoformat((relevantData["Availability Date"].values[0])).date()

    # Calculate Move In Window
    moveInWindow: int = (moveInDate - listingDate).days

    # Calculate Z Score
    mean: float = distribution["Mean"]
    stdev: float = distribution["Stdev"]
    zScore: float = ((moveInWindow - mean) / stdev)
    percentile: float = NormalDist().cdf(zScore)

    return percentile if moveInWindow < mean else 1