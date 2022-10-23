from test.dummy_chat import DummyChat
from test.dummy_user import DummyUser


class DummyMessage:
    def __init__(self, chat, from_user):
        self.from_user = from_user
        self.chat = chat
