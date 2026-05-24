from sqlalchemy.orm import Session
from datetime import datetime, date, time
from backend.models import Event

def create_single_event(db: Session, title: str, description: str, event_date: date):

    #cоздает одиночное событие в базе данных.
    #пока на весь день
    start_time = datetime.combine(event_date, time(0, 0))
    end_time = datetime.combine(event_date, time(23, 59))
    
    new_event = Event(
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time
    )
    
    db.add(new_event)
    db.commit()
    
    db.refresh(new_event)
    return new_event

def get_events_by_date(db: Session, event_date: date):
    #список всех событий за определенный день
    start_of_day = datetime.combine(event_date, time(0, 0))
    end_of_day = datetime.combine(event_date, time(23, 59))
    
    #фильтр событий, которые начинаются в пределах этого дня
    return db.query(Event).filter(
        Event.start_time >= start_of_day,
        Event.start_time <= end_of_day
    ).order_by(Event.start_time).all()

def get_events_by_date_range(db: Session, start_date: date, end_date: date):
    #список событий на всю сетку
    start_dt = datetime.combine(start_date, time(0, 0))
    end_dt = datetime.combine(end_date, time(23, 59))
    
    return db.query(Event).filter(
        Event.start_time >= start_dt,
        Event.start_time <= end_dt
    ).all()