import streamlit as st
from models.emissions import MarineEmissionsTwin
from models.thermodynamics import EngineThermodynamics

st.set_page_config(page_title="TCC EFOMM", layout="wide")

st.title("TCC EFOMM")
st.markdown("Interface integrando fundamentos termodinâmicos, matrizes de cálculo da MEPC.364(79) e conformidade MARPOL referenciada por DNV/ABS.")

st.sidebar.header("Parâmetros Teledinâmicos de Entrada")
st.sidebar.subheader("Arquitetura do Motor")
bore = st.sidebar.number_input("Diâmetro do Cilindro (Bore) [m]", value=0.50, format="%.2f")
stroke = st.sidebar.number_input("Curso do Pistão (Stroke) [m]", value=2.00, format="%.2f")
cylinders = st.sidebar.number_input("Número de Cilindros", value=6, step=1)
rpm = st.sidebar.number_input("Rotação (RPM)", value=100.0, step=1.0)
power_kw = st.sidebar.number_input("Potência Efetiva (kW)", value=15000.0)
fuel_flow = st.sidebar.number_input("Consumo de Combustível (kg/h)", value=2500.0)

st.sidebar.subheader("Dinâmica da Viagem e Combustível")
fuel_type = st.sidebar.selectbox("Combustível Primário", ["Heavy Fuel Oil (HFO)", "Diesel/Gas Oil (MGO)", "Liquefied Natural Gas (LNG)", "Methanol"])
capacity = st.sidebar.number_input("Capacidade de Transporte (DWT)", value=50000.0)
v_ref = st.sidebar.number_input("Velocidade de Cruzeiro (Nós)", value=14.5)

engine = EngineThermodynamics(bore, stroke, cylinders)
emissions = MarineEmissionsTwin()

sfc_calculated = engine.calculate_sfc(fuel_flow, power_kw)
eedi_score = emissions.calculate_eedi_mepc364(power_kw, sfc_calculated, capacity, v_ref, fuel_type)
nox_compliance = emissions.get_marpol_nox_tier_limit(rpm, tier="Tier III")

col1, col2, col3 = st.columns(3)
col1.metric("Volume Deslocado", f"{engine.displacement_m3:.3f} m³")
col2.metric("SFC Específico", f"{sfc_calculated:.1f} g/kWh")
col3.metric("Fator de Carbono Estequiométrico", f"{emissions.fetch_cf_factor(fuel_type):.3f}")

st.divider()
st.subheader("Balanço Ambiental e Índices MARPOL Anexo VI")

col_a, col_b = st.columns(2)
col_a.info(f"**EEDI Teórico Atingido:** {eedi_score:.2f} gCO2/ton.mile\n\n*Aprovação de projeto DNV/ABS atrelada à curva diretriz base.*")
col_b.warning(f"**Limite NOx Estrito (Tier III):** {nox_compliance:.2f} g/kWh\n\n*Condicional para operação em Áreas de Controle de Emissão (ECAs).*")

st.divider()
st.subheader("Simulador What-If: Transição para GNL")
st.write("Cálculo preditivo de redução das emissões brutas através do retrofit ou adoção operacional de Gás Natural Liquefeito.")
eedi_lng_projected = emissions.calculate_eedi_mepc364(power_kw, sfc_calculated, capacity, v_ref, "Liquefied Natural Gas (LNG)")
percentual_reduction = ((eedi_score - eedi_lng_projected) / eedi_score) * 100 if eedi_score > 0 else 0

st.success(f"O TCC EFOMM projeta que a adoção de GNL resultaria em um EEDI reduzido de {eedi_lng_projected:.2f} gCO2/ton.mile. Uma drástica contração regulatória de {percentual_reduction:.1f}%.")