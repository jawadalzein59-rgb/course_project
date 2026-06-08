from dataclasses import dataclass

@dataclass
class DCS:
    CR: float = 1.5
    CR_min: float = 1.5
    CR_max: float = 5.0
    P_line: float = 500.0
    q_ext: float = 0.0

    def P_in(self, CR: float = None) -> float:
        if CR is None:
            CR = self.CR
        return self.P_line / CR

    def q_total(self, q_wells: float) -> float:
        return q_wells + self.q_ext
