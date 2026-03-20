import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import re
from fpdf import FPDF

# 1. CONFIGURAÇÃO INICIAL (TESTADA)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO)
st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] {
        background-color: #e0f2f1 !important;
        color: #004d40 !important;
        font-weight: bold;
        border: 1px solid #b2dfdb !important;
    }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
    }
    /* Estilo para o botão de PDF */
    div.stDownloadButton > button {
        background-color: #d32f2f !important;
        color: white !important;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO (MÁSCARAS E LOGICA) ---
def limpar(v): return re.sub(r'\D', '', str(v))

def aplicar_mascaras():
    # CPF/CNPJ
    doc = limpar(st.session_state.cli_doc_input)
    if len(doc) == 11: st.session_state.dados['cpf_cnpj'] = f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14: st.session_state.dados['cpf_cnpj'] = f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    
    # WhatsApp / Telefones
    zap = limpar(st.session_state.cli_zap_input)
    if len(zap) == 11: st.session_state.dados['whatsapp'] = f"({zap[:2]}) {zap[2]} {zap[3:7]}-{zap[7:]}"
    
    # CEP e Busca
    cep = limpar(st.session_state.cli_cep_input)
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

# --- FUNÇÃO DE APOIO PARA LIMPAR EMOJIS (EVITA O ERRO DE ENCODING) ---
def limpar_texto_pdf(texto):
    # Remove emojis e caracteres que o FPDF não entende
    return texto.replace('🟢', '').replace('🟡', '').replace('🔴', '').strip()

# --- 3. GERADOR DE PDF (CORRIGIDO PARA NÃO DAR ERRO DE UNICODE) ---
def gerar_pdf_tecnico(d):
    # Usamos 'latin-1' que é o padrão do FPDF para evitar o erro que você recebeu
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LAUDO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " IDENTIFICACAO DO CLIENTE", 1, 1, 'L', 1)
    
    pdf.set_font("Arial", '', 10)
    # Usamos .encode('latin-1', 'ignore').decode('latin-1') para garantir que acentos funcionem
    pdf.cell(100, 8, f" Cliente: {d['nome']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(90, 8, f" Doc: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(100, 8, f" Endereco: {d['endereco']}, {d['numero']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(90, 8, f" CEP: {d['cep']}", 1, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, " DADOS DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(64, 8, f" Fab: {d['fabricante']}", 1)
    pdf.cell(63, 8, f" Mod: {d['modelo']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(63, 8, f" Cap: {d['capacidade']} BTU", 1, 1)
    
    pdf.cell(64, 8, f" S.Evap: {d['serie_evap']}", 1)
    
    # AQUI ESTAVA O ERRO: Limpamos o emoji do status antes de enviar para o PDF
    status_limpo = limpar_texto_pdf(d['status_maquina'])
    pdf.cell(126, 8, f" Status: {status_limpo}".encode('latin-1', 'ignore').decode('latin-1'), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- MANTENHA O RESTANTE DO SEU CÓDIGO IGUAL (INTERFACE E SIDEBAR) ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LAUDO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " IDENTIFICACAO DO CLIENTE", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 8, f" Cliente: {d['nome']}", 1)
    pdf.cell(90, 8, f" Doc: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(100, 8, f" Endereco: {d['endereco']}, {d['numero']}", 1)
    pdf.cell(90, 8, f" CEP: {d['cep']}", 1, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, " DADOS DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(64, 8, f" Fab: {d['fabricante']}", 1)
    pdf.cell(63, 8, f" Mod: {d['modelo']}", 1)
    pdf.cell(63, 8, f" Cap: {d['capacidade']} BTU", 1, 1)
    pdf.cell(64, 8, f" S.Evap: {d['serie_evap']}", 1)
    pdf.cell(126, 8, f" Status: {d['status_maquina']}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# 2. MOTOR DE SESSÃO (CHAVES VERIFICADAS)
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

# 3. INTERFACE DE ABA ÚNICA
tabs = st.tabs(["📋 Identificação e Equipamento"])
tab1 = tabs[0]

with tab1:
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        
        # MÁSCARA INDEXADA PARA DOC E WHATSAPP
        c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_input", on_change=aplicar_mascaras)
        c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap_input", on_change=aplicar_mascaras)

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        
        # BUSCA DE CEP AUTOMÁTICA VIA ON_CHANGE
        ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_input", on_change=aplicar_mascaras)

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            # INDEXAÇÃO CORRIGIDA
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            
            linhas = ["Residencial", "Comercial", "Industrial"]
            st.session_state.dados['linha'] = st.selectbox("Linha:", linhas, index=linhas.index(st.session_state.dados['linha']))
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            caps = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", caps, index=caps.index(st.session_state.dados['capacidade']))
            
            fluidos = ["R410A", "R134a", "R22", "R32", "R290"]
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", fluidos, index=fluidos.index(st.session_state.dados['fluido']))
            
            servicos = ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"]
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", servicos, index=servicos.index(st.session_state.dados['tipo_servico']))
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

    # --- BOTÃO DE GERAR PDF (NOVO) ---
    st.markdown("---")
    if st.session_state.dados['nome']:
        # --- FUNÇÃO DE APOIO PARA LIMPAR EMOJIS (EVITA O ERRO DE ENCODING) ---
def limpar_texto_pdf(texto):
    # Remove emojis e caracteres que o FPDF não entende
    return texto.replace('🟢', '').replace('🟡', '').replace('🔴', '').strip()

# --- 3. GERADOR DE PDF (CORRIGIDO PARA NÃO DAR ERRO DE UNICODE) ---
def gerar_pdf_tecnico(d):
    # Usamos 'latin-1' que é o padrão do FPDF para evitar o erro que você recebeu
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LAUDO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " IDENTIFICACAO DO CLIENTE", 1, 1, 'L', 1)
    
    pdf.set_font("Arial", '', 10)
    # Usamos .encode('latin-1', 'ignore').decode('latin-1') para garantir que acentos funcionem
    pdf.cell(100, 8, f" Cliente: {d['nome']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(90, 8, f" Doc: {d['cpf_cnpj']}", 1, 1)
    pdf.cell(100, 8, f" Endereco: {d['endereco']}, {d['numero']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(90, 8, f" CEP: {d['cep']}", 1, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, " DADOS DO EQUIPAMENTO", 1, 1, 'L', 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(64, 8, f" Fab: {d['fabricante']}", 1)
    pdf.cell(63, 8, f" Mod: {d['modelo']}".encode('latin-1', 'ignore').decode('latin-1'), 1)
    pdf.cell(63, 8, f" Cap: {d['capacidade']} BTU", 1, 1)
    
    pdf.cell(64, 8, f" S.Evap: {d['serie_evap']}", 1)
    
    # AQUI ESTAVA O ERRO: Limpamos o emoji do status antes de enviar para o PDF
    status_limpo = limpar_texto_pdf(d['status_maquina'])
    pdf.cell(126, 8, f" Status: {status_limpo}".encode('latin-1', 'ignore').decode('latin-1'), 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- MANTENHA O RESTANTE DO SEU CÓDIGO IGUAL (INTERFACE E SIDEBAR) ---
        st.download_button(label="📄 Gerar Relatório Técnico em PDF", data=pdf_data, file_name=f"Laudo_{st.session_state.dados['tag_id']}.pdf", mime="application/pdf", use_container_width=True)

# --- SIDEBAR (CONGELADO E PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
        f"🆔 CPF/CNPJ: {st.session_state.dados['cpf_cnpj']}\n"
        f"📍 END: {st.session_state.dados['endereco']}, {st.session_state.dados['numero']} - {st.session_state.dados['bairro']}\n"
        f"🏙️ {st.session_state.dados['cidade']}/{st.session_state.dados['uf']} | CEP: {st.session_state.dados['cep']}\n"
        f"📞 Contato: {st.session_state.dados['whatsapp']} | Email: {st.session_state.dados['email']}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados['tag_id']} | Linha: {st.session_state.dados['linha']}\n"
        f"🏭 Fab: {st.session_state.dados['fabricante']} | Mod: {st.session_state.dados['modelo']}\n"
        f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n"
        f"🔢 S.Evap: {st.session_state.dados['serie_evap']} | S.Cond: {st.session_state.dados['serie_cond']}\n"
        f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📜 Registro: {st.session_state.dados['tecnico_registro']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )
    
    zap_limpo = limpar(st.session_state.dados['whatsapp'])
    link_final = f"https://wa.me/55{zap_limpo}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico:
                st.session_state.dados[key] = ""
        st.rerun()
