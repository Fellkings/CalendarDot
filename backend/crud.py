from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from datetime import datetime, date, time
from backend.models import Event, Category

def create_single_event(db: Session, title: str, description: str, event_date: date, user_id: int,
                        start_t: time = None, end_t: time = None, category_id: int = None):
    #создает одиночное событие в базе данных
    actual_start_time = start_t if start_t else time(0, 0)
    actual_end_time = end_t if end_t else time(23, 59)
    
    start_datetime = datetime.combine(event_date, actual_start_time)
    end_datetime = datetime.combine(event_date, actual_end_time)
    
    new_event = Event(
        title=title,
        description=description,
        start_time=start_datetime,
        end_time=end_datetime,
        category_id=category_id,
        user_id=user_id
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_events_by_date(db: Session, event_date: date, user_id: int):
    #список всех событий за определенный день
    start_of_day = datetime.combine(event_date, time(0, 0))
    end_of_day = datetime.combine(event_date, time(23, 59))
    
    #фильтр событий, которые начинаются в пределах этого дня
    return db.query(Event).options(joinedload(Event.category)).filter(
        Event.user_id == user_id,
        Event.start_time >= start_of_day,
        Event.start_time <= end_of_day
    ).order_by(Event.start_time).all()

def get_events_by_date_range(db: Session, start_date: date, end_date: date, user_id: int):
    #список событий на всю сетку
    start_dt = datetime.combine(start_date, time(0, 0))
    end_dt = datetime.combine(end_date, time(23, 59))
    
    return db.query(Event).options(joinedload(Event.category)).filter(
        Event.user_id == user_id,
        Event.start_time >= start_dt,
        Event.start_time <= end_dt
    ).all()

def delete_event(db: Session, event_id: int, user_id: int):
    #удаление события
    event = db.query(Event).filter(Event.id == event_id, Event.user_id == user_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False

def get_all_categories(db: Session, user_id: int):
    #список категорий
    categories = db.query(Category).filter(Category.user_id == user_id).order_by(Category.name).all()
    if not categories:
        default_cats = [
            Category(name="Работа", color="BLUE", emoji="💼", user_id=user_id),
            Category(name="Личное", color="GREEN", emoji="🏠", user_id=user_id),
            Category(name="Важное", color="RED", emoji="🔥", user_id=user_id),
            Category(name="Отдых", color="PURPLE", emoji="☕", user_id=user_id)
        ]
        db.add_all(default_cats)
        db.commit()
        
        categories = db.query(Category).filter(Category.user_id == user_id).order_by(Category.name).all()
        
    return categories

def search_user_events(db: Session, user_id: int, query: str):
    #поиск по событиям пользователя
    search_pattern = f"%{query}%"
    
    return db.query(Event).filter(
        Event.user_id == user_id,
        or_(
            Event.title.ilike(search_pattern),
            Event.description.ilike(search_pattern)
        )
    ).order_by(Event.start_time).limit(20).all()