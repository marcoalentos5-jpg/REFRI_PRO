import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re
from fpdf import FPDF

# 1. CONFIGURAÇÃO E ESTILO (BLOQUEADO)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stTextInput>div>div>input { background-color: #f0f2f6 !important; }
    div.stDownloadButton > button {
        background-color: #0b5394 !important;
        color: white !important;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# 2. FUNÇÕES DE APOIO (MÁSCARAS E BUSCA)
def limpar(v): return re.sub(r'\D', '', str(v))

def formatar_cpf_cnpj(v):
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

# 3. GERADOR DE PDF (TODOS OS CAMPOS DA ABA 1)
def gerar_pdf_hvac(d):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "RELATORIO TECNICO HVAC - PRO", 0, 1, 'C')
    pdf.ln(5)
    
    def bloco(titulo, info):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(0, 8, titulo, 1, 1, 'L', 1)
        pdf.set_font("Arial", '', 10)
        for label, texto in info:
            pdf.cell(95, 8, f"{label}: {texto}", 1)
            if info.index((label, texto)) % 2 != 0: pdf.ln(8)
        pdf.ln(5)

    bloco("DADOS DO CLIENTE", [
        ("Nome", d['nome']), ("Doc", d['cpf_cnpj']),
        ("WhatsApp", d['whatsapp']), ("Email", d['email']),
        ("Endereço", f"{d['endereco']}, {d['numero']}"), ("CEP", d['cep']),
        ("Bairro", d['bairro']), ("Cidade/UF", f"{d['cidade']}/{d['uf']}")
    ])
    
    bloco("DADOS DO EQUIPAMENTO", [
        ("Fabricante", d['fabricante']), ("Modelo", d['modelo']),
        ("Capacidade", d['capacidade']), ("Fluido", d['fluido']),
        ("Série Evap", d['serie_evap']), ("Série Cond", d['serie_cond']),
        ("TAG", d['tag_id']), ("Status", d['status_maquina'])
    ])
    
    return pdf.output(dest='S').encode('latin-1')

# 4. SESSION STATE (28 CAMPOS ORIGINAIS)
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

# 5. INTERFACE - ABA 1 (IDENTIFICAÇÃO E EQUIPAMENTO)
tab1 = st.tabs(["📋 Identificação e Equipamento"])[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = formatar_cpf_cnpj(c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj']))
        st.session_state.dados['whatsapp'] = formatar_tel(c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp']))

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = formatar_tel(cx1.text_input("Celular:", value=st.session_state.dados['celular']))
        st.session_state.dados['tel_fixo'] = formatar_tel(cx2.text_input("Fixo:", value=st.session_state.dados['tel_fixo']))
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_raw = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        st.session_state.dados['cep'] = formatar_cep(cep_raw)
        
        # BUSCA DE CEP AUTOMÁTICA
        if len(limpar(cep_raw)) == 8 and st.session_state.dados['endereco'] == '':
            try:
                r = requests.get(f"https://viacep.com.br/ws/{limpar(cep_raw)}/json/").json()
                if "erro" not in r:
                    st.session_state.dados['endereco'] = r.get('logradouro', '')
                    st.session_state.dados['bairro'] = r.get('bairro', '')
                    st.session_state.dados['cidade'] = r.get('localidade', '')
                    st.session_state.dados['uf'] = r.get('uf', '')
                    st.rerun()
            except: pass

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    st.subheader("⚙️ Especificações Técnicas")
    with st.expander("Detalhes do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']))
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Série Evap:", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Série Cond:", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("BTUs:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R22", "R134a"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

    # --- BOTÃO DE GERAR PDF ---
    st.markdown("---")
    if st.session_state.dados['nome']:
        pdf_data = gerar_pdf_hvac(st.session_state.dados)
        st.download_button(label="📥 Baixar Relatório Técnico (PDF)", data=pdf_data, file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf", mime="application/pdf")

# 6. SIDEBAR ORIGINAL (BLOQUEADO)
with st.sidebar:
    st.title("🚀 Painel")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Registro:", value=st.session_state.dados['tecnico_registro'])
    st.markdown("---")
    zap_url = f"https://wa.me/55{limpar(st.session_state.dados['whatsapp'])}"
    st.link_button("📲 Enviar WhatsApp", zap_url, use_container_width=True)
