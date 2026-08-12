# main.py
# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.database import init_db, async_session_maker
from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.products import router as products_router
from app.api.comments import router as comments_router
from app.api.stocks import router as stocks_router
from app.api.market import router as market_router
from app.api.leaderboard import router as leaderboard_router
from app.api.rewards import router as rewards_router
from app.api.websocket import router as ws_router
from app.services.market_data import price_loop
import os, asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("✅ Database ready!")
    asyncio.create_task(price_loop(async_session_maker))
    print("✅ Live prices running!")
    yield

app = FastAPI(title="Market Mogul Pro", lifespan=lifespan)

static_dir = "app/static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(products_router)
app.include_router(comments_router)
app.include_router(stocks_router)
app.include_router(market_router)
app.include_router(leaderboard_router)
app.include_router(rewards_router)
app.include_router(ws_router)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("app/templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()