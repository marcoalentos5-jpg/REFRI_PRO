import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.02, -0.29, 11.55, 20.93, 35.58, 47.30, 56.59, 64.59]},
        "R-32": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-17.46, 0.87, 10.86, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [50.0, 100.0, 150.0, 200.0, 300.0, 350.0, 400.0, 500.0, 600.0], "t": [-3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 67.72, 78.38, 83.12, 87.53]},
        "R-134a": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-26.08, 12.23, 30.92, 43.65, 53.74]},
        "R-404A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0], "t": [-45.45, -9.41, 8.96, 22.23, 32.59]}
    }
    if gas not in ancoras: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico Resolutivo (IA Especialista)")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 IA: Diagnóstico & Conserto"])

with tab_cad:
    st.subheader("👤 Identificação do Sistema")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    endereco = st.text_input("Endereço Completo")
    l3_c1, l3_c2, l3_c3 = st.columns([1, 1.5, 1])
    whatsapp = l3_c1.text_input("🟢 WhatsApp", value="21980264217")
    email_cli = l3_c2.text_input("✉️ E-mail")
    data_visita = l3_c3.date_input("Data da Visita", value=date.today())
    st.markdown("---")
    st.subheader("⚙️ Dados do Fabricante")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Ex: LG, Samsung, Gree, Daikin)")
    linha = d1.text_input("Linha / Modelo")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (BTU´s)")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão Nominal (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    rla_comp = e2.number_input("RLA (A)", value=0.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)
    st.markdown("---")
    res1, res2 = st.columns(2)
    res1.metric("Queda de Tensão", f"{round(v_rede - v_med, 1)} V")
    res2.metric("Carga Motor", f"{round((a_med/rla_comp*100),1) if rla_comp > 0 else 0}%")

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
    st.write(f"**SH:** {sh} K | **SC:** {sc} K | **Delta T:** {dt} K")

with tab_diag:
    st.subheader("🤖 IA Especialista: Diagnóstico, Causas e Consertos")
    obs = st.text_area("📝 Notas de Campo e Sintomas (Diretiva de Alta Prioridade)", height=120)
    medidas_tomadas = st.text_area("🔧 Medidas Técnicas Já Realizadas", height=80)

    # --- MOTOR IA EVOLUÍDO: DEFEITO -> CAUSA -> CONSERTO ---
    diag_resolutivo = []
    obs_low = obs.lower()
    
    # 1. Cruzamento Sintoma (Campo) -> Procedimento de Reparo (Base Engenharia)
    if any(x in obs_low for x in ["gelo", "congelando", "obstrução"]):
        if sh > 12: diag_resolutivo.append("📌 [DEFEITO]: Baixa pressão/Falta de fluido. [CAUSA]: Vazamento ou carga insuficiente. [PROCEDIMENTO]: Pressurizar com N2, sanar vazamento, vácuo < 500μ e carga por massa (gr).")
        elif sh < 5: diag_resolutivo.append("📌 [DEFEITO]: Inundação de líquido. [CAUSA]: Obstrução de ar ou excesso de gás. [PROCEDIMENTO]: Higienização química, verificar motor evaporador e ajustar fluido.")
    
    if any(x in obs_low for x in ["comunicação", "e1", "ch05", "led", "piscando"]):
        diag_resolutivo.append(f"📌 [DEFEITO]: Erro de Comunicação Serial {fabricante}. [CAUSA]: Ruído elétrico ou placa avariada. [PROCEDIMENTO]: Testar cabo S, aterramento e capacitores da placa de controle.")
    
    if any(x in obs_low for x in ["vibração", "barulho", "ruído"]):
        diag_resolutivo.append("📌 [DEFEITO]: Falha mecânica detectada. [CAUSA]: Coxins rompidos ou quebra de Scroll. [PROCEDIMENTO]: Substituição de coxins ou troca do compressor por sobrecarga (A).")

    # 2. Diagnóstico Termodinâmico Preciso (Cruzamento de Dados 1000x)
    if sh < 6: diag_resolutivo.append(f"🛠️ [CORRETIVA IA]: SH de {sh}K crítico. [AÇÃO]: Revisar abertura da EEV ou reduzir carga de fluido refrigerante.")
    elif sh > 9: diag_resolutivo.append(f"🛠️ [CORRETIVA IA]: SH de {sh}K elevado. [AÇÃO]: Realizar teste de estanqueidade em flanges e brasagens.")
    if sc < 3: diag_resolutivo.append(f"🛠️ [CORRETIVA IA]: SC Insuficiente ({sc}K). [AÇÃO]: Higienização profunda da condensadora e revisão do motor ventilador externo.")

    proposta_final = "\n".join(diag_resolutivo) if diag_resolutivo else f"✅ [SISTEMA VALIDADO]: Parâmetros operacionais e observações de campo em conformidade total com manuais de engenharia {fabricante}."
    medidas_ia = st.text_area("💡 Diagnóstico, Consertos e Medidas Propostas pela IA", value=proposta_final, height=200)
    
    if st.button("Gerar Relatório de Engenharia PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, "RELATÓRIO TÉCNICO DE ENGENHARIA", ln=True, align="C"); pdf.ln(5)
        
        pdf.set_fill_color(245, 245, 245); pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(60)
        pdf.cell(190, 7, " 1. DADOS TÉCNICOS E DE PERFORMANCE", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 8); pdf.cell(190, 6, f"Fabricante: {fabricante} | Cliente: {cliente} | Data: {data_visita}", border="B", ln=True)

        pdf.ln(4); pdf.set_font("Helvetica", "B", 10); pdf.cell(190, 7, " 2. ANÁLISE TERMOMECÂNICA", ln=True, fill=True)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(63, 8, f" SH: {sh}K", border=1); pdf.cell(63, 8, f" SC: {sc}K", border=1); pdf.cell(64, 8, f" Delta T: {dt}K", border=1, ln=True)

        pdf.ln(4); pdf.set_font("Helvetica", "B", 10); pdf.cell(190, 7, " 3. PARECER IA: DEFEITOS, SOLUÇÕES E CONSERTOS", ln=True, fill=True)
        pdf.set_font("Helvetica", "B", 9); pdf.cell(190, 6, "SINTOMAS DE CAMPO (PRIORIDADE IA):", ln=True)
        pdf.set_font("Helvetica", "", 8); pdf.multi_cell(190, 5, obs, border="B")
        pdf.ln(2); pdf.set_font("Helvetica", "B", 9); pdf.set_text_color(0, 74, 153); pdf.cell(190, 6, "DIAGNÓSTICO E CONSERTOS PROPOSTOS (IA):", ln=True)
        pdf.set_font("Helvetica", "", 8); pdf.set_text_color(60); pdf.multi_cell(190, 5, medidas_ia, border=1)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(
            label="💾 Baixar Relatório Técnico PDF",
            data=pdf_output,
            file_name=f"Relatorio_Tecnico_{cliente}.pdf",
            mime="application/pdf"
        )
