import flet as ft
from frontend.components import CalendarGrid
from frontend.event_window import EventPanel

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.window_width = 1200
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT  #cветлая тема
    page.padding = 20

    #заголовок приложения
    header = ft.Text("CalendarDot", size=32, weight=ft.FontWeight.BOLD)

    def refresh_ui():
        event_panel.show_events_list(event_panel.selected_date)

    event_panel = EventPanel(on_event_saved=refresh_ui)

    def handle_day_click(date_obj):
        event_panel.show_events_list(date_obj)

    calendar_grid = CalendarGrid(on_day_click=handle_day_click)

    content_row = ft.Row(
        controls=[calendar_grid, event_panel],
        expand=True
    )

    page.add(header, content_row)