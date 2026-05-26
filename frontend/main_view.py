import flet as ft
from datetime import date
from frontend.components import CalendarGrid
from frontend.event_window import EventPanel

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.padding = ft.padding.all(0)
    page.theme_mode = ft.ThemeMode.LIGHT  #по дефолту cветлая тема

    #переключение темы
    def on_theme_change(e):
        page.theme_mode = ft.ThemeMode.DARK if theme_switch.value else ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.Switch(label="Включить темную тему", value=False, on_change=on_theme_change)

    def close_settings(e):
        settings_dialog.open = False
        page.update()

    settings_dialog = ft.AlertDialog(
        title=ft.Text("Настройки интерфейса"),
        content=ft.Column([
            ft.Text("Персонализация", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
            theme_switch,
        ], tight=True, spacing=15),
        actions=[
            ft.TextButton("Закрыть", on_click=close_settings)
        ]
    )

    #кнопка настроек
    def open_settings(e):
        theme_switch.value = (page.theme_mode == ft.ThemeMode.DARK)
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()

    settings_btn = ft.IconButton(icon=ft.icons.SETTINGS, tooltip="Настройки", on_click=open_settings)

    def refresh_ui():
        event_panel.show_events_list(event_panel.selected_date)
        calendar_grid.build_grid()
        calendar_grid.update()

    event_panel = EventPanel(on_event_saved=refresh_ui)

    def handle_day_click(date_obj):
        event_panel.show_events_list(date_obj)

    calendar_grid = CalendarGrid(on_day_click=handle_day_click)
    calendar_grid.visible = True 

    week_grid_placeholder = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.VIEW_WEEK, size=64, color=ft.colors.PRIMARY),
            ft.Text("Недельный режим", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Здесь будет почасовая сетка расписания.", 
                    text_align=ft.TextAlign.CENTER, color=ft.colors.ON_SURFACE_VARIANT)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.alignment.center,
        visible=False 
    )

    center_area = ft.Stack(
        controls=[calendar_grid, week_grid_placeholder],
        expand=True
    )

    center_container = ft.Container(
        content=center_area, 
        expand=True, 
        padding=ft.padding.only(left=20, right=10, bottom=20, top=20)
    )

    active_style = ft.ButtonStyle(
        bgcolor=ft.colors.SECONDARY_CONTAINER,
        color=ft.colors.ON_SECONDARY_CONTAINER,
        shape=ft.RoundedRectangleBorder(radius=8),
    )
    inactive_style = ft.ButtonStyle(
        bgcolor=ft.colors.TRANSPARENT,
        color=ft.colors.ON_SURFACE_VARIANT,
        shape=ft.RoundedRectangleBorder(radius=8),
    )

    def switch_view(e):
        view_name = e.control.data
        if view_name == "month":
            calendar_grid.visible = True
            week_grid_placeholder.visible = False
            btn_month.style = active_style
            btn_week.style = inactive_style
        else:
            calendar_grid.visible = False
            week_grid_placeholder.visible = True
            btn_week.style = active_style
            btn_month.style = inactive_style

        btn_month.update()
        btn_week.update()
        center_area.update()

    btn_month = ft.TextButton("Месяц", icon=ft.icons.CALENDAR_VIEW_MONTH, data="month", on_click=switch_view, style=active_style)
    btn_week = ft.TextButton("Неделя", icon=ft.icons.VIEW_WEEK, data="week", on_click=switch_view, style=inactive_style)

    view_switcher = ft.Container(
        content=ft.Row([btn_month, btn_week], spacing=2),
        bgcolor=ft.colors.SURFACE,
        border_radius=10,
        padding=2,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT)
    )

    def return_to_today(e):
            today_date = date.today()
            calendar_grid.go_to_today() 
            event_panel.show_events_list(today_date) 

    clickable_logo = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.CALENDAR_MONTH, size=32, color=ft.colors.PRIMARY),
            ft.Text("CalendarDot", size=28, weight=ft.FontWeight.BOLD),
        ], spacing=10),
        on_click=return_to_today,
        border_radius=8,
        tooltip="Вернуться к текущему дню",
        ink=True,
        padding=ft.padding.symmetric(horizontal=10, vertical=5)
    )

    header = ft.Container(
        content=ft.Row(
            controls=[
                clickable_logo,
                ft.Row([view_switcher, settings_btn], spacing=15) 
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        bgcolor=ft.colors.SURFACE_VARIANT 
    )

    content_row = ft.Row(
        controls=[
            center_container,
            ft.Container(content=event_panel, padding=ft.padding.only(right=20, bottom=20, top=20))
        ],
        expand=True,
        spacing=0
    )

    page.add(header, content_row)