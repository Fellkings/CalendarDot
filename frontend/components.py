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
    def __init__(self, on_day_click):
        super().__init__()
        self.expand = True
        self.on_day_click = on_day_click
        
        #текущий год и месяц
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        
        self.build_grid()

    def build_grid(self):
        self.controls.clear()
        
        cal = calendar.Calendar()
        month_dates = list(cal.itermonthdates(self.current_year, self.current_month))
        month_name = MONTH_NAMES[self.current_month - 1]
        today = date.today()
        
        db = SessionLocal()
        try:
            all_events = get_events_by_date_range(db, month_dates[0], month_dates[-1])
            
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
                ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="Предыдущий месяц", on_click=self.prev_month),
                ft.Text(f"{month_name} {self.current_year}", size=22, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="Следующий месяц", on_click=self.next_month),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700), 
                    alignment=ft.alignment.center, 
                    expand=1
                ) for day in days_of_week
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        weeks = [month_dates[i:i+7] for i in range(0, len(month_dates), 7)]
        
        grid_rows = []
        for week in weeks:
            week_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, expand=1)
            for date_obj in week:
                is_current_month = (date_obj.month == self.current_month)
                is_today = (date_obj == today)
                
                if is_today:
                    text_color = ft.colors.ORANGE_800
                    bg_color = ft.colors.ORANGE_50
                    border_color = ft.colors.ORANGE_200
                    font_weight = ft.FontWeight.BOLD
                else:
                    text_color = ft.colors.BLACK if is_current_month else ft.colors.GREY_400
                    bg_color = ft.colors.WHITE if is_current_month else ft.colors.GREY_50
                    border_color = ft.colors.GREY_200
                    font_weight = ft.FontWeight.NORMAL

                daily_events = events_by_date.get(date_obj, [])
                dots = []
                
                for ev in daily_events[:3]:
                    if ev.category:
                        bright_color_name = ev.category.color.replace("_100", "_400")
                        dot_color = getattr(ft.colors, bright_color_name, ft.colors.BLUE)
                    else:
                        dot_color = ft.colors.BLUE

                    dots.append(
                        ft.Container(
                            width=6, height=6, 
                            border_radius=3, 
                            bgcolor=dot_color,
                        )
                    )
                
                dots_column = ft.Column(controls=dots, spacing=3)
                
                day_content = ft.Row(
                    controls=[
                        ft.Text(str(date_obj.day), size=16, color=text_color, weight=font_weight),
                        dots_column
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )

                day_container = ft.Container(
                    content=day_content,
                    alignment=ft.alignment.top_left,
                    padding=10,
                    border=ft.border.all(1, border_color),
                    border_radius=8,
                    expand=1,
                    bgcolor=bg_color,
                    on_hover=lambda e, default_bg=bg_color: self.highlight_day(e, default_bg),
                    on_click=lambda e, d=date_obj: self.on_day_click(d)
                )
                week_row.controls.append(day_container)
            grid_rows.append(week_row)

        self.controls.extend([month_header, header_row] + grid_rows)

    def highlight_day(self, e, default_bgcolor):
        e.control.bgcolor = ft.colors.BLUE_50 if e.data == "true" else default_bgcolor
        e.control.update()

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