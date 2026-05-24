import flet as ft
from datetime import date

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
        print(f"--- НОВОЕ СОБЫТИЕ ---")
        print(f"Дата: {self.selected_date.strftime('%d.%m.%Y')}")
        print(f"Название: {self.title_input.value}")
        print(f"Описание: {self.desc_input.value}\n")
        self.close_panel(e)