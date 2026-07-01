from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BaaS API - Véglegesített Adatbázissal")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/bots/", response_model=schemas.BotResponse)
def create_bot(bot: schemas.BotCreate, db: Session = Depends(get_db)):
    """Új bot létrehozása és elmentése az adatbázisba."""
    db_bot = models.Bot(
        name=bot.name,
        platform=bot.platform,
        system_prompt=bot.system_prompt
    )
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@app.get("/api/bots/", response_model=List[schemas.BotResponse])
def get_all_bots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Az összes regisztrált bot lekérdezése."""
    bots = db.query(models.Bot).offset(skip).limit(limit).all()
    return bots

@app.get("/api/bots/{bot_id}", response_model=schemas.BotResponse)
def get_bot(bot_id: int, db: Session = Depends(get_db)):
    """Egy konkrét bot lekérdezése azonosító alapján."""
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if bot is None:
        raise HTTPException(status_code=404, detail="A bot nem található")
    return bot

from fastapi import BackgroundTasks
import engine

@app.post("/api/bots/{bot_id}/start")
def start_bot(bot_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Elindítja az adott azonosítójú botot a háttérben."""
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="A bot nem található")
    if bot.is_active:
        raise HTTPException(status_code=400, detail="A bot már fut")
        

    bot.is_active = True
    db.commit()
    

    background_tasks.add_task(engine.run_bot_instance, bot_id)
    
    return {"message": f"A(z) {bot_id}. azonosítójú bot elindítva."}

@app.post("/api/bots/{bot_id}/stop")
def stop_bot(bot_id: int, db: Session = Depends(get_db)):
    """Leállítja a futó botot."""
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    
    if not bot:
        raise HTTPException(status_code=404, detail="A bot nem található")
    if not bot.is_active:
        raise HTTPException(status_code=400, detail="A bot jelenleg sem fut")
        

    bot.is_active = False
    db.commit()
    
    return {"message": f"A(z) {bot_id}. azonosítójú bot leállítása megkezdődött."}