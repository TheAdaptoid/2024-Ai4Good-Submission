from nicegui import ui
from Gateway import *
from Pipeline import *

def Detect_Fraud() -> None:
    ui.notify(
        message="Identifying fraudulent listings...",
        position="top",
        type="ongoing"
    )

    # Prepare data
    segments: dict[str, DataFrame] = Prepare_Data()

    # Train models
    for segmentName, segmentData in segments.items():
        Process_Segment(segmentName, segmentData)

    # Detect fraud
    currentListings: DataFrame = Get_Listings(sIndex=0, eIndex=-1)
    for index, row in currentListings.iterrows():
        currentListings.at[index, 'Price Fraud'] = Detect_Price_Fraud(row.to_frame().T)
        currentListings.at[index, 'Time Fraud'] = Detect_Time_Fraud(row.to_frame().T)

    # Update listings
    Update_Listings(currentListings)

    # Reload page
    ui.navigate.reload()

def Debug_Card(data: dict) -> None:
    fraudMarker = ""
    if data["Time Fraud"] or data["Price Fraud"]:
        fraudMarker = "background-color: maroon; opacity: 0.5;"

    with ui.card().classes("w-full flex-col flex-nowrap justify-between").style(f"{fraudMarker}"):
        ui.label(f"List Number: {data["List Number"]}")

        ui.label(f"Building Type: {data['Building Type']}")

        ui.label(f"List Price: ${data['List Price']}")

        # Fraud
        with ui.row().classes("w-full flex-row flex-nowrap justify-end items-center"):
            ui.label(f"Time Fraud: {data['Time Fraud']}")
            ui.label(f"Price Fraud: {data['Price Fraud']}")

        # Location
        with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
            ui.label(f"{data['City']}, {data['State']}")
            ui.separator().props("vertical")
            ui.label(f"{int(data['Zip Code'])}")
            ui.separator().props("vertical")
            ui.label(f"{data['County']} County")
            ui.separator().props("vertical")
            ui.label(f"{data['Latitude']}, {data['Longitude']}").classes("text-sm -mt-4")

def Admin_Page() -> None:
    for index, row in Get_Listings(sIndex=0, eIndex=100).iterrows():
        Debug_Card(row.to_dict())

    # Set the theme to dark mode
    ui.dark_mode(True)

    # Header
    with ui.header(bordered=True).classes("justify-between items-center"):

        ui.label("Fraud Dashboard").classes("text-2xl font-bold")

        ui.button(
            text="Sign Out",
            on_click=lambda: ui.navigate.to("/listings"),
            icon="logout",
        )

    # Sidebar
    with ui.right_drawer().props("width=500"):
        with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
            with ui.column().classes("w-full flex-col flex-nowrap justify-between"):
                fraudCounts = Get_Fraud_Counts()
                ui.label(f"{fraudCounts['Time']} Time Fraud Instances")
                ui.label(f"{fraudCounts['Price']} Price Fraud Instances")

            ui.button(
                text="Detect Fruadulent Listings", 
                on_click=lambda: Detect_Fraud(),
            ).classes("w-full")

        ui.separator()

    # Footer
    with ui.footer(bordered=True).classes("justify-start items-center"):
        ui.label("Powered by Adaptive Technologies Inc.")