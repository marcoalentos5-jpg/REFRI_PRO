import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re
from fpdf import FPDF

# 1. CONFIGURAÇÃO (BLOQUEADA)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# 2. FUNÇÕES DE APOIO (MÁSCARAS E BUSCA)
def limpar(v): return re.sub(r'\D', '', str(v))

def formatar_doc(v):
    v = limpar(v)
    if len(v) == 11: return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
    if len(v) == 14: return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
    return v

def formatar_cep(v):
    v = limpar(v)
    return f"{v[:5]}-{v[5:]}" if len(v) == 8 else v

def formatar_tel(v):
    v = limpar(v)
    if len(v) == 11: return f"({v[:2]}) {v[2]} {v[3:7]}-{v[7:]}"
    if len(v) == 10: return f"({v[:2]}) {v[2:6]}-{v[6:]}"
    return v

def buscar_cep(cep):
    cep_limpo = limpar(cep)
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: return False
    return False

# 3. GERADOR DE PDF PROFISSIONAL
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'RELATORIO TECNICO DE MANUTENCAO HVAC', 0, 1, 'C')
        self.ln(5)

def gerar_pdf(d):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Seções
    sections = [
        ("DADOS DO CLIENTE", [
            (f"Nome: {d['nome']}", f"CPF/CNPJ: {d['cpf_cnpj']}"),
            (f"Endereço: {d['endereco']}, {d['numero']}", f"CEP: {d['cep']}"),
            (f"Bairro: {d['bairro']}", f"Cidade/UF: {d['cidade']}/{d['uf']}"),
            (f"WhatsApp: {d['whatsapp']}", f"Email: {d['email']}")
        ]),
        ("ESPECIFICACOES DO EQUIPAMENTO", [
            (f"Fabricante: {d['fabricante']}", f"Modelo: {d['modelo']}"),
            (f"Capacidade: {d['capacidade']} BTU", f"Fluido: {d['fluido']}"),
            (f"Serie Evap: {d['serie_evap']}", f"Serie Cond: {d['serie_cond']}"),
            (f"TAG: {d['tag_id']}", f"Status: {d['status_maquina']}")
        ])
    ]
    
    for title, rows in sections:
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 8, title, 1, 1, 'L', 1)
        for r in rows:
            pdf.cell(95, 8, r[0], 1)
            pdf.cell(95, 8, r[1], 1, 1)
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

# 4. SESSION STATE INTEGRAL
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"), 'cep': '', 'endereco': '', 'bairro': '', 
        'cidade': '', 'uf': '', 'numero': '', 'complemento': '', 'fabricante': 'Carrier', 
        'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial', 'serie_evap': '', 
        'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional'
    }

# 5. INTERFACE (ABA 1)
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = formatar_doc(c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj']))
        st.session_state.dados['whatsapp'] = formatar_tel(c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp']))

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        st.session_state.dados['cep'] = formatar_cep(cep_input)
        if len(limpar(cep_input)) == 8 and buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    st.subheader("⚙️ Especificações Técnicas")
    with st.expander("Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']))
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap:", value=st.session_state.dados['serie_evap'])
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("BTUs:", ["9.000", "12.000", "18.000", "24.000"], index=1)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

    # --- BOTÃO DE PDF REAL ---
    st.markdown("---")
    pdf_bytes = gerar_pdf(st.session_state.dados)
    st.download_button(label="📥 Baixar Relatório Técnico (PDF)", data=pdf_bytes, file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf", mime="application/pdf", use_container_width=True)

# 6. SIDEBAR
with st.sidebar:
    st.title("🚀 Painel")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    zap_url = f"https://wa.me/55{limpar(st.session_state.dados['whatsapp'])}"
    st.link_button("📲 WhatsApp", zap_url, use_container_width=True)
