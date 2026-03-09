import streamlit as st
from datetime import date
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia", layout="wide", page_icon="❄️")

# --- 2. SCRIPT PARA PULAR CAMPOS COM ENTER ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const focusable = doc.querySelectorAll('input, select, textarea, button');
            const index = Array.from(focusable).indexOf(doc.activeElement);
            if (index > -1 && index + 1 < focusable.length) {
                focusable[index + 1].focus();
                e.preventDefault();
            }
        }
    });
    </script>
    """,
    height=0,
)

# --- 3. ESTILIZAÇÃO MPN (CORES DE SATURAÇÃO DIFERENCIADAS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] { background-color: #E3F2FD; border-radius: 10px; padding: 15px; border: 1px solid #BBDEFB; }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] { background-color: #E8F5E9; border-radius: 10px; padding: 15px; border: 1px solid #C8E6C9; }
    
    /* CORES DE SATURAÇÃO (3 e 4) - Laranja e Âmbar */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] { background-color: #FFF3E0 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFB74D !important; }
    div[data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] { background-color: #FFFDE7 !important; border-radius: 10px; padding: 15px; border: 2px solid #FFF176 !important; }
    
    .stTabs [aria-selected="true"] { background-color: #004A99 !important; color: white !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; height: 3.5em; background-color: #004A99; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA TÉCNICA REFINADA (FOCO R-410A) ---
def calcular_tsat(psig, gas):
    if psig <= 0: return 0.0
    # Coeficientes de alta precisão para a faixa de operação residencial/comercial
    tabelas = {
        "R-410A": 0.1542 * (psig**0.935) - 20.4, # Curva ajustada para R410A
        "R-22": 0.2845 * psig - 25.05,
        "R-134a": 0.5185 * psig - 38.41,
        "R-32": 0.3085 * psig - 24.85,
        "R-404A": 0.2098 * psig - 16.45
    }
    # Fallback para linear simples caso o gás não tenha curva complexa mapeada
    if gas not in tabelas:
        return round(0.23 * psig - 22.0, 2)
        
    return round(tabelas.get(gas), 2)

# --- 5. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico & Relatório"
])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c1.text_input("CPF / CNPJ")
    endereco = c2.text_input("Endereço Completo")
    whatsapp_input = c3.text_input("🟢 WhatsApp (com DDD)", value="21980264217")
    data_visita = c3.date_input("Data da Visita", value=date.today(), format="DD/MM/YYYY")
    email_cli = c2.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha (Ex: Artcool, WindFree)")
    tecnologia = d2.selectbox("Tecnologia do Compressor", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "Multi-Split", "VRF/VRV", "Geladeira", "Freezer", "Chiller", "Câmara Fria", "Balcão Frigorífico", "Bebedouro", "Ar-Condicionado Janela", "Self-Contained", "Fan-Coil"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-22", "R-32", "R-134a", "R-600a", "R-290", "R-404A", "R-407C", "R-417A", "R-507A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        mod_evap = st.text_input("Modelo da Unidade (Evap)")
        serie_evap = st.text_input("Nº de Série da Unidade (Evap)")
    with col_u2:
        mod_cond = st.text_input("Modelo da Unidade (Cond)")
        serie_cond = st.text_input("Nº de Série da Unidade (Cond)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    col_v, col_a = st.columns(2)
    with col_v:
        v_nom_str = st.selectbox("Tensão Nominal (V)", ["127", "220", "360", "480"])
        v_nom = float(v_nom_str)
        v_med = st.number_input("Tensão Medida (V)", value=0.0)
        st.write(f"Diferença: {round(abs(v_nom - v_med), 1)}V")
    with col_a:
        a_rla = st.number_input("Corrente RLA (A)", value=0.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        st.write(f"Diferença: {round(abs(a_rla - a_med), 1)}A")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    t1, t2 = st.columns(2)
    with t1:
        p_suc = st.number_input("Pressão Sucção (PSIG)", value=120.0)
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=10.0)
    with t2:
        p_liq = st.number_input("Pressão Descarga (PSIG)", value=350.0)
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    
    # CÁLCULOS TÉCNICOS CORRIGIDOS
    tsat_suc = calcular_tsat(p_suc, fluido)
    tsat_liq = calcular_tsat(p_liq, fluido)
    
    # SH = Tubo - Sat (Superaquecimento)
    sh = round(t_suc_tubo - tsat_suc, 1)
    # SC = Sat - Tubo (Sub-resfriamento) - CORREÇÃO FINAL AQUI
    sc = round(tsat_liq - t_liq_tubo, 1)

    st.markdown("### 📊 Performance & Saturação")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Superaquecimento (SH)", f"{sh} K")
    m2.metric("Sub-resfriamento (SC)", f"{sc} K")
    # Cores de Saturação (Laranja/Amarelo)
    m3.metric("T-Sat Sucção", f"{tsat_suc} °C")
    m4.metric("T-Sat Líquido", f"{tsat_liq} °C")

with tab_diag:
    st.subheader("🤖 Diagnóstico Final")
    st.text_area("Análise Técnica", height=150)
    st.button("Gerar Relatório")
