from dataclasses import dataclass

@dataclass
class Well:
    fluid: object
    k: float
    h: float
    re: float
    rw: float
    tubing: object

    def q(self, P_res: float, P_bhp: float) -> float:
        mu = self.fluid.mu(P_res)
        z = self.fluid.z(P_res)
        T = self.fluid.T
        C = (self.k * self.h) / (1422 * mu * z * T)
        q = C * (P_res**2 - P_bhp**2)
        return max(0, q)
