import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import urllib.parse
import unicodedata

# =========================================================
# 0. NÚCLEO DE CÁLCULO E TRATAMENTO DE DADOS
# =========================================================
def clean(txt):
    if not txt: return "N/A"
    return str(txt).encode('latin-1', 'replace').decode('latin-1')

def remover_acentos(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def calcular_psicrometria(temp, ur):
    """Calcula Umidade Absoluta (g/kg) para diagnóstico de dreno"""
    try:
        es = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))
        e = es * (ur / 100)
        ua = (622 * e) / (1013.25 - e)
        return round(ua, 2)
    except: return 0.0

def get_tsat_global(psig, gas):
    """Tabela de Saturação para SH e SC"""
    ancoras = {
        "R-410A": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.0, -0.29, 20.93, 35.58, 47.3, 56.59, 64.59]},
        "R-32": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.7, 0.87, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-40.8, 15.80, 38.56, 54.89, 67.8, 78.0, 85.0]},
        "R-134a": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.1, 12.2, 30.9, 43.6, 53.7]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# =========================================================
# 1. INTERFACE E ESTRUTURA (LAYOUT BLOQUEADO)
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 18px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 1.4, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="k_cliente")
    doc_cliente = c2.text_input("CPF/CNPJ", key="k_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp (Ex: 21980264217)", value="21980264217")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    fabricante = g1.text_input("Marca")
    tecnologia = g2.selectbox("Tecnologia", ["Inverter", "WindFree", "On-Off", "VRF", "Scroll"])
    fluido = g3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
    sistema = g4.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Chiller", "MultiSplit"])

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos e Estabilidade")
    el1, el2, el3 = st.columns(3)
    v_rede = el1.number_input("Tensão Nominal (Rede)", value=220.0)
    v_med = el1.number_input("Tensão Medida (V)", value=220.0)
    rla_comp = el2.number_input("Corrente RLA (Placa)", value=1.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)
    fp = el3.number_input("Fator de Potência (cos Φ)", value=0.87, min_value=0.0, max_value=1.0)
    lra_comp = el3.number_input("LRA (Partida)", value=0.0)
    
    # Cálculos Elétricos
    p_aparente = v_med * a_med
    p_ativa = p_aparente * fp
    p_reativa = math.sqrt(max(0, (p_aparente**2) - (p_ativa**2)))
    diff_tensao = v_med - v_rede
    diff_corrente = a_med - rla_comp
    
    st.divider()
    res1, res2, res3, res4, res5 = st.columns(5)
    res1.metric("Potência Ativa", f"{p_ativa:.1f} W")
    res2.metric("Potência Reativa", f"{p_reativa:.1f} VAr")
    res3.metric("Potência Aparente", f"{p_aparente:.1f} VA")
    res4.metric("Dif. Tensão", f"{diff_tensao:.1f} V", delta=f"{diff_tensao:.1f} V", delta_color="inverse")
    res5.metric("Dif. Corrente", f"{diff_corrente:.1f} A", delta=f"{diff_corrente:.1f} A", delta_color="inverse")

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=118.0)
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        st.info(f"T-Sat Sucção: {ts_suc} °C")
    with tr2:
        p_liq = st.number_input("Pressão Líquido (PSI)", value=345.0)
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.info(f"T-Sat Líquido: {ts_liq} °C")
    with tr3:
        t_ret = st.number_input("Temp. Retorno (°C)", value=25.0)
        ur_ret = st.slider("UR Retorno (%)", 0, 100, 50)
        t_ins = st.number_input("Temp. Insuflação (°C)", value=12.0)
        ur_ins = st.slider("UR Insuflação (%)", 0, 100, 90)
        ua_ret = calcular_psicrometria(t_ret, ur_ret)
        ua_ins = calcular_psicrometria(t_ins, ur_ins)
        dreno = round(max(0, ua_ret - ua_ins), 2)
        st.success(f"SH: {sh_val} K | SC: {sc_val} K")
        st.metric("Remoção de Umidade", f"{dreno} g/kg")

# =========================================================
# 2. MOTOR DE INTELIGÊNCIA HVAC
# =========================================================
diag_lista = []
if sh_val > 12: diag_lista.append("Superaquecimento elevado (Possível baixa carga)")
if sh_val < 4: diag_lista.append("Superaquecimento baixo (Risco de golpe de líquido)")
if sc_val < 2: diag_lista.append("Subresfriamento insuficiente (Ineficiência de condensação)")
if fp < 0.90: diag_lista.append("Baixo Fator de Potência (Capacitor/Harmônicas)")
if abs(diff_tensao) > (v_rede * 0.1): diag_lista.append("Instabilidade na Tensão de Rede")
if dreno < 0.8 and sh_val < 10: diag_lista.append("Baixa Troca Térmica (Sujeira/Filtros)")

diag_ia_txt = " | ".join(diag_lista) if diag_lista else "Sistema operando em conformidade técnica."
cop_aprox = round((dreno + 2) / (sh_val + 0.5), 2) if sh_val > -0.5 else 0.0
acoes_txt = "Realizar limpeza técnica e ajuste de carga." if diag_lista else "Manutenção preventiva padrão."

# --- ABA 4: DIAGNÓSTICO E RELATÓRIO (RESTURADOS) ---
with tab_diag:
    st.header("🤖 DIAGNÓSTICO FINAL")
    d1, d2 = st.columns(2)
    with d1:
        st.info(f"### 🔎 Análise do Sistema\n{diag_ia_txt}")
    with d2:
        st.success(f"### 🛠️ Medidas Recomendadas\n{acoes_txt}")
        st.metric("COP Estimado", cop_aprox)

    st.divider()
    
    # Formatação do Relatório (Layout Protegido)
    rel_wpp = f"*MPN ENGENHARIA - RELATÓRIO TÉCNICO*\n" \
              f"-------------------------------------------\n" \
              f"CLIENTE: {cliente if cliente else 'N/A'}\n" \
              f"DIAGNÓSTICO: {diag_ia_txt}\n" \
              f"COP: {cop_aprox} | Dif.V: {diff_tensao}V\n" \
              f"-------------------------------------------\n" \
              f"Data: {data_visita.strftime('%d/%m/%Y %H:%M')}"
    
    st.text_area("📄 Resumo do Relatório", rel_wpp, height=150)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        # Codificação correta para o WhatsApp não falhar
        texto_codificado = urllib.parse.quote(rel_wpp)
        link_wpp = f"https://wa.me/{whatsapp}?text={texto_codificado}"
        st.markdown(f'<a href="{link_wpp}" target="_blank"><button style="width:100%; padding:12px; background-color:#25D366; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🟢 ENVIAR VIA WHATSAPP</button></a>', unsafe_allow_html=True)
    
    with col_btn2:
        if st.button("📄 GERAR RELATÓRIO PDF", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Courier", 'B', 14)
            pdf.cell(0, 10, clean("MPN ENGENHARIA - LAUDO TECNICO"), 0, 1, 'C')
            pdf.ln(5)
            pdf.set_font("Courier", '', 10)
            corpo_pdf = f"CLIENTE: {cliente}\nDATA: {data_visita.strftime('%d/%m/%Y')}\n" \
                        f"MARCA: {fabricante} | SISTEMA: {sistema}\n" \
                        f"DIAGNOSTICO: {diag_ia_txt}\n" \
                        f"COP: {cop_aprox} | F.P: {fp}\n" \
                        f"DIF. TENSAO: {diff_tensao}V | DIF. CORRENTE: {diff_corrente}A\n" \
                        f"DRENO: {dreno} g/kg\n\nRECOMENDACOES: {acoes_txt}"
            pdf.multi_cell(0, 7, clean(corpo_pdf))
            pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 Baixar PDF", data=pdf_out, file_name=f"Laudo_{remover_acentos(cliente)}.pdf", mime="application/pdf")

# --- ABA 5: HISTÓRICO ---
with tab_hist:
    st.subheader("📜 Histórico")
    st.write(f"Último diagnóstico realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
