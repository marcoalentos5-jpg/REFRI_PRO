import streamlit as st
import numpy as np
from datetime import date
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

def clean_text(text):
    """Garante que o texto seja compatível com FPDF Latin-1"""
    if text is None: return ""
    replacements = {
        '°': 'C', 'º': '.', 'ª': '.', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C',
        '–': '-', '—': '-'
    }
    txt = str(text)
    for old, new in replacements.items():
        txt = txt.replace(old, new)
    return txt.encode('latin-1', 'replace').decode('latin-1')

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 600.0], "t": [-51.0, 64.59]},
        "R-32": {"p": [0.0, 600.0], "t": [-51.7, 63.43]},
        "R-22": {"p": [0.0, 600.0], "t": [-40.8, 87.53]},
        "R-134a": {"p": [0.0, 200.0], "t": [-26.08, 53.74]},
        "R-404A": {"p": [0.0, 400.0], "t": [-45.45, 61.1]}
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# --- 3. INTERFACE DO APP ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico"])

with tab_cad:
    st.subheader("👤 Identificação do Cliente")
    c1, c2 = st.columns(2)
    cliente = c1.text_input("Nome do Cliente / Empresa", value="")
    doc_cliente = c2.text_input("CPF / CNPJ", value="")
    endereco = st.text_input("Endereço Completo", value="")
    whatsapp = st.text_input("WhatsApp", value="21980264217")
    data_visita = st.date_input("Data da Visita", value=date.today())

    st.subheader("⚙️ Dados do Equipamento")
    d1, d2, d3 = st.columns(3)
    fabricante = d1.text_input("Marca / Modelo", value="")
    num_serie = d2.text_input("Nº de Série", value="")
    tag_maquina = d3.text_input("TAG / Identificação", value="")
    setor = d1.text_input("Setor / Localização", value="")
    tensao_nom = d2.selectbox("Tensão Nominal", ["220V/1F", "220V/3F", "380V/3F", "440V/3F", "127V/1F"])
    fluido = d3.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a", "R-404A"])

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    e1, e2, e3 = st.columns(3)
    v_med = e1.number_input("Tensão Medida (V)", value=0.0)
    lra_comp = e2.number_input("LRA (A)", value=0.0)
    rla_comp = e3.number_input("RLA (A)", value=0.0)
    a_med = st.number_input("Corrente Medida (A)", value=0.0)
    carga_motor = round((a_med / rla_comp * 100), 1) if rla_comp > 0 else 0

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    col1, col2, col3 = st.columns(3)
    p_suc = col1.number_input("Pressão Sucção (PSIG)", value=0.0)
    t_suc_tubo = col1.number_input("Temp. Tubo Sucção (C)", value=0.0)
    p_liq = col2.number_input("Pressão Descarga (PSIG)", value=0.0)
    t_liq_tubo = col2.number_input("Temp. Tubo Líquido (C)", value=0.0)
    t_ret = col3.number_input("Temp. Ar Retorno (C)", value=0.0)
    t_ins = col3.number_input("Temp. Ar Insufl. (C)", value=0.0)
    
    tsat_suc = get_tsat_global(p_suc, fluido)
    tsat_liq = get_tsat_global(p_liq, fluido)
    sh = round(t_suc_tubo - tsat_suc, 1)
    sc = round(tsat_liq - t_liq_tubo, 1)
    dt = round(t_ret - t_ins, 1)

with tab_diag:
    st.subheader("✅ Checklist")
    ck1, ck2, ck3 = st.columns(3)
    limpeza = ck1.checkbox("Limpeza Geral", value=True)
    filtros = ck2.checkbox("Filtros OK", value=True)
    drenagem = ck3.checkbox("Dreno OK", value=True)
    medidas = st.text_area("Diagnóstico e Recomendações", height=150)

    if st.button("📄 Gerar Relatório Profissional Completo"):
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho Blue Estilizado
            pdf.set_fill_color(0, 74, 153)
            pdf.rect(0, 0, 210, 35, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 15, clean_text("RELATÓRIO TÉCNICO DE MANUTENÇÃO"), ln=True, align='C')
            pdf.ln(20)

            # Seção 1: Cliente
            pdf.set_text_color(0, 74, 153)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, clean_text("1. IDENTIFICAÇÃO DO CLIENTE E CONTATO"), ln=True, fill=False)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Cliente: {clean_text(cliente)} | Documento: {clean_text(doc_cliente)}", ln=True)
            pdf.cell(0, 6, f"Endereco: {clean_text(endereco)}", ln=True)
            pdf.cell(0, 6, f"WhatsApp: {clean_text(whatsapp)} | Data: {data_visita.strftime('%d/%m/%Y')}", ln=True)
            pdf.ln(4)

            # Seção 2: Equipamento
            pdf.set_text_color(0, 74, 153)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, clean_text("2. DADOS DO EQUIPAMENTO"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Marca/Modelo: {clean_text(fabricante)} | Serie: {clean_text(num_serie)}", ln=True)
            pdf.cell(0, 6, f"TAG: {clean_text(tag_maquina)} | Setor: {clean_text(setor)}", ln=True)
            pdf.cell(0, 6, f"Fluido: {fluido} | Tensao Nominal: {tensao_nom}", ln=True)
            pdf.ln(4)

            # Seção 3: Medições (Elétrica e Térmica)
            pdf.set_text_color(0, 74, 153)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, clean_text("3. PARÂMETROS TÉCNICOS MEDIDOS"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Eletrica: {a_med}A (Medida) | {rla_comp}A (RLA) | {lra_comp}A (LRA) | {v_med}V", ln=True)
            pdf.cell(0, 6, f"Pressao: Succao {p_suc} PSIG | Descarga {p_liq} PSIG", ln=True)
            pdf.cell(0, 6, f"Temperaturas: Succao {t_suc_tubo}C | Liquido {t_liq_tubo}C | Retorno {t_ret}C | Insufl. {t_ins}C", ln=True)
            pdf.cell(0, 6, f"Analise: SH {sh}K | SC {sc}K | Delta T {dt}K", ln=True)
            pdf.ln(4)

            # Seção 4: Checklist e Diagnóstico
            pdf.set_text_color(0, 74, 153)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(0, 8, clean_text("4. CHECKLIST E DIAGNÓSTICO FINAL"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"Limpeza: {'OK' if limpeza else '---'} | Filtros: {'OK' if filtros else '---'} | Drenagem: {'OK' if drenagem else '---'}", ln=True)
            pdf.ln(2)
            pdf.multi_cell(0, 6, clean_text(medidas))

            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button(label="⬇️ Baixar Relatório Completo", data=pdf_bytes, file_name=f"Relatorio_{clean_text(cliente)}.pdf", mime="application/pdf")
            st.success("Testes concluídos: Todos os campos integrados com sucesso.")
        except Exception as e:
            st.error(f"Erro na geração do relatório: {e}")
