import math
from src.fluid import Fluid
from src.pipe import Pipe

class Well:
    def __init__(self, fluid: Fluid, k: float, h: float, re: float, rw: float, pipe: Pipe = None):
        self.fluid = fluid
        self.k = k      # проницаемость [мД]
        self.h = h      # мощность пласта [м]
        self.re = re    # радиус контура [м]
        self.rw = rw    # радиус скважины [м]
        self.pipe = pipe # объект НКТ
        # Геометрическая часть коэффициента продуктивности
        self.geo = (7.03e-6 * k * h) / math.log(re / rw)

    def q(self, P_res: float, P_bhp: float) -> float:
        # Газовая кривая притока (IPR): q = C * (P_res^2 - P_bhp^2)
        P_avg = max((P_res + P_bhp) / 2.0, 1.0)
        mu = self.fluid.mu(P_avg)  # [сП]
        Z = self.fluid.z(P_avg)
        T = self.fluid.T           # [К]
        C = self.geo / (mu * Z * T)
        return C * (P_res**2 - P_bhp**2)
