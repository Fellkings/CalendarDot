import flet as ft
from frontend.components import CalendarGrid
from frontend.event_window import EventPanel

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.window_width = 1200
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT  #по дефолту cветлая тема
    page.padding = 20

    #переключение темы
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.icons.LIGHT_MODE
            theme_btn.tooltip = "Светлая тема"
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.icons.DARK_MODE
            theme_btn.tooltip = "Темная тема"
        page.update()

    #кнопка настроек
    def open_settings(e):
        #заглушка
        page.snack_bar = ft.SnackBar(ft.Text("Меню настроек появится в будущих обновлениях!"))
        page.snack_bar.open = True
        page.update()

    theme_btn = ft.IconButton(icon=ft.icons.DARK_MODE, tooltip="Темная тема", on_click=toggle_theme)
    settings_btn = ft.IconButton(icon=ft.icons.SETTINGS, tooltip="Настройки", on_click=open_settings)

    header = ft.Row(
        controls=[
            ft.Text("CalendarDot", size=32, weight=ft.FontWeight.BOLD),
            ft.Row([theme_btn, settings_btn])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    def refresh_ui():
        event_panel.show_events_list(event_panel.selected_date)
        calendar_grid.build_grid()
        calendar_grid.update()

    event_panel = EventPanel(on_event_saved=refresh_ui)

    def handle_day_click(date_obj):
        event_panel.show_events_list(date_obj)

    calendar_grid = CalendarGrid(on_day_click=handle_day_click)

    content_row = ft.Row(
        controls=[calendar_grid, event_panel],
        expand=True
    )

    page.add(header, content_row)