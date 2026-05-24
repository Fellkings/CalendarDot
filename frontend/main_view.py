import flet as ft
from frontend.components import CalendarGrid

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.window_width = 1000
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT  #cветлая тема
    page.padding = 20

    #заголовок приложения
    header = ft.Text("CalendarDot", size=32, weight=ft.FontWeight.BOLD)

    calendar_grid = CalendarGrid()

    page.add(header, calendar_grid)