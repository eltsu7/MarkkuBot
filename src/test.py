# -*- coding: utf-8 -*-
from io import StringIO
import unittest

from test.dummy_bot import DummyBot
from test.dummy_update import DummyUpdate
from test.dummy_message import DummyMessage
from test.dummy_chat import DummyChat
from test.dummy_user import DummyUser
from test.dummy_db import DummyDB

from core.get_ids import get_ids
from core.toptenlist import toptenlist

from command_handlers.command_router import CommandRouter

update_generic = DummyUpdate(chat=DummyChat('609'), from_user=DummyUser('1377', 'kurkkumopo'))


class TestCoreFunctions(unittest.TestCase):
    def test_get_ids(self):
        update = DummyUpdate(chat=DummyChat(123123), from_user=DummyUser(456456, 'moippa'))
        self.assertEqual(get_ids(update), (456456, 123123))

    def test_top_ten_list(self):
        db = DummyDB()
        t = toptenlist(db, 1337, 'countteri')
        exp_t = "Top 10 laskurissa countteri:\n" + \
                "1. jäbä1: 9999\n" + \
                "2. jäbä2: 9998\n" + \
                "3. jäbä3: 9997\n" + \
                "4. jäbä4: 9996\n" + \
                "5. jäbä5: 9995\n" + \
                "6. jäbä6: 9994\n" + \
                "7. jäbä7: 9993\n" + \
                "8. jäbä8: 9992\n" + \
                "9. jäbä9: 9991\n" + \
                "10. jäbä19: 9990\n"

        self.assertEqual(t, exp_t)

class TestSensorReading(unittest.TestCase):
    def test_sensor_messages(self):
        cr = CommandRouter(DummyDB())

        sensor_light = CommandRouter.handle_sensor({"value": 255, "inserted": "2021-02-08T14:12:10.935Z", "sensor": "light1"})
        sensor_voice = CommandRouter.handle_sensor({"value": 1, "inserted": "2021-02-08T14:12:10.935Z", "sensor": "voice1"})
        
        self.assertEqual("Someone is in the darkroom 😊", cr.get_light_message(sensor_light))
        self.assertEqual("Somebody is in the virtual darkroom 😊", cr.get_voice_message(sensor_voice))

        sensor_light = CommandRouter.handle_sensor({"value": 0, "inserted": "2021-02-08T14:12:10.935Z", "sensor": "light1"})
        sensor_voice = CommandRouter.handle_sensor({"value": 0, "inserted": "2021-02-08T14:12:10.935Z", "sensor": "voice1"})
        
        self.assertEqual("Darkroom is empty ☹️", cr.get_light_message(sensor_light))
        self.assertEqual("Virtual darkroom is empty ☹️", cr.get_voice_message(sensor_voice))


if __name__ == '__main__':
    print("Yksikkötestit")
    unittest.main()