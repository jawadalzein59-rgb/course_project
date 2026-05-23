class DCS:
    def __init__(self, CR: float, P_line: float, q_ext: float = 0.0):
        self.CR = CR          # степень сжатия
        self.P_line = P_line  # давление магистрали [атм]
        self.q_ext = q_ext    # сторонний газ [ст.м³/сут]

    def P_in(self) -> float:
        # Если CR=1, станция выключена -> давление на входе = давлению в магистрали
        if self.CR <= 1.0:
            return self.P_line
        # P_out = CR * P_in  =>  P_in = P_line / CR
        return self.P_line / self.CR
