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