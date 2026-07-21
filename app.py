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

# ------------------------------------------
# ABA 2: EMISSÕES (MARPOL / CLASSIFICADORAS)
# ------------------------------------------
with tab2:
    st.header("Inventário de Emissões de GEE (Normas ABS / DNV GL)")
    
    col_comb1, col_comb2 = st.columns(2)
    
    with col_comb1:
        tipo_combustivel = st.selectbox("Selecione o Combustível:", ["MDO (Marine Diesel Oil)", "HFO (Heavy Fuel Oil)"])
    with col_comb2:
        # Padrão MARPOL global é 0.5%. Em HFO costuma ser mais alto se não tratado.
        valor_padrao_enxofre = 0.50 if tipo_combustivel == "MDO (Marine Diesel Oil)" else 2.50
        teor_enxofre = st.number_input("Teor de Enxofre no Combustível (%)", min_value=0.01, max_value=5.00, value=valor_padrao_enxofre, step=0.05)
    
    # Fatores de Emissão
    f_co2 = 3.206 if tipo_combustivel == "MDO (Marine Diesel Oil)" else 3.114
    
    # SOx: 1g de Enxofre (S) gera aprox. 2g de Dióxido de Enxofre (SO2) após a queima
    f_sox = (teor_enxofre / 100) * 2 
    
    # NOx: Fator genérico aproximado por kg de combustível consumido
    f_nox = 0.055 if tipo_combustivel == "MDO (Marine Diesel Oil)" else 0.070
    
    # Cálculos diários (kg/h * 24h = kg/dia) -> divide por 1000 para Toneladas/dia
    emis_co2 = (consumo_atual * f_co2 * 24) / 1000
    emis_sox = (consumo_atual * f_sox * 24) / 1000
    emis_nox_ton = (consumo_atual * f_nox * 24) / 1000

    col_e1, col_e2, col_e3 = st.columns(3)
    
    col_e1.metric(label="Emissão de CO₂", value=f"{emis_co2:.2f} Ton/dia", help="Dióxido de Carbono (Efeito Estufa)")
    col_e2.metric(label="Emissão de SOx", value=f"{emis_sox:.4f} Ton/dia", help="Depende do Teor de Enxofre inserido.")
    col_e3.metric(label="Emissão de NOx (Total)", value=f"{emis_nox_ton:.4f} Ton/dia", help="Massa total de Óxidos de Nitrogênio gerada.")
    
    st.divider()
    
    # --- AUDITORIA MARPOL (ANEXO VI - NOx) ---
    st.subheader("Auditoria MARPOL (Limites de NOx - Tier II)")
    st.markdown("A MARPOL regula a emissão específica de NOx (g/kWh) baseada na Rotação Nominal (RPM) do motor.")
    
    # Fórmula MARPOL Tier II para limite de NOx (g/kWh)
    if rpm < 130:
        limite_nox_g_kwh = 14.4
    elif rpm < 2000:
        limite_nox_g_kwh = 44.0 * (rpm ** -0.23)
    else:
        limite_nox_g_kwh = 7.7
        
    # Calcular a emissão específica de NOx do motor atual
    nox_gerado_hora_g = consumo_atual * f_nox * 1000 # Convertendo kg para gramas
    nox_especifico_atual = nox_gerado_hora_g / pb_kw if pb_kw > 0 else 0
    
    col_n1, col_n2 = st.columns(2)
    col_n1.metric(label="NOx Específico do Motor", value=f"{nox_especifico_atual:.2f} g/kWh")
    col_n2.metric(label="Limite Máximo MARPOL (Para o RPM atual)", value=f"{limite_nox_g_kwh:.2f} g/kWh")
    
    if nox_especifico_atual <= limite_nox_g_kwh:
        st.success("✅ **APROVADO:** O motor atende às regulamentações de emissão de NOx da IMO Tier II.")
    else:
        st.error(f"🚨 **REPROVADO:** O motor excede o limite da MARPOL em {(nox_especifico_atual - limite_nox_g_kwh):.2f} g/kWh. Necessário ajuste de combustão ou sistema SCR.")

# Rodapé
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Desenvolvido por: Costa, Lucas Duarte, Bernardo</p>", unsafe_allow_html=True)