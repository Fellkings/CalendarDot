import flet as ft

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.window_width = 1000
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT  #cветлая тема
    page.padding = 20

    #заголовок приложения
    header = ft.Text("CalendarDot", size=32, weight=ft.FontWeight.BOLD)

    #заглушка
    calendar_placeholder = ft.Container(
        content=ft.Text("Здесь скоро появится сетка календаря (неделя/месяц)...", color=ft.colors.GREY),
        alignment=ft.alignment.center,
        expand=True,
        bgcolor=ft.colors.GREY_100,
        border_radius=10
    )

    page.add(header, calendar_placeholder)