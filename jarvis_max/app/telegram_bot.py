import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .brain import AIBrain

logger = logging.getLogger("jarvis.telegram")

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.brain = AIBrain()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Hello! I am Jarvis MAX. How can I assist you?')
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_message = update.message.text
        logger.info(f"Received Telegram message: {user_message}")
        
        # Process through AI brain
        response = await self.brain.process_query(user_message)
        await update.message.reply_text(response)
        
    def run(self):
        if not self.token:
            logger.error("No TELEGRAM_BOT_TOKEN found in environment")
            return
            
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start the bot
        application.run_polling()
