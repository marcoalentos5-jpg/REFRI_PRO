import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL MPN ---
st.set_page_config(page_title="MPN Refrigeração | Diagnóstico Pro", layout="wide", page_icon="❄️")

# CSS para aplicar as cores da marca (Azul Royal e Prata)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #004A99; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .stMetric { background-color: #ffffff; border-left: 5px solid #004A99; border-radius: 5px; }
    h1, h2, h3 { color: #004A99; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ENGENHARIA (PxT) ---
def calcular_t_sat(psi, gas):
    if psi is None or not gas: return None
    if gas == "R-410A": return (psi * 0.165) - 34.5
    if gas == "R-22": return (psi * 0.27) - 38.5
    if gas == "R-134a": return (psi * 0.44) - 36.0
    if gas == "R-32": return (psi * 0.171) - 36.2
    return None

# --- GERADOR DE PDF MPN ---
def gerar_pdf_mpn(dados, diag):
    pdf = FPDF()
    pdf.add_page()
    # Título do Relatório
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 74, 153) # Azul Royal MPN
    pdf.cell(200, 15, "MPN REFRIGERACAO E CLIMATIZACAO", ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(5)
    
    # Seções do Relatório
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(0, 0, 0)
    
    # 1. Identificação
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, " 1. IDENTIFICACAO DO CLIENTE E TECNICO", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Cliente: {dados['Cliente']}", ln=True)
    pdf.cell(0, 7, f"Tecnico: {dados['Tecnico']}", ln=True)
    pdf.ln(2)

    # 2. Equipamento
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, " 2. ESPECIFICACOES DO EQUIPAMENTO", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Fabricante: {dados['Fabricante']} | Linha: {dados['Linha']}", ln=True)
    pdf.cell(0, 7, f"Modelo: {dados['Modelo']} | Serie: {dados['Serie']}", ln=True)
    pdf.cell(0, 7, f"Tensao: {dados['Tensao']} | Gas: {dados['Gas']}", ln=True)
    pdf.ln(2)

    # 3. Medições
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, " 3. MEDICOES TECNICAS DE CAMPO", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Delta T (Troca Termica): {dados['DeltaT']} C", ln=True)
    pdf.cell(0, 7, f"Pressao de Succao (Valvula): {dados['Pressao']} PSI", ln=True)
    pdf.cell(0, 7, f"Temperatura de Saturacao: {dados['TempSat']} C", ln=True)
    pdf.cell(0, 7, f"Temperatura Final (Linha): {dados['TempFinal']} C", ln=True)
    pdf.cell(0, 7, f"SUPERAQUECIMENTO (SH): {dados['SH']} K", ln=True)
    pdf.cell(0, 7, f"Corrente Medida: {dados['I_Medida']} A (RLA: {dados['RLA']} A / LRA: {dados['LRA']} A)", ln=True)
    pdf.ln(2)

    # 4. Parecer
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, " 4. PARECER TECNICO FINAL", ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    for msg in diag:
        pdf.multi_cell(0, 7, f"* {msg}")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE MPN ---
st.title("❄️ MPN: Engenharia & Diagnóstico")
st.write("---")

# 1. IDENTIFICAÇÃO (CAMPOS VAZIOS)
with st.container():
    st.subheader("👤 Identificação")
    c1, c2, c3 = st.columns(3)
    cliente = c1.text_input("Cliente", placeholder="Nome/Empresa", value="")
    tecnico = c2.text_input("Técnico Responsável", placeholder="Seu Nome", value="")
    fabricante = c3.text_input("Fabricante", placeholder="Ex: Daikin", value="")

    c4, c5, c6 = st.columns(3)
    linha = c4.text_input("Linha", placeholder="Ex: Inverter", value="")
    modelo_eq = c5.text_input("Modelo", placeholder="Código Etiqueta", value="")
    serie_eq = c6.text_input("Série", placeholder="S/N", value="")

# 2. SETUP TÉCNICO (SIDEBAR)
st.sidebar.header("⚙️ Configuração")
tipo_eq = st.sidebar.selectbox("Equipamento", ["", "Split Hi-Wall", "K-7", "Piso-Teto", "ACJ", "Geladeira"])
tecnologia = st.sidebar.radio("Tecnologia", ["ON-OFF", "Inverter"])
gas_eq = st.sidebar.selectbox("Fluido Gás", ["", "R-410A", "R-22", "R-134a", "R-32"])
tensao_eq = st.sidebar.selectbox("Tensão", ["", "110V", "220V", "380V"])

# 3. MEDIÇÕES DE CAMPO (CAMPOS VAZIOS)
st.subheader("🛠️ Coleta de Dados Termodinâmicos")
m1, m2, m3 = st.columns(3)

with m1:
    st.info("🌬️ Troca Térmica")
    t_ret = st.number_input("Temp. Retorno (Entrada) [°C]", value=None)
    t_ins = st.number_input("Temp. Insuflação (Saída) [°C]", value=None)
    dt = t_ret - t_ins if (t_ret is not None and t_ins is not None) else None
    st.metric("DELTA T", f"{dt:.1f} °C" if dt is not None else "--")

with m2:
    st.info("🧪 Ciclo do Fluido")
    p_suc = st.number_input("Pressão de Sucção (PSI)", value=None)
    t_fin = st.number_input("Temperatura Final [°C]", value=None)
    
    tsat = calcular_t_sat(p_suc, gas_eq)
    # CORREÇÃO DO ERRO ANTERIOR: Variáveis agora batem (t_fin e tsat)
    sh = t_fin - tsat if (t_fin is not None and tsat is not None) else None
    
    if tsat is not None: st.caption(f"Saturação: {tsat:.1f} °C")
    st.metric("SUPER AQUECIMENTO", f"{sh:.1f} K" if sh is not None else "--")

with m3:
    st.info("⚡ Elétrica")
    v_rla = st.number_input("Corrente RLA [A]", value=None)
    v_lra = st.number_input("Corrente LRA [A]", value=None)
    v_med = st.number_input("Corrente Medida [A]", value=None)
    st.metric("AMPERAGEM", f"{v_med:.1f} A" if v_med is not None else "--")

# --- PROCESSAMENTO E PDF ---
if st.button("🚀 EXECUTAR DIAGNÓSTICO MASTER"):
    if None in [t_ret, t_ins, p_suc, t_fin, v_rla, v_med]:
        st.warning("⚠️ Atenção: Preencha todos os campos técnicos para análise.")
    else:
        st.divider()
        # Lógica de Diagnóstico Cruzado (Especialistas + Manuais)
        diag_final = []
        if dt < 8: diag_final.append("Baixa troca termica. Verifique carga ou serpentina suja.")
        if dt > 15: diag_final.append("Alta restricao de ar. Verifique filtros ou turbina.")
        if sh < 5: diag_final.append("🚨 RISCO DE GOLPE DE LIQUIDO. Superaquecimento muito baixo.")
        if sh > 12: diag_final.append("Falta de fluido refrigerante detectada (SH Alto).")
        if v_med > v_rla * 1.1: diag_final.append("Sobrecorrente eletrica. Verifique limpeza externa.")
        
        if not diag_final: diag_final.append("Equipamento operando em perfeito estado conforme manuais.")

        st.subheader("📋 Parecer Técnico")
        for d in diag_final: st.write(f"- {d}")

        # Preparar dados PDF
        dados_resumo = {
            "Cliente": cliente, "Tecnico": tecnico, "Fabricante": fabricante, "Linha": linha,
            "Modelo": modelo_eq, "Serie": serie_eq, "Tensao": tensao_eq, "Gas": gas_eq,
            "DeltaT": f"{dt:.1f}", "Pressao": f"{p_suc}", "TempSat": f"{tsat:.1f}",
            "TempFinal": f"{t_fin}", "SH": f"{sh:.1f}", "RLA": v_rla, "LRA": v_lra, "I_Medida": v_med
        }
        
        pdf_bytes = gerar_pdf_mpn(dados_resumo, diag_final)
        st.download_button("📥 Baixar Relatório PDF MPN", data=pdf_bytes, file_name=f"MPN_{cliente}.pdf", mime="application/pdf")
