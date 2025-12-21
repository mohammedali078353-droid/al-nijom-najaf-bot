from flask import Flask, request
import asyncio
from aiogram import types
from main import bot, dp

app = Flask(__name__)

@app.post("/")
async def webhook():
    data = request.json
    update = types.Update.to_object(data)
    await dp.feed_update(bot, update)
    return "ok"
