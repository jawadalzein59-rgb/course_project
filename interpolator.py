class LinearInterpolator:
    def __init__(self, xs: list, ys: list):
        self.xs = xs
        self.ys = ys

    def predict(self, xp: float) -> float:
        if xp < self.xs[0]:
            return self.ys[0]
        if xp > self.xs[-1]:
            return self.ys[-1]
        for i in range(len(self.xs) - 1):
            if self.xs[i] <= xp <= self.xs[i+1]:
                x0, x1 = self.xs[i], self.xs[i+1]
                y0, y1 = self.ys[i], self.ys[i+1]
                return y0 + (xp - x0) * (y1 - y0) / (x1 - x0)
        return self.ys[-1]
