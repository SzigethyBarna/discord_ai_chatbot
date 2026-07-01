from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    platform = Column(String)
    system_prompt = Column(String)
    is_active = Column(Boolean, default=False)