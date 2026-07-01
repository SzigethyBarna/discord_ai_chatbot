import asyncio
import os
import discord
import traceback
from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

import models
from database import SessionLocal

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not GROQ_API_KEY or not DISCORD_BOT_TOKEN:
    raise ValueError("Hiányzik a GROQ_API_KEY vagy a DISCORD_BOT_TOKEN a .env fájlból!")

groq_client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

async def run_bot_instance(bot_id: int):
    print(f"[MOTOR] A {bot_id}. azonosítójú bot motorja inicializálás alatt...")
    
    db: Session = SessionLocal()
    bot_data = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot_data or not bot_data.is_active:
        db.close()
        return
        
    system_prompt = bot_data.system_prompt
    bot_name = bot_data.name
    db.close()

    intents = discord.Intents.default()
    intents.message_content = True
    discord_client = discord.Client(intents=intents)

    @discord_client.event
    async def on_ready():
        print(f"[DISCORD] '{bot_name}' ({discord_client.user}) sikeresen csatlakozott!")
        discord_client.loop.create_task(check_if_stopped())

    @discord_client.event
    async def on_message(message):
        if message.author == discord_client.user:
            return

        print(f"[CHAT] {message.author.name}: {message.content}")

        async with message.channel.typing():
            try:
                response = await groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{message.author.name} kérdezi: {message.content}"}
                    ]
                )
                answer = response.choices[0].message.content
 
                await message.channel.send(answer)
                
            except Exception as e:
                print("\n" + "="*40)
                print("[RÉSZLETES AI HIBA JELENTÉS]")
                traceback.print_exc() 
                print("="*40 + "\n")
                await message.channel.send("Bocsi, valami hiba történt a szerveremen, nem tudok válaszolni.")
    
    async def check_if_stopped():
        while not discord_client.is_closed():
            await asyncio.sleep(5) 
            db_check: Session = SessionLocal()
            current_bot = db_check.query(models.Bot).filter(models.Bot.id == bot_id).first()
            
            if not current_bot or not current_bot.is_active:
                print(f"[MOTOR] A {bot_id}. bot leállítása kérve az API-n keresztül. Kijelentkezés...")
                await discord_client.close()
            db_check.close()

    try:
        await discord_client.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"[DISCORD HIBA] Nem sikerült elindítani a botot: {e}")
        
        
        db_fail: Session = SessionLocal()
        bot_fail = db_fail.query(models.Bot).filter(models.Bot.id == bot_id).first()
        if bot_fail:
            bot_fail.is_active = False
            db_fail.commit()
        db_fail.close()