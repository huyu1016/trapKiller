class contract:
    """智能合约的相关信息"""
    def __init__(self, contr_name, main, boo, ts, ssp, stp, sp, ft):
        self.name = contr_name
        self.main_contr = main
        self.boolean = boo
        self.TS = ts
        self.SSP = ssp
        self.STP = stp
        self.SP = sp
        self.FT = ft
    def get_name(self):
        return self.name
    def get_main_contr(self):
        return self.main_contr
    def get_boolean(self):
        return self.boolean
    def is_ts(self):
        return self.TS
    def is_ssp(self):
        return self.SSP
    def is_stp(self):
        return self.STP
    def is_sp(self):
        return self.SP
    def is_ft(self):
        return self.FT