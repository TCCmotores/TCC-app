import math

class EngineThermodynamics:
    def __init__(self, bore_m, stroke_m, num_cylinders):
        self.bore = bore_m
        self.stroke = stroke_m
        self.cylinders = num_cylinders
        # Processamento da capacidade volumétrica cúbica (cilindrada)
        self.displacement_m3 = (math.pi * (bore_m ** 2) / 4) * stroke_m * num_cylinders
        
    def calculate_sfc(self, fuel_flow_kg_h, effective_power_kw):
        # Conversão linear para compatibilidade com matrizes de emissões (g/kWh)
        if effective_power_kw <= 0:
            return 0.0
        fuel_flow_g_h = fuel_flow_kg_h * 1000.0
        return fuel_flow_g_h / effective_power_kw

    def mechanical_efficiency(self, indicated_power_kw, effective_power_kw):
        if indicated_power_kw <= 0:
            return 0.0
        return (effective_power_kw / indicated_power_kw) * 100.0