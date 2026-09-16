"""
Telegram-бот для уведомлений сотрудников.
Работает через requests (простой HTTP).
"""

import threading
import time
import requests
from config import Config


class TelegramBot:
    def __init__(self, db, order_service=None):
        self.db = db
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.enabled = bool(self.token)
        self.order_service = order_service
        self.base_url = "https://api.telegram.org/bot" + self.token
        self.offset = 0
        self.running = False

    def api(self, method, **kwargs):
        if not self.enabled:
            return None
        try:
            r = requests.post(self.base_url + "/" + method,
                              json=kwargs, timeout=3)
            data = r.json()
            if data.get("ok"):
                return data.get("result")
            return None
        except Exception as e:
            print("[TG] error:", e)
            return None

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.api("sendMessage", **payload)

    def answer_callback(self, callback_id, text=""):
        return self.api("answerCallbackQuery",
                        callback_query_id=callback_id, text=text)

    # ============== КОМАНДЫ ==============
    def handle_start(self, chat_id, tg_user):
        self.send_message(chat_id,
            "<b>Warehouse Bot</b>\n\n"
            "Привет! Я буду присылать уведомления о заказах.\n\n"
            "Для привязки аккаунта:\n"
            "1. Зайдите в панель на http://localhost:5000\n"
            "2. Профиль - Получить код\n"
            "3. Отправьте мне: /link ВАШКОД")

    def handle_link(self, chat_id, tg_user, code):
        if not code:
            self.send_message(chat_id, "Используйте: /link КОД")
            return
        user = self.db.get_user_by_telegram_code(code)
        if not user:
            self.send_message(chat_id, "Неверный код.")
            return
        self.db.update_user(user["id"],
                            telegram_id=chat_id,
                            telegram_code=None)
        name = user.get("full_name") or user.get("username")
        self.send_message(chat_id,
            "<b>Аккаунт привязан!</b>\n"
            "Вы: " + name + "\n"
            "Роль: " + user["role"])

    def handle_unlink(self, chat_id, tg_user):
        user = self.db.get_user_by_telegram(chat_id)
        if user:
            self.db.update_user(user["id"],
                                telegram_id=None, telegram_code=None)
            self.send_message(chat_id, "Аккаунт отвязан.")
        else:
            self.send_message(chat_id, "У вас нет привязанного аккаунта.")

    def handle_my_orders(self, chat_id, tg_user):
        user = self.db.get_user_by_telegram(chat_id)
        if not user:
            self.send_message(chat_id, "Привяжите аккаунт: /link КОД")
            return
        orders = self.db.get_orders(status="taken")
        my = [o for o in orders if o.get("taken_by") == user["id"]]
        if not my:
            self.send_message(chat_id, "У вас нет активных заказов.")
            return
        for o in my[:5]:
            text = ("<b>Order #" + str(o["id"]) + "</b>\n"
                    "Клиент: " + o["customer_name"] + "\n"
                    "Адрес: " + (o.get("address") or "-") + "\n"
                    "Сумма: " + str(round(o["total_amount"])) + " RUB")
            kb = {"inline_keyboard": [[
                {"text": "Доставлен",
                 "callback_data": "deliver_" + str(o["id"])}
            ]]}
            self.send_message(chat_id, text, reply_markup=kb)

    def handle_message(self, update):
        message = update.get("message") or update.get("edited_message")
        if not message:
            return
        chat_id = message["chat"]["id"]
        tg_user = message.get("from", {})
        text = (message.get("text") or "").strip()

        if text.startswith("/start"):
            self.handle_start(chat_id, tg_user)
        elif text.startswith("/link"):
            parts = text.split(maxsplit=1)
            code = parts[1].strip() if len(parts) > 1 else ""
            self.handle_link(chat_id, tg_user, code)
        elif text.startswith("/unlink"):
            self.handle_unlink(chat_id, tg_user)
        elif text.startswith("/my_orders"):
            self.handle_my_orders(chat_id, tg_user)
        elif text.startswith("/help"):
            self.send_message(chat_id,
                "Команды:\n"
                "/start - приветствие\n"
                "/link КОД - привязать\n"
                "/unlink - отвязать\n"
                "/my_orders - активные заказы")

    def handle_callback(self, callback):
        cb_id = callback.get("id")
        data = callback.get("data", "")
        chat_id = callback["message"]["chat"]["id"]

        user = self.db.get_user_by_telegram(chat_id)
        if not user:
            self.answer_callback(cb_id, "Привяжите аккаунт")
            return

        if data.startswith("take_"):
            oid = int(data.split("_")[1])
            if self.db.take_order(oid, user["id"]):
                self.answer_callback(cb_id, "Вы взяли заказ")
            else:
                self.answer_callback(cb_id, "Заказ уже взят")
        elif data.startswith("deliver_"):
            oid = int(data.split("_")[1])
            if self.db.mark_delivered(oid, user["id"]):
                self.answer_callback(cb_id, "Доставлено")
            else:
                self.answer_callback(cb_id, "Ошибка")
        else:
            self.answer_callback(cb_id, "OK")

    # ============== POLLING ==============
    def poll_loop(self):
        print("[TG] Bot polling started")
        while self.running:
            try:
                data = self.api("getUpdates", offset=self.offset, timeout=2)
                if data:
                    for update in data:
                        self.offset = update["update_id"] + 1
                        if "callback_query" in update:
                            self.handle_callback(update["callback_query"])
                        else:
                            self.handle_message(update)
            except Exception as e:
                print("[TG] poll error:", e)
                time.sleep(3)

    def start(self):
        if not self.enabled:
            print("[TG] Bot disabled (no token)")
            return
        self.running = True
        t = threading.Thread(target=self.poll_loop, daemon=True)
        t.start()
        print("[TG] Bot started")

    def stop(self):
        self.running = False


bot = None