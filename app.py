import streamlit as st
from datetime import datetime
import requests
import urllib.parse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# 1. CONFIGURAÇÃO (Sempre a primeira linha)
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="❄️")

# =========================================================
# 2. FUNÇÃO DO PDF (ESTRUTURA COMPLETA)
# =========================================================
def gerar_pdf_profissional(dados, eletrica):
    file_path = "relatorio_tecnico_mpn.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    cor_hvac = colors.HexColor("#0b5394")

    def formatar_tabela(titulo, conteudo):
        elements.append(Paragraph(f"<b>{titulo}</b>", styles['Heading3']))
        t = Table(conteudo, colWidths=[6*cm, 10*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), cor_hvac),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

    formatar_tabela("DADOS DO CLIENTE", [
        ["Campo", "Valor"],
        ["Cliente", str(dados.get('nome', ''))],
        ["Documento", str(dados.get('cpf_cnpj', ''))],
        ["Endereço", f"{dados.get('endereco', '')}, {dados.get('numero', '')}"],
        ["WhatsApp", str(dados.get('whatsapp', ''))]
    ])

    formatar_tabela("EQUIPAMENTO", [
        ["Campo", "Valor"],
        ["Marca/Modelo", f"{dados.get('fabricante', '')} / {dados.get('modelo', '')}"],
        ["TAG/ID", str(dados.get('tag_id', ''))],
        ["Status", str(dados.get('status_maquina', ''))]
    ])

    formatar_tabela("ANÁLISE ELÉTRICA", [
        ["Parâmetro", "Medição"],
        ["Tensão Nominal", f"{eletrica.get('tensao_rede','')} V"],
        ["Tensão Medida", f"{eletrica.get('tensao_medida','')} V"],
        ["Variação", f"{eletrica.get('dif_tensao','')} V"],
        ["Corrente", f"{eletrica.get('corrente_medida','')} A"],
        ["Notas", str(eletrica.get('obs', ''))]
    ])

    # Assinaturas
    elements.append(Spacer(1, 40))
    ass_tabela = Table([
        ["__________________________", "__________________________"],
        [f"Técnico: {dados.get('tecnico_nome', '')}", "Assinatura do Cliente"]
    ], colWidths=[8*cm, 8*cm])
    ass_tabela.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(ass_tabela)

    doc.build(elements)
    return file_path

# =========================================================
# 3. GESTÃO DE ESTADO
# =========================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'endereco': '', 'numero': '',
        'fabricante': 'Carrier', 'modelo': '', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'status_maquina': '🟢 Operacional'
    }

if 'eletrica' not in st.session_state:
    st.session_state.eletrica = {'tensao_rede': '220', 'tensao_medida': '', 'dif_tensao': '0', 'corrente_medida': '', 'obs': ''}

# =========================================================
# 4. INTERFACE
# =========================================================
tab1, tab2 = st.tabs(["📋 Identificação", "⚡ Elétrica"])

with tab1:
    with st.expander("👤 Cliente", expanded=True):
        st.session_state.dados['nome'] = st.text_input("Nome", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = st.text_input("WhatsApp", value=st.session_state.dados['whatsapp'])
        st.session_state.dados['endereco'] = st.text_input("Endereço", value=st.session_state.dados['endereco'])

    with st.expander("⚙️ Equipamento", expanded=True):
        st.session_state.dados['fabricante'] = st.selectbox("Marca", ["Carrier", "Daikin", "LG", "Samsung", "Trane"], index=0)
        st.session_state.dados['modelo'] = st.text_input("Modelo", value=st.session_state.dados['modelo'])
        st.session_state.dados['tag_id'] = st.text_input("TAG", value=st.session_state.dados['tag_id'])
        st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🟡 Manutenção", "🔴 Parado"], horizontal=True)

with tab2:
    st.subheader("⚡ Medições")
    v_nom = st.text_input("Tensão Nominal", value=st.session_state.eletrica['tensao_rede'])
    v_med = st.text_input("Tensão Medida", value=st.session_state.eletrica['tensao_medida'])
    
    try:
        diff = round(abs(float(v_nom.replace(',','.')) - float(v_med.replace(',','.'))), 1) if v_med else 0
        st.session_state.eletrica.update({'tensao_rede': v_nom, 'tensao_medida': v_med, 'dif_tensao': str(diff)})
    except: pass

    st.session_state.eletrica['corrente_medida'] = st.text_input("Corrente (A)", value=st.session_state.eletrica['corrente_medida'])
    st.session_state.eletrica['obs'] = st.text_area("Observações", value=st.session_state.eletrica['obs'])

with st.sidebar:
    st.title("🚀 Painel")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico", value=st.session_state.dados['tecnico_nome'])
    if st.button("📄 GERAR PDF"):
        path = gerar_pdf_profissional(st.session_state.dados, st.session_state.eletrica)
        with open(path, "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name=path)
            ====================================================================
   import streamlit as st
from datetime import datetime
import urllib.parse
import math
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="HVAC Pro - Marcos Alexandre", layout="wide", page_icon="❄️")

# =========================================================
# 2. MOTOR DO PDF (ATUALIZADO PARA NOVOS CAMPOS)
# =========================================================
def gerar_pdf_profissional(dados, eletrica):
    file_path = "relatorio_tecnico_mpn.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    cor_azul = colors.HexColor("#0b5394")

    def criar_secao(titulo, lista):
        elements.append(Paragraph(f"<b>{titulo}</b>", styles['Heading3']))
        t = Table(lista, colWidths=[6*cm, 10*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), cor_azul),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

    # Blocos de Dados
    criar_secao("IDENTIFICAÇÃO", [
        ["Cliente", str(dados.get('nome',''))],
        ["Endereço", f"{dados.get('endereco','')}, {dados.get('numero','')}"],
        ["Equipamento", f"{dados.get('fabricante','')} - {dados.get('modelo','')}"],
        ["Status", str(dados.get('status_maquina',''))]
    ])

    criar_secao("ANÁLISE ELÉTRICA TRIFÁSICA", [
        ["Tensões (RS/ST/TR)", f"{eletrica.get('tensao_rs','')} / {eletrica.get('tensao_st','')} / {eletrica.get('tensao_tr','')} V"],
        ["Correntes (R/S/T)", f"{eletrica.get('corrente_r','')} / {eletrica.get('corrente_s','')} / {eletrica.get('corrente_t','')} A"],
        ["Potência Ativa (P)", f"{eletrica.get('potencia_kw','')} kW"],
        ["Fator de Potência", str(eletrica.get('fp',''))]
    ])

    doc.build(elements)
    return file_path

# =========================================================
# 3. SESSION STATE (MEMÓRIA DO APP)
# =========================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {'nome': '', 'whatsapp': '', 'status_maquina': '🟢 Operacional', 'tecnico_nome': 'Marcos Alexandre', 'data': datetime.now().strftime("%d/%m/%Y"), 'capacidade': '12.000'}
if 'eletrica' not in st.session_state:
    st.session_state.eletrica = {'fp': '0.92', 'aterramento': 'OK', 'tensao_rs': '0', 'tensao_st': '0', 'tensao_tr': '0', 'corrente_r': '0', 'corrente_s': '0', 'corrente_t': '0'}
if 'checklist' not in st.session_state:
    st.session_state.checklist = {'filtro': False, 'serpentina': False, 'dreno': False, 'contatos': False}

# =========================================================
# 4. INTERFACE PRINCIPAL
# =========================================================
tab1, tab2 = st.tabs(["📋 Identificação", "⚡ Elétrica & Checklist"])

with tab1:
    with st.expander("👤 Dados do Cliente & Ativo", expanded=True):
        c1, c2 = st.columns([2, 1])
        st.session_state.dados['nome'] = c1.text_input("Cliente", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = c2.text_input("WhatsApp (DDD)", value=st.session_state.dados['whatsapp'])
        st.session_state.dados['status_maquina'] = st.radio("Status", ["🟢 Operacional", "🟡 Manutenção", "🔴 Parado"], horizontal=True)

    # Link WhatsApp de Identificação (Conforme seu modelo)
    zap_num = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
    msg_id = f"*LAUDO HVAC*\n*Cliente:* {st.session_state.dados['nome']}\n*Status:* {st.session_state.dados['status_maquina']}"
    st.link_button("📲 Enviar Identificação via WhatsApp", f"https://wa.me/55{zap_num}?text={urllib.parse.quote(msg_id)}", use_container_width=True)

with tab2:
    e = st.session_state.eletrica
    st.subheader("⚡ Medições e Cálculos")
    
    with st.expander("📏 Tensões e Correntes Trifásicas", expanded=True):
        v1, v2, v3 = st.columns(3)
        e['tensao_rs'] = v1.text_input("RS (V)", value=e['tensao_rs'])
        e['tensao_st'] = v2.text_input("ST (V)", value=e['tensao_st'])
        e['tensao_tr'] = v3.text_input("TR (V)", value=e['tensao_tr'])
        
        i1, i2, i3 = st.columns(3)
        e['corrente_r'] = i1.text_input("Fase R (A)", value=e['corrente_r'])
        e['corrente_s'] = i2.text_input("Fase S (A)", value=e['corrente_s'])
        e['corrente_t'] = i3.text_input("Fase T (A)", value=e['corrente_t'])

    # --- LÓGICA DE CÁLCULO AVANÇADA ---
    try:
        v_med = (float(e['tensao_rs']) + float(e['tensao_st']) + float(e['tensao_tr'])) / 3
        i_med = (float(e['corrente_r']) + float(e['corrente_s']) + float(e['corrente_t'])) / 3
        fp = float(e['fp'])
        # Potência Ativa (P) = √3 * V * I * cosφ
        p_ativa = (1.732 * v_med * i_med * fp) / 1000
        e['potencia_kw'] = f"{p_ativa:.2f}"
        
        # Exibição de Métricas
        m1, m2 = st.columns(2)
        m1.metric("Potência Ativa Calculada", f"{e['potencia_kw']} kW")
        m2.metric("Tensão Média", f"{v_med:.1f} V")
    except: pass

    st.markdown("---")
    st.subheader("📋 Check-list Técnico")
    ch1, ch2 = st.columns(2)
    st.session_state.checklist['filtro'] = ch1.checkbox("Filtros Limpos", value=st.session_state.checklist['filtro'])
    st.session_state.checklist['contatos'] = ch2.checkbox("Contatos Reapertados", value=st.session_state.checklist['contatos'])
    
    st.session_state.dados['recomendacoes'] = st.text_area("Conclusão e Recomendações", height=100)

# --- SIDEBAR FINAL ---
with st.sidebar:
    st.title("🚀 Finalizar")
    st.session_state.dados['tecnico_nome'] = st.text_input("Técnico", value=st.session_state.dados['tecnico_nome'])
    
    if st.button("📄 GERAR RELATÓRIO PDF", use_container_width=True):
        path = gerar_pdf_profissional(st.session_state.dados, st.session_state.eletrica)
        with open(path, "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name="Laudo_Tecnico.pdf", use_container_width=True)
