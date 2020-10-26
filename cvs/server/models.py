from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Numeric, Boolean, Text
from sqlalchemy import ForeignKey, func

Base = declarative_base()


class Session(Base):
    """ Video session
    """
    __tablename__ = 'session'
    id = Column(String, primary_key=True)
    app_id = Column(String, ForeignKey('application.id'), nullable=False)
    room_num = Column(Numeric, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=False)
    allow_anonymous = Column(Boolean, nullable=False)
    display_name = Column(String)
    expired_at = Column(DateTime, nullable=False)


class Application(Base):
    """ Application
    """
    __tablename__ = 'application'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    modified_at = Column(DateTime, server_default=func.now(), nullable=False)
    description = Column(String, nullable=False)
    jwt_secret = Column(String, nullable=False)
