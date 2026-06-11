import os
import flet as ft
from backend.database import engine, Base
from frontend.auth_view import setup_auth_view
from frontend.main_view import setup_main_view

print("Проверяем базу данных calendar_dot...")
Base.metadata.create_all(bind=engine)
print("Таблицы готовы!")

def main(page: ft.Page):
    user_id = page.session.get("user_id")
    
    if user_id:
        setup_main_view(page)
    else:
        setup_auth_view(page)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=port
    )