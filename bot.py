import asyncio
import logging
import json
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import Command

from config import TOKEN
from parser import parse_ozon, detect_ozon
from analyzer import analyze_product
from models import Product
from utils import log_execution

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

HISTORY_FILE = "history.json"


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_history(product, analysis):
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "product_name": product.name,
        "price": product.price,
        "risk_score": analysis.risk_score,
        "verdict": analysis.verdict
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-50:], f, ensure_ascii=False, indent=2)  # last 50


def get_ozon_url(text: str):
    if not text:
        return None
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    for u in urls:
        u = u.rstrip(".,)!")
        if detect_ozon(u):
            return u
    return None


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 <b>Welcome to Authenticity AI</b>\n\n"
        "I analyze Ozon products and detect risk of counterfeit items.\n\n"
        "Just send the product link!"
    )


@dp.message(Command("history"))
async def show_history(message: Message):
    history = load_history()
    if not history:
        await message.answer("No analysis history yet.")
        return

    text = "<b>📊 Last Analyses:</b>\n\n"
    for entry in history[-5:]:
        text += f"• {entry['timestamp'][:16]}\n"
        text += f"   {entry['product_name'][:50]}...\n"
        text += f"   Risk: <b>{entry['risk_score']}/100</b> — {entry['verdict']}\n\n"
    await message.answer(text)


@dp.message()
@log_execution
async def handle(message: Message):
    url = get_ozon_url(message.text or "")

    if not url:
        await message.answer("🔗 Please send an <b>Ozon</b> product link.")
        return

    status = await message.answer("🔍 <b>Authenticity AI is analyzing...</b>")

    steps = [
        "📡 Fetching data from Ozon...",
        "📊 Analyzing price...",
        "⭐ Checking rating & reviews...",
        "🕵️ Scanning for suspicious signs...",
        "🧠 Generating final report..."
    ]

    for step in steps:
        await asyncio.sleep(0.9)
        await status.edit_text(step)

    data, error = await asyncio.get_event_loop().run_in_executor(None, parse_ozon, url)

    if error or not data:
        await status.edit_text(f"❌ {error or 'Failed to load product.'}")
        return

    product = Product(
        name=data.get("name", "Unknown Product"),
        price=data.get("price"),
        rating=data.get("rating"),
        reviews=data.get("reviews", 0),
        url=url
    )

    analysis = analyze_product(product)
    save_history(product, analysis)

    # Beautiful Message
    lines = [
        f"📦 <b>{product.name}</b>\n",
        f"💰 Price: <b>{product.price:,} ₸</b>" if product.price else "",
        f"⭐ Rating: <b>{product.rating}</b> ({product.reviews} reviews)" if product.rating else "",
        "\n" + "═" * 40,
        f"{analysis.emoji} <b>{analysis.verdict}</b>",
        f"Risk Score: <b>{analysis.risk_score}/100</b> — {analysis.risk_level}\n"
    ]

    if analysis.flags:
        lines.append("<b>⚠️ Red Flags:</b>")
        for f in analysis.flags:
            lines.append(f"• {f}")

    if analysis.good:
        lines.append("\n<b>✅ Positive Signals:</b>")
        for g in analysis.good:
            lines.append(f"• {g}")

    lines.append(f"\n<i>Analyzed at {analysis.timestamp}</i>")

    await status.edit_text("\n".join(filter(None, lines)))


async def main():
    logging.info("🚀 Authenticity AI Bot started successfully!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())