import flet as ft
from datetime import date, time
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
        self.desc_input = ft.TextField(label="Описание", multiline=True, min_lines=2)
        hours = [ft.dropdown.Option(f"{i:02d}") for i in range(24)]
        minutes = [ft.dropdown.Option(f"{i:02d}") for i in range(0, 60, 15)]
        
        self.start_hour = ft.Dropdown(options=hours, width=70, dense=True, hint_text="ЧЧ")
        self.start_minute = ft.Dropdown(options=minutes, width=70, dense=True, hint_text="ММ")
        self.end_hour = ft.Dropdown(options=hours, width=70, dense=True, hint_text="ЧЧ")
        self.end_minute = ft.Dropdown(options=minutes, width=70, dense=True, hint_text="ММ")

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
                #если время ровно 00:00 до 23:59, пишем "Весь день"
                is_all_day = (ev.start_time.hour == 0 and ev.start_time.minute == 0 and 
                              ev.end_time.hour == 23 and ev.end_time.minute == 59)
                
                if is_all_day:
                    time_str = "Весь день"
                else:
                    time_str = f"{ev.start_time.strftime('%H:%M')} - {ev.end_time.strftime('%H:%M')}"

                events_controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column([
                                    ft.Text(ev.title, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(time_str, size=12, color=ft.colors.BLUE_700, weight=ft.FontWeight.W_500),
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
        self.start_hour.value = None
        self.start_minute.value = None
        self.end_hour.value = None
        self.end_minute.value = None

        self.dynamic_content.content = ft.Column([
            ft.Text("Создание события", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700),
            self.title_input,
            
            ft.Row([
                ft.Text("Начало:", width=60), 
                self.start_hour, ft.Text(":"), self.start_minute
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Row([
                ft.Text("Конец:", width=60), 
                self.end_hour, ft.Text(":"), self.end_minute
            ], alignment=ft.MainAxisAlignment.START),

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

        start_t = None
        end_t = None
        
        if self.start_hour.value:
            s_hour = int(self.start_hour.value)
            s_minute = int(self.start_minute.value) if self.start_minute.value else 0
            start_t = time(s_hour, s_minute)
            
        if self.end_hour.value:
            e_hour = int(self.end_hour.value)
            e_minute = int(self.end_minute.value) if self.end_minute.value else 0
            end_t = time(e_hour, e_minute)

        db = SessionLocal()
        try:
            create_single_event(db, title=title, description=desc, event_date=self.selected_date, start_t=start_t, end_t=end_t)
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