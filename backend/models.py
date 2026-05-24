from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id = Column(Integer, primary_key=True, index=True)
    frequency = Column(String, nullable=False)
    interval = Column(Integer, default=1)
    by_day = Column(String, nullable=True)
    until = Column(DateTime, nullable=True)
    count = Column(Integer, nullable=True)

    events = relationship("Event", back_populates="recurrence_rule")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    recurrence_rule_id = Column(Integer, ForeignKey("recurrence_rules.id"), nullable=True)
    recurrence_rule = relationship("RecurrenceRule", back_populates="events")