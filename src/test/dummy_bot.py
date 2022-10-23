import sys


class DummyBot:
    def __init__(self, out=sys.stdout):
        self.out = out

    def send_message(self, chat_id, text):
        self.out.write(text)
