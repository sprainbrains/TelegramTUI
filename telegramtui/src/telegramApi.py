# telegramtui/src/telegramApi.py
import threading
import asyncio
import socks
import os
from telethon import TelegramClient, events
from datetime import timedelta
from telegramtui.src.config import get_config


class TelegramApi:
    def __init__(self):
        self._loop = None
        self._thread = None
        self.client = None
        self.me = None
        self.dialogs = []
        self.messages = []
        self.online = []

        self.need_update_message = 0
        self.need_update_online = 0
        self.need_update_current_user = -1
        self.need_update_read_messages = 0

        self.timezone = 0
        self.message_dialog_len = 0

        # Запускаем отдельный поток с asyncio loop'ом
        self._start_background_loop()

    def _start_background_loop(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, args=(self._loop,), daemon=True)
        self._thread.start()

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def _run_async(self, coro):
        """Выполняет корутину в фоновом loop'е и возвращает результат (блокирующий вызов)"""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()  # Блокируется до завершения

    def init_client(self):
        """Синхронная инициализация клиента (вызывается из main thread)"""
        config = get_config()
        api_id = int(config.get('telegram_api', 'api_id'))
        api_hash = config.get('telegram_api', 'api_hash')
        session_name = config.get('telegram_api', 'session_name')

        self.timezone = int(config.get('other', 'timezone'))
        self.message_dialog_len = int(config.get('app', 'message_dialog_len'))

        # Proxy
        proxy = None
        proxy_type_str = config.get('proxy', 'type')
        if proxy_type_str in ("HTTP", "SOCKS4", "SOCKS5"):
            proxy_type = {"HTTP": socks.HTTP, "SOCKS4": socks.SOCKS4, "SOCKS5": socks.SOCKS5}[proxy_type_str]
            addr = config.get('proxy', 'addr')
            port = int(config.get('proxy', 'port')) if config.get('proxy', 'port').isdigit() else None
            username = config.get('proxy', 'username') or None
            password = config.get('proxy', 'password') or None
            if addr and port:
                proxy = (proxy_type, addr, port, True, username, password)

        session_path = os.path.expanduser("~") + '/.config/telegramtui/' + session_name

        # Создаём и запускаем клиента в фоновом loop'е
        async def _init():
            self.client = TelegramClient(session_path, api_id, api_hash, proxy=proxy)
            await self.client.start()
            self.me = await self.client.get_me()
            self.dialogs = await self.client.get_dialogs(limit=self.message_dialog_len)
            self.messages = [None] * len(self.dialogs)
            self.online = [""] * len(self.dialogs)

            if self.dialogs:
                self.messages[0] = await self.client.get_messages(self.dialogs[0].entity, limit=self.message_dialog_len)

            # === Обработчики событий ===
            @self.client.on(events.NewMessage)
            async def on_new_message(event):
                chat_id = event.chat_id
                for i, dialog in enumerate(self.dialogs):
                    if dialog.id == chat_id:
                        # Добавляем сообщение в кэш
                        # if self.messages[i] is not None:
                        #     self.messages[i].insert(0, event.message)
                        #     self.messages[i].sort(key=lambda x: x.id, reverse=True)
                        #     self._remove_duplicates(self.messages[i])

                        self.dialogs[i].unread_count += 1
                        self.need_update_message = 1
                        self.need_update_current_user = i
                        break

            @self.client.on(events.UserUpdate())
            async def on_user_update(event):
                if not hasattr(event, '_chat_peer') or not hasattr(event._chat_peer, 'user_id'):
                    return
                sender_id = event._chat_peer.user_id
                for i, dialog in enumerate(self.dialogs):
                    if hasattr(dialog.dialog.peer, 'user_id') and dialog.dialog.peer.user_id == sender_id:
                        if event.online:
                            self.online[i] = "Online"
                        elif event.last_seen is not None:
                            tz_offset = timedelta(hours=self.timezone)
                            localized_time = event.last_seen + tz_offset
                            self.online[i] = f"Last seen at {localized_time}"
                        else:
                            self.online[i] = ""
                        self.need_update_current_user = i
                        self.need_update_online = 1
                        break

            # Raw-обработчик для прочтения можно оставить, но он сложен — пока опустим

        try:
            self._run_async(_init())
        except Exception as ex:
            print("Something wrong: " + str(ex))
            exit(1)

    # === Синхронные методы-обёртки ===

    def get_messages(self, user_id):
        async def _get():
            # ВСЕГДА обновляем кэш
            data = await self.client.get_messages(
                self.dialogs[user_id].entity,
                limit=self.message_dialog_len
            )
            self.messages[user_id] = list(data)
            self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
            return self.messages[user_id]
        return self._run_async(_get())
    
    def get_message_by_id(self, user_id, message_id):
        if self.messages[user_id] is None:
            return None
        for msg in self.messages[user_id]:
            if msg.id == message_id:
                return msg
        return None

    def message_send(self, message, user_id, reply=None):
        async def _send():
            sent = await self.client.send_message(self.dialogs[user_id].entity, message, reply_to=reply)
            await self.client.send_read_acknowledge(self.dialogs[user_id].entity, max_id=sent.id)
            # Обновим кэш
            new_msgs = await self.client.get_messages(self.dialogs[user_id].entity, min_id=sent.id - 1)
            for msg in reversed(new_msgs):
                if not any(m.id == msg.id for m in self.messages[user_id]):
                    self.messages[user_id].insert(0, msg)
            self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
            self._remove_duplicates(self.messages[user_id])
        self._run_async(_send())

    def delete_message(self, user_id, message_id):
        self._run_async(self.client.delete_messages(self.dialogs[user_id].entity, message_id))

    def download_media(self, media, path):
        return self._run_async(self.client.download_media(media, path))

    def file_send(self, file, user_id, progress_callback=None):
        async def _send():
            sent = await self.client.send_file(self.dialogs[user_id].entity, file, progress_callback=progress_callback)
            new_msgs = await self.client.get_messages(self.dialogs[user_id].entity, min_id=sent.id - 1)
            for msg in reversed(new_msgs):
                if not any(m.id == msg.id for m in self.messages[user_id]):
                    self.messages[user_id].insert(0, msg)
            self.messages[user_id].sort(key=lambda x: x.id, reverse=True)
            self._remove_duplicates(self.messages[user_id])
        self._run_async(_send())

    def read_all_messages(self, user_id):
        if self.messages[user_id] and len(self.messages[user_id]) > 0:
            max_id = self.messages[user_id][0].id
            self._run_async(self.client.send_read_acknowledge(self.dialogs[user_id].entity, max_id=max_id))

    def _remove_duplicates(self, messages):
        seen = set()
        i = 0
        while i < len(messages):
            msg_id = messages[i].id
            if msg_id in seen:
                del messages[i]
            else:
                seen.add(msg_id)
                i += 1

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)