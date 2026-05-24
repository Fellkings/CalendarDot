from sqlalchemy.orm import Session
from datetime import datetime, date, time
from backend.models import Event

def create_single_event(db: Session, title: str, description: str, event_date: date, start_t: time = None, end_t: time = None):
    #cоздает одиночное событие в базе данных.
    actual_start_time = start_t if start_t else time(0, 0)
    actual_end_time = end_t if end_t else time(23, 59)
    
    start_datetime = datetime.combine(event_date, actual_start_time)
    end_datetime = datetime.combine(event_date, actual_end_time)
    
    new_event = Event(
        title=title,
        description=description,
        start_time=start_datetime,
        end_time=end_datetime
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

def delete_event(db: Session, event_id: int):
    #удаление события
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False