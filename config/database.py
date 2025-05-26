from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    feedback_type = Column(String(20), nullable=False)
    rating = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)
    page = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

class NewsAnalysis(Base):
    __tablename__ = "news_analysis"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    input_text = Column(Text, nullable=False)
    roberta_prediction = Column(String(10), nullable=False)
    roberta_confidence = Column(Float, nullable=False)
    newsapi_confidence = Column(Float, nullable=False)
    final_prediction = Column(String(20), nullable=False)
    perplexity_prediction = Column(String(20), nullable=True)
    perplexity_report = Column(Text, nullable=True)
    articles_analyzed = Column(Integer, default=0)
    trusted_sources_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

@st.cache_resource
def get_database_engine():
    from config.settings import DATABASE_URL
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session():
    engine = get_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()
