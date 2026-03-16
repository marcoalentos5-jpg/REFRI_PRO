import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import urllib.parse
import unicodedata

# =========================================================
# 0. NÚCLEO TÉCNICO E TRATAMENTO DE DADOS
# =========================================================
def clean(txt):
    if not txt: return "N/A"
    return str(txt).encode('latin-1', 'replace').decode('latin-1')

def remover_acentos(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def calcular_psicrometria(temp, ur):
    try:
        es = 6.112 * math.exp((17.67 * temp) / (temp + 243.5))
        e = es * (ur / 100)
        ua = (622 * e) / (1013.25 - e)
        return round(ua, 2)
    except: return 0.0

def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.0, -0.29, 20.93, 35.58, 47.3, 56.59, 64.59]},
        "R-32": {"p": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.7, 0.87, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0], "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 54.89, 67.8]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 150.0, 200.0], "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 43.65, 53.74]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# =========================================================
# 1. CONFIGURAÇÃO E INTERFACE (LAYOUT BLOQUEADO)
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 18px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# --- ABA 1: IDENTIFICAÇÃO (COMPLETA) ---
with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="k_cliente")
    doc_cliente = c2.text_input("CPF/CNPJ", key="k_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_fixo = c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Comp.")
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        fabricante = st.text_input("Marca")
        modelo_eq = st.text_input("Modelo Geral")
        serie_evap = st.text_input("Série Evaporadora")
    with g2:
        linha = st.text_input("Linha")
        cap_btu = st.text_input("Capacidade (BTU/h)")
        serie_cond = st.text_input("Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        sistema = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"])
        loc_cond = st.text_input("Local Condensadora")

# --- ABA 2: ELÉTRICA (POTÊNCIAS E DELTAS INTEGRADOS) ---
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
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
# 2. MOTOR DE DIAGNÓSTICO IA
# =========================================================
diag_lista = []
if sh_val > 12: diag_lista.append("Superaquecimento Elevado (Baixa Carga)")
if sh_val < 4: diag_lista.append("Superaquecimento Baixo (Risco Golpe Líquido)")
if sc_val < 2: diag_lista.append("Subresfriamento Baixo (Ineficiência)")
if abs(diff_tensao) > (v_rede * 0.1): diag_lista.append("Instabilidade de Tensão")
if diff_corrente > (rla_comp * 0.15): diag_lista.append("Sobrecorrente no Compressor")

diag_ia_txt = " | ".join(diag_lista) if diag_lista else "Sistema em Conformidade Técnica"
cop_aprox = round((dreno + 2) / (sh_val + 0.5), 2) if sh_val > -0.5 else 0.0

# =========================================================
# 3. ABA DIAGNÓSTICO E RELATÓRIO (FORMATO PLANILHA TÉCNICA)
# =========================================================
with tab_diag:
    st.header("🤖 DIAGNÓSTICO E RELATÓRIOS")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📄 GERAR RELATÓRIO PDF (PLANILHA)", use_container_width=True):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, clean("MPN ENGENHARIA - RELATÓRIO TÉCNICO DE INSPEÇÃO"), 0, 1, 'C')
            pdf.ln(4)
            
            def add_row(label, value, is_header=False):
                if is_header:
                    pdf.set_fill_color(230, 230, 230)
                    pdf.set_font("Arial", 'B', 9)
                    pdf.cell(0, 7, clean(label), 1, 1, 'L', True)
                else:
                    pdf.set_font("Arial", 'B', 8)
                    pdf.cell(55, 6, clean(label), 1, 0, 'L')
                    pdf.set_font("Arial", '', 8)
                    pdf.cell(0, 6, clean(str(value)), 1, 1, 'L')

            # Tabela de Identificação
            add_row("1. IDENTIFICAÇÃO DO CLIENTE E LOCAL", "", True)
            add_row("Cliente", cliente)
            add_row("Documento", doc_cliente)
            add_row("Data Visita", data_visita.strftime('%d/%m/%Y'))
            add_row("Endereço", f"{tipo_logr} {nome_logr}, {numero} - {bairro} (CEP: {cep})")
            add_row("Contatos", f"Whats: {whatsapp} | Cel: {celular} | Fixo: {tel_fixo}")
            add_row("E-mail", email_cli)
            pdf.ln(3)

            # Tabela de Equipamento
            add_row("2. DADOS DO EQUIPAMENTO", "", True)
            add_row("Marca/Modelo", f"{fabricante} / {modelo_eq} ({linha})")
            add_row("Capacidade/Fluido", f"{cap_btu} BTU/h - {fluido}")
            add_row("Série Evaporadora", serie_evap)
            add_row("Série Condensadora", serie_cond)
            add_row("Localização", f"Evap: {loc_evap} | Cond: {loc_cond}")
            pdf.ln(3)

            # Tabela Elétrica
            add_row("3. ANÁLISE ELÉTRICA", "", True)
            add_row("Tensão (V)", f"Medida: {v_med}V | Dif: {diff_tensao}V")
            add_row("Corrente (A)", f"Medida: {a_med}A | Placa: {rla_comp}A | Dif: {diff_corrente}A")
            add_row("Potências", f"Ativa: {p_ativa:.1f}W | Aparente: {p_aparente:.1f}VA | FP: {fp}")
            pdf.ln(3)

            # Tabela Termodinâmica e IA
            add_row("4. CICLO E DIAGNÓSTICO", "", True)
            add_row("SH / SC", f"{sh_val} K / {sc_val} K")
            add_row("Dreno/COP", f"{dreno} g/kg | COP Est: {cop_aprox}")
            pdf.set_font("Arial", 'B', 8)
            pdf.multi_cell(0, 7, clean(f"DIAGNÓSTICO IA: {diag_ia_txt}"), 1)

            st.download_button("📥 BAIXAR RELATÓRIO COMPLETO", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name=f"Relatorio_{remover_acentos(cliente)}.pdf")

    with col_btn2:
        rel_msg = f"*MPN ENGENHARIA*\nCliente: {cliente}\nDiag: {diag_ia_txt}\nCOP: {cop_aprox}\nDif.V: {diff_tensao}V"
        link_wpp = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(rel_msg)}"
        st.markdown(f'<a href="{link_wpp}" target="_blank"><button style="width:100%; padding:12px; background-color:#25D366; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🟢 ENVIAR VIA WHATSAPP</button></a>', unsafe_allow_html=True)

# --- ABA 5: HISTÓRICO ---
with tab_hist:
    st.subheader("📜 Histórico de Diagnósticos")
    st.info(f"Sistema pronto. Data local: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
