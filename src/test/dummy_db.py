class DummyDB:
    def get_counter_top(self, chat_id, var, amount):
        topn = {
            "jäbä1": 9999,
            "jäbä2": 9998,
            "jäbä3": 9997,
            "jäbä4": 9996,
            "jäbä5": 9995,
            "jäbä6": 9994,
            "jäbä7": 9993,
            "jäbä8": 9992,
            "jäbä9": 9991,
            "jäbä19": 9990,
            "jäbä11": 9989,
            "jäbä12": 9988,
            "jäbä13": 9987,
            "jäbä14": 9986,
            "jäbä15": 9985,
        }

        return dict(list(topn.items())[:amount])
