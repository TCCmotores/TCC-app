class MarineEmissionsTwin:
    def __init__(self):
        # Dicionário incorporando o fator estequiométrico Cf
        self.cf_factors = {
            'Diesel/Gas Oil (MGO)': 3.206,
            'Heavy Fuel Oil (HFO)': 3.114,
            'Liquefied Natural Gas (LNG)': 2.750,
            'Methanol': 1.375
        }
    
    def fetch_cf_factor(self, fuel_type):
        return self.cf_factors.get(fuel_type, 3.206)

    def calculate_eedi_mepc364(self, power_kw, sfc_g_kwh, capacity_dwt, v_ref_knots, fuel_type):
        cf = self.fetch_cf_factor(fuel_type)
        # O processamento da MEPC requer a translação do consumo específico horário 
        # juntamente com o fator CF associado. Resulta em gCO2 / ton.nautical_mile
        total_co2_emission = power_kw * cf * sfc_g_kwh  
        transport_work = capacity_dwt * v_ref_knots
        
        if transport_work == 0:
            return 0.0
        return total_co2_emission / transport_work

    def get_marpol_nox_tier_limit(self, engine_rpm, tier="Tier III"):
        # Mapeamento estrito da resolução do Anexo VI MARPOL
        if engine_rpm < 130:
            return 3.4 if tier == "Tier III" else (14.4 if tier == "Tier II" else 17.0)
        elif engine_rpm < 2000:
            if tier == "Tier III":
                return 9.0 * (engine_rpm ** -0.2)
            elif tier == "Tier II":
                return 44.0 * (engine_rpm ** -0.23)
            else:
                return 45.0 * (engine_rpm ** -0.2)
        else:
            return 2.0 if tier == "Tier III" else (7.7 if tier == "Tier II" else 9.8)