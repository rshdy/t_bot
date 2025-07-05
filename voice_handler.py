"""
معالج تحويل النص إلى صوت - محسن لـ Railway
"""

import logging
import io
import asyncio
from gtts import gTTS
from config import Config
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceHandler:
    """معالج تحويل النص إلى صوت"""
    
    def __init__(self):
        self.config = Config()
        logger.info("✅ تم إعداد معالج الصوت")
    
    async def text_to_speech(self, text: str, language: str = None) -> Optional[bytes]:
        """تحويل النص إلى صوت"""
        try:
            if not text or not text.strip():
                return None
            
            # تحديد اللغة
            if not language:
                language = self.config.VOICE_LANGUAGE
            
            # تنظيف النص
            text = self.clean_text(text)
            
            # التحقق من طول النص
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            # إنشاء الصوت
            tts = gTTS(text=text, lang=language, slow=False)
            
            # حفظ في الذاكرة
            audio_buffer = io.BytesIO()
            
            # استخدام asyncio.to_thread للعمليات المتزامنة
            await asyncio.to_thread(tts.write_to_fp, audio_buffer)
            
            # إرجاع البيانات
            audio_buffer.seek(0)
            return audio_buffer.read()
            
        except Exception as e:
            logger.error(f"خطأ في تحويل النص إلى صوت: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """تنظيف النص للصوت"""
        # إزالة الرموز التعبيرية
        import re
        
        # إزالة الرموز التعبيرية
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub(r' ', text)
        
        # إزالة الأحرف الخاصة
        text = re.sub(r'[^\w\s\u0600-\u06FF.,!?;:]', ' ', text)
        
        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        
        # تنظيف النص
        text = text.strip()
        
        return text
    
    async def generate_voice_message(self, text: str, language: str = None) -> Optional[bytes]:
        """إنشاء رسالة صوتية"""
        try:
            # تحويل النص إلى صوت
            audio_data = await self.text_to_speech(text, language)
            
            if audio_data:
                logger.info(f"✅ تم إنشاء رسالة صوتية بحجم {len(audio_data)} بايت")
                return audio_data
            else:
                logger.error("❌ فشل في إنشاء الرسالة الصوتية")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء الرسالة الصوتية: {e}")
            return None
    
    def detect_language(self, text: str) -> str:
        """كشف لغة النص"""
        try:
            import re
            
            # فحص وجود أحرف عربية
            arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
            # فحص وجود أحرف إنجليزية
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if arabic_chars > english_chars:
                return 'ar'
            elif english_chars > 0:
                return 'en'
            else:
                return self.config.DEFAULT_LANGUAGE
                
        except Exception as e:
            logger.error(f"خطأ في كشف اللغة: {e}")
            return self.config.DEFAULT_LANGUAGE
    
    async def create_voice_response(self, text: str, auto_detect_language: bool = True) -> Optional[bytes]:
        """إنشاء رد صوتي"""
        try:
            # كشف اللغة تلقائياً
            if auto_detect_language:
                language = self.detect_language(text)
            else:
                language = self.config.VOICE_LANGUAGE
            
            # إنشاء الصوت
            return await self.generate_voice_message(text, language)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الرد الصوتي: {e}")
            return None
    
    def get_supported_languages(self) -> dict:
        """الحصول على اللغات المدعومة"""
        return {
            'ar': 'العربية',
            'en': 'English',
            'fr': 'Français',
            'es': 'Español',
            'de': 'Deutsch',
            'it': 'Italiano',
            'ru': 'Русский',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文'
        }
    
    def validate_language(self, language: str) -> bool:
        """التحقق من صحة اللغة"""
        supported_languages = self.get_supported_languages()
        return language in supported_languages
    
    async def test_voice_generation(self) -> bool:
        """اختبار إنشاء الصوت"""
        try:
            test_text = "مرحبا، هذا اختبار للصوت"
            audio_data = await self.text_to_speech(test_text)
            return audio_data is not None
        except Exception as e:
            logger.error(f"خطأ في اختبار الصوت: {e}")
            return False