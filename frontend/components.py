import flet as ft
import calendar
from datetime import datetime

MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]

def create_month_grid():
    #текущий год и месяц
    now = datetime.now()
    year = now.year
    month = now.month

    cal = calendar.Calendar()
    month_dates = list(cal.itermonthdates(year, month))

    month_name = MONTH_NAMES[month - 1] 
    
    month_header = ft.Row(
        controls=[
            ft.IconButton(icon=ft.icons.CHEVRON_LEFT, tooltip="Предыдущий месяц"),
            ft.Text(f"{month_name} {year}", size=22, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, tooltip="Следующий месяц"),
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
        week_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        for date_obj in week:
            is_current_month = (date_obj.month == month)
            
            text_color = ft.colors.BLACK if is_current_month else ft.colors.GREY_400
            bg_color = ft.colors.WHITE if is_current_month else ft.colors.GREY_50

            day_container = ft.Container(
                content=ft.Text(str(date_obj.day), size=16, color=text_color),
                alignment=ft.alignment.top_left,
                padding=10,
                border=ft.border.all(1, ft.colors.GREY_200),
                border_radius=8,
                expand=1,
                height=100,
                bgcolor=bg_color,
                on_hover=lambda e, default_bg=bg_color: highlight_day(e, default_bg)
            )
            week_row.controls.append(day_container)
        grid_rows.append(week_row)

    return ft.Column(controls=[month_header, header_row] + grid_rows, expand=True)

#для подсветки ячейки при наведении
def highlight_day(e, default_bgcolor):
    e.control.bgcolor = ft.colors.BLUE_50 if e.data == "true" else default_bgcolor
    e.control.update()