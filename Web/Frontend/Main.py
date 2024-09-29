from nicegui import ui
from Admin import Admin_Page
from Listings import Listings_Page

@ui.page("/admin")
def Admin() -> None:
    ui.page_title("Admin")
    Admin_Page()

@ui.page("/listings")
def Listings() -> None:
    ui.page_title("Listings")
    Listings_Page()

@ui.page("/")
def Home() -> None:
    ui.navigate.to("/listings")

if __name__ in {"__main__", "__mp_main__"}:
    # Open the listings page
    Home()

    # Run the app
    ui.run()