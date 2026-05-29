import flet as ft
import calendar
from datetime import datetime, date, timedelta
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


class WeekGrid(ft.Column):
    def __init__(self, user_id: int, on_day_click):
        super().__init__()
        self.user_id = user_id
        self.on_day_click = on_day_click
        self.expand = True
        self.spacing = 0

        now = date.today()
        self.start_of_week = now - timedelta(days=now.weekday())

        self.build_grid()

    def prev_week(self, e):
        self.start_of_week -= timedelta(days=7)
        self.build_grid()
        self.update()

    def next_week(self, e):
        self.start_of_week += timedelta(days=7)
        self.build_grid()
        self.update()

    def build_grid(self):
        self.controls.clear()
        days_of_week = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
        week_dates = [self.start_of_week + timedelta(days=i) for i in range(7)]

        db = SessionLocal()
        try:
            week_events = get_events_by_date_range(db, week_dates[0], week_dates[-1], self.user_id)
            events_by_date = {}
            for ev in week_events:
                ev_date = ev.start_time.date()
                if ev_date not in events_by_date:
                    events_by_date[ev_date] = []
                events_by_date[ev_date].append(ev)
        finally:
            db.close()

        month_name = MONTH_NAMES[self.start_of_week.month - 1]
        year = self.start_of_week.year

        week_nav_header = ft.Row(
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="Предыдущая неделя", on_click=self.prev_week),
                    ft.Text(f"{month_name} {year}", size=22, weight=ft.FontWeight.W_500),
                    ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="Следующая неделя", on_click=self.next_week),
                ])
            ],
            alignment=ft.MainAxisAlignment.START
        )

        header_controls = [ft.Container(width=60)]
        
        for i, d in enumerate(week_dates):
            is_today = d == date.today()
            date_num = ft.Container(
                content=ft.Text(
                    str(d.day), size=22, 
                    color=ft.colors.ON_PRIMARY if is_today else ft.colors.ON_SURFACE, 
                    weight=ft.FontWeight.W_400 if not is_today else ft.FontWeight.W_500
                ),
                bgcolor=ft.colors.PRIMARY if is_today else ft.colors.TRANSPARENT,
                width=46, height=46, border_radius=23, alignment=ft.alignment.center
            )
            day_name = ft.Text(days_of_week[i], size=11, color=ft.colors.PRIMARY if is_today else ft.colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
            
            header_controls.append(
                ft.Container(
                    content=ft.Column([day_name, date_num], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=1, alignment=ft.alignment.center, padding=ft.padding.only(top=5, bottom=5),
                    on_click=lambda e, current_d=d: self.on_day_click(current_d), # Делаем заголовок кликабельным
                    ink=True
                )
            )

        header_row = ft.Row(controls=header_controls, alignment=ft.MainAxisAlignment.START, spacing=0)
        grid_line_color = ft.colors.with_opacity(0.15, ft.colors.ON_SURFACE)

        time_col = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        f"{h:02d}:00" if h > 0 else "", size=11, color=ft.colors.ON_SURFACE_VARIANT, offset=ft.transform.Offset(0, -0.6) 
                    ),
                    height=60, alignment=ft.alignment.top_right, padding=ft.padding.only(right=8)
                ) for h in range(24)
            ],
            width=60, spacing=0
        )

        bg_columns = ft.Row(expand=True, spacing=0)
        for i, d in enumerate(week_dates):
            
            day_grid_lines = ft.Column(
                controls=[
                    ft.Container(
                        height=60,
                        border=ft.border.only(
                            top=ft.border.BorderSide(1, grid_line_color),
                            left=ft.border.BorderSide(1, grid_line_color) if i == 0 else None,
                            right=ft.border.BorderSide(1, grid_line_color)
                        )
                    ) for _ in range(24)
                ],
                spacing=0
            )

            daily_events_controls = []
            for ev in events_by_date.get(d, []):
                start_mins = ev.start_time.hour * 60 + ev.start_time.minute
                end_mins = ev.end_time.hour * 60 + ev.end_time.minute
                duration = end_mins - start_mins
                if duration < 20: duration = 20

                base_color = ft.colors.PRIMARY
                if ev.category:
                    base_color = getattr(ft.colors, ev.category.color, ft.colors.PRIMARY)
                
                bg_event_color = ft.colors.with_opacity(0.15, base_color)
                border_left = ft.border.only(left=ft.border.BorderSide(3, base_color))

                ev_card = ft.Container(
                    top=start_mins, height=duration, left=2, right=4,
                    bgcolor=bg_event_color, border=border_left, border_radius=4,
                    padding=ft.padding.only(left=6, top=2, right=2, bottom=2),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Column([
                        ft.Text(ev.title, size=11, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, no_wrap=True),
                        ft.Text(f"{ev.start_time.strftime('%H:%M')} - {ev.end_time.strftime('%H:%M')}", size=9, color=ft.colors.ON_SURFACE_VARIANT, no_wrap=True)
                    ], spacing=1)
                )
                daily_events_controls.append(ev_card)

            day_stack = ft.Stack(
                controls=[day_grid_lines] + daily_events_controls,
                height=1440,
            )
            
            bg_columns.controls.append(
                ft.Container(
                    content=day_stack, 
                    expand=1,
                    on_click=lambda e, current_d=d: self.on_day_click(current_d)
                )
            )

        scrollable_area = ft.Column(
            controls=[
                ft.Row([time_col, bg_columns], alignment=ft.MainAxisAlignment.START, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)
            ],
            scroll=ft.ScrollMode.AUTO, 
            expand=True
        )

        self.controls.extend([
            ft.Container(content=week_nav_header, padding=ft.padding.only(bottom=5)),
            header_row,
            ft.Divider(height=1, color=ft.colors.OUTLINE_VARIANT),
            scrollable_area
        ])