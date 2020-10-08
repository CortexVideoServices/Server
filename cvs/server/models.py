from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Numeric, Boolean
from sqlalchemy import func

Base = declarative_base()


class Session(Base):
    """ Video session
    """
    __tablename__ = 'session'
    id = Column(String, primary_key=True)
    room_num = Column(Numeric, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=False)
    allow_anonymous = Column(Boolean, nullable=False)
    display_name = Column(String)
    expired_at = Column(DateTime, nullable=False)
