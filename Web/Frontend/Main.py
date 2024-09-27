from nicegui import ui

@ui.page("/")
def Home() -> None:
    ui.label("Hello World!")

    ui.run()

if __name__ in {"__main__", "__mp_main__"}:
    Home()