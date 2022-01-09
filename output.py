class SSRPWM:
    def __init__(self, gpio: int, freq = None):
        self._gpio = gpio
        self._freq = freq

    def write(self, duty_cycle: float):
        pass