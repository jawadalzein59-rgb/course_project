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
        self.R = 8.314462618  # J/(mol·K)
        self.P_std = 1.01325   # atm
        self.T_std = 293.15    # K

        # Load viscosity data
        df = pd.read_csv('interp_data.csv')
        self.mu_interp = LinearInterpolator(df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist())

    def z(self, P: float) -> float:
        # GERG-91 модифицированный (универсальная аппроксимация для природного газа)
        # Если у тебя есть точная формула из hw2.ipynb, замени тело этой функции
        Pc = 46.0  # атм
        Tc = 190.0 # K
        Pr = P / Pc
        Tr = self.T / Tc
        Z = 1.0 - 3.52 * Pr / (Tr**2.2) + 0.274 * (Pr**2) / (Tr**5.3)
        return max(Z, 0.1)

    def ro(self, P: float) -> float:
        Z = self.z(P)
        P_pa = P * 101325.0
        # rho = P*M / (Z*R*T), M в г/моль -> делим на 1000
        rho = (P_pa * (self.M / 1000.0)) / (Z * self.R * self.T)
        return rho

    def bg(self, P: float) -> float:
        Z = self.z(P)
        # B_g = Z*T*P_std / (P*T_std) при Z_std ~ 1
        return (Z * self.T * self.P_std) / (P * self.T_std)

    def mu(self, P: float) -> float:
        return self.mu_interp.predict(P)
