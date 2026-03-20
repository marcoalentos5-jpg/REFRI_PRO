import streamlit as st
from datetime import datetime
import requests
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# --- 2. FUNÇÕES TÉCNICAS (MÁSCARAS E BUSCA) ---
def limpar(v): return re.sub(r'\D', '', str(v))

def formatar_doc(v):
    v = limpar(v)
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def formatar_tel(v):
    v = limpar(v)
    if len(v) == 11: return f"({v[:2]}) {v[2]} {v[3:7]}-{v[7:]}"
    return v

def buscar_cep(cep):
    c = limpar(cep)
    if len(c) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{c}/json/").json()
            if "erro" not in r:
                st.session_state.dados['endereco'] = r.get('logradouro', '')
                st.session_state.dados['bairro'] = r.get('bairro', '')
                st.session_state.dados['cidade'] = r.get('localidade', '')
                st.session_state.dados['uf'] = r.get('uf', '')
                return True
        except: pass
    return False

# --- 3. GERADOR DE PDF PROFISSIONAL ---
def criar_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "RELATORIO TECNICO DE MANUTENCAO", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, "DADOS DO CLIENTE", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Nome: {d['nome']}  |  Doc: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(0, 8, f"Endereco: {d['endereco']}, {d['numero']} - {d['bairro']}", 1, 1)
    pdf.cell(0, 8, f"Cidade/UF: {d['cidade']}/{d['uf']}  |  CEP: {d['cep']}", 1, 1)
    pdf.cell(0, 8, f"WhatsApp: {d['whatsapp']}  |  Email: {d['email']}", 1, 1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "ESPECIFICACOES DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Fabricante: {d['fabricante']}  |  Modelo: {d['modelo']}", 1, 1)
    pdf.cell(0, 8, f"Serie Evap: {d['serie_evap']}  |  Serie Cond: {d['serie_cond']}", 1, 1)
    pdf.cell(0, 8, f"Capacidade: {d['capacidade']} BTU  |  Fluido: {d['fluido']}", 1, 1)
    pdf.cell(0, 8, f"TAG: {d['tag_id']}  |  Status: {d['status_maquina']}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 4. INICIALIZAÇÃO DOS DADOS ---
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
        st.session_state.dados['nome'] = c1.text_input("Nome/Razão Social", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = formatar_doc(c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj']))
        st.session_state.dados['whatsapp'] = formatar_tel(c3.text_input("WhatsApp", value=st.session_state.dados['whatsapp']))

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_raw = ce1.text_input("CEP", value=st.session_state.dados['cep'])
        if len(limpar(cep_raw)) == 8 and st.session_state.dados['endereco'] == '':
            if buscar_cep(cep_raw): st.rerun()
        st.session_state.dados['cep'] = (f"{limpar(cep_raw)[:5]}-{limpar(cep_raw)[5:]}" if len(limpar(cep_raw))==8 else cep_raw)
        
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº", value=st.session_state.dados['numero'])

        ce4, ce5, ce6 = st.columns(3)
        st.session_state.dados['bairro'] = ce4.text_input("Bairro", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce5.text_input("Cidade", value=st.session_state.dados['cidade'])
        st.session_state.dados['email'] = ce6.text_input("E-mail", value=st.session_state.dados['email'])

    with st.expander("⚙️ Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante", ["Carrier", "Daikin", "LG", "Samsung"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['modelo'] = st.text_input("Modelo", value=st.session_state.dados['modelo'])
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap", value=st.session_state.dados['serie_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("BTUs", ["9.000", "12.000", "18.000", "24.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG", value=st.session_state.dados['tag_id'])

    st.markdown("---")
    # BOTÃO DE PDF (Obrigatório preencher o Nome)
    if st.session_state.dados['nome']:
        pdf_out = criar_pdf(st.session_state.dados)
        st.download_button("📥 Baixar Relatório Técnico (PDF)", data=pdf_out, file_name="Relatorio_HVAC.pdf", mime="application/pdf", use_container_width=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("Painel")
    st.write(f"Técnico: {st.session_state.dados['tecnico_nome']}")
