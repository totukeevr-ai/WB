import os
import logging
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from dotenv import load_dotenv

# Import our modules
from .brain import AIBrain
from .executor import Executor
from .voice import VoiceManager
from .tts import TTSManager
from .telegram_bot import TelegramBot

load_dotenv()

# Validate required environment variables
required_vars = ['TELEGRAM_BOT_TOKEN', 'DEEPSEEK_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    # Don't exit immediately to allow partial functionality
    # In production, you might want to exit

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("jarvis")

app = FastAPI(title="Jarvis MAX", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
brain = AIBrain()
executor = Executor()
voice_manager = VoiceManager()
tts_manager = TTSManager()

# Start Telegram bot in background
def start_telegram_bot():
    bot = TelegramBot()
    bot.run()

# Start the bot when the app starts
telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
telegram_thread.start()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received via WebSocket: {data}")
            
            # Validate input
            if not data or len(data.strip()) == 0:
                await websocket.send_text("Error: Empty query")
                continue
                
            if len(data) > 1000:
                await websocket.send_text("Error: Query too long")
                continue
            
            try:
                # Process the query through AI brain
                response = await brain.process_query(data)
                await websocket.send_text(f"AI Response: {response}")
                
                # Optionally, execute commands if they're in the response
                if "execute:" in response.lower():
                    command = response.split("execute:")[-1].strip()
                    result = await executor.execute_command(command)
                    await websocket.send_text(f"Command result: {result}")
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                await websocket.send_text(f"Error processing your request: {str(e)}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7863)
