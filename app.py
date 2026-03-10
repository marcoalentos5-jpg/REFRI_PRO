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
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Dados do Cliente & Contato")
    
    # 1ª LINHA: Nome, Endereço, Bairro e CPF lado a lado
    l1_c1, l1_c2, l1_c3, l1_c4 = st.columns([2, 2, 1.5, 1.5])
    cliente = l1_c1.text_input("Nome do Cliente / Empresa")
    endereco = l1_c2.text_input("Endereço (Rua e Número)")
    bairro = l1_c3.text_input("Bairro")
    doc_cliente = l1_c4.text_input("CPF / CNPJ")
    
    # 2ª LINHA: WhatsApp, CEP, Data e E-mail
    l2_c1, l2_c2, l2_c3, l2_c4 = st.columns(4)
    # Reduzindo visualmente o campo WhatsApp e CEP
    col_zap, _ = l2_c1.columns([0.8, 0.2])
    whatsapp = col_zap.text_input("🟢 WhatsApp", value="21980264217")
    
    col_cep, _ = l2_c2.columns([0.8, 0.2])
    cep = col_cep.text_input("CEP", placeholder="00000-000")
    
    data_visita = l2_c3.date_input("Data da Visita", value=date.today())
    email_cli = l2_c4.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Fabricante (Marca)")
    linha = d1.text_input("Linha")
    tecnologia = d2.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off"])
    tipo_eq = d2.selectbox("Tipo de Sistema", ["Split Hi-Wall", "Cassete", "Piso-Teto", "VRF", "Chiller"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])
    cap_digitada = d3.text_input("Capacidade (Mil BTU´s)")
    
    col_evap1, col_evap2 = st.columns(2)
    mod_evap = col_evap1.text_input("Modelo Unidade Evaporadora")
    serie_evap = col_evap2.text_input("Nº de Série Evaporadora")
    
    col_cond1, col_cond2 = st.columns(2)
    mod_cond = col_cond1.text_input("Modelo Unidade Condensadora")
    serie_cond = col_cond2.text_input("Nº de Série Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    v_med = st.number_input("Tensão Medida (V)", value=0.0)
    a_med = st.number_input("Corrente Medida (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2 = st.columns(2)
    p_suc = col1.number_input("Pressão de Sucção (PSIG)", value=118.0)
    t_suc_tubo = col1.number_input("Temp. do Tubo de Sucção (°C)", value=12.0)
    p_liq = col2.number_input("Pressão de Descarga (PSIG)", value=345.0)
    t_liq_tubo = col2.number_input("Temp. do Tubo de Líquido (°C)", value=30.0)
    t_ret = col1.number_input("Temp. do Ar de Retorno (°C)", value=24.0)
    t_ins = col2.number_input("Temp. do Ar de Insuflamento (°C)", value=12.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)
    
    st.markdown("---")
    # DESTAQUE COM FONTE GRANDE E SÍMBOLO Δ
    st.markdown(f"### Temperatura de Saturação (Sucção): {tsat_suc} °C")
    st.markdown(f"### Superaquecimento (SH): {sh} K")
    st.markdown(f"### Temperatura de Saturação (Líquido): {tsat_liq} °C")
    st.markdown(f"### Sub-resfriamento (SC): {sc} K")
    st.markdown(f"### Diferencial de Temperatura (ΔT): {dt} K")

with tab_diag:
    obs = st.text_area("Observações Técnicas Detalhadas", height=150)
    
    if st.button("Gerar Relatório PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_font("Helvetica", "B", 14)
        if os.path.exists("logo.png"):
            pdf.image("logo.png", 10, 8, 22)
            pdf.set_x(10)
        
        pdf.set_text_color(0, 74, 153)
        pdf.cell(190, 10, "RELATÓRIO TÉCNICO", ln=True, align="C")
        pdf.ln(5)
        
        # 1. Identificação
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(60)
        pdf.cell(190, 7, " 1. IDENTIFICAÇÃO DO CLIENTE", ln=True, fill=True)
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(190, 6, f"CPF/CNPJ DO CLIENTE: {doc_cliente}", border="B", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(135, 7, f"Cliente: {cliente}", border="B") 
        
        pdf.set_font("Helvetica", "B", 8); pdf.set_fill_color(235, 235, 235)
        pdf.cell(55, 7, f" DATA DA VISITA: {data_visita.strftime('%d/%m/%Y')} ", border=1, fill=True, align="C", ln=True)
        
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(190, 6, f"Endereço: {endereco} - Bairro: {bairro}", border="B", ln=True)
        pdf.cell(63, 6, f"CEP: {cep}", border="B")
        pdf.cell(63, 6, f"WhatsApp: {whatsapp}", border="B")
        pdf.cell(64, 6, f"E-mail: {email_cli}", border="B", ln=True)

        # 2. Equipamento
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, " 2. DADOS DO EQUIPAMENTO", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(63, 6, f"Fabricante: {fabricante}", border="B")
        pdf.cell(63, 6, f"Linha: {linha}", border="B")
        pdf.cell(64, 6, f"Capacidade: {cap_digitada} Mil BTU's", border="B", ln=True)
        
        pdf.cell(95, 6, f"Mod. Evaporadora: {mod_evap}", border="B")
        pdf.cell(95, 6, f"Série Evaporadora: {serie_evap}", border="B", ln=True)
        pdf.cell(95, 6, f"Mod. Condensadora: {mod_cond}", border="B")
        pdf.cell(95, 6, f"Série Condensadora: {serie_cond}", border="B", ln=True)
        
        pdf.cell(63, 6, f"Tecnologia: {tecnologia}", border="B")
        pdf.cell(63, 6, f"Tipo: {tipo_eq}", border="B")
        pdf.cell(64, 6, f"Gás: {fluido}", border="B", ln=True)

        # 3. Medições
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, " 3. ANÁLISE TÉCNICA E MEDIÇÕES", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(47, 6, f"Pressão Sucção: {p_suc} PSI", border="B")
        pdf.cell(47, 6, f"T-Sat Sucção: {tsat_suc} C", border="B")
        pdf.cell(48, 6, f"Pressão Líquido: {p_liq} PSI", border="B")
        pdf.cell(48, 6, f"T-Sat Líquido: {tsat_liq} C", border="B", ln=True)
        pdf.cell(47, 6, f"T. Tubo Suc: {t_suc_tubo} C", border="B")
        pdf.cell(47, 6, f"T. Tubo Liq: {t_liq_tubo} C", border="B")
        pdf.cell(48, 6, f"Tensão: {v_med} V", border="B")
        pdf.cell(48, 6, f"Corrente: {a_med} A", border="B", ln=True)
        pdf.cell(47, 6, f"T. Ar Retorno: {t_ret} C", border="B")
        pdf.cell(47, 6, f"T. Ar Insufl.: {t_ins} C", border="B")
        
        # Linha de resultados (LAYOUT MANTIDO)
        pdf.set_font("Helvetica", "B", 8); pdf.set_fill_color(248, 248, 248)
        pdf.cell(32, 6, f" SH: {sh} K", border="B", fill=True)
        pdf.cell(32, 6, f" SC: {sc} K", border="B", fill=True)
        # Escrita segura para evitar erro de Unicode e manter layout
        pdf.cell(32, 6, f" Delta T: {dt} K", border="B", fill=True, ln=True)

        # 4. Diagnóstico
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(190, 7, " 4. DIAGNÓSTICO E OBSERVAÇÕES", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(190, 5, obs if obs else "Equipamento operando conforme especificações.", border=1)

        # Rodapé
        pdf.ln(12)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(190, 4, "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO", ln=True, align="C")
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(190, 4, "CNPJ: 51.274.762/0001-17", ln=True, align="C")

        # Conversão PDF
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        st.download_button(label="📥 Baixar Relatório", data=io.BytesIO(pdf_bytes), file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
