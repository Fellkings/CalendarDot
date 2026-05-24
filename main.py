import flet as ft
from backend.database import engine, Base
from frontend.main_view import setup_main_view 

def init_db():
    print("Проверяем базу данных calendar_dot...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы готовы!")

def main(page: ft.Page):
    # Вызываем настройку интерфейса
    setup_main_view(page)

if __name__ == "__main__":
    # Сначала проверяем/создаем БД
    init_db()
    # Затем запускаем десктопное приложение Flet
    ft.app(target=main)