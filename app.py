import streamlit as st
from datetime import datetime
import requests
import re
import urllib.parse
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# --- 2. FUNÇÕES DE LIMPEZA E FORMATAÇÃO ---
def limpar(v): return re.sub(r'\D', '', str(v))

def formatar_doc(v):
    v = limpar(v)
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def formatar_tel(v):
    v = limpar(v)
    if len(v) == 11: return f"({v[:2]}) {v[2]} {v[3:7]}-{v[7:]}"
    if len(v) == 10: return f"({v[:2]}) {v[2:6]}-{v[6:]}"
    return v

def formatar_cep(v):
    v = limpar(v)
    return f"{v[:5]}-{v[5:]}" if len(v) == 8 else v

# --- 3. LOGICA DE BUSCA DE CEP ---
def busca_cep_logic():
    cep = limpar(st.session_state.cep_input)
    if len(cep) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
            if "erro" not in r:
                st.session_state.dados['endereco'] = r.get('logradouro', '')
                st.session_state.dados['bairro'] = r.get('bairro', '')
                st.session_state.dados['cidade'] = r.get('localidade', '')
                st.session_state.dados['uf'] = r.get('uf', '')
                st.session_state.dados['cep'] = f"{cep[:5]}-{cep[5:]}"
        except: pass

# --- 4. GERADOR DE PDF (ABA 1 COMPLETA) ---
def gerar_relatorio_pdf(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LAUDO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
    pdf.ln(5)
    
    # Tabela Cliente
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " IDENTIFICACAO DO CLIENTE", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, f" Cliente: {d['nome']}", 1)
    pdf.cell(90, 8, f" CPF/CNPJ: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(100, 8, f" Endereco: {d['endereco']}, {d['numero']}", 1)
    pdf.cell(90, 8, f" Bairro: {d['bairro']}", 1, 1)
    pdf.cell(100, 8, f" Cidade/UF: {d['cidade']}/{d['uf']}", 1)
    pdf.cell(90, 8, f" CEP: {d['cep']}", 1, 1)
    pdf.cell(100, 8, f" WhatsApp: {d['whatsapp']}", 1)
    pdf.cell(90, 8, f" Email: {d['email']}", 1, 1)
    pdf.ln(5)

    # Tabela Equipamento
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, " DETALHES DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(64, 8, f" Fabricante: {d['fabricante']}", 1)
    pdf.cell(63, 8, f" Modelo: {d['modelo']}", 1)
    pdf.cell(63, 8, f" Capacidade: {d['capacidade']}", 1, 1)
    pdf.cell(64, 8, f" Serie Evap: {d['serie_evap']}", 1)
    pdf.cell(63, 8, f" Serie Cond: {d['serie_cond']}", 1)
    pdf.cell(63, 8, f" Fluido: {d['fluido']}", 1, 1)
    pdf.cell(64, 8, f" TAG: {d['tag_id']}", 1)
    pdf.cell(126, 8, f" Status: {d['status_maquina']}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INICIALIZAÇÃO ---
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'email': '', 'celular': '', 'tel_fixo': '',
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_evap': '', 'local_cond': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01', 'status_maquina': '🟢 Operacional',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_registro': '', 'data': datetime.now().strftime("%d/%m/%Y")
    }

# --- 6. INTERFACE ABA 1 ---
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Localização", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = col1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = formatar_doc(col2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj']))
        st.session_state.dados['whatsapp'] = formatar_tel(col3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp']))

        c_end1, c_end2, c_end3 = st.columns([1, 2, 1])
        # CEP com busca automática ao mudar de campo
        st.text_input("CEP *", value=st.session_state.dados['cep'], key="cep_input", on_change=busca_cep_logic)
        st.session_state.dados['endereco'] = c_end2.text_input("Logradouro", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = c_end3.text_input("Nº", value=st.session_state.dados['numero'])

        c_end4, c_end5, c_end6, c_end7 = st.columns(4)
        st.session_state.dados['bairro'] = c_end4.text_input("Bairro", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = c_end5.text_input("Cidade", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = c_end6.text_input("UF", value=st.session_state.dados['uf'])
        st.session_state.dados['email'] = c_end7.text_input("E-mail", value=st.session_state.dados['email'])

    with st.expander("⚙️ Detalhes do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante", fab_list, index=fab_list.index(st.session_state.dados['fabricante']))
            st.session_state.dados['modelo'] = st.text_input("Modelo", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Série Cond", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['linha'] = st.selectbox("Linha", ["Residencial", "Comercial", "Industrial"])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido", ["R410A", "R32", "R22", "R134a"])
            st.session_state.dados['tag_id'] = st.text_input("TAG ID", value=st.session_state.dados['tag_id'])

    st.markdown("---")
    # GERAÇÃO DO PDF
    if st.session_state.dados['nome'] and st.session_state.dados['serie_evap']:
        pdf_bytes = gerar_relatorio_pdf(st.session_state.dados)
        st.download_button(label="📥 Gerar e Baixar Relatório PDF", data=pdf_bytes, file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.warning("⚠️ Preencha o Nome do Cliente e a Série da Evap para habilitar o PDF.")

# --- 7. SIDEBAR ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico Responsável", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro (CFT/CREA)", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    zap_limpo = limpar(st.session_state.dados['whatsapp'])
    if zap_limpo:
        url_zap = f"https://wa.me/55{zap_limpo}?text=Olá,%20segue%20o%20laudo%20técnico%20da%20máquina%20{st.session_state.dados['tag_id']}"
        st.link_button("📲 Enviar Notificação WhatsApp", url_zap, use_container_width=True)
