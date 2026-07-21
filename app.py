import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Digital Twin Naval - TCC Renê",
    page_icon="🚢",
    layout="wide"
)

# ==========================================
# TÍTULO E CABEÇALHO
# ==========================================
st.title("Software para análise")
st.divider()

# ==========================================
# BARRA LATERAL (ENTRADAS DO DIGITAL TWIN)
# ==========================================
st.sidebar.header("⚙️ Parâmetros do Motor (Entradas)")

# Dados do Motor
st.sidebar.subheader("Especificações Físicas")
rpm = st.sidebar.number_input("Rotação do Motor (RPM)", min_value=1, value=3000, step=100)
cilindros = st.sidebar.number_input("Número de Cilindros (N)", min_value=1, value=6, step=1)
vd = st.sidebar.number_input("Volume Deslocado por Cilindro (L)", min_value=0.1, value=0.5, step=0.1)

# Dados Termodinâmicos Atuais
st.sidebar.subheader("Dados Operacionais (Tempo Real)")
mep = st.sidebar.number_input("Pressão Média Efetiva Indicada - MEP (bar)", min_value=1.0, value=15.0, step=0.5)
eficiencia_mecanica = st.sidebar.slider("Eficiência Mecânica Estimada (%)", min_value=50, max_value=100, value=85)
consumo_atual = st.sidebar.number_input("Consumo de Combustível Atual (kg/h)", min_value=1.0, value=45.0, step=1.0)

# Dados de Projeto (Baseline para o Gêmeo Digital)
st.sidebar.subheader("Baseline de Projeto (Bula)")
consumo_projeto = st.sidebar.number_input("Consumo Ideal de Fábrica (kg/h)", min_value=1.0, value=42.0, step=1.0)

# ==========================================
# PROCESSAMENTO MATEMÁTICO
# ==========================================
# Cálculo da Potência Indicada (PI) em kW (Motor 4 tempos)
# Fórmula adaptada: PI(kW) = (MEP(bar) * Vd(L) * N * RPM) / 1200
pi_kw = (mep * vd * cilindros * rpm) / 1200

# Cálculo da Potência Efetiva (Pb) em kW
pb_kw = pi_kw * (eficiencia_mecanica / 100)

# Cálculo do BSFC (Brake Specific Fuel Consumption) - g/kWh
# Multiplica por 1000 para converter kg/h para g/h
if pb_kw > 0:
    bsfc = (consumo_atual * 1000) / pb_kw
else:
    bsfc = 0

# ==========================================
# CONSTRUÇÃO DAS ABAS (TABS)
# ==========================================
tab1, tab2 = st.tabs(["📊 Eficiência Térmica (Digital Twin)", "☁️ Emissões (MARPOL)"])

# ------------------------------------------
# ABA 1: EFICIÊNCIA TÉRMICA
# ------------------------------------------
with tab1:
    st.header("Análise de Desempenho e Eficiência")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Potência Indicada (PI)", value=f"{pi_kw:.2f} kW", 
                  help="Potência gerada pela expansão dos gases dentro dos cilindros.")
    with col2:
        st.metric(label="Potência Efetiva (Pb)", value=f"{pb_kw:.2f} kW", 
                  help="Potência real que chega ao eixo do motor (descontando atrito).")
    with col3:
        # Verifica se o BSFC está alto ou baixo
        bsfc_delta = "Alta eficiência" if bsfc < 220 else "Baixa eficiência"
        delta_color = "normal" if bsfc < 220 else "inverse"
        st.metric(label="Consumo Específico (BSFC)", value=f"{bsfc:.2f} g/kWh", delta=bsfc_delta, delta_color=delta_color)

    st.subheader("Diagnóstico do Gêmeo Digital (Comparação de Projeto)")
    
    # Lógica do Digital Twin
    desvio_consumo = ((consumo_atual - consumo_projeto) / consumo_projeto) * 100
    
    if desvio_consumo <= 2:
        st.success(f"✅ O motor está operando dentro dos parâmetros ideais do fabricante. Desvio de apenas {desvio_consumo:.1f}%.")
    elif desvio_consumo <= 5:
        st.warning(f"⚠️ Alerta: O consumo está {desvio_consumo:.1f}% acima da Baseline de projeto. Possível desgaste leve ou injeção desregulada.")
    else:
        st.error(f"🚨 Crítico: O motor está consumindo {desvio_consumo:.1f}% a mais que o ideal de projeto! Risco de degradação térmica profunda (verificar anéis de segmento e bicos injetores).")

# ------------------------------------------
# ABA 2: EMISSÕES (MARPOL / CLASSIFICADORAS)
# ------------------------------------------
with tab2:
    st.header("Inventário de Emissões de GEE (Normas ABS / DNV GL)")
    
    tipo_combustivel = st.selectbox("Selecione o Tipo de Combustível Utilizado:", ["MDO (Marine Diesel Oil)", "HFO (Heavy Fuel Oil)"])
    
    # Fatores de Emissão (Aproximados - Padrão IMO)
    if tipo_combustivel == "MDO (Marine Diesel Oil)":
        f_co2, f_sox, f_nox = 3.206, 0.002, 0.055
    else:
        f_co2, f_sox, f_nox = 3.114, 0.050, 0.070
    
    # Cálculos diários (kg/h * 24h = kg/dia) -> divide por 1000 para Toneladas/dia
    emis_co2 = (consumo_atual * f_co2 * 24) / 1000
    emis_sox = (consumo_atual * f_sox * 24) / 1000
    emis_nox = (consumo_atual * f_nox * 24) / 1000

    col_e1, col_e2, col_e3 = st.columns(3)
    
    col_e1.metric(label="Emissão de CO₂", value=f"{emis_co2:.2f} Ton/dia", help="Dióxido de Carbono")
    col_e2.metric(label="Emissão de SOx", value=f"{emis_sox:.4f} Ton/dia", help="Óxidos de Enxofre (Controlado pelo Anexo VI MARPOL)")
    col_e3.metric(label="Emissão de NOx", value=f"{emis_nox:.4f} Ton/dia", help="Óxidos de Nitrogênio (Regras Tier II/III)")
    
    st.info("💡 Estes cálculos simulam as auditorias de eficiência e poluição requeridas pelas Sociedades Classificadoras para a obtenção de certificados de conformidade ambiental.")

# Rodapé
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desenvolvido por: Costa, Lucas Duarte, Bernardo</p>", unsafe_allow_html=True)