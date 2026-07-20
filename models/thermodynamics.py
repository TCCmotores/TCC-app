import math

class EngineThermodynamics:
    def __init__(self, potencia_kw, rpm, diametro_cilindro_mm, curso_pistao_mm):
        self.potencia = potencia_kw
        self.rpm = rpm
        self.diametro = diametro_cilindro_mm / 1000  # Convertendo para metros
        self.curso = curso_pistao_mm / 1000          # Convertendo para metros

    def calcular_torque(self):
        # Fórmula: Torque = (Potência em Watts * 60) / (2 * pi * RPM)
        if self.rpm <= 0:
            return 0
        potencia_watts = self.potencia * 1000
        torque = (potencia_watts * 60) / (2 * math.pi * self.rpm)
        return torque

    def calcular_eficiencia_termica(self):
        # A eficiência térmica varia levemente com a rotação (RPM) devido a perdas por atrito.
        # Rotações muito altas diminuem a eficiência mecânica.
        eficiencia_base = 0.45  # 45% de eficiência base para motores navais
        perda_por_rpm = (self.rpm / 10000) * 0.05
        eficiencia_real = eficiencia_base - perda_por_rpm
        
        # Garante que a eficiência não seja irreal
        if eficiencia_real < 0.30:
            eficiencia_real = 0.30
            
        return eficiencia_real

    def calcular_consumo_especifico(self):
        # Retorna o consumo em g/kWh com base na eficiência influenciada pelo RPM
        eficiencia = self.calcular_eficiencia_termica()
        # Poder calorífico inferior médio do diesel marítimo (aprox 42.7 MJ/kg)
        pci_kwh_kg = 11.86
        
        consumo_kg_kwh = 1 / (eficiencia * pci_kwh_kg)
        consumo_g_kwh = consumo_kg_kwh * 1000
        
        return consumo_g_kwh