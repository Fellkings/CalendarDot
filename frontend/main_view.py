import flet as ft
from datetime import date
from frontend.components import CalendarGrid
from frontend.event_window import EventPanel
from backend.database import SessionLocal
from backend.models import User
from backend.crud import search_user_events

def setup_main_view(page: ft.Page):
    page.title = "CalendarDot"
    page.padding = ft.padding.all(0)
    page.theme_mode = ft.ThemeMode.LIGHT  #по дефолту cветлая тема

    user_avatar = page.session.get("avatar") or "😎"
    username = page.session.get("username") or "Пользователь"
    user_id = page.session.get("user_id")

    #переключение темы
    def on_theme_change(e):
        page.theme_mode = ft.ThemeMode.DARK if theme_switch.value else ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.Switch(label="Включить темную тему", value=False, on_change=on_theme_change)

    def close_settings(e):
        settings_dialog.open = False
        page.update()

    def logout(e):
        page.session.clear() 
        settings_dialog.open = False
        page.controls.clear()
        from frontend.auth_view import setup_auth_view
        setup_auth_view(page)
        page.update()

    dialog_title = ft.Text(f"Профиль: {username} {user_avatar}", size=20, weight=ft.FontWeight.BOLD)
    
    user_avatar_btn = ft.Container(
        content=ft.Text(user_avatar, size=24),
        padding=8,
        border_radius=25,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        ink=True,
        tooltip="Настройки профиля"
    )

    def change_avatar(e):
        new_avatar = e.control.data
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.avatar = new_avatar
                db.commit()
        finally:
            db.close()

        page.session.set("avatar", new_avatar)
        dialog_title.value = f"Профиль: {username} {new_avatar}"
        user_avatar_btn.content.value = new_avatar
        
        for c in avatar_row_settings.controls:
            c.bgcolor = ft.colors.PRIMARY_CONTAINER if c.data == new_avatar else ft.colors.TRANSPARENT
        page.update()

    avatar_options = ["😎", "🐱", "🦋", "🦄"]
    avatar_row_settings = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
    for emoji in avatar_options:
        avatar_row_settings.controls.append(
            ft.Container(
                content=ft.Text(emoji, size=24),
                data=emoji,
                padding=8,
                border_radius=25,
                bgcolor=ft.colors.PRIMARY_CONTAINER if emoji == user_avatar else ft.colors.TRANSPARENT,
                on_click=change_avatar,
                ink=True
            )
        )

    logout_btn = ft.ElevatedButton("Выйти из аккаунта", on_click=logout, bgcolor=ft.colors.ERROR_CONTAINER, color=ft.colors.ON_ERROR_CONTAINER)

    settings_dialog = ft.AlertDialog(
        title=dialog_title,
        content=ft.Column([
            ft.Text("Сменить аватар", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
            avatar_row_settings,
            ft.Divider(),
            ft.Text("Персонализация", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
            theme_switch,
            ft.Divider(),
            logout_btn
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

    user_avatar_btn.on_click = open_settings

    def refresh_ui():
        event_panel.show_events_list(event_panel.selected_date)
        calendar_grid.build_grid()
        calendar_grid.update()

    event_panel = EventPanel(user_id=user_id, on_event_saved=refresh_ui)

    def handle_day_click(date_obj):
        event_panel.show_events_list(date_obj)

    calendar_grid = CalendarGrid(user_id=user_id, on_day_click=handle_day_click)
    calendar_grid.visible = True 

    #система поиска
    search_results = ft.ListView(expand=True, spacing=5, height=300)

    def go_to_searched_date(target_date):
        search_dialog.open = False
        calendar_grid.current_year = target_date.year
        calendar_grid.current_month = target_date.month
        calendar_grid.build_grid()
        calendar_grid.update()
        event_panel.show_events_list(target_date)
        page.update()

    def perform_search(e):
        query = e.control.value.strip()
        search_results.controls.clear()
        
        if len(query) < 2:
            search_results.update()
            return

        db = SessionLocal()
        try:
            events = search_user_events(db, user_id, query)
            if not events:
                search_results.controls.append(
                    ft.Text("Ничего не найдено...", color=ft.colors.OUTLINE, italic=True)
                )
            else:
                for ev in events:
                    search_results.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.EVENT, color=ft.colors.PRIMARY),
                            title=ft.Text(ev.title, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(ev.start_time.strftime("%d.%m.%Y %H:%M")),
                            on_click=lambda e, d=ev.start_time.date(): go_to_searched_date(d)
                        )
                    )
        finally:
            db.close()
        search_results.update()

    search_input = ft.TextField(
        hint_text="Введите название или описание...",
        prefix_icon=ft.icons.SEARCH,
        autofocus=True,
        on_change=perform_search
    )

    search_dialog = ft.AlertDialog(
        title=ft.Text("Поиск событий"),
        content=ft.Column([search_input, search_results], tight=True, width=450),
        actions=[ft.TextButton("Закрыть", on_click=lambda e: setattr(search_dialog, 'open', False) or page.update())]
    )

    def open_search(e):
        search_input.value = ""
        search_results.controls.clear()
        page.dialog = search_dialog
        search_dialog.open = True
        page.update()

    search_btn = ft.IconButton(icon=ft.icons.SEARCH, tooltip="Поиск", on_click=open_search)

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
        calendar_grid.go_to_today() 
        event_panel.show_events_list(date.today()) 

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
                ft.Row([search_btn, view_switcher, user_avatar_btn], spacing=15)
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