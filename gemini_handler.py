"""
معالج Google Gemini AI - محسن لـ Railway
"""

import logging
import google.generativeai as genai
from config import Config
from typing import Optional, List
import asyncio

logger = logging.getLogger(__name__)

class GeminiHandler:
    """معالج Google Gemini AI"""
    
    def __init__(self):
        self.config = Config()
        
        # إعداد Gemini
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        
        # النماذج
        self.text_model = genai.GenerativeModel(self.config.GEMINI_MODEL)
        self.vision_model = genai.GenerativeModel(self.config.GEMINI_VISION_MODEL)
        
        # إعدادات الأمان
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # إعدادات التوليد
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        logger.info("✅ تم إعداد معالج Gemini")
    
    async def generate_text(self, prompt: str, context: str = None) -> str:
        """توليد نص باستخدام Gemini"""
        try:
            # تحضير النص
            if context:
                full_prompt = f"السياق: {context}\n\nالسؤال: {prompt}"
            else:
                full_prompt = prompt
            
            # إضافة تعليمات اللغة العربية
            system_prompt = """أنت مساعد ذكي يتحدث العربية. أجب بطريقة مفيدة ومهذبة.
            إذا كان السؤال بالإنجليزية، يمكنك الإجابة بالإنجليزية.
            إذا كان السؤال بالعربية، أجب بالعربية.
            كن دقيقاً ومفيداً في إجاباتك."""
            
            final_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # التوليد
            response = await asyncio.to_thread(
                self.text_model.generate_content,
                final_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "❌ لم أتمكن من الحصول على إجابة. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            logger.error(f"خطأ في توليد النص: {e}")
            return f"❌ حدث خطأ في الذكاء الاصطناعي: {str(e)}"
    
    async def analyze_image(self, image_data: bytes, prompt: str = None) -> str:
        """تحليل صورة باستخدام Gemini Vision"""
        try:
            # التحقق من حجم الصورة
            if len(image_data) > 4 * 1024 * 1024:  # 4MB
                return "❌ الصورة كبيرة جداً. يرجى استخدام صورة أصغر من 4MB."
            
            # تحضير النص
            if not prompt:
                prompt = "صف هذه الصورة بالتفصيل باللغة العربية"
            
            # إضافة تعليمات
            system_prompt = """أنت محلل صور ذكي. صف الصورة بالتفصيل باللغة العربية.
            اذكر الأشياء المرئية، الألوان، الأشخاص، الأماكن، والأنشطة.
            كن دقيقاً ومفيداً في وصفك."""
            
            final_prompt = f"{system_prompt}\n\n{prompt}"
            
            # تحضير الصورة
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            # التحليل
            response = await asyncio.to_thread(
                self.vision_model.generate_content,
                [final_prompt, image_part],
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "❌ لم أتمكن من تحليل الصورة. يرجى المحاولة مرة أخرى."
                
        except Exception as e:
            logger.error(f"خطأ في تحليل الصورة: {e}")
            return f"❌ حدث خطأ في تحليل الصورة: {str(e)}"
    
    async def summarize_text(self, text: str) -> str:
        """تلخيص النص"""
        try:
            prompt = f"""قم بتلخيص النص التالي بطريقة واضحة ومفيدة:

النص:
{text}

قدم تلخيصاً شاملاً يغطي النقاط الرئيسية."""
            
            return await self.generate_text(prompt)
            
        except Exception as e:
            logger.error(f"خطأ في تلخيص النص: {e}")
            return f"❌ حدث خطأ في تلخيص النص: {str(e)}"
    
    async def translate_text(self, text: str, target_language: str = "ar") -> str:
        """ترجمة النص"""
        try:
            language_names = {
                "ar": "العربية",
                "en": "الإنجليزية",
                "fr": "الفرنسية",
                "es": "الإسبانية",
                "de": "الألمانية",
                "it": "الإيطالية",
                "ru": "الروسية",
                "ja": "اليابانية",
                "ko": "الكورية",
                "zh": "الصينية"
            }
            
            target_lang_name = language_names.get(target_language, target_language)
            
            prompt = f"""قم بترجمة النص التالي إلى {target_lang_name}:

النص:
{text}

قدم الترجمة بدقة مع مراعاة المعنى والسياق."""
            
            return await self.generate_text(prompt)
            
        except Exception as e:
            logger.error(f"خطأ في ترجمة النص: {e}")
            return f"❌ حدث خطأ في ترجمة النص: {str(e)}"
    
    async def answer_question(self, question: str, context: str = None) -> str:
        """الإجابة على سؤال"""
        try:
            # تحضير النص
            if context:
                prompt = f"""بناءً على السياق التالي، أجب على السؤال:

السياق: {context}

السؤال: {question}

قدم إجابة شاملة ومفيدة."""
            else:
                prompt = f"أجب على السؤال التالي بطريقة مفيدة وشاملة: {question}"
            
            return await self.generate_text(prompt)
            
        except Exception as e:
            logger.error(f"خطأ في الإجابة على السؤال: {e}")
            return f"❌ حدث خطأ في الإجابة على السؤال: {str(e)}"
    
    async def chat_response(self, message: str, user_name: str = None) -> str:
        """رد محادثة عادية"""
        try:
            # تحضير النص
            if user_name:
                prompt = f"""أنت مساعد ذكي تتحدث مع {user_name}. 
                
رسالة المستخدم: {message}

أجب بطريقة ودية ومفيدة."""
            else:
                prompt = f"أجب على الرسالة التالية بطريقة ودية ومفيدة: {message}"
            
            return await self.generate_text(prompt)
            
        except Exception as e:
            logger.error(f"خطأ في رد المحادثة: {e}")
            return f"❌ حدث خطأ في المحادثة: {str(e)}"
    
    def test_connection(self) -> bool:
        """اختبار الاتصال بـ Gemini"""
        try:
            # اختبار بسيط
            response = self.text_model.generate_content("مرحبا")
            return response.text is not None
        except Exception as e:
            logger.error(f"خطأ في اختبار الاتصال: {e}")
            return False