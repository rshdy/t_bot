"""
معالجات البوت - محسن لـ Railway
"""

import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config

logger = logging.getLogger(__name__)

class UserManager:
    """إدارة المستخدمين"""
    
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users_data = self.load_users()
    
    def load_users(self) -> Dict:
        """تحميل بيانات المستخدمين"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"خطأ في تحميل المستخدمين: {e}")
            return {}
    
    def save_users(self) -> bool:
        """حفظ بيانات المستخدمين"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ المستخدمين: {e}")
            return False
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """إضافة مستخدم جديد"""
        try:
            user_id_str = str(user_id)
            if user_id_str not in self.users_data:
                self.users_data[user_id_str] = {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'join_date': datetime.now().isoformat(),
                    'last_interaction': datetime.now().isoformat(),
                    'message_count': 1,
                    'is_active': True
                }
                logger.info(f"مستخدم جديد: {user_id} - {first_name}")
            else:
                # تحديث آخر تفاعل
                self.users_data[user_id_str]['last_interaction'] = datetime.now().isoformat()
                self.users_data[user_id_str]['message_count'] += 1
                if username:
                    self.users_data[user_id_str]['username'] = username
                if first_name:
                    self.users_data[user_id_str]['first_name'] = first_name
            
            return self.save_users()
        except Exception as e:
            logger.error(f"خطأ في إضافة المستخدم: {e}")
            return False
    
    def get_user_count(self) -> int:
        """الحصول على عدد المستخدمين"""
        return len(self.users_data)
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        return list(self.users_data.values())
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات المستخدمين"""
        all_users = self.get_all_users()
        total_messages = sum(user.get('message_count', 0) for user in all_users)
        
        return {
            'total_users': len(all_users),
            'total_messages': total_messages,
            'avg_messages_per_user': round(total_messages / len(all_users), 2) if all_users else 0
        }

class BotHandlers:
    """معالجات البوت"""
    
    def __init__(self, gemini_handler, voice_handler):
        self.config = Config()
        self.gemini_handler = gemini_handler
        self.voice_handler = voice_handler
        self.user_manager = UserManager()
        self.user_states = {}  # لتتبع حالة المستخدمين
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر البدء"""
        try:
            user = update.effective_user
            
            # إضافة المستخدم
            self.user_manager.add_user(user.id, user.username, user.first_name)
            
            # رسالة الترحيب
            welcome_message = f"""
🎉 مرحباً {user.first_name}!

🤖 أنا بوت الذكاء الاصطناعي المتقدم، يمكنني مساعدتك في:

🧠 الإجابة على أسئلتك
📸 تحليل الصور
🎵 تحويل النص إلى صوت
📝 تلخيص النصوص
🌍 ترجمة النصوص

استخدم الأزرار أدناه أو اكتب رسالتك مباشرة!
            """
            
            # الأزرار
            keyboard = [
                [
                    InlineKeyboardButton("🎵 تحويل لصوت", callback_data="voice_convert"),
                    InlineKeyboardButton("📝 تلخيص", callback_data="summarize")
                ],
                [
                    InlineKeyboardButton("🌍 ترجمة", callback_data="translate"),
                    InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")
                ],
                [
                    InlineKeyboardButton("❓ المساعدة", callback_data="help")
                ]
            ]
            
            # إضافة أزرار المدير
            if self.config.is_admin(user.id):
                keyboard.append([
                    InlineKeyboardButton("👑 لوحة المدير", callback_data="admin_panel")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج البدء: {e}")
            await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر المساعدة"""
        try:
            help_message = """
❓ كيفية استخدام البوت:

🗣️ **للمحادثة العادية:**
• اكتب أي سؤال أو رسالة وسأجيب عليها

📸 **لتحليل الصور:**
• أرسل صورة مع أو بدون وصف
• سأقوم بتحليل الصورة وإخبارك بما فيها

🎵 **لتحويل النص إلى صوت:**
• اكتب النص ثم اضغط زر "تحويل لصوت"
• أو اكتب النص واضغط على زر التحويل

📝 **لتلخيص النص:**
• اكتب أو أرسل النص الطويل
• اضغط زر "تلخيص" وسأقوم بتلخيصه

🌍 **للترجمة:**
• اكتب النص المراد ترجمته
• اضغط زر "ترجمة" واختر اللغة المطلوبة

📊 **للإحصائيات:**
• اضغط زر "الإحصائيات" لرؤية بيانات الاستخدام

💡 **نصائح:**
• يمكنك استخدام الأزرار أو الكتابة المباشرة
• البوت يدعم العربية والإنجليزية
• يمكنك إرسال عدة أسئلة متتالية

🚀 **ابدأ الآن بكتابة رسالتك!**
            """
            
            keyboard = [
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(help_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج المساعدة: {e}")
            await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def stats_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر الإحصائيات"""
        try:
            stats = self.user_manager.get_stats()
            
            stats_message = f"""
📊 إحصائيات البوت:

👥 إجمالي المستخدمين: {stats['total_users']}
💬 إجمالي الرسائل: {stats['total_messages']}
📈 متوسط الرسائل لكل مستخدم: {stats['avg_messages_per_user']}

⏰ آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 تحديث", callback_data="stats")],
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الإحصائيات: {e}")
            await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        try:
            user = update.effective_user
            message_text = update.message.text
            
            # إضافة المستخدم
            self.user_manager.add_user(user.id, user.username, user.first_name)
            
            # فحص حالة المستخدم
            user_state = self.user_states.get(user.id, {})
            
            if user_state.get('waiting_for_broadcast') and self.config.is_admin(user.id):
                # إرسال رسالة جماعية
                await self.broadcast_message(update, context, message_text)
                return
            
            # إرسال رسالة "يكتب..."
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # الحصول على رد من Gemini
            response = await self.gemini_handler.chat_response(message_text, user.first_name)
            
            # إرسال الرد
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الرسائل: {e}")
            await update.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الصور"""
        try:
            user = update.effective_user
            
            # إضافة المستخدم
            self.user_manager.add_user(user.id, user.username, user.first_name)
            
            # إرسال رسالة "يكتب..."
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # الحصول على الصورة
            photo_file = await update.message.photo[-1].get_file()
            photo_data = await photo_file.download_as_bytearray()
            
            # الحصول على النص المرفق (إن وجد)
            caption = update.message.caption or "صف هذه الصورة بالتفصيل"
            
            # تحليل الصورة
            response = await self.gemini_handler.analyze_image(bytes(photo_data), caption)
            
            # إرسال الرد
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الصور: {e}")
            await update.message.reply_text("❌ حدث خطأ في تحليل الصورة. يرجى المحاولة مرة أخرى.")
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        try:
            query = update.callback_query
            await query.answer()
            
            user = query.from_user
            data = query.data
            
            # إضافة المستخدم
            self.user_manager.add_user(user.id, user.username, user.first_name)
            
            if data == "start":
                await self.start_handler(update, context)
            elif data == "help":
                await self.help_handler(update, context)
            elif data == "stats":
                await self.stats_handler(update, context)
            elif data == "voice_convert":
                await self.voice_convert_handler(update, context)
            elif data == "summarize":
                await self.summarize_handler(update, context)
            elif data == "translate":
                await self.translate_handler(update, context)
            elif data == "admin_panel":
                await self.admin_panel_handler(update, context)
            elif data == "broadcast":
                await self.broadcast_handler(update, context)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الأزرار: {e}")
            await query.message.reply_text("❌ حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def voice_convert_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج تحويل النص إلى صوت"""
        try:
            message = """
🎵 تحويل النص إلى صوت:

أرسل النص الذي تريد تحويله إلى صوت وسأقوم بتحويله لك.

💡 يمكنني تحويل النصوص بالعربية والإنجليزية وعدة لغات أخرى.
            """
            
            keyboard = [
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديث حالة المستخدم
            self.user_states[update.effective_user.id] = {'waiting_for_voice_text': True}
            
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج تحويل الصوت: {e}")
    
    async def summarize_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج التلخيص"""
        try:
            message = """
📝 تلخيص النص:

أرسل النص الطويل الذي تريد تلخيصه وسأقوم بتلخيصه لك.

💡 يمكنني تلخيص المقالات والنصوص الطويلة بأي لغة.
            """
            
            keyboard = [
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديث حالة المستخدم
            self.user_states[update.effective_user.id] = {'waiting_for_summary_text': True}
            
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج التلخيص: {e}")
    
    async def translate_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الترجمة"""
        try:
            message = """
🌍 ترجمة النص:

أرسل النص الذي تريد ترجمته وسأقوم بترجمته لك.

💡 يمكنني الترجمة من وإلى عدة لغات.
            """
            
            keyboard = [
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديث حالة المستخدم
            self.user_states[update.effective_user.id] = {'waiting_for_translation_text': True}
            
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الترجمة: {e}")
    
    async def admin_panel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج لوحة المدير"""
        try:
            if not self.config.is_admin(update.effective_user.id):
                await update.callback_query.message.reply_text("❌ ليس لديك صلاحية للوصول لهذه الميزة.")
                return
            
            stats = self.user_manager.get_stats()
            
            admin_message = f"""
👑 لوحة تحكم المدير:

📊 الإحصائيات:
• المستخدمين: {stats['total_users']}
• الرسائل: {stats['total_messages']}
• المتوسط: {stats['avg_messages_per_user']} رسالة/مستخدم

🛠️ الأدوات المتاحة:
            """
            
            keyboard = [
                [InlineKeyboardButton("📤 رسالة جماعية", callback_data="broadcast")],
                [InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data="admin_panel")],
                [InlineKeyboardButton("🏠 العودة للرئيسية", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.message.reply_text(admin_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في لوحة المدير: {e}")
    
    async def broadcast_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل الجماعية"""
        try:
            if not self.config.is_admin(update.effective_user.id):
                await update.callback_query.message.reply_text("❌ ليس لديك صلاحية للوصول لهذه الميزة.")
                return
            
            message = """
📤 إرسال رسالة جماعية:

اكتب الرسالة التي تريد إرسالها لجميع المستخدمين.

⚠️ تأكد من الرسالة قبل الإرسال.
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # تحديث حالة المستخدم
            self.user_states[update.effective_user.id] = {'waiting_for_broadcast': True}
            
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"خطأ في معالج الرسائل الجماعية: {e}")
    
    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """إرسال رسالة جماعية"""
        try:
            # إزالة حالة الانتظار
            self.user_states[update.effective_user.id] = {}
            
            # الحصول على جميع المستخدمين
            all_users = self.user_manager.get_all_users()
            
            sent_count = 0
            failed_count = 0
            
            # إرسال رسالة البدء
            await update.message.reply_text(f"🚀 بدء إرسال الرسالة لـ {len(all_users)} مستخدم...")
            
            for user in all_users:
                try:
                    await context.bot.send_message(
                        chat_id=user['user_id'],
                        text=f"📢 رسالة من الإدارة:\n\n{message_text}"
                    )
                    sent_count += 1
                    
                    # تأخير بسيط لتجنب الحد الأقصى
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"فشل إرسال الرسالة للمستخدم {user['user_id']}: {e}")
            
            # إرسال تقرير النتائج
            result_message = f"""
✅ تم إرسال الرسالة الجماعية:

📤 تم الإرسال بنجاح: {sent_count}
❌ فشل في الإرسال: {failed_count}
📊 المجموع: {len(all_users)}
            """
            
            await update.message.reply_text(result_message)
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الرسالة الجماعية: {e}")
            await update.message.reply_text("❌ حدث خطأ في إرسال الرسالة الجماعية.")
    
    async def admin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر المدير"""
        if self.config.is_admin(update.effective_user.id):
            await self.admin_panel_handler(update, context)
        else:
            await update.message.reply_text("❌ ليس لديك صلاحية للوصول لهذه الميزة.")
