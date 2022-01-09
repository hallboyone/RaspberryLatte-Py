class MovingAverage:
    def __init__(self, num_samples: int, initial_val: float = 0.0):
        self._samples = []
        self._samples = [initial_val for i in range(num_samples)]

    def addPoint(self, point: float) -> float:
        self._samples.insert(0, point)
        self._samples.pop()
        return self.val()

    def val(self) -> float:
        return sum(self._samples) / len(self._samples)

    def reset(self):
        self._samples = [0 for i in range(len(self._samples))]