import struct


# import spidev

class SpiDev:
    def __init__(self):
        self.max_speed_hz = 0
        self.mode = 0b00

    def open(self, para1: int, para2: int):
        pass

    def readbytes(self, para1: int):
        return [0, 1, 2, 3]

    def close(self):
        pass


class MAX31855:
    def __init__(self, bus, device):
        self._sensor = SpiDev()
        self._sensor.max_speed_hz = 100_000
        self._sensor.mode = 0b00
        self._sensor.open(bus, device)

    def read(self, internal=False) -> float:
        buf = self._sensor.readbytes(4)
        if 1 & buf[3]:
            raise RuntimeError("thermocouple not connected")
        elif 2 & buf[3]:
            raise RuntimeError("short circuit to ground")
        elif 4 & buf[3]:
            raise RuntimeError("short circuit to power")
        elif 1 & buf[1]:
            raise RuntimeError("faulty reading")
        thermo_temp, internal_temp = struct.unpack(">hh", buf)
        if internal:
            internal_temp >>= 4
            return internal_temp / 16.0
        thermo_temp >>= 2
        return thermo_temp / 4.0

    def __del__(self):
        self._sensor.close()
