#!/usr/bin/env python3
"""
بوت تلكرام للذكاء الاصطناعي - محسن لـ Railway
"""

import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import Config
from gemini_handler import GeminiHandler
from voice_handler import VoiceHandler
from bot_handlers import BotHandlers

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """بوت تلكرام الذكي"""
    
    def __init__(self):
        self.config = Config()
        self.gemini_handler = GeminiHandler()
        self.voice_handler = VoiceHandler()
        self.bot_handlers = BotHandlers(self.gemini_handler, self.voice_handler)
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البدء"""
        await self.bot_handlers.start_handler(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        await self.bot_handlers.help_handler(update, context)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الإحصائيات"""
        await self.bot_handlers.stats_handler(update, context)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل"""
        await self.bot_handlers.message_handler(update, context)
    
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الصور"""
        await self.bot_handlers.photo_handler(update, context)
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        await self.bot_handlers.callback_handler(update, context)
    
    async def admin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج المدراء"""
        await self.bot_handlers.admin_handler(update, context)
    
    def setup_handlers(self):
        """إعداد معالجات البوت"""
        # أوامر أساسية
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("admin", self.admin_handler))
        
        # معالجات المحتوى
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.photo_handler))
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))
        
        logger.info("✅ تم إعداد معالجات البوت")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"خطأ في البوت: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ حدث خطأ مؤقت. يرجى المحاولة مرة أخرى."
            )
    
    def run(self):
        """تشغيل البوت"""
        try:
            # إنشاء التطبيق
            self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # إعداد المعالجات
            self.setup_handlers()
            
            # معالج الأخطاء
            self.application.add_error_handler(self.error_handler)
            
            # تشغيل البوت
            port = int(os.environ.get('PORT', 8000))
            logger.info(f"🚀 تشغيل البوت على المنفذ {port}")
            
            # تشغيل الخدمة
            self.application.run_polling(drop_pending_updates=True)
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            raise

def main():
    """الدالة الرئيسية"""
    try:
        logger.info("🤖 بدء تشغيل بوت الذكاء الاصطناعي")
        
        # إنشاء وتشغيل البوت
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت")
    except Exception as e:
        logger.error(f"❌ خطأ قاتل: {e}")

if __name__ == "__main__":
    main()