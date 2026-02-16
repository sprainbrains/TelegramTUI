from telegramtui.src.ui import App
from telegramtui.src.telegramApi import TelegramApi

client = None

def main():
    global client
    client = TelegramApi()
    client.init_client()

    app = App(client=client)
    app.run()

if __name__ == "__main__":
    main()