import math
from dataclasses import dataclass
from src.fluid import Fluid
from src.state import NodeState

class Pipe:
    def __init__(self, L: float, D: float, roughness: float, fluid: Fluid, vertical_depth: float = 0.0):
        self.L = L
        self.D = D
        self.roughness = roughness
        self.fluid = fluid
        self.H = vertical_depth

    def _friction_factor(self, Re: float) -> float:
        if Re < 2300:
            return 64.0 / Re
        # Colebrook-White (iterative)
        lam = 0.02
        for _ in range(50):
            term = self.roughness / (3.7 * self.D) + 2.51 / (Re * math.sqrt(lam))
            lam_new = 1.0 / (-2.0 * math.log10(term))**2
            if abs(lam_new - lam) < 1e-6:
                return lam_new
            lam = lam_new
        return lam

    def dp(self, P: float, q: float) -> NodeState:
        q_m3s = q / (24 * 3600)
        bg = self.fluid.bg(P)
        q_res = q * bg
        q_res_m3s = q_res / (24 * 3600)

        A = math.pi * (self.D**2) / 4
        v = q_res_m3s / A if A > 0 else 0.0
        rho = self.fluid.ro(P)
        mu_pa_s = self.fluid.mu(P) * 0.001
        Re = (rho * v * self.D) / mu_pa_s if mu_pa_s > 0 else 0.0

        lam = self._friction_factor(Re)

        # Дарси-Вейсбах + гидростатика (в Па)
        g = 9.81
        dp_friction = lam * (self.L / self.D) * (rho * v**2) / 2.0
        dp_gravity = rho * g * self.H
        dp_atm = (dp_friction + dp_gravity) / 101325.0

        return NodeState(
            name="pipe",
            P_in=P,
            P_out=max(P - dp_atm, 0.01),
            dP=dp_atm,
            q_std=q,
            q_res=q_res,
            v=v,
            rho=rho
        )
