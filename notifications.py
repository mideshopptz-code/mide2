"""
Уведомления: WebSocket + Telegram + БД
"""


class NotificationCenter:
    def __init__(self, db, socketio=None, telegram=None):
        self.db = db
        self.socketio = socketio
        self.telegram = telegram

    def notify_user(self, user_id, title, body="", send_telegram=True):
        # 1. Сохраняем в БД
        nid = self.db.add_notification(user_id, title, body)

        # 2. WebSocket — мгновенно в браузере
        if self.socketio:
            try:
                self.socketio.emit("staff_notification", {
                    "title": title,
                    "body": body,
                }, room="user_" + str(user_id))
            except Exception:
                pass

        # 3. Telegram
        if send_telegram and self.telegram and self.telegram.enabled:
            user = self.db.get_user_by_id(user_id)
            if user and user.get("telegram_id"):
                try:
                    self.telegram.send_message(
                        user["telegram_id"],
                        "<b>" + title + "</b>\n" + (body or ""))
                except Exception:
                    pass

        return nid

    def notify_admins(self, title, body=""):
        admins = self.db.list_users(role="admin")
        for a in admins:
            self.notify_user(a["id"], title, body)

    def notify_order_created(self, order):
        title = "New order #" + str(order["id"])
        body = (order["customer_name"] + " / " +
                str(round(order["total_amount"])) + " RUB")
        admins = self.db.list_users(role="admin")
        for a in admins:
            self.notify_user(a["id"], title, body)