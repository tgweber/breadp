class Bundle(object):
    def __init__(self):
        self.payload = {}

    def put(self, item_type, item):
        self.payload[item_type] = item

    def get(self, item_type):
        return self.payload.get(item_type, None)

    def has(self, item_type):
        return item_type in self.payload.keys()

