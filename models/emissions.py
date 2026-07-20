class MarineEmissionsTwin:
    def __init__(self, potencia_kw, consumo_g_kwh, tipo_combustivel):
        # Recebe os dados exatos vindos do painel principal
        self.potencia = potencia_kw
        self.consumo = consumo_g_kwh
        self.combustivel = tipo_combustivel

    def calcular_emissoes(self):
        # 1. Calcula o consumo total de combustível em kg/h
        # (Consumo específico * Potência) / 1000 para converter gramas em quilos
        consumo_kg_h = (self.consumo * self.potencia) / 1000
        
        # 2. Fatores de emissão baseados nas diretrizes da MARPOL / DNV GL
        if "HFO" in self.combustivel:
            fator_co2 = 3.114  # kg CO2 por kg de combustível
            fator_sox = 0.045  # Estimativa de Enxofre pesado
            fator_nox = 0.075  
        else: # "MDO" (Óleo Diesel Marítimo)
            fator_co2 = 3.206  
            fator_sox = 0.015  # Combustível mais limpo, menos SOx
            fator_nox = 0.055  
            
        # 3. Calcula os valores finais
        co2 = consumo_kg_h * fator_co2
        sox = consumo_kg_h * fator_sox
        nox = consumo_kg_h * fator_nox
        
        return co2, sox, nox