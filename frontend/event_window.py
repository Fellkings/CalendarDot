import flet as ft
from datetime import date
from backend.database import SessionLocal
from backend.crud import create_single_event

class EventPanel(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 300
        self.visible = False
        self.bgcolor = ft.colors.GREY_50
        self.padding = 20
        self.border_radius = 10
        self.border = ft.border.all(1, ft.colors.GREY_200)

        self.selected_date = None

        self.title_input = ft.TextField(label="Название события", autofocus=True)
        self.desc_input = ft.TextField(label="Описание", multiline=True, min_lines=3)
        
        self.date_label = ft.Text("", size=18, weight=ft.FontWeight.BOLD)

        #содержимое панели
        self.content = ft.Column([
            ft.Row([
                self.date_label,
                ft.IconButton(icon=ft.icons.CLOSE, on_click=self.close_panel, tooltip="Закрыть")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            self.title_input,
            self.desc_input,
            ft.ElevatedButton("Сохранить", on_click=self.save_click, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
        ])

    def open_panel(self, d: date):
        self.selected_date = d
        self.date_label.value = d.strftime('%d.%m.%Y')
        self.title_input.value = ""
        self.desc_input.value = ""
        self.visible = True
        self.update()

    def close_panel(self, e):
        self.visible = False
        self.update()

    def save_click(self, e):
        title = self.title_input.value.strip()
        desc = self.desc_input.value.strip()
        
        if not title:
            print("Ошибка: Название события не может быть пустым.")
            return

        db = SessionLocal()
        try:
            create_single_event(db, title=title, description=desc, event_date=self.selected_date)
            print(f"Событие '{title}' успешно сохранено в PostgreSQL!")
        except Exception as ex:
            print(f"Произошла ошибка при сохранении: {ex}")
        finally:
            db.close()

        self.close_panel(e)