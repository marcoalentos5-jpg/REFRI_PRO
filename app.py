import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re
from fpdf import FPDF

# --- FUNÇÃO: LIMPEZA PARA PDF (EVITA ERRO DE UNICODE) ---
def limpar_pdf(txt):
    if not txt: return ""
    # Remove emojis que quebram o FPDF (🟢, 🔴, etc)
    txt = re.sub(r'[^\x00-\x7f-\xc0-\xff]', '', str(txt))
    return txt.encode('latin-1', 'ignore').decode('latin-1')

# --- FUNÇÕES DE MÁSCARA (PONTOS E TRAÇOS) ---
def aplicar_mascara_cpf_cnpj(v):
    v = re.sub(r'\D', '', v)
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def aplicar_mascara_cep(v):
    v = re.sub(r'\D', '', v)
    if len(v) == 8: return f"{v[:5]}-{v[5:]}"
    return v

def aplicar_mascara_tel(v):
    v = re.sub(r'\D', '', v)
    if len(v) == 11: return f"({v[:2]}) {v[2:7]}-{v[7:]}"
    if len(v) == 10: return f"({v[:2]}) {v[2:6]}-{v[6:]}"
    return v

# --- FUNÇÃO: GERADOR DE PDF ---
# --- FUNÇÃO: GERADOR DE PDF (CORRIGIDA) ---
def gerar_pdf_hvac(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, limpar_pdf("LAUDO TÉCNICO DE MANUTENÇÃO HVAC"), 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, limpar_pdf(" 1. IDENTIFICAÇÃO DO CLIENTE"), 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, limpar_pdf(f" Cliente: {d['nome']}"), 1, 1)
    pdf.cell(0, 8, limpar_pdf(f" CPF/CNPJ: {aplicar_mascara_cpf_cnpj(d['cpf_cnpj'])}"), 1, 1)
    pdf.cell(0, 8, limpar_pdf(f" Endereço: {d['endereco']}, {d['numero']} - {d['bairro']}"), 1, 1)
    pdf.cell(0, 8, limpar_pdf(f" CEP: {aplicar_mascara_cep(d['cep'])} | WhatsApp: {aplicar_mascara_tel(d['whatsapp'])}"), 1, 1)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, limpar_pdf(" 2. DADOS DO EQUIPAMENTO"), 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 8, limpar_pdf(f" Fabricante: {d['fabricante']}"), 1)
    pdf.cell(95, 8, limpar_pdf(f" Modelo: {d['modelo']}"), 1, 1)
    pdf.cell(64, 8, limpar_pdf(f" Cap: {d['capacidade']} BTU"), 1)
    pdf.cell(63, 8, limpar_pdf(f" Fluido: {d['fluido']}"), 1)
    pdf.cell(63, 8, limpar_pdf(f" TAG: {d['tag_id']}"), 1, 1)
    pdf.cell(0, 8, limpar_pdf(f" Status: {d['status_maquina']}"), 1, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, limpar_pdf(f"Técnico: {d['tecnico_nome']} | Registro: {d['tecnico_registro']} | Data: {d['data']}"), 0, 0, 'C')
    
    # --- AQUI ESTAVA O ERRO: CORREÇÃO ABAIXO ---
    return pdf.output() # No FPDF2, output() já retorna bytes por padrão
    return pdf.output(dest='S').encode('latin-1')

# 1. CONFIGURAÇÃO INICIAL
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# 2. MOTOR DE SESSÃO
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional'
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# 3. INTERFACE
tabs = st.tabs(["📋 Identificação e Equipamento"])
tab1 = tabs[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], help="Apenas números")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'])

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])
        
        # Outros campos automáticos do CEP
        ce4, ce5, ce6, ce7 = st.columns(4)
        st.session_state.dados['bairro'] = ce4.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce5.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce6.text_input("UF:", value=st.session_state.dados['uf'])
        st.session_state.dados['email'] = ce7.text_input("E-mail:", value=st.session_state.dados['email'])

    with st.expander("⚙️ Detalhes Técnicos do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]), index=0)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
        with e3:
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# --- SIDEBAR (CONGELADO E PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CREA/CFT:", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # WHATSAPP LINK
    zap_limpo = re.sub(r'\D', '', st.session_state.dados['whatsapp'])
    msg_zap = f"Olá, segue o laudo do equipamento {st.session_state.dados['tag_id']}"
    link_zap = f"https://wa.me/55{zap_limpo}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar via WhatsApp", link_zap, use_container_width=True)

    # BOTÃO PDF (AGORA NO LUGAR CORRETO E VISÍVEL)
    st.markdown("---")
    if st.session_state.dados['nome'] and st.session_state.dados['cep']:
        pdf_bytes = gerar_pdf_hvac(st.session_state.dados)
        st.download_button(
            label="📄 Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # LIMPAR FORMULÁRIO
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        for key in st.session_state.dados.keys():
            if key not in ['tecnico_nome', 'tecnico_registro', 'data']:
                st.session_state.dados[key] = ""
        st.rerun()
