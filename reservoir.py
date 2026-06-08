from dataclasses import dataclass

@dataclass
class ResProps:
    P: float        # Current pressure [atm]
    V_res: float    # Reservoir volume [m³]
    T: float        # Temperature [K]

class Reservoir:
    def __init__(self, props: ResProps, fluid: object):
        self.resprops = props
        self.fluid = fluid
        self.P_init = props.P
        self.V_res = props.V_res
        self.T = props.T

    def p2(self, q_res_m3: float, dt: float) -> float:
        """Update reservoir pressure via material balance"""
        # P2 = P1 * (1 - produced_volume / reservoir_volume)
        produced_volume = q_res_m3 * dt  # m³ produced this timestep
        if produced_volume < self.V_res:
            self.resprops.P = self.P_init * (1 - produced_volume / self.V_res)
        else:
            self.resprops.P = self.P_init * 0.5  # Safety clamp
        self.P_init = self.resprops.P  # Update initial for next step
        return self.resprops.P
