from dataclasses import dataclass
from src.fluid import Fluid

@dataclass
class ResProps:
    P: float  # [атм]
    V: float  # [м³]
    T: float  # [К]

class Reservoir:
    def __init__(self, resprops: ResProps, fluid: Fluid):
        self.resprops = resprops
        self.fluid = fluid

    def p2(self, q_total: float, dt: float = 1.0) -> float:
        # Материальный баланс: давление падает пропорционально отобранному объёму
        bg = self.fluid.bg(self.resprops.P)
        delta_V = q_total * dt * bg  # м³ добытого газа при пластовых условиях
        # Линейная аппроксимация истощения
        P_new = self.resprops.P * (1.0 - delta_V / self.resprops.V)
        return max(P_new, 1.0)
