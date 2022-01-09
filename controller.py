from dataclasses import dataclass
import threading
import time

from filters import MovingAverage

@dataclass
class PIDGains:
    p: float
    i: float = 0
    d: float = 0


class DiscreteIntegral:
    def __init__(self, sample_time: float = 1.0, min_area: float = None,
                 max_area: float = None):
        self._sample_time = sample_time
        self._min_area = min_area
        self._max_area = max_area

        self._area = 0.0
        self._prev_val = 0.0

    def add(self, val: float) -> float:
        self._area += self._sample_time * (self._prev_val + val) / 2.0
        if self._area < self._min_area:
            self._area = self._min_area
        elif self._area > self._max_area:
            self._area = self._max_area
        self._prev_val = val
        return self._area

    def reset(self):
        self._area = 0
        self._prev_val = 0

    @property
    def area(self) -> float:
        return self._area

    @property
    def min_val(self) -> float:
        return self._min_area

    @min_val.setter
    def min_val(self, new_val: float):
        if new_val > self._max_area:
            raise ValueError("min_val must be less than max_val")
        self._min_area = new_val

    @property
    def max_val(self) -> float:
        return self._max_area

    @max_val.setter
    def max_val(self, new_val: float):
        if new_val < self._min_area:
            raise ValueError("min_val must be less than max_val")
        self._max_area = new_val
# end DiscreteIntegral


class DiscreteDerivative:
    def __init__(self, sample_time: float = 1.0, filter_range: int = 1):
        self._sample_time = sample_time
        self._slope = MovingAverage(filter_range)
        self._prev_val = 0.0

    def add(self, val: float) -> float:
        self._slope.addPoint((self._prev_val - val) / self._sample_time)
        self._prev_val = val
        return self._slope.val()

    def slope(self) -> float:
        return self._slope.val()

    def reset(self):
        self._slope.reset()
        self._prev_val = 0
# end DiscreteDerivative


class PIDController:
    def __init__(self, sensor, gains: PIDGains, freq: float = 100.0, output=None):
        self._sensor = sensor
        self._K = gains
        self._freq = freq
        self._output = output

        self._active = False
        self._setpoint = 0.0
        self._err_slope = DiscreteDerivative()
        self._err_area = DiscreteIntegral()

        self._lock = threading.Lock()
        self._cl_thread = None

    def controlLoop(self):
        while self._active:
            with self._lock:
                loop_end = round(1.0E9 / self._freq + time.time_ns())
                val = self._sensor.read()
                err = self._setpoint - val
                u = (self._K.p * err
                     + self._K.i * self._err_area.add(err)
                     + self._K.d * self._err_slope.add(val))
                if self._output:
                    self._output.write(u)
            time.sleep(loop_end - time.time_ns())

    def start(self):
        if not self._active:
            self._active = True
            self._cl_thread = threading.Thread(target=self.controlLoop, args=(self,))

    def stop(self):
        with self._lock:
            self._active = False
        self._cl_thread.join()
