"""
إعدادات البوت - محسن لـ Railway
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات البوت"""
    
    def __init__(self):
        # مفاتيح API
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        self.ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '0'))
        
        # إعدادات Gemini
        self.GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
        self.GEMINI_VISION_MODEL = os.getenv('GEMINI_VISION_MODEL', 'gemini-pro-vision')
        
        # إعدادات عامة
        self.MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
        self.VOICE_LANGUAGE = os.getenv('VOICE_LANGUAGE', 'ar')
        self.DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'ar')
        
        # إعدادات Railway
        self.PORT = int(os.getenv('PORT', '8000'))
        self.RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'production')
        
        # التحقق من الإعدادات
        self.validate_config()
    
    def validate_config(self):
        """التحقق من صحة الإعدادات"""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': self.TELEGRAM_BOT_TOKEN,
            'GEMINI_API_KEY': self.GEMINI_API_KEY,
            'ADMIN_CHAT_ID': self.ADMIN_CHAT_ID
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"متغيرات البيئة المفقودة: {', '.join(missing_vars)}")
        
        print("✅ تم التحقق من جميع الإعدادات بنجاح")
    
    def is_admin(self, user_id: int) -> bool:
        """التحقق من أن المستخدم مدير"""
        return user_id == self.ADMIN_CHAT_ID
    
    def get_info(self) -> dict:
        """الحصول على معلومات الإعدادات"""
        return {
            'environment': self.RAILWAY_ENVIRONMENT,
            'port': self.PORT,
            'max_message_length': self.MAX_MESSAGE_LENGTH,
            'voice_language': self.VOICE_LANGUAGE,
            'default_language': self.DEFAULT_LANGUAGE,
            'gemini_model': self.GEMINI_MODEL,
            'gemini_vision_model': self.GEMINI_VISION_MODEL
        }