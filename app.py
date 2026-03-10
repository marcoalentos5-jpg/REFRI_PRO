import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO (AJUSTE DE PRECISÃO PERICIAL) ---
def get_tsat_global(psig, gas):
    # Ancoras expandidas para garantir precisão em toda a faixa de operação
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0], 
                   "t": [-45.45, -9.41, 8.96, 22.23, 32.59, 41.2, 48.6, 55.2, 61.1]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    l2_c1, l2_c2, l2_c3 = st.columns(3)
    endereco = l2_c1.text_input("Endereço (Rua e Número)")
    bairro = l2_c2.text_input("Bairro")
    cep = l2_c3.text_input("CEP", placeholder="00000-000")
    l3_c1, l3_c2, l3_c3 = st.columns([1, 1.5, 1])
    whatsapp = l3_c1.text_input("🟢 WhatsApp", value="21980264217")
    email_cli = l3_c2.text_input("✉️ E-mail")
    data_visita = l3_c3.date_input("Data da Visita", value=date.today())
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    col_ev1, col_ev2 = st.columns(2)
    mod_evap = col_ev1.text_input("Modelo Unidade Evaporadora")
    serie_evap = col_ev2.text_input("Nº de Série Evaporadora")
    col_cd1, col_cd2 = st.columns(2)
    mod_cond = col_cd1.text_input("Modelo Unidade Condensadora")
    serie_cond = col_cd2.text_input("Nº de Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão da Rede (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    lra_comp = e2.number_input("LRA (A)", value=0.0)
    rla_comp = e2.number_input("RLA (A)", value=0.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)
    diff_v = round(v_rede - v_med, 1)
    diff_a = round(rla_comp - a_med, 1)
    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Queda de Tensão", f"{diff_v} V", delta=f"-{diff_v}V", delta_color="inverse")
    res2.metric("Folga Corrente (RLA-Med)", f"{diff_a} A")
    res3.metric("Carga Motor", f"{round((a_med/rla_comp*100),1) if rla_comp > 0 else 0}%")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = col3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = col3.number_input("Temp. Ar Insufl. (°C)", value=12.0)
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)
    st.markdown("---")
    ct1, ct2 = st.columns(2)
    with ct1:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #ffcc00;color:white;'><b>🌡️ T-Sat Sucção:</b><h2 style='margin:0;color:white;'>{tsat_suc} °C</h2><b>🔥 Superaquecimento (SH):</b><h2 style='margin:0;color:white;'>{sh} K</h2></div>""", unsafe_allow_html=True)
    with ct2:
        st.markdown(f"""<div style='background-color:#004a99;padding:15px;border-radius:10px;border-left:5px solid #00d2ff;color:white;'><b>❄️ T-Sat Líquido:</b><h2 style='margin:0;color:white;'>{tsat_liq} °C</h2><b>💧 Sub-resfriamento (SC):</b><h2 style='margin:0;color:white;'>{sc} K</h2></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='background-color:#004a99;padding:20px;border-radius:15px;text-align:center;margin-top:10px;border:2px solid #ffcc00;'><span style='color:white;font-weight:bold;'>📈 Diferencial de Temperatura (ΔT)</span><h1 style='margin:0;color:white;font-size:45px;'>{dt} K</h1></div>""", unsafe_allow_html=True)

with tab_diag:
    st.subheader("🤖 Diagnóstico e Recomendações")
    obs = st.text_area("Observações Técnicas Detalhadas", height=100)
    medidas_tomadas = st.text_area("🔧 Medidas Técnicas Tomadas", height=100)

    st.markdown("### 🔧 Medidas Técnicas Propostas pela IA")
    col_ia_1, col_ia_2 = st.columns(2)
    
    diag_termo = []
    diag_eletr = []
    obs_low = obs.lower()
    
    if any(x in obs_low for x in ["óleo", "mancha", "vazamento"]):
        if sh > 12: diag_termo.append("🚨 [MEDIDA]: Vazamento confirmado. Localizar fuga com N2 e refazer carga por massa.")
        else: diag_termo.append("⚠️ [MEDIDA]: Presença de óleo relatada. Verificar estanqueidade das flanges.")
    if any(x in obs_low for x in ["gelo", "congelando"]):
        if sc > 10: diag_termo.append("⚙️ [MEDIDA]: Restrição na expansão. Substituir filtro secador ou capilar.")
        elif sh < 5: diag_termo.append("❄️ [MEDIDA]: Inundação do evaporador. Higienizar serpentinas e testar ventilador.")
    
    if sh < 6: diag_termo.append(f"🌡️ [SH CRÍTICO]: {sh}K. Risco de golpe de líquido.")
    if diff_v > (v_rede * 0.05): diag_eletr.append(f"⚡ [QUEDA TENSÃO]: {diff_v}V excedida.")

    with col_ia_1:
        st.info("**🌡️ Ciclo Frigorífico**")
        txt_termo = "\n".join(diag_termo) if diag_termo else "✅ Sem anomalias térmicas."
        st.write(txt_termo)

    with col_ia_2:
        st.info("**⚡ Parte Elétrica**")
        txt_eletr = "\n".join(diag_eletr) if diag_eletr else "✅ Sem anomalias elétricas."
        st.write(txt_eletr)

    medidas_ia_pdf = f"TERMODINAMICA:\n{txt_termo}\n\nELETRICA:\n{txt_eletr}"
    
    # --- GERAÇÃO DE PDF PROFISSIONAL COMPLETO ---
    if st.button("Gerar Relatório PDF Profissional"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_line_width(0.5)
        
        def fix_text(t):
            if t is None: return ""
            subst = {"🚨": "!!", "⚠️": "!", "⚙️": "*", "⚡": ">>", "🔥": "!!", "❌": "X", "✅": "OK", "❄️": "*", "🌡️": "T", "📋": "-", "🤖": "IA", "🔧": "CORRECAO:"}
            t = str(t)
            for k, v in subst.items(): t = t.replace(k, v)
            return t.encode('latin-1', 'ignore').decode('latin-1')

        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 33)
            pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 16); pdf.set_text_color(40, 40, 40)
        pdf.cell(190, 10, fix_text("LAUDO TÉCNICO DE ENGENHARIA"), ln=True, align="R")
        pdf.set_draw_color(40, 40, 40); pdf.line(10, 32, 200, 32); pdf.ln(8)

        # 1. IDENTIFICAÇÃO COMPLETA
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 1. DADOS DO CLIENTE E LOCALIDADE"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(95, 7, fix_text(f"Cliente: {cliente}"), border=1); pdf.cell(95, 7, fix_text(f"CPF/CNPJ: {doc_cliente}"), border=1, ln=True)
        pdf.cell(190, 7, fix_text(f"Endereço: {endereco}, {bairro} - CEP: {cep}"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"WhatsApp: {whatsapp}"), border=1); pdf.cell(95, 7, fix_text(f"E-mail: {email_cli}"), border=1, ln=True)
        pdf.cell(190, 7, fix_text(f"Data: {data_visita}"), border=1, ln=True); pdf.ln(3)

        # 2. ESPECIFICAÇÕES DO EQUIPAMENTO
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 2. ESPECIFICAÇÕES DO EQUIPAMENTO"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(63.3, 7, fix_text(f"Fab: {fabricante}"), border=1); pdf.cell(63.3, 7, fix_text(f"Lin: {linha}"), border=1); pdf.cell(63.4, 7, fix_text(f"Tec: {tecnologia}"), border=1, ln=True)
        pdf.cell(63.3, 7, fix_text(f"Tipo: {tipo_eq}"), border=1); pdf.cell(63.3, 7, fix_text(f"Flu: {fluido}"), border=1); pdf.cell(63.4, 7, fix_text(f"Cap: {cap_digitada}"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"Mod. Evap: {mod_evap}"), border=1); pdf.cell(95, 7, fix_text(f"Série Evap: {serie_evap}"), border=1, ln=True)
        pdf.cell(95, 7, fix_text(f"Mod. Cond: {mod_cond}"), border=1); pdf.cell(95, 7, fix_text(f"Série Cond: {serie_cond}"), border=1, ln=True); pdf.ln(3)

        # 3. PARÂMETROS ELÉTRICOS
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 3. GRANDEZAS ELÉTRICAS"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(47.5, 7, fix_text(f"V.Rede: {v_rede}V"), 1); pdf.cell(47.5, 7, fix_text(f"V.Med: {v_med}V"), 1); pdf.cell(47.5, 7, fix_text(f"LRA: {lra_comp}A"), 1); pdf.cell(47.5, 7, fix_text(f"RLA: {rla_comp}A"), 1, ln=True)
        pdf.cell(95, 7, fix_text(f"Corrente Med: {a_med}A"), 1); pdf.cell(95, 7, fix_text(f"Queda: {diff_v}V"), 1, ln=True); pdf.ln(3)

        # 4. TERMODINÂMICA (PRECISÃO PERICIAL)
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 4. CICLO FRIGORÍFICO (TERMOMETRIA)"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(31.6, 7, "P.SUC", 1, 0, 'C'); pdf.cell(31.6, 7, "P.LIQ", 1, 0, 'C'); pdf.cell(31.6, 7, "T.SUC", 1, 0, 'C'); pdf.cell(31.6, 7, "T.LIQ", 1, 0, 'C'); pdf.cell(31.6, 7, "SH(K)", 1, 0, 'C'); pdf.cell(32, 7, "SC(K)", 1, 1, 'C')
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(31.6, 7, f"{p_suc}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{p_liq}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{t_suc_tubo}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{t_liq_tubo}", 1, 0, 'C'); pdf.cell(31.6, 7, f"{sh}", 1, 0, 'C'); pdf.cell(32, 7, f"{sc}", 1, 1, 'C')
        pdf.cell(63.3, 7, fix_text(f"Ar Retorno: {t_ret}C"), 1); pdf.cell(63.3, 7, fix_text(f"Ar Insufl: {t_ins}C"), 1); pdf.cell(63.4, 7, fix_text(f"Delta T: {dt}K"), 1, ln=True); pdf.ln(3)

        # 5. DIAGNÓSTICO E OBSERVAÇÕES
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 8, fix_text(" 5. PARECER TÉCNICO E PROVIDÊNCIAS"), ln=True, fill=True, border=1)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Propostas (IA):"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_ia_pdf), border='LRB'); pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Obs Detalhadas Campo:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(obs), border='LRB'); pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, fix_text("> Medidas Tomadas Local:"), ln=True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(190, 5, fix_text(medidas_tomadas), border='LRB')

        pdf.ln(15); pdf.line(60, pdf.get_y(), 130, pdf.get_y())
        pdf.set_font("Helvetica", "I", 8); pdf.cell(190, 5, fix_text("Assinatura do Responsável Técnico"), ln=True, align="C")

        pdf_output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str): pdf_content = pdf_content.encode('latin-1', 'replace')
        pdf_output.write(pdf_content)
        st.download_button(label="📥 Baixar Laudo Profissional", data=pdf_output.getvalue(), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")
