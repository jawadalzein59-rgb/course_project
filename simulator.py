import numpy as np
from scipy.optimize import fsolve
import pandas as pd
from tqdm import tqdm
from src.state import NodeState

class FieldSimulator:
    def __init__(self, reservoir, wells: list, shlyf, dcs):
        self.reservoir = reservoir
        self.wells = wells
        self.shlyf = shlyf
        self.dcs = dcs

    def solve(self, P_res: float) -> dict:
        P_dcs_in = self.dcs.P_in()
        # Начальное приближение: q~500, P_man ~ P_dcs_in + 2 атм
        x0 = [500.0, 500.0, 500.0, P_dcs_in + 2.0]

        def equations(vars):
            q1, q2, q3, P_man = vars
            q_total = max(q1 + q2 + q3 + self.dcs.q_ext, 0.0)

            # Забойные давления: P_bhp = P_man + перепад в НКТ
            p_bhp1 = P_man + self.wells[0].pipe.dp(P_man, max(q1,0)).dP
            p_bhp2 = P_man + self.wells[1].pipe.dp(P_man, max(q2,0)).dP
            p_bhp3 = P_man + self.wells[2].pipe.dp(P_man, max(q3,0)).dP

            # Невязки притока
            f1 = self.wells[0].q(P_res, p_bhp1) - q1
            f2 = self.wells[1].q(P_res, p_bhp2) - q2
            f3 = self.wells[2].q(P_res, p_bhp3) - q3

            # Невязка манифольда: P_man = P_dcs_in + dp_shlyf
            dp_sh = self.shlyf.dp(P_man, q_total).dP
            f4 = P_man - P_dcs_in - dp_sh
            return [f1, f2, f3, f4]

        sol = fsolve(equations, x0)
        q1, q2, q3, P_man = sol
        # Закрываем скважины с отрицательным дебитом
        q1, q2, q3 = max(q1, 0.0), max(q2, 0.0), max(q3, 0.0)

        # Собираем состояния
        states = {}
        for i, q in enumerate([q1, q2, q3]):
            well = self.wells[i]
            dp_t = well.pipe.dp(P_man, q).dP
            states[f'well_{i+1}'] = NodeState(name=f'well_{i+1}', P_in=P_man+dp_t, P_out=P_man, dP=dp_t, q_std=q)

        q_sys = q1 + q2 + q3 + self.dcs.q_ext
        dp_sh = self.shlyf.dp(P_man, q_sys).dP
        states['shlyf'] = NodeState(name='shlyf', P_in=P_man, P_out=P_man-dp_sh, dP=dp_sh, q_std=q_sys)
        states['dcs'] = NodeState(name='dcs', P_in=self.dcs.P_in(), P_out=self.dcs.P_line, dP=self.dcs.P_line - self.dcs.P_in(), q_std=q_sys)
        return states

    def run(self, N_days: int, dt: float = 1.0) -> pd.DataFrame:
        rows = []
        for t in tqdm(range(N_days), desc="Simulating"):
            st = self.solve(self.reservoir.resprops.P)
            q1 = st['well_1'].q_std
            q2 = st['well_2'].q_std
            q3 = st['well_3'].q_std
            P_man = st['shlyf'].P_in
            q_wells = q1 + q2 + q3
            rows.append({'t': t, 'P_res': self.reservoir.resprops.P, 'P_man': P_man,
                         'q1': q1, 'q2': q2, 'q3': q3, 'q_total': q_wells + self.dcs.q_ext})
            # Обновляем пластовое давление (без стороннего газа!)
            self.reservoir.resprops.P = self.reservoir.p2(q_wells, dt)

        df = pd.DataFrame(rows)
        df['Gp'] = (df['q1'] + df['q2'] + df['q3']).cumsum() * dt / 1000.0  # тыс. ст.м³
        return df
