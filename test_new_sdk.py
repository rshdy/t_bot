"""
اختبار SDK الجديد لـ Gemini
"""

import asyncio
import sys
import os
from gemini_handler import GeminiHandler

async def test_new_sdk():
    """اختبار SDK الجديد"""
    
    print("🚀 اختبار SDK الجديد لـ Gemini")
    print("=" * 50)
    
    try:
        # إنشاء معالج Gemini
        print("📡 إنشاء معالج Gemini...")
        handler = GeminiHandler()
        
        # اختبار الاتصال
        print("🔍 اختبار الاتصال...")
        if handler.test_connection():
            print("✅ الاتصال يعمل!")
        else:
            print("❌ فشل الاتصال!")
            return False
        
        # اختبار توليد النص
        print("\n📝 اختبار توليد النص...")
        response = await handler.generate_text("مرحباً، كيف حالك؟")
        print(f"📤 السؤال: مرحباً، كيف حالك؟")
        print(f"📥 الإجابة: {response}")
        
        # اختبار المحادثة
        print("\n💬 اختبار المحادثة...")
        chat_response = await handler.chat_response("أخبرني نكتة", "أحمد")
        print(f"📤 السؤال: أخبرني نكتة")
        print(f"📥 الإجابة: {chat_response}")
        
        # اختبار التلخيص
        print("\n📋 اختبار التلخيص...")
        text_to_summarize = """
        الذكاء الاصطناعي هو تقنية حديثة تهدف إلى محاكاة الذكاء البشري في الآلات.
        يتضمن الذكاء الاصطناعي عدة مجالات مثل التعلم الآلي، معالجة اللغة الطبيعية، 
        والرؤية الحاسوبية. يستخدم في تطبيقات مختلفة مثل السيارات ذاتية القيادة،
        المساعدين الصوتيين، والتشخيص الطبي.
        """
        summary = await handler.summarize_text(text_to_summarize)
        print(f"📤 النص الأصلي: {text_to_summarize[:100]}...")
        print(f"📥 التلخيص: {summary}")
        
        print("\n🎉 جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    # تشغيل الاختبار
    success = asyncio.run(test_new_sdk())
    
    if success:
        print("\n✅ SDK الجديد يعمل بشكل ممتاز!")
        print("🚀 يمكنك الآن رفع البوت إلى Railway")
    else:
        print("\n❌ هناك مشكلة في SDK الجديد")
        print("🔧 تحقق من المفتاح وإعدادات البيئة")
