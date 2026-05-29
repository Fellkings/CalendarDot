import flet as ft
from datetime import date, time, datetime
from backend.database import SessionLocal
from backend.crud import create_single_event, get_events_by_date, delete_event, get_all_categories

class EventPanel(ft.Container):
    def __init__(self, user_id: int, on_event_saved):
        super().__init__()
        self.user_id = user_id
        self.width = 320
        self.bgcolor = ft.colors.SURFACE_VARIANT
        self.padding = 20
        self.border_radius = 10
        self.border = ft.border.all(1, ft.colors.OUTLINE_VARIANT)
        
        self.on_event_saved = on_event_saved 
        self.selected_date = date.today()

        self.date_label = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
        
        self.title_input = ft.TextField(label="Название события")
        self.desc_input = ft.TextField(label="Описание", multiline=True, min_lines=2)
        
        self.start_time_val = None
        self.end_time_val = None

        self.start_time_btn = ft.OutlinedButton(
            text="Выбрать",
            icon=ft.icons.ACCESS_TIME,
            on_click=self.open_start_time_picker
        )
        self.end_time_btn = ft.OutlinedButton(
            text="Выбрать",
            icon=ft.icons.ACCESS_TIME,
            on_click=self.open_end_time_picker
        )

        self.category_dropdown = ft.Dropdown(label="Категория", dense=True)
        self.dynamic_content = ft.Container(expand=True)

        #содержимое панели
        self.content = ft.Column([
            self.date_label,
            ft.Divider(),
            self.dynamic_content
        ], expand=True)

        self.show_events_list(self.selected_date)

    def load_categories_to_dropdown(self):
        #список категорий
        db = SessionLocal()
        categories = get_all_categories(db, self.user_id)
        db.close()
        
        options = []
        for cat in categories:
            options.append(ft.dropdown.Option(key=str(cat.id), text=f"{cat.emoji} {cat.name}"))
        
        self.category_dropdown.options = options

    def show_events_list(self, d: date):
        self.selected_date = d
        self.date_label.value = d.strftime('%d.%m.%Y')
        
        db = SessionLocal()
        events = get_events_by_date(db, d, self.user_id) 
        db.close()

        events_controls = []
        if not events:
            events_controls.append(ft.Text("Нет событий на этот день", color=ft.colors.ON_SURFACE_VARIANT, italic=True))
        else:
            for ev in events:
                #если время ровно 00:00 до 23:59, пишем "Весь день"
                is_all_day = (ev.start_time.hour == 0 and ev.start_time.minute == 0 and 
                              ev.end_time.hour == 23 and ev.end_time.minute == 59)
                time_str = "Весь день" if is_all_day else f"{ev.start_time.strftime('%H:%M')} - {ev.end_time.strftime('%H:%M')}"
                
                if ev.category:
                    base_color = getattr(ft.colors, ev.category.color, ft.colors.PRIMARY)
                    bg_color = ft.colors.with_opacity(0.1, base_color)
                    card_border = ft.border.only(left=ft.border.BorderSide(4, base_color))
                    display_title = f"{ev.category.emoji} {ev.title}"
                else:
                    bg_color = ft.colors.SURFACE_VARIANT
                    card_border = None
                    display_title = ev.title

                title_color = ft.colors.ON_SURFACE
                time_color = ft.colors.ON_SURFACE
                desc_color = ft.colors.ON_SURFACE_VARIANT

                events_controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column([
                                    ft.Text(display_title, weight=ft.FontWeight.BOLD, size=14, color=title_color),
                                    ft.Text(time_str, size=12, color=time_color, weight=ft.FontWeight.W_500),
                                    ft.Text(ev.description or "", size=12, color=desc_color)
                                ], spacing=2, expand=True),
                                
                                ft.IconButton(
                                    icon=ft.icons.DELETE_OUTLINE, 
                                    icon_color=ft.colors.ERROR, 
                                    tooltip="Удалить событие",
                                    on_click=lambda e, ev_id=ev.id: self.delete_click(ev_id)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START
                        ),
                        bgcolor=bg_color,
                        border=card_border,
                        padding=10,
                        border_radius=8,
                        margin=ft.margin.only(bottom=10)
                    )
                )

        add_btn = ft.ElevatedButton(
            "   + Новое событие   ", 
            on_click=self.show_creation_form,
            bgcolor=ft.colors.PRIMARY,
            color=ft.colors.ON_PRIMARY
        )

        self.dynamic_content.content = ft.Column([
            ft.ListView(controls=events_controls, expand=True),
            ft.Row([add_btn], alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True)
        
        if self.page:
            self.update()

    def open_date_picker(self, e):
        if not hasattr(self, 'date_picker'):
            self.date_picker = ft.DatePicker(on_change=self.on_date_changed, help_text="Выберите день события")
            self.page.overlay.append(self.date_picker)
        self.date_picker.value = datetime.combine(self.selected_date, time(0, 0))
        self.date_picker.open = True
        self.page.update()

    def on_date_changed(self, e):
        if self.date_picker.value:
            self.selected_date = self.date_picker.value.date()
            if hasattr(self, 'form_date_btn'):
                self.form_date_btn.text = self.selected_date.strftime('%d.%m.%Y')
            self.update()

    def open_start_time_picker(self, e):
        if not hasattr(self, 'start_time_picker'):
            self.start_time_picker = ft.TimePicker(
                on_change=self.on_start_time_changed,
                help_text="Введите время начала",
                confirm_text="ОК",
                cancel_text="ОТМЕНА",
                time_picker_entry_mode=ft.TimePickerEntryMode.INPUT
            )
            self.page.overlay.append(self.start_time_picker)
        self.start_time_picker.open = True
        self.page.update()

    def on_start_time_changed(self, e):
        if self.start_time_picker.value:
            self.start_time_val = self.start_time_picker.value
            self.start_time_btn.text = self.start_time_val.strftime('%H:%M')
            self.update()

    def open_end_time_picker(self, e):
        if not hasattr(self, 'end_time_picker'):
            self.end_time_picker = ft.TimePicker(
                on_change=self.on_end_time_changed,
                help_text="Введите время окончания",
                confirm_text="ОК",
                cancel_text="ОТМЕНА",
                time_picker_entry_mode=ft.TimePickerEntryMode.INPUT
            )
            self.page.overlay.append(self.end_time_picker)
        self.end_time_picker.open = True
        self.page.update()

    def on_end_time_changed(self, e):
        if self.end_time_picker.value:
            self.end_time_val = self.end_time_picker.value
            self.end_time_btn.text = self.end_time_val.strftime('%H:%M')
            self.update()

    def show_creation_form(self, e):
        self.title_input.value = ""
        self.desc_input.value = ""
        
        self.start_time_val = None
        self.end_time_val = None
        self.start_time_btn.text = "Выбрать"
        self.end_time_btn.text = "Выбрать"
        
        self.load_categories_to_dropdown()
        self.category_dropdown.value = None 

        self.form_date_btn = ft.OutlinedButton(
            text=self.selected_date.strftime('%d.%m.%Y'),
            icon=ft.icons.CALENDAR_MONTH,
            on_click=self.open_date_picker
        )

        self.dynamic_content.content = ft.Column([
            ft.Text("Создание события", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
            self.title_input,
            self.category_dropdown,
            ft.Row([
                ft.Text("Дата:", width=60), 
                self.form_date_btn
            ], alignment=ft.MainAxisAlignment.START),
            
            ft.Row([
                ft.Text("Начало:", width=60), 
                self.start_time_btn
            ], alignment=ft.MainAxisAlignment.START),

            ft.Row([
                ft.Text("Конец:", width=60), 
                self.end_time_btn
            ], alignment=ft.MainAxisAlignment.START),

            self.desc_input,
            ft.Row([
                ft.TextButton("Отмена", on_click=lambda _: self.show_events_list(self.selected_date)),
                ft.ElevatedButton("Сохранить", on_click=self.save_click, bgcolor=ft.colors.PRIMARY, color=ft.colors.ON_PRIMARY)
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=15)
        
        if self.page:
            self.update()

    def save_click(self, e):
        title = self.title_input.value.strip()
        desc = self.desc_input.value.strip()
        
        if not title:
            return

        cat_id = int(self.category_dropdown.value) if self.category_dropdown.value else None

        db = SessionLocal()
        try:
            create_single_event(db, title=title, description=desc, event_date=self.selected_date, 
                                user_id=self.user_id,
                                start_t=self.start_time_val, end_t=self.end_time_val, category_id=cat_id)
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
            delete_event(db, event_id, self.user_id)
            print(f"Событие ID {event_id} удалено.")
        except Exception as ex:
            print(f"Ошибка при удалении: {ex}")
        finally:
            db.close()

        if self.on_event_saved:
            self.on_event_saved()

        self.show_events_list(self.selected_date)