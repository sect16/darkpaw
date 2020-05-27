import logging
from time import sleep

from ina219 import DeviceRangeError
from ina219 import INA219

logger = logging.getLogger(__name__)
SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 3.1
ADDRESS = 0x41
REFRESH_RATE = 1


class PowerMeter:

    def __init__(self):
        logger.debug('Initializing INA219')
        self.ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=ADDRESS)
        self.ina.configure(self.ina.RANGE_32V)

    def read_ina219(self):
        # self.ina.wake()
        # self.ina.sleep()
        try:
            logger.debug('Bus Voltage: {0:0.2f}V'.format(self.ina.voltage()))
            logger.debug('Bus Current: {0:0.2f}mA'.format(self.ina.current()))
            logger.debug('Power: {0:0.2f}mW'.format(self.ina.power()))
            logger.debug('Shunt Voltage: {0:0.2f}mV\n'.format(self.ina.shunt_voltage()))
            return self.ina.voltage(), self.ina.current(), self.ina.power(), self.ina.shunt_voltage()
        except DeviceRangeError as e:
            # Current out of device range with specified shunt resister
            logger.error(e)

    def run(self):
        self.read_ina219()
        print('Bus Voltage: {0:0.2f}V'.format(self.ina.voltage()))
        print('Bus Current: {0:0.2f}mA'.format(self.ina.current()))
        print('Power: {0:0.2f}mW'.format(self.ina.power()))
        print('Shunt Voltage: {0:0.2f}mV\n'.format(self.ina.shunt_voltage()))
        # self.ina.sleep()
        sleep(REFRESH_RATE)
        # self.ina.wake()


if __name__ == '__main__':
    powerMeter = PowerMeter()
    while True:
        try:
            powerMeter.run()
        except:
            break
