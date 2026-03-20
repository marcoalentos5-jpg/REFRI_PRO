import streamlit as st
from datetime import datetime
import requests
import re
import urllib.parse
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# --- 2. FUNÇÕES DE MÁSCARA E BUSCA (SÓ DISPARAM NO ENTER) ---
def limpar(v): return re.sub(r'\D', '', str(v))

def aplicar_mascaras():
    # Formata CPF/CNPJ
    doc = limpar(st.session_state.doc_input)
    if len(doc) == 11: st.session_state.dados['cpf_cnpj'] = f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14: st.session_state.dados['cpf_cnpj'] = f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    
    # Formata WhatsApp
    zap = limpar(st.session_state.zap_input)
    if len(zap) == 11: st.session_state.dados['whatsapp'] = f"({zap[:2]}) {zap[2]} {zap[3:7]}-{zap[7:]}"
    
    # Busca CEP e Formata
    cep = limpar(st.session_state.cep_input)
    if len(cep) == 8:
        st.session_state.dados['cep'] = f"{cep[:5]}-{cep[5:]}"
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5).json()
            if "erro" not in r:
                st.session_state.dados['endereco'] = r.get('logradouro', '')
                st.session_state.dados['bairro'] = r.get('bairro', '')
                st.session_state.dados['cidade'] = r.get('localidade', '')
                st.session_state.dados['uf'] = r.get('uf', '')
        except: pass

# --- 3. GERADOR DE PDF ---
def gerar_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LAUDO TECNICO HVAC - MARCOS ALEXANDRE", 0, 1, 'C')
    pdf.ln(5)
    
    # Seção Cliente
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, " IDENTIFICACAO DO CLIENTE", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, f" Nome: {d['nome']}", 1)
    pdf.cell(90, 8, f" CPF/CNPJ: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(190, 8, f" Endereco: {d['endereco']}, {d['numero']} - {d['bairro']}", 1, 1)
    pdf.cell(100, 8, f" Cidade/UF: {d['cidade']}/{d['uf']}", 1)
    pdf.cell(90, 8, f" CEP: {d['cep']}", 1, 1)
    pdf.ln(5)

    # Seção Equipamento
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, " DETALHES DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 8, f" Fabricante: {d['fabricante']}", 1)
    pdf.cell(95, 8, f" Modelo: {d['modelo']}", 1, 1)
    pdf.cell(95, 8, f" Serie Evap: {d['serie_evap']}", 1)
    pdf.cell(95, 8, f" Serie Cond: {d['serie_cond']}", 1, 1)
    pdf.cell(95, 8, f" Capacidade: {d['capacidade']}", 1)
    pdf.cell(95, 8, f" Fluido: {d['fluido']}", 1, 1)
    pdf.cell(190, 8, f" TAG: {d['tag_id']} | Status: {d['status_maquina']}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SESSION STATE ---
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'email': '', 'cep': '', 
        'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'tag_id': 'TAG-01',
        'status_maquina': '🟢 Operacional', 'tecnico_nome': 'Marcos Alexandre'
    }

# --- 5. INTERFACE (ABA 1) ---
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome/Razão Social *", value=st.session_state.dados['nome'])
        # Disparam a máscara apenas quando sai do campo (on_change)
        c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="doc_input", on_change=aplicar_mascaras)
        c3.text_input("WhatsApp (DDD)", value=st.session_state.dados['whatsapp'], key="zap_input", on_change=aplicar_mascaras)

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cep_input", on_change=aplicar_mascaras)
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº", value=st.session_state.dados['numero'])

        ce4, ce5, ce6 = st.columns(3)
        st.session_state.dados['bairro'] = ce4.text_input("Bairro", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce5.text_input("Cidade", value=st.session_state.dados['cidade'])
        st.session_state.dados['email'] = ce6.text_input("E-mail", value=st.session_state.dados['email'])

    with st.expander("⚙️ Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante", ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🟡 Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['modelo'] = st.text_input("Modelo", value=st.session_state.dados['modelo'])
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap", value=st.session_state.dados['serie_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade", ["9.000", "12.000", "18.000", "24.000", "30.000", "60.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG ID", value=st.session_state.dados['tag_id'])
            st.session_state.dados['serie_cond'] = st.text_input("Série Cond", value=st.session_state.dados['serie_cond'])

    st.markdown("---")
    # BOTÃO PDF REAL (SÓ APARECE SE TIVER NOME)
    if st.session_state.dados['nome']:
        pdf_bytes = gerar_pdf(st.session_state.dados)
        st.download_button("📥 Baixar Relatório Técnico (PDF)", data=pdf_bytes, file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf", mime="application/pdf", use_container_width=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("Painel de Controle")
    st.write(f"Técnico: {st.session_state.dados['tecnico_nome']}")
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.dados = {k: "" for k in st.session_state.dados}
        st.rerun()
