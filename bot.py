import os, asyncio, yfinance as yf, pandas as pd, pytz, ta
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PAIRS = ["EURUSD=X", "GBPUSD=X", "BTC-USD"]
TF = "1m"

bot = Bot(token=TOKEN)

def signal(symbol):
    df = yf.download(symbol, period="1d", interval=TF, progress=False)
    if len(df) < 25: return None
    c = df['Close']
    rsi = ta.momentum.RSIIndicator(c, 14).rsi().iloc[-1]
    bb = ta.volatility.BollingerBands(c, 20, 2)
    price, low, high = c.iloc[-1], bb.bollinger_lband().iloc[-1], bb.bollinger_hband().iloc[-1]
    name = symbol.replace("=X","").replace("-USD","/USD")
    if price <= low and rsi < 30: return f"شراء 🟢 {name} | {TF} | RSI {rsi:.1f}"
    if price >= high and rsi > 70: return f"بيع 🔴 {name} | {TF} | RSI {rsi:.1f}"

async def check():
    for p in PAIRS:
        try:
            s = signal(p)
            if s: await bot.send_message(CHAT_ID, s)
        except: pass

async def main():
    scheduler = AsyncIOScheduler(timezone='Asia/Riyadh')
    scheduler.add_job(check, 'interval', seconds=55)
    scheduler.start()
    await asyncio.Event().wait()

if __name__ == '__main__': asyncio.run(main())
