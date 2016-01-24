import serial
import serial.tools.list_ports
import queue
import threading
import logging
from .exceptions import FlotillaNotFound
from .dial import Dial
from .slider import Slider
from .weather import Weather
from .rainbow import Rainbow
from .matrix import Matrix
import sys

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
name_to_module = {
    'dial': Dial,
    'weather': Weather,
    'rainbow': Rainbow,
    'slider': Slider,
    'matrix': Matrix
}


class Client(object):
    VID = "16d0"
    PID = "08c3"
    channels = {
        '0': None,
        '1': None,
        '2': None,
        '3': None,
        '4': None,
        '5': None,
        '6': None,
        '7': None,
        '8': None,
        '10': None  # for other types of info, like version
    }
    COMMAND_MODULES_LIST = 'e'
    COMMAND_VERSION_INFO = 'v'

    def __init__(self, port=None, baud=9600, debug=False, vid=None, pid=None):
        self.debug = debug
        self.port = port
        self.baud = baud
        self.vid = vid or self.VID
        self.pid = pid or self.PID
        self.num_channels = 8
        self.queue = queue.deque(maxlen=50)

        if self.port is None:
            self.port = self._get_flotilla_port()
        else:
            log.debug('Overriding port: {}'.format(self.port))

        self.serial = serial.Serial(port=self.port.device, baudrate=self.baud, timeout=None)
        log.info('Connection established with Flotilla Dock')
        self._get_modules()

    def start_listener(self):
        t = threading.Thread(target=self._read)
        t.setDaemon(True)
        t.start()
        # Update the modules
        self._get_modules()

    def _get_flotilla_port(self):
        """Try to get the port by using the vid and pid"""
        ports = [p for p in serial.tools.list_ports.grep(
            'VID:PID={}:{}'.format(self.vid, self.pid))]
        if ports:
            log.debug('Found port for Flotilla Dock at: {}'.format(ports[0].device))
            return ports[0]
        else:
            raise FlotillaNotFound('Flotilla Dock not found.')

    def _get_modules(self):
        self._write(self.COMMAND_MODULES_LIST)

    def _decode_data(self, data):
        data = "".join(data)
        log.debug('Got the following data: {}'.format(data))
        if data.startswith('u'):
            # data update
            _, origin, *value = data.split()
            channel, module = origin.split('/')
            try:
                self.channels[channel].set_value(value)
                log.debug('Data received on channel {} from module {}'.format(channel, module))
            except AttributeError:
                log.debug('Received data for channel {} before its set up'.format(channel))

        if data.startswith('d'):
            # disconnected
            _, origin = data.split()
            channel, module = origin.split('/')
            # remove the module from the list
            self.channels[channel] = None
            log.debug('Module {} disconnected on channel {}'.format(module, channel))
        if data.startswith('c'):
            # connected
            _, origin = data.split()
            channel, module = origin.split('/')
            # add the module from the list
            self.channels[channel] = name_to_module[module](name=module, channel=channel, client=self)
            log.debug('Module {} connected on channel {}'.format(module, channel))

    def _write(self, data):
        self.serial.write(bytes(data + "\r", "ascii"))

    def _read(self):
        while True:
            data = []
            while True:
                c = self.serial.read(1).decode()
                if c == '\n':
                    self._decode_data(data)
                    break
                else:
                    data.append(c)

    def list_modules(self):
        return self.channels