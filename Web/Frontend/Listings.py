from nicegui import ui
from Gateway import *
from pandas import DataFrame
from Common import CONFIDENCE_INTERVAL, TRUE_NOW
from datetime import date, timedelta

@ui.refreshable
def Listing_Details(data: dict) -> ui.element:
    with ui.column().classes("w-full h-full flex-col flex-nowrap justify-start"):
        # Image
        ui.image(source=data["Image"]).classes("w-full basis-1/4")

        # Type and Location
        ui.label(f"{data['Building Type']}").classes("text-xl")
        with ui.row().classes("w-full flex-row flex-nowrap justify-between -mt-4"):
            ui.label(f"{data['City']}, {data['State']} | {int(data['Zip Code'])}").classes("text-sm")
            ui.label(f"{data['County']} County").classes("text-sm")
        ui.separator()

        # Dates
        with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
            ui.label(f"Listed on {TRUE_NOW - timedelta(days=data['Days on Market'])}").classes("text-xl")
            ui.label(f"Available on {str(data['Availability Date']).split('T')[0]}").classes("text-xl")

        # Price
        with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
            ui.label(f"${data['List Price']:,} / month").classes("text-2xl")
            ui.button("Contact Agent", icon="mail", on_click=lambda: ui.notify("Not Implemented"))

        # Details
        with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
            ui.label(f"{data['Bedrooms Total']} Bedrooms")
            ui.label(f"{data['Bathrooms Full']} Full Bathrooms")
            ui.label(f"{int(data['Bathrooms Half'])} Half Bathrooms")
        ui.label(f"{data['Living Area']:,} Square Feet").classes("text-lg")

        ui.space()
        
        # Fraud
        with ui.row().classes("w-full flex-row flex-nowrap justify-end items-center"):
            if data["Time Fraud"] <= CONFIDENCE_INTERVAL and data["Price Fraud"] <= CONFIDENCE_INTERVAL:
                ui.label("This listing might be fraudulent. Please use caution when contacting the listing agent.")
            ui.button(text="Report", icon="flag", color="negative", on_click=lambda: Report_Listing(data["List Number"])).classes("basis-1/3")

def Listing_Object(data: dict) -> ui.element:
    with ui.card().classes("w-full flex-col flex-nowrap justify-between").on(
        type="click",
        handler=lambda: Listing_Details.refresh(data)
    ):

        with ui.row().classes("w-full flex-row flex-nowrap justify-between"):
            # image
            ui.image(
                source=data['Image']
            ).classes("basis-1/4")

            with ui.column().classes("w-full flex-col flex-nowrap justify-between"):
                with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
                    with ui.column().classes("w-full basis-1/2 flex-col flex-nowrap justify-between"):
                        ui.label(f"{data['Building Type']}").classes("text-lg")

                        # location
                        ui.label(f"{data['City']}, {data['State']} | {int(data['Zip Code'])}").classes("text-xs -mt-4")

                    # Fraud Flag
                    if data["Time Fraud"] < CONFIDENCE_INTERVAL and data["Price Fraud"] < CONFIDENCE_INTERVAL:
                        ui.label()
                        with ui.icon(
                            name='flag',
                            size='sm',
                            color='red',
                        ):
                            ui.tooltip('This listing might be fruadulent')
                ui.separator()

                # details
                ui.label(f"${data['List Price']:,} per month")

                with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center -mt-5"):
                    ui.label(f"{data['Bedrooms Total']} Bedrooms | {data['Bathrooms Total']} Bathrooms")
                    ui.button(
                        text="Contact",
                        on_click=lambda: ui.notify("Not Implemented"),
                        icon="email"
                    )

@ui.refreshable
def Main_Content(sIndex: int = 0, eIndex: int = 10, city: str = None, type: str = None, bedrooms: int = None) -> None:
    # Get the relevant listings
    rentalData: DataFrame = Get_Listings(
        sIndex=sIndex,
        eIndex=eIndex,
        cityName=city,
        buildingType=type,
        bedrooms=bedrooms
    )

    # Display the listings
    for index, row in rentalData.iterrows():
        Listing_Object(row.to_dict())

    with ui.row().classes("w-full flex-row flex-nowrap justify-between items-center"):
        ui.button(
            text="Prev Page",
            on_click=lambda: Main_Content.refresh(
                sIndex=sIndex-10,
                eIndex=eIndex-10
            ) if sIndex > 0 else None,
            icon="arrow_left"
        )

        ui.label(
            text=f"Page {int(eIndex / 10)}",
        )

        ui.button(
            text="Next Page",
            on_click=lambda: Main_Content.refresh(
                sIndex=sIndex+10,
                eIndex=eIndex+10
            ),
            icon="arrow_right"
        )

def Listings_Page() -> None:
    # Set the theme to dark mode
    ui.dark_mode(True)

    # Listing Filters
    with ui.row().classes("w-full flex-row flex-nowrap justify-evenly"):
        ui.select(
            options=Get_Cities(),
            label="City",
            on_change=lambda x: Main_Content.refresh(
                city=x.value
            ),
            clearable=True
        ).classes("w-full").props("outlined filled")

        ui.select(
            options=Get_Building_Types(),
            label="Building Type",
            on_change=lambda x: Main_Content.refresh(
                type=x.value
            ),
            clearable=True
        ).classes("w-full").props("outlined filled")

        ui.select(
            options=[x for x in range(1, 6)],
            label="Bedrooms",
            on_change=lambda x: Main_Content.refresh(
                bedrooms=x.value
            ),
            clearable=True
        ).classes("w-full").props("outlined filled")

    # Body
    Main_Content()

    # Header
    with ui.header(bordered=True).classes("justify-between items-center"):

        ui.label("Adaptive Real Estate").classes("text-2xl font-bold")

        ui.button(
            text="Sign In",
            on_click=lambda: ui.navigate.to("/admin"),
            icon="login",
        )

    # Sidebar
    with ui.right_drawer().props("width=500"):
        Listing_Details(Get_Listings(0, 1).iloc[0].to_dict())

    # Footer
    with ui.footer(bordered=True).classes("justify-start items-center"):
        ui.label("Powered by Adaptive Technologies Inc.")