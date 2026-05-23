class LinearInterpolator:
    def __init__(self, xs: list, ys: list):
        self.xs = xs
        self.ys = ys
        if len(self.xs) != len(self.ys):
            raise ValueError("xs and ys must have the same length")
        for i in range(len(self.xs) - 1):
            if self.xs[i] > self.xs[i+1]:
                raise ValueError("xs must be sorted in ascending order")

    def predict(self, xp: float) -> float:
        if xp < self.xs[0] or xp > self.xs[-1]:
            raise ValueError(f"Value {xp} is out of bounds [{self.xs[0]}, {self.xs[-1]}]")
        for i in range(len(self.xs) - 1):
            if self.xs[i] <= xp <= self.xs[i+1]:
                x0, x1 = self.xs[i], self.xs[i+1]
                y0, y1 = self.ys[i], self.ys[i+1]
                return y0 + (xp - x0) * (y1 - y0) / (x1 - x0)
        raise ValueError("Could not find interpolation segment")
