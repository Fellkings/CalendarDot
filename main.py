import flet as ft
from backend.database import engine, Base
from frontend.main_view import setup_main_view 

def init_db():
    print("Проверяем базу данных calendar_dot...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы готовы!")

def main(page: ft.Page):
    setup_main_view(page)

if __name__ == "__main__":
    init_db()

    ft.app(target=main, view=ft.AppView.WEB_BROWSER)