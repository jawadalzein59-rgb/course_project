import pandas as pd
import math
from src.interpolator import LinearInterpolator

class Fluid:
    def __init__(self, M: float, rho_c: float, xa: float, xy: float, T: float):
        self.M = M
        self.rho_c = rho_c
        self.xa = xa
        self.xy = xy
        self.T = T
        self.R = 8.314462618
        self.P_std = 1.01325
        self.T_std = 293.15
        self.P_pc = 46.0
        self.T_pc = 190.0
        df = pd.read_csv('interp_data.csv')
        self.mu_interp = LinearInterpolator(df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist())

    def z(self, P: float) -> float:
        Pr = P / self.P_pc
        Tr = self.T / self.T_pc
        if Tr > 1.0 and Pr < 15:
            Z = 1 - 3.52 * Pr / (10 ** (0.9813 * Tr)) + 0.274 * (Pr ** 2) / (10 ** (0.8157 * Tr))
        else:
            Z = 1 - 3.52 * Pr / (Tr ** 2.2) + 0.274 * (Pr ** 2) / (Tr ** 5.3)
        return max(0.7, min(2.0, Z))

    def ro(self, P: float) -> float:
        Z = self.z(P)
        P_pa = P * 101325.0
        rho = (P_pa * (self.M / 1000.0)) / (Z * self.R * self.T)
        return rho

    def bg(self, P: float) -> float:
        Z = self.z(P)
        return (Z * self.T * self.P_std) / (P * self.T_std)

    def mu(self, P: float) -> float:
        return self.mu_interp.predict(P)
