from queue import deque


class Module(object):
    name = None
    channel = None

    def __init__(self, name, channel, client):
        self.name = name
        self.channel = channel
        self.client = client
        self.queue = deque()

    def __repr__(self):
        return '{} module'.format(self.name.capitalize())

    def send(self, data):
        # format is "s $CHANNEL $DATA"
        data = "s {} {}".format(self.channel, data)
        self.client._write(data)

    def set_value(self, value):
        self.queue.append(value)

    def read_value(self):
        return self.queue.pop()