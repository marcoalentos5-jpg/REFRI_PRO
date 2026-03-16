import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata

# =========================================================
# 0. FUNÇÕES DE SUPORTE E MATEMÁTICA HVAC
# =========================================================
def clean(txt):
    if not txt: return "N/A"
    return str(txt).encode('latin-1', 'replace').decode('latin-1')

def remover_acentos(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def seguro(val):
    try: return float(val)
    except: return 0.0

def calcular_psicrometria(temp, ur):
    """Calcula a Umidade Absoluta (g/kg)"""
    es = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))
    e = es * (ur / 100)
    ua = (622 * e) / (1013.25 - e)
    return round(ua, 2)

def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], 
                   "t": [-51.0, -0.29, 20.93, 35.58, 47.3, 56.59, 64.59]},
        "R-32": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], 
                 "t": [-51.7, 0.87, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 54.89, 67.8]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 150.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 43.65, 53.74]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# =========================================================
# 1. CONFIGURAÇÕES E INTERFACE
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 20px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# --- ABA 1: IDENTIFICAÇÃO COMPLETA ---
with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="k_cliente")
    doc_cliente = c2.text_input("CPF/CNPJ", key="k_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="k_data_v")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="k_wpp")
    celular = c5.text_input("📱 Celular", key="k_cel")
    tel_fixo = c6.text_input("📞 Fixo", key="k_fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="k_tlogr")
    nome_logr = e2.text_input("Logradouro", key="k_logr")
    numero = e3.text_input("Nº", key="k_num")
    complemento = e4.text_input("Comp.", key="k_comp")
    bairro = e5.text_input("Bairro", key="k_bairro")
    cep = e6.text_input("CEP", key="k_cep")
    email_cli = e7.text_input("✉️ E-mail", key="k_email")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        fabricante = st.text_input("Marca", key="k_marca")
        modelo_eq = st.text_input("Modelo Geral", key="k_mod")
        serie_evap = st.text_input("Série Evaporadora", key="k_sevap")
    with g2:
        linha = st.text_input("Linha", key="k_linha")
        cap_btu = st.text_input("Capacidade (BTU/h)", value="0", key="k_cap")
        serie_cond = st.text_input("Série Condensadora", key="k_scond")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="k_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"], key="k_gas")
        loc_evap = st.text_input("Local Evaporadora", key="k_locevap")
    with g4:
        sistema = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="k_sis")
        loc_cond = st.text_input("Local Condensadora", key="k_loccond")

# --- ABA 2: ELÉTRICA (Triângulo de Potências) ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    v_rede = el1.number_input("Tensão Rede (V)", value=220.0, key="k_v_rede")
    v_med = el1.number_input("Tensão Medida (V)", value=218.0, key="k_v_med")
    rla_comp = el2.number_input("Corrente RLA (A)", value=1.0, key="k_rla")
    a_med = el2.number_input("Corrente Medida (A)", value=0.0, key="k_a_med")
    fp = el3.number_input("Fator de Potência (cos Φ)", value=0.87, min_value=0.0, max_value=1.0, key="k_fp")
    lra_comp = el3.number_input("LRA (A)", value=0.0, key="k_lra")
    
    # Cálculos Elétricos
    p_aparente = v_med * a_med
    p_ativa = p_aparente * fp
    p_reativa = math.sqrt(max(0, (p_aparente**2) - (p_ativa**2)))
    
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Potência Ativa", f"{p_ativa:.1f} W")
    res2.metric("Potência Reativa", f"{p_reativa:.1f} VAr")
    res3.metric("Potência Aparente", f"{p_aparente:.1f} VA")

# --- ABA 3: TERMODINÂMICA (SH, SC e Dreno) ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.write("**Baixa (Sucção)**")
        p_suc = st.number_input("Pressão Sucção (PSI)", value=118.0, key="k_psuc")
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0, key="k_tsuc_t")
        ts_suc = get_tsat_global(p_suc, fluido)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        st.info(f"T-Sat Sucção: {ts_suc} °C")
    
    with tr2:
        st.write("**Alta (Líquido)**")
        p_liq = st.number_input("Pressão Líquido (PSI)", value=345.0, key="k_pliq")
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0, key="k_tliq_t")
        ts_liq = get_tsat_global(p_liq, fluido)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.info(f"T-Sat Líquido: {ts_liq} °C")

    with tr3:
        st.write("**Psicrometria (Ar)**")
        t_ret = st.number_input("Temp. Retorno (°C)", value=25.0, key="k_tret")
        ur_ret = st.slider("UR Retorno (%)", 0, 100, 50, key="k_uret")
        t_ins = st.number_input("Temp. Insuflação (°C)", value=12.0, key="k_tins")
        ur_ins = st.slider("UR Insuflação (%)", 0, 100, 90, key="k_uins")
        
        ua_ret = calcular_psicrometria(t_ret, ur_ret)
        ua_ins = calcular_psicrometria(t_ins, ur_ins)
        dreno = round(max(0, ua_ret - ua_ins), 2)
        
        st.success(f"SH: {sh_val} K | SC: {sc_val} K")
        st.metric("Remoção de Umidade", f"{dreno} g/kg")

# =========================================================
# 2. MOTOR DE INTELIGÊNCIA HVAC
# =========================================================
diag_lista = []
prob_map = {}

def registrar_ia(falha, causa, peso):
    if falha not in diag_lista: diag_lista.append(falha)
    prob_map[causa] = peso

if sh_val > 12: registrar_ia("Superaquecimento elevado", "Baixa carga de fluido", 75)
if sc_val < 2: registrar_ia("Subresfriamento insuficiente", "Eficiência da condensação reduzida", 60)
if fp < 0.90: registrar_ia("Baixo Fator de Potência", "Capacitor de marcha desgastado", 85)
if dreno < 1.0 and sh_val < 10: registrar_ia("Baixa Troca Térmica", "Sujeira na serpentina/filtros", 70)

try: cop_aprox = round((dreno + 2) / (sh_val + 0.5), 2)
except: cop_aprox = 0.0

diag_ia_txt = " | ".join(diag_lista) if diag_lista else "Sistema operando nos padrões"
prob_ia_txt = " | ".join([f"{c} ({p}%)" for c, p in prob_map.items()]) if prob_map else "Sem falhas críticas"
acoes_txt = "Revisar carga e limpeza técnica" if diag_lista else "Manutenção preventiva padrão"

# --- ABA 4: DIAGNÓSTICO FINAL ---
with tab_diag:
    st.header("🤖 DIAGNÓSTICO FINAL")
    d_c1, d_c2 = st.columns(2)
    with d_c1:
        st.info(f"### 🔎 Análise do Sistema\n{diag_ia_txt}")
        st.warning(f"### 📊 Causas Prováveis\n{prob_ia_txt}")
    with d_c2:
        st.success(f"### 🛠️ Medidas Recomendadas\n{acoes_txt}")
        st.metric("COP Estimado", cop_aprox)
        st.metric("Fator de Potência", fp)

    st.divider()
    relatorio_txt = f"""*MPN ENGENHARIA*
---------------------------
CLIENTE: {cliente}
DIAGNÓSTICO: {diag_ia_txt}
AÇÕES: {acoes_txt}
COP: {cop_aprox} | FP: {fp}
DRENO: {dreno} g/kg
---------------------------
{datetime.now().strftime('%d/%m/%Y %H:%M')}"""

    st.text_area("📄 Resumo para WhatsApp", relatorio_txt, height=180)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        wpp_url = f"https://api.whatsapp.com/send?phone={whatsapp}&text={relatorio_txt.replace(' ', '%20')}"
        st.markdown(f'<a href="{wpp_url}" target="_blank"><button style="width:100%; padding:12px; background-color:#25D366; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🟢 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)
    
    with col_btn2:
        if st.button("📄 Gerar Laudo PDF", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Courier", 'B', 14)
            pdf.cell(0, 10, clean("MPN ENGENHARIA - LAUDO TECNICO"), 0, 1, 'C')
            pdf.ln(5)
            pdf.set_font("Courier", '', 10)
            corpo_pdf = f"CLIENTE: {cliente}\nDATA: {data_visita}\nEQUIPAMENTO: {fabricante} {modelo_eq}\nSISTEMA: {sistema}\n\nDIAGNOSTICO: {diag_ia_txt}\nCOP ESTIMADO: {cop_aprox}\nFATOR POTENCIA: {fp}\nDRENO: {dreno} g/kg\n\nRECOMENDACOES: {acoes_txt}"
            pdf.multi_cell(0, 7, clean(corpo_pdf))
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 Baixar Laudo PDF", data=pdf_bytes, file_name=f"Laudo_{remover_acentos(cliente)}.pdf", mime="application/pdf")

# --- ABA 5: HISTÓRICO ---
with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    st.info("O banco de dados local 'banco_dados.db' está pronto para integração.")
