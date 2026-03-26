class EventBus:
    def __init__(self):
        self._listeners = {}

    def listen(self, event_name, callback):
        self._listeners.setdefault(event_name, []).append(callback)

    def post(self, event_name, **data):
        for cb in self._listeners.get(event_name, ()):
            cb(data)
