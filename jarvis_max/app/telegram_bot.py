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
        
        try:
            # Validate input
            if not user_message or len(user_message.strip()) == 0:
                await update.message.reply_text("Please provide a valid message")
                return
                
            if len(user_message) > 1000:
                await update.message.reply_text("Message too long. Please keep it under 1000 characters.")
                return
            
            # Process through AI brain
            response = await self.brain.process_query(user_message)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error handling Telegram message: {str(e)}")
            await update.message.reply_text("Sorry, I encountered an error processing your message. Please try again.")
        
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
