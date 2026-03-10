import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF
import io
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

# --- 2. BASE DE CÓDIGOS DE ERRO ---
DB_ERROS = {
    "LG": {"CH05": "Falha de comunicação entre UI e UE.", "CH02": "Sensor de evaporadora aberto/curto.", "CH61": "Superaquecimento da condensadora."},
    "Samsung": {"E101": "Erro de comunicação (UI/UE).", "E121": "Erro no sensor de temperatura UI.", "E464": "Sobrecorrente no compressor (IPM)."},
    "Daikin": {"U4": "Erro de transmissão entre unidades.", "A6": "Bloqueio do motor do ventilador UI.", "E5": "Erro de partida do compressor."},
    "Midea/Carrier": {"E1": "Erro de comunicação.", "EL": "Vazamento de fluido detectado.", "PC04": "Erro no módulo inversor."},
    "Gree": {"E6": "Falha de comunicação.", "H3": "Sobrecarga do compressor.", "F1": "Erro no sensor ambiente."},
    "Fujitsu": {"00:11": "Erro de comunicação.", "00:0F": "Erro no sensor de descarga.", "00:16": "Erro no sensor de pressão."}
}

# --- 3. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
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

# --- 4. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    l2_c1, l2_c2, l2_c3 = st.columns(3)
    endereco = l2_c1.text_input("Endereço")
    bairro = l2_c2.text_input("Bairro")
    cep = l2_c3.text_input("CEP")
    l3_c1, l3_c2, l3_c3 = st.columns([1, 1.5, 1])
    whatsapp = l3_c1.text_input("WhatsApp", value="21980264217")
    email_cli = l3_c2.text_input("E-mail")
    data_visita = l3_c3.date_input("Data", value=date.today())
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.selectbox("Fabricante", ["LG", "Samsung", "Daikin", "Midea/Carrier", "Gree", "Fujitsu", "Outros"])
    linha = d1.text_input("Linha")
    local_eq = d1.text_input("Localização / Setor")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (BTU)", value="0")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2 = st.columns(2)
    v_rede = e1.number_input("Tensão Rede (V)", value=220.0)
    v_med = e1.number_input("Tensão Medida (V)", value=218.0)
    rla_comp = e2.number_input("RLA (A)", value=1.0)
    a_med = e2.number_input("Corrente Medida (A)", value=0.0)
    diff_v = round(v_rede - v_med, 1)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão Líquido (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (°C)", value=30.0)
    t_ret = col3.number_input("Temp. Ar Retorno (°C)", value=24.0)
    t_ins = col3.number_input("Temp. Ar Insufl. (°C)", value=12.0)
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)

with tab_diag:
    st.subheader("🔍 Códigos de Erro & Diagnóstico")
    codigo_input = st.text_input("Digite o Código de Erro").upper()
    desc_erro = DB_ERROS.get(fabricante, {}).get(codigo_input, "Código não catalogado.") if codigo_input else ""
    
    alertas = []
    if sh > 12 and sc < 3: alertas.append("Causa: Falta de fluido (SH Alto / SC Baixo).")
    elif sh < 5 and sc > 12: alertas.append("Causa: Excesso de fluido (SH Baixo / SC Alto).")
    if dt < 8: alertas.append("Causa: Baixa troca térmica (Delta T insuficiente).")
    if a_med > rla_comp: alertas.append(f"Causa: Sobrecarga elétrica ({a_med}A > {rla_comp}A).")
    
    ia_raw = st.text_area("Diagnóstico Final", value=f"{' | '.join(alertas) if alertas else 'Parâmetros Normais.'}\nErro Painel: {desc_erro}")

    st.markdown("---")
    if st.button("📄 Gerar Relatório Profissional"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(0, 74, 153)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 16)
        
        def clean_pdf(txt):
            return str(txt).encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(0, 15, clean_pdf("RELATORIO TECNICO PERICIAL"), ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 11)
        pdf.ln(25)
        pdf.cell(0, 8, clean_pdf(f"CLIENTE: {cliente}"), ln=True)
        pdf.cell(0, 8, clean_pdf(f"LOCALIZACAO: {local_eq}"), ln=True)
        pdf.cell(0, 8, clean_pdf(f"EQUIPAMENTO: {fabricante} {cap_digitada} BTU"), ln=True)
        pdf.ln(5)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 8, clean_pdf(f"DIAGNOSTICO:\n{ia_raw}"))
        
        pdf_output = pdf.output()
        pdf_bytes = bytes(pdf_output) if not isinstance(pdf_output, str) else pdf_output.encode('latin-1', 'replace')

        st.download_button(
            label="⬇️ Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"Laudo_{cliente if cliente else 'Tecnico'}.pdf",
            mime="application/pdf"
        )
