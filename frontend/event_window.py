import flet as ft
from datetime import date
from backend.database import SessionLocal
from backend.crud import create_single_event, get_events_by_date, delete_event

class EventPanel(ft.Container):
    def __init__(self, on_event_saved):
        super().__init__()
        self.width = 320
        self.bgcolor = ft.colors.GREY_50
        self.padding = 20
        self.border_radius = 10
        self.border = ft.border.all(1, ft.colors.GREY_200)
        
        self.on_event_saved = on_event_saved 
        self.selected_date = date.today()

        self.date_label = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
        
        self.title_input = ft.TextField(label="Название события")
        self.desc_input = ft.TextField(label="Описание", multiline=True, min_lines=3)

        self.dynamic_content = ft.Container(expand=True)

        #содержимое панели
        self.content = ft.Column([
            self.date_label,
            ft.Divider(),
            self.dynamic_content
        ], expand=True)

        self.show_events_list(self.selected_date)

    def show_events_list(self, d: date):
        self.selected_date = d
        self.date_label.value = d.strftime('%d.%m.%Y')
        
        db = SessionLocal()
        events = get_events_by_date(db, d)
        db.close()

        events_controls = []
        if not events:
            events_controls.append(ft.Text("Нет событий на этот день", color=ft.colors.GREY_500, italic=True))
        else:
            for ev in events:
                events_controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column([
                                    ft.Text(ev.title, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(ev.description or "", size=12, color=ft.colors.GREY_700)
                                ], spacing=2, expand=True),
                                
                                #кнопка удаления
                                ft.IconButton(
                                    icon=ft.icons.DELETE_OUTLINE, 
                                    icon_color=ft.colors.RED_400,
                                    tooltip="Удалить событие",
                                    on_click=lambda e, ev_id=ev.id: self.delete_click(ev_id)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START
                        ),
                        bgcolor=ft.colors.ORANGE_100,
                        padding=10,
                        border_radius=6,
                        margin=ft.margin.only(bottom=10)
                    )
                )

        add_btn = ft.ElevatedButton(
            "   + Новое событие   ", 
            on_click=self.show_creation_form,
            bgcolor=ft.colors.BLUE,
            color=ft.colors.WHITE
        )

        self.dynamic_content.content = ft.Column([
            ft.ListView(controls=events_controls, expand=True),
            ft.Row([add_btn], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True)
        
        if self.page:
            self.update()

    def show_creation_form(self, e):
        self.title_input.value = ""
        self.desc_input.value = ""

        self.dynamic_content.content = ft.Column([
            ft.Text("Создание события", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
            self.title_input,
            self.desc_input,
            ft.Row([
                ft.TextButton("Отмена", on_click=lambda _: self.show_events_list(self.selected_date)),
                ft.ElevatedButton("Сохранить", on_click=self.save_click, bgcolor=ft.colors.BLUE, color=ft.colors.WHITE)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=15)
        
        if self.page:
            self.update()

    def save_click(self, e):
        title = self.title_input.value.strip()
        desc = self.desc_input.value.strip()
        
        if not title:
            return

        db = SessionLocal()
        try:
            create_single_event(db, title=title, description=desc, event_date=self.selected_date)
        except Exception as ex:
            print(f"Произошла ошибка при сохранении: {ex}")
        finally:
            db.close()

        if self.on_event_saved:
            self.on_event_saved()

        self.show_events_list(self.selected_date)

    def delete_click(self, event_id):
        db = SessionLocal()
        try:
            delete_event(db, event_id)
            print(f"Событие ID {event_id} удалено.")
        except Exception as ex:
            print(f"Ошибка при удалении: {ex}")
        finally:
            db.close()

        if self.on_event_saved:
            self.on_event_saved()

        self.show_events_list(self.selected_date)