import flet as ft
import calendar
from datetime import datetime, date
from backend.database import SessionLocal
from backend.crud import get_events_by_date_range

MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

class CalendarGrid(ft.Column):
    def __init__(self, user_id: int, on_day_click):
        super().__init__()
        self.expand = True
        self.spacing = 0 
        self.on_day_click = on_day_click
        self.user_id = user_id

        #текущий год и месяц
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        
        self.build_grid()

    def go_to_today(self):
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.build_grid()
        if self.page:
            self.update()

    def build_grid(self):
        self.controls.clear()
        
        cal = calendar.Calendar()
        month_dates = list(cal.itermonthdates(self.current_year, self.current_month))
        month_name = MONTH_NAMES[self.current_month - 1]
        today = date.today()
        
        db = SessionLocal()
        try:
            all_events = get_events_by_date_range(db, month_dates[0], month_dates[-1], self.user_id)
            events_by_date = {}
            for ev in all_events:
                ev_date = ev.start_time.date()
                if ev_date not in events_by_date:
                    events_by_date[ev_date] = []
                events_by_date[ev_date].append(ev)
        finally:
            db.close()

        month_header = ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="Предыдущий месяц", on_click=self.prev_month),
                    ft.Text(f"{month_name} {self.current_year}", size=22, weight=ft.FontWeight.W_500),
                    ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="Следующий месяц", on_click=self.next_month),
                ])
            ],
            alignment=ft.MainAxisAlignment.START
        )

        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, size=12, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT), 
                    alignment=ft.alignment.center, 
                    expand=1,
                    padding=ft.padding.only(bottom=8)
                ) for day in days_of_week
            ],
            spacing=0, 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        weeks = [month_dates[i:i+7] for i in range(0, len(month_dates), 7)]
        
        border_color = ft.colors.OUTLINE 
        
        grid_rows = []
        for week in weeks:
            week_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=1, spacing=0)
            for date_obj in week:
                is_current_month = (date_obj.month == self.current_month)
                is_today = (date_obj == today)
                
                bg_color = ft.colors.SURFACE if is_current_month else ft.colors.SURFACE_VARIANT
                
                if is_today:
                    text_color = ft.colors.ON_PRIMARY
                    day_number_container = ft.Container(
                        content=ft.Text(str(date_obj.day), size=14, color=text_color, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.colors.PRIMARY,
                        width=28, height=28,
                        border_radius=14,
                        alignment=ft.alignment.center
                    )
                else:
                    text_color = ft.colors.ON_SURFACE if is_current_month else ft.colors.OUTLINE
                    day_number_container = ft.Container(
                        content=ft.Text(str(date_obj.day), size=14, color=text_color),
                        width=28, height=28,
                        alignment=ft.alignment.center
                    )

                daily_events = events_by_date.get(date_obj, [])
                dots = []
                
                for ev in daily_events[:3]:
                    if ev.category:
                        bright_color_name = ev.category.color.replace("_100", "_400")
                        dot_color = getattr(ft.colors, bright_color_name, ft.colors.PRIMARY)
                    else:
                        dot_color = ft.colors.PRIMARY

                    dots.append(
                        ft.Container(width=6, height=6, border_radius=3, bgcolor=dot_color)
                    )
                
                dots_column = ft.Column(controls=dots, spacing=3)
                
                day_content = ft.Row(
                    controls=[
                        day_number_container,
                        dots_column
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START 
                )

                day_container = ft.Container(
                    content=day_content,
                    alignment=ft.alignment.top_left,
                    padding=10,
                    border=ft.border.all(0.5, border_color),
                    expand=1,
                    bgcolor=bg_color,
                    on_click=lambda e, d=date_obj: self.on_day_click(d)
                )
                week_row.controls.append(day_container)
            grid_rows.append(week_row)

        clipped_grid = ft.Container(
            content=ft.Column(controls=grid_rows, spacing=0, expand=True),
            border_radius=19,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS, 
            expand=True
        )

        grid_table_container = ft.Container(
            content=clipped_grid,
            border_radius=20, 
            border=ft.border.all(1.5, border_color), 
            expand=True
        )

        self.controls.extend([
            ft.Container(content=month_header, padding=ft.padding.only(bottom=10)), 
            header_row,
            grid_table_container
        ])

    def prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.build_grid()
        self.update()

    def next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.build_grid()
        self.update()