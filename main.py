import time

from controller import PIDGains, PIDController
from sensor import MAX31855
from output import SSRPWM

K = PIDGains(p = 1, i = 0.1, d = 0.2)
thermocouple = MAX31855(1, 0)
heater_ssr = SSRPWM(gpio = 0, freq = 0.5)

ctrl = PIDController(sensor=thermocouple, gains=K, freq=1, output=heater_ssr)
ctrl.start()
time.sleep(60)
ctrl.stop()