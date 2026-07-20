import streamlit as st
from models.thermodynamics import EngineThermodynamics
from models.emissions import MarineEmissionsTwin

# 1. Configuração da Página e Título (Alterado para o novo nome)
st.set_page_config(page_title="TCC EFOMM por enquanto", layout="wide")
st.title("TCC EFOMM por enquanto")
st.markdown("Simulador Digital Twin para análise de Eficiência e Emissões de Motores Marítimos.")

# 2. Painel Lateral - Entrada de Dados (Simulador What-If)
st.sidebar.header("Parâmetros de Entrada do Motor")

potencia = st.sidebar.number_input("Potência do Motor (kW)", min_value=1000.0, max_value=80000.0, value=15000.0, step=500.0)
rpm = st.sidebar.slider("Rotação do Motor (RPM)", min_value=50, max_value=3000, value=120, step=10)
diametro = st.sidebar.number_input("Diâmetro do Cilindro (mm)", min_value=100.0, max_value=1000.0, value=500.0, step=10.0)
curso = st.sidebar.number_input("Curso do Pistão (mm)", min_value=100.0, max_value=3000.0, value=2000.0, step=10.0)

# GNL Removido conforme solicitado. Focado apenas em Diesel Marítimo.
combustivel = st.sidebar.selectbox("Tipo de Combustível", [
    "HFO (Óleo Combustível Pesado)", 
    "MDO (Óleo Diesel Marítimo)"
])

st.write("---")

# 3. Processamento e Cálculos
if st.button("Executar Simulação do Gêmeo Digital"):
    
    # --- MÓDULO TERMODINÂMICO (Brunetti) ---
    motor = EngineThermodynamics(potencia, rpm, diametro, curso)
    
    # Agora o RPM afeta diretamente os resultados matemáticos
    torque_calculado = motor.calcular_torque()
    eficiencia_calculada = motor.calcular_eficiencia_termica()
    consumo_calculado = motor.calcular_consumo_especifico()
    
    st.subheader("Resultados Termodinâmicos (Desempenho)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Torque do Motor", f"{torque_calculado:,.2f} Nm")
    col2.metric("Eficiência Térmica", f"{eficiencia_calculada * 100:.2f} %")
    col3.metric("Consumo Específico", f"{consumo_calculado:.2f} g/kWh")
    
    st.write("---")
    
    # --- MÓDULO DE EMISSÕES (MARPOL / DNV GL / ABS) ---
    emissoes = MarineEmissionsTwin(potencia, consumo_calculado, combustivel)
    co2, sox, nox = emissoes.calcular_emissoes()
    
    st.subheader("Estimativa de Emissões Ambientais")
    col4, col5, col6 = st.columns(3)
    col4.metric("Emissão de CO₂", f"{co2:,.2f} kg/h")
    col5.metric("Emissão de SOx", f"{sox:,.2f} kg/h")
    col6.metric("Emissão de NOx", f"{nox:,.2f} kg/h")

st.write("---")

# 4. Rodapé / Caixa Verde (Texto atualizado)
st.markdown("""
<div style='background-color: #2e7d32; padding: 15px; border-radius: 8px; color: white; text-align: center; font-size: 16px; font-weight: bold;'>
    Simulador TCC EFOMM operando com sucesso! Os parâmetros de RPM agora impactam fisicamente o Torque e a Eficiência.
</div>
""", unsafe_allow_html=True)