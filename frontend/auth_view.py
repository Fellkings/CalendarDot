import flet as ft
from backend.database import SessionLocal
from backend.auth import create_user, authenticate_user

def setup_auth_view(page: ft.Page):
    page.controls.clear()
    page.title = "Вход - CalendarDot"
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    is_login = True
    
    avatar_options = ["😎", "🐱", "🦋", "🦄"]
    selected_avatar = avatar_options[0]
    
    def update_avatar(e):
        nonlocal selected_avatar
        selected_avatar = e.control.data
        for c in avatar_row.controls:
            c.bgcolor = ft.colors.PRIMARY_CONTAINER if c.data == selected_avatar else ft.colors.TRANSPARENT
        avatar_row.update()

    avatar_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, visible=False)
    for emoji in avatar_options:
        avatar_row.controls.append(
            ft.Container(
                content=ft.Text(emoji, size=28),
                data=emoji,
                padding=10,
                border_radius=25,
                bgcolor=ft.colors.PRIMARY_CONTAINER if emoji == selected_avatar else ft.colors.TRANSPARENT,
                on_click=update_avatar,
                ink=True
            )
        )

    title = ft.Text("С возвращением!", size=28, weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("Войдите в свой аккаунт CalendarDot", color=ft.colors.ON_SURFACE_VARIANT, size=14)
    error_text = ft.Text("", color=ft.colors.ERROR, size=12, visible=False)

    username_input = ft.TextField(label="Имя пользователя", prefix_icon=ft.icons.PERSON, visible=False)
    email_input = ft.TextField(label="Email", prefix_icon=ft.icons.EMAIL)
    password_input = ft.TextField(label="Пароль", prefix_icon=ft.icons.LOCK, password=True, can_reveal_password=True)

    def toggle_mode(e):
        nonlocal is_login
        is_login = not is_login
        
        if is_login:
            title.value = "С возвращением!"
            subtitle.value = "Войдите в свой аккаунт CalendarDot"
            username_input.visible = False
            avatar_row.visible = False
            submit_btn.text = "Войти"
            toggle_btn.text = "Нет аккаунта? Создать"
        else:
            title.value = "Создать аккаунт"
            subtitle.value = "Выберите аватар и присоединяйтесь"
            username_input.visible = True
            avatar_row.visible = True
            submit_btn.text = "Зарегистрироваться"
            toggle_btn.text = "Уже есть аккаунт? Войти"
            
        error_text.visible = False
        auth_card.update()

    def submit(e):
        error_text.visible = False
        email = email_input.value.strip()
        password = password_input.value.strip()
        username = username_input.value.strip()

        if not email or not password or (not is_login and not username):
            error_text.value = "Пожалуйста, заполните все поля"
            error_text.visible = True
            auth_card.update()
            return

        db = SessionLocal()
        try:
            if is_login:
                user = authenticate_user(db, email, password)
                if not user:
                    error_text.value = "Неверный email или пароль"
                    error_text.visible = True
                    auth_card.update()
                    return
            else:
                user = create_user(db, username, email, password, selected_avatar)
                if not user:
                    error_text.value = "Пользователь с таким email или именем уже существует"
                    error_text.visible = True
                    auth_card.update()
                    return

            # Сохраняем все данные профиля в сессию браузера!
            page.session.set("user_id", user.id)
            page.session.set("username", user.username)
            page.session.set("avatar", user.avatar) 
            
            from frontend.main_view import setup_main_view 
            page.controls.clear()
            setup_main_view(page)
            page.update()
            
        finally:
            db.close()

    submit_btn = ft.ElevatedButton("Войти", on_click=submit, bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY, height=45, width=400)
    toggle_btn = ft.TextButton("Нет аккаунта? Создать", on_click=toggle_mode)

    auth_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.CALENDAR_MONTH, size=48, color=ft.colors.PRIMARY),
                title,
                subtitle,
                avatar_row, # <-- Выбор смайлика
                error_text,
                username_input,
                email_input,
                password_input,
                ft.Container(height=10),
                submit_btn,
                toggle_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        width=400,
        padding=40,
        border_radius=12,
        bgcolor=ft.colors.SURFACE,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.colors.with_opacity(0.1, ft.colors.SHADOW))
    )
    page.add(auth_card)