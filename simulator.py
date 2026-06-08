import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from tqdm import tqdm
from src.state import NodeState

class FieldSimulator:
    def __init__(self, reservoir, wells, shlyf, dcs):
        self.reservoir = reservoir
        self.wells = wells
        self.shlyf = shlyf
        self.dcs = dcs

    def solve(self, P_res: float) -> dict:
        P_dcs_in = self.dcs.P_in()
        x0 = [500.0, 500.0, 500.0, P_dcs_in + 2.0]

        def residuals(x):
            q1, q2, q3, P_man = x
            P_bhp1 = P_man + self.wells[0].tubing.dp(P_man, q1).dP
            res1 = self.wells[0].q(P_res, P_bhp1) - q1
            P_bhp2 = P_man + self.wells[1].tubing.dp(P_man, q2).dP
            res2 = self.wells[1].q(P_res, P_bhp2) - q2
            P_bhp3 = P_man + self.wells[2].tubing.dp(P_man, q3).dP
            res3 = self.wells[2].q(P_res, P_bhp3) - q3
            q_total = q1 + q2 + q3 + self.dcs.q_ext
            P_shlyf_out = self.shlyf.dp(P_man, q_total).P_out
            res4 = P_shlyf_out - P_dcs_in
            if q1 < 0: res1 = -q1
            if q2 < 0: res2 = -q2
            if q3 < 0: res3 = -q3
            return [res1, res2, res3, res4]

        solution = fsolve(residuals, x0)
        q1, q2, q3, P_man = solution
        q1, q2, q3 = max(0, q1), max(0, q2), max(0, q3)

        return {
            'well_1': NodeState('well_1', P_res, P_man, P_res - P_man, q1),
            'well_2': NodeState('well_2', P_res, P_man, P_res - P_man, q2),
            'well_3': NodeState('well_3', P_res, P_man, P_res - P_man, q3),
            'manifold': NodeState('manifold', P_man, P_dcs_in, P_man - P_dcs_in, q1 + q2 + q3)
        }

    def run(self, N_days: int, dt: float = 1.0) -> pd.DataFrame:
        rows = []
        cumulative_Gp = 0.0
        for t in tqdm(range(N_days), desc="Simulating"):
            P_res = self.reservoir.resprops.P
            st = self.solve(P_res)
            q1 = st['well_1'].q_std
            q2 = st['well_2'].q_std
            q3 = st['well_3'].q_std
            q_total = q1 + q2 + q3

            # Convert to reservoir conditions and update pressure
            bg = self.wells[0].fluid.bg(P_res)
            q_res = q_total * bg
            cumulative_Gp += q_total * dt
            self.reservoir.p2(q_res, dt)

            rows.append({
                't': t,
                'P_res': self.reservoir.resprops.P,
                'P_man': st['manifold'].P_in,
                'q1': q1,
                'q2': q2,
                'q3': q3,
                'q_total': q_total,
                'Gp': cumulative_Gp / 1000  # Convert to thousand std m³
            })

        return pd.DataFrame(rows)
