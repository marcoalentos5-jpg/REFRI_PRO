import streamlit as st
from datetime import datetime
import requests
import urllib.parse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# =========================================================
# 1. FUNÇÃO DO PDF (MÁQUINA DE GERAR RELATÓRIOS)
# =========================================================
def gerar_pdf_profissional(dados, eletrica):
    file_path = "relatorio_tecnico_mpn.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    azul = colors.HexColor("#0b5394")

    # Logo
    try:
        logo = Image("logo.png", width=6*cm, height=3*cm)
        elements.append(logo)
    except:
        pass

    # Cabeçalho Profissional
    elements.append(Paragraph("<b>MPN SOLUÇÕES EM REFRIGERAÇÃO</b>", styles['Title']))
    elements.append(Paragraph("Laudo Técnico de Manutenção e Diagnóstico", styles['Normal']))
    elements.append(Spacer(1, 12))

    # --- FUNÇÃO AUXILIAR PARA TABELAS ---
    def tabela_secao(titulo, dados_tabela):
        elements.append(Paragraph(f"<b>{titulo}</b>", styles['Heading3']))
        tabela = Table(dados_tabela, colWidths=[6*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), azul),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))
        elements.append(tabela)
        elements.append(Spacer(1, 12))

    # --- MONTAGEM DAS SEÇÕES NO PDF ---
    tabela_secao("CLIENTE", [
        ["Campo", "Valor"],
        ["Nome", dados.get('nome','')],
        ["CPF/CNPJ", dados.get('cpf_cnpj','')],
        ["Telefone", dados.get('whatsapp','')],
    ])

    tabela_secao("EQUIPAMENTO", [
        ["Campo", "Valor"],
        ["Fabricante", dados.get('fabricante','')],
        ["Modelo", dados.get('modelo','')],
        ["Status", dados.get('status_maquina','')],
    ])

    if eletrica: # Só adiciona elétrica se não for o relatório parcial
        tabela_secao("ANÁLISE ELÉTRICA", [
            ["Campo", "Valor"],
            ["Tensão Rede", eletrica.get('tensao_rede','')],
            ["Corrente Medida", eletrica.get('corrente_medida','')],
            ["Potência", f"{eletrica.get('potencia_kw','')} kW"],
        ])

    # Assinaturas
    elements.append(Spacer(1, 30))
    assinatura = [
        ["______________________________", "______________________________"],
        ["Marcos Alexandre Almeida", dados.get('nome','')],
        ["Técnico Responsável", "Cliente"]
    ]
    table_ass = Table(assinatura, colWidths=[8*cm, 8*cm])
    elements.append(table_ass)

    # Rodapé com Data
    data_atual = datetime.now().strftime("%d/%m/%Y")
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Gerado em {data_atual} | MPN Soluções", styles['Normal']))
    return file_path 
# =========================================================
# 2. CONFIGURAÇÃO DA PÁGINA E SIDEBAR (FORA DA FUNÇÃO)
# =========================================================
st.set_page_config(page_title="HVAC Pro - MPN", layout="wide")
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'whatsapp': '', 'fabricante': '', 'modelo': '', 
        'status_maquina': 'Operacional', 'tag_id': 'TAG-01'
        # ... adicione aqui os nomes de outros campos que seu código usa ...
    }
with st.sidebar:
    st.header("📲 Finalizar")
    
    if st.button("📄 GERAR RELATÓRIO TOTAL", use_container_width=True):
        path = gerar_pdf_profissional(st.session_state.dados, st.session_state.get('eletrica', {}))
        with open(path, "rb") as f:
            st.download_button("📥 Baixar PDF Completo", f, file_name=path)
            
    zap_num = st.session_state.dados.get('whatsapp', '')
    msg = urllib.parse.quote(f"Olá! Segue o laudo da MPN Soluções.")
    st.link_button("🟢 ENVIAR VIA WHATSAPP", f"https://wa.me/55{zap_num}?text={msg}", use_container_width=True)

# AQUI CONTINUA O RESTO DO SEU APP (TABS, CSS, ETC)
    # ================= FUNÇÃO TABELA =================
    def tabela_secao(titulo, dados_tabela):
        elements.append(Paragraph(f"<b>{titulo}</b>", styles['Heading3']))

        tabela = Table(dados_tabela, colWidths=[6*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), azul),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ]))

        elements.append(tabela)
        elements.append(Spacer(1, 12))

    # ================= CLIENTE =================
if 'dados' not in locals():
    dados = {}

tabela_secao("CLIENTE", [
    ["Campo", "Valor"],
    ["Nome", str(dados.get('nome', ''))],
    ["CPF/CNPJ", str(dados.get('cpf_cnpj', ''))],
    ["Telefone", str(dados.get('whatsapp', ''))],
    ["Email", str(dados.get('email', ''))],
])

# ================= ENDEREÇO =================
tabela_secao("ENDEREÇO", [
        ["Campo", "Valor"],
        ["Logradouro", f"{dados.get('endereco','')}, {dados.get('numero','')}"],
        ["Bairro", dados.get('bairro','')],
        ["Cidade", dados.get('cidade','')],
        ["UF", dados.get('uf','')],
        ["CEP", dados.get('cep','')],
    ])

    # ================= EQUIPAMENTO =================
tabela_secao("EQUIPAMENTO", [
        ["Campo", "Valor"],
        ["Fabricante", dados.get('fabricante','')],
        ["Modelo", dados.get('modelo','')],
        ["Capacidade", f"{dados.get('capacidade','')} BTU"],
        ["Fluido", dados.get('fluido','')],
        ["Linha", dados.get('linha','')],
        ["Status", dados.get('status_maquina','')],
    ])

    # ================= ELÉTRICA =================
tabela_secao("ANÁLISE ELÉTRICA", [
        ["Campo", "Valor"],
        ["Tensão Rede", eletrica.get('tensao_rede','')],
        ["Tensão Medida", eletrica.get('tensao_medida','')],
        ["Diferença Tensão", eletrica.get('dif_tensao','')],
        ["Corrente Medida", eletrica.get('corrente_medida','')],
        ["RLA", eletrica.get('rla','')],
        ["LRA", eletrica.get('lra','')],
        ["Diferença Corrente", eletrica.get('dif_corrente','')],
        ["RS / ST / TR", f"{eletrica.get('tensao_rs','')} / {eletrica.get('tensao_st','')} / {eletrica.get('tensao_tr','')}"],
        ["Correntes", f"{eletrica.get('corrente_r','')} / {eletrica.get('corrente_s','')} / {eletrica.get('corrente_t','')}"],
        ["Potência", f"{eletrica.get('potencia_kw','')} kW"],
    ])

    # ================= DIAGNÓSTICO AUTOMÁTICO =================
diagnostico = []

try:
        if float(eletrica.get('dif_tensao') or 0) > 10:
            diagnostico.append("Sobretensão detectada")

        if float(eletrica.get('dif_corrente') or 0) > 5:
            diagnostico.append("Corrente acima do nominal (sobrecarga)")

        if not diagnostico:
            diagnostico.append("Sistema operando dentro dos parâmetros")

except:
        diagnostico.append("Dados insuficientes para diagnóstico")

tabela_secao("DIAGNÓSTICO TÉCNICO", [
        ["Resultado", " | ".join(diagnostico)],
        ["Observações", eletrica.get('obs','')],
    ])

elements.append(Spacer(1, 30))

    # ================= ASSINATURAS =================
assinatura = [
        ["______________________________", "______________________________"],
        ["Marcos Alexandre Almeida do Nascimento", dados.get('nome','')],
        ["Técnico Responsável", "Cliente"],
        ["CNPJ: 51.274.762/0001-17", f"CPF/CNPJ: {dados.get('cpf_cnpj','')}"],
    ]

table_ass = Table(assinatura, colWidths=[8*cm, 8*cm])
table_ass.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER')
    ]))

elements.append(table_ass)

    # ================= RODAPÉ =================
data_atual = datetime.datetime.now().strftime("%d/%m/%Y")

elements.append(Spacer(1, 20))
elements.append(Paragraph(
        f"Relatório gerado em {data_atual} | MPN Soluções em Refrigeração e Climatização",
        styles['Normal']
    ))

doc.build(elements)

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
    </style>
""", unsafe_allow_html=True)

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

# 3. INTERFACE COM DUAS ABAS (SEM AFETAR NADA EXISTENTE)
tabs = st.tabs(["📋 Identificação e Equipamento", "⚡ Análise Elétrica"])
tab1 = tabs[0]
tab2 = tabs[1]

with tab1:
    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF ou CNPJ", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Cel.:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Telefone Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Número/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 1])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'])

    # --- SEÇÃO EQUIPAMENTO ---
    col_titulo, col_data = st.columns([3, 1])
    with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
    with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
            st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
            st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
            st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# --- SIDEBAR (CONGELADO E PROTEGIDO) ---
with st.sidebar:
    st.title("🚀 Painel de Controle")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    # VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    # MENSAGEM WHATSAPP - ENVIO DE TODOS OS DADOS SEM EXCEÇÃO
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
        f"📍 Loc.Evap: {st.session_state.dados['local_evap']} | Loc.Cond: {st.session_state.dados['local_cond']}\n"
        f"🛠️ Serviço: {st.session_state.dados['tipo_servico']}\n"
        f"🩺 Status: {st.session_state.dados['status_maquina']}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
        f"📜 Registro: {st.session_state.dados['tecnico_registro']}\n"
        f"📅 Data: {st.session_state.dados['data']}"
    )
    
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    # LIMPAR FORMULÁRIO (PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico:
                st.session_state.dados[key] = ""
        st.rerun()

# ================= WHATSAPP - ABA IDENTIFICAÇÃO =================
st.markdown("---")
st.subheader("📲 Enviar Laudo de Identificação")

# limpa número
zap_num = "".join(filter(str.isdigit, st.session_state.dados.get('whatsapp', '')))

# mensagem SOMENTE da aba 1
msg_identificacao = (
    f"*LAUDO HVAC - IDENTIFICAÇÃO*\n\n"

    f"👤 *CLIENTE*\n"
    f"{st.session_state.dados.get('nome','')}\n"
    f"CPF/CNPJ: {st.session_state.dados.get('cpf_cnpj','')}\n"
    f"WhatsApp: {st.session_state.dados.get('whatsapp','')}\n"
    f"E-mail: {st.session_state.dados.get('email','')}\n\n"

    f"📍 *ENDEREÇO*\n"
    f"{st.session_state.dados.get('endereco','')}, {st.session_state.dados.get('numero','')}\n"
    f"{st.session_state.dados.get('bairro','')}\n"
    f"{st.session_state.dados.get('cidade','')}/{st.session_state.dados.get('uf','')}\n"
    f"CEP: {st.session_state.dados.get('cep','')}\n\n"

    f"⚙️ *EQUIPAMENTO*\n"
    f"Fabricante: {st.session_state.dados.get('fabricante','')}\n"
    f"Modelo: {st.session_state.dados.get('modelo','')}\n"
    f"Capacidade: {st.session_state.dados.get('capacidade','')} BTU\n"
    f"Linha: {st.session_state.dados.get('linha','')}\n"
    f"Fluido: {st.session_state.dados.get('fluido','')}\n\n"

    f"🔢 Série Evap: {st.session_state.dados.get('serie_evap','')}\n"
    f"🔢 Série Cond: {st.session_state.dados.get('serie_cond','')}\n\n"

    f"📍 Locais:\n"
    f"Evap: {st.session_state.dados.get('local_evap','')}\n"
    f"Cond: {st.session_state.dados.get('local_cond','')}\n\n"

    f"🛠️ Serviço: {st.session_state.dados.get('tipo_servico','')}\n"
    f"🩺 Status: {st.session_state.dados.get('status_maquina','')}\n\n"

    f"👨‍🔧 *TÉCNICO*\n"
    f"{st.session_state.dados.get('tecnico_nome','')}\n"
    f"Registro: {st.session_state.dados.get('tecnico_registro','')}\n"
    f"📅 Data: {st.session_state.dados.get('data','')}"
)

# link
link_identificacao = f"https://wa.me/55{zap_num}?text={urllib.parse.quote(msg_identificacao)}"

# botão
st.link_button("📲 Enviar Laudo de Identificação", link_identificacao, use_container_width=True)

st.markdown("---")
st.subheader("📄 Enviar Relatório Técnico")

if st.button("📄 Gerar e Baixar PDF", use_container_width=True):
    pdf_path = gerar_pdf_profissional(st.session_state.dados, st.session_state.get('eletrica', {}))
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Baixar Relatório Técnico",
            data=f,
            file_name="relatorio_tecnico.pdf",
            mime="application/pdf",
            use_container_width=True
        )
st.markdown("---")
st.subheader("📄 Enviar Relatório Técnico")

if st.button("📄 Gerar Relatório Profissional", use_container_width=True):
    pdf = gerar_pdf_profissional(
        st.session_state.dados,
        st.session_state.get('eletrica', {})
    )

    with open(pdf, "rb") as f:
        st.download_button(
            "📥 Baixar PDF",
            f,
            file_name="Relatorio_Tecnico_HVAC.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ================== ABA 2 - ELÉTRICA (FINAL) ==================
with tab2:
    st.subheader("⚡ Análise Elétrica Profissional")

    # ===== GARANTE SESSION =====
    if 'eletrica' not in st.session_state:
        st.session_state.eletrica = {}

    defaults_eletrica = {
        # CAMPOS GERAIS
        'tensao_rede': '',
        'tensao_medida': '',
        'dif_tensao': '',
        'corrente_medida': '',
        'dif_corrente': '',
        'rla': '',
        'lra': '',

        # TRIFÁSICO
        'tensao_rs': '', 'tensao_st': '', 'tensao_tr': '',
        'corrente_r': '', 'corrente_s': '', 'corrente_t': '',

        # OUTROS
        'fp': '0.92',
        'potencia_kw': '',
        'disjuntor': '',
        'cabo': '',
        'aterramento': 'OK',
        'obs': ''
    }

    for k, v in defaults_eletrica.items():
        if k not in st.session_state.eletrica:
            st.session_state.eletrica[k] = v

    e = st.session_state.eletrica

    # ================= TOPO - DADOS GERAIS =================
    with st.expander("📌 Dados Gerais", expanded=True):
        c1, c2, c3 = st.columns(3)
        e['tensao_rede'] = c1.text_input("Tensão da Rede (V):", value=e.get('tensao_rede', ''))
        e['tensao_medida'] = c2.text_input("Tensão Medida (V):", value=e.get('tensao_medida', ''))
        e['dif_tensao'] = c3.text_input("Diferença (V):", value=e.get('dif_tensao', ''), disabled=True)

        c4, c5, c6 = st.columns(3)
        e['corrente_medida'] = c4.text_input("Corrente Medida (A):", value=e.get('corrente_medida', ''))
        e['rla'] = c5.text_input("RLA (A):", value=e.get('rla', ''))
        e['lra'] = c6.text_input("LRA (A):", value=e.get('lra', ''))

        e['dif_corrente'] = st.text_input("Diferença de Corrente (A):", value=e.get('dif_corrente', ''), disabled=True)

    # ===== CÁLCULOS GERAIS =====
    try:
        tensao_rede = float(e.get('tensao_rede') or 0)
        tensao_medida = float(e.get('tensao_medida') or 0)
        corrente_medida = float(e.get('corrente_medida') or 0)
        rla = float(e.get('rla') or 0)

        dif_tensao = tensao_medida - tensao_rede
        dif_corrente = corrente_medida - rla if rla > 0 else 0

        e['dif_tensao'] = f"{dif_tensao:.2f}"
        e['dif_corrente'] = f"{dif_corrente:.2f}"

    except:
        e['dif_tensao'] = ""
        e['dif_corrente'] = ""

    # ================= TENSÕES =================
    with st.expander("📏 Tensões entre Fases (V)", expanded=True):
        v1, v2, v3 = st.columns(3)
        e['tensao_rs'] = v1.text_input("RS (V):", value=e.get('tensao_rs', ''))
        e['tensao_st'] = v2.text_input("ST (V):", value=e.get('tensao_st', ''))
        e['tensao_tr'] = v3.text_input("TR (V):", value=e.get('tensao_tr', ''))

    # ================= CORRENTES =================
    with st.expander("🔌 Correntes por Fase (A)", expanded=True):
        c1, c2, c3 = st.columns(3)
        e['corrente_r'] = c1.text_input("Fase R:", value=e.get('corrente_r', ''))
        e['corrente_s'] = c2.text_input("Fase S:", value=e.get('corrente_s', ''))
        e['corrente_t'] = c3.text_input("Fase T:", value=e.get('corrente_t', ''))

    # ================= CÁLCULO TRIFÁSICO =================
    try:
        v_rs = float(e.get('tensao_rs') or 0)
        v_st = float(e.get('tensao_st') or 0)
        v_tr = float(e.get('tensao_tr') or 0)

        i_r = float(e.get('corrente_r') or 0)
        i_s = float(e.get('corrente_s') or 0)
        i_t = float(e.get('corrente_t') or 0)

        fp = float(e.get('fp') or 0.92)

        v_med = (v_rs + v_st + v_tr) / 3 if (v_rs + v_st + v_tr) > 0 else 0
        i_med = (i_r + i_s + i_t) / 3 if (i_r + i_s + i_t) > 0 else 0

        potencia = (1.732 * v_med * i_med * fp) / 1000
        e['potencia_kw'] = f"{potencia:.2f}"

        # Desequilíbrios
        v_max = max(v_rs, v_st, v_tr)
        des_v = ((v_max - v_med) / v_med * 100) if v_med > 0 else 0

        i_max = max(i_r, i_s, i_t)
        des_i = ((i_max - i_med) / i_med * 100) if i_med > 0 else 0

    except:
        e['potencia_kw'] = ""
        v_med = i_med = des_v = des_i = 0

        # ================= RESULTADOS =================
    with st.expander("📊 Resultados", expanded=True):

        try:
            # BASE
            v_med = (v_rs + v_st + v_tr) / 3 if (v_rs + v_st + v_tr) > 0 else 0
            i_med = (i_r + i_s + i_t) / 3 if (i_r + i_s + i_t) > 0 else 0

            fp = float(e.get('fp') or 0.92)

            # ===== POTÊNCIAS =====
            # Aparente (S)
            S = (1.732 * v_med * i_med) / 1000  # kVA

            # Ativa (P)
            P = S * fp  # kW

            # Reativa (Q)
            import math
            Q = S * math.sqrt(1 - fp**2) if fp <= 1 else 0  # kVAr

            # Elétrica (entrada)
            P_eletrica = P  # kW (mesma ativa)

            # Mecânica (estimativa com rendimento)
            rendimento = 0.85  # típico compressor
            P_mecanica = P * rendimento

            # ===== OUTROS =====
            v_max = max(v_rs, v_st, v_tr)
            des_v = ((v_max - v_med) / v_med * 100) if v_med > 0 else 0

            i_max = max(i_r, i_s, i_t)
            des_i = ((i_max - i_med) / i_med * 100) if i_med > 0 else 0

            # Eficiência estimada
            eficiencia = (P_mecanica / P_eletrica * 100) if P_eletrica > 0 else 0

        except:
            S = P = Q = P_eletrica = P_mecanica = eficiencia = 0
            des_v = des_i = 0

        # ===== EXIBIÇÃO =====
        r1, r2, r3 = st.columns(3)
        r1.metric("Potência Aparente (kVA)", f"{S:.2f}")
        r2.metric("Potência Ativa (kW)", f"{P:.2f}")
        r3.metric("Potência Reativa (kVAr)", f"{Q:.2f}")

        r4, r5, r6 = st.columns(3)
        r4.metric("Potência Elétrica (kW)", f"{P_eletrica:.2f}")
        r5.metric("Potência Mecânica (kW)", f"{P_mecanica:.2f}")
        r6.metric("Fator de Potência", f"{fp:.2f}")

        r7, r8, r9 = st.columns(3)
        r7.metric("Eficiência Estimada (%)", f"{eficiencia:.1f}")
        r8.metric("Desequilíbrio Tensão (%)", f"{des_v:.1f}")
        r9.metric("Desequilíbrio Corrente (%)", f"{des_i:.1f}")

        r10, r11 = st.columns(2)
        r10.metric("Tensão Média (V)", f"{v_med:.1f}")
        r11.metric("Corrente Média (A)", f"{i_med:.2f}")

    # ================= PROTEÇÃO =================
    with st.expander("🔧 Proteção Elétrica", expanded=True):
        p1, p2 = st.columns(2)
        e['disjuntor'] = p1.text_input("Disjuntor (A):", value=e.get('disjuntor', ''))
        e['cabo'] = p2.text_input("Seção do Cabo (mm²):", value=e.get('cabo', ''))

        e['aterramento'] = st.radio(
            "Aterramento:",
            ["OK", "Irregular", "Inexistente"],
            index=["OK", "Irregular", "Inexistente"].index(e.get('aterramento', 'OK')),
            horizontal=True
        )

    # ================= OBS =================
    with st.expander("📝 Observações Técnicas", expanded=True):
        e['obs'] = st.text_area("Observações:", value=e.get('obs', ''))

# ================= WHATSAPP - ABA ELÉTRICA =================
st.markdown("---")
st.subheader("📲 Enviar Laudo Elétrico")

# limpa número
zap_num = "".join(filter(str.isdigit, st.session_state.dados.get('whatsapp', '')))

# mensagem elétrica (somente dados da aba elétrica)
msg_eletrica = (
    f"*LAUDO ELÉTRICO HVAC*\n\n"

    f"👤 Cliente: {st.session_state.dados.get('nome','')}\n\n"

    f"⚡ *DADOS GERAIS*\n"
    f"Tensão Rede: {e.get('tensao_rede','')} V\n"
    f"Tensão Medida: {e.get('tensao_medida','')} V\n"
    f"Diferença: {e.get('dif_tensao','')} V\n\n"

    f"Corrente Medida: {e.get('corrente_medida','')} A\n"
    f"RLA: {e.get('rla','')} A | LRA: {e.get('lra','')} A\n"
    f"Diferença Corrente: {e.get('dif_corrente','')} A\n\n"

    f"🔌 *TRIFÁSICO*\n"
    f"RS: {e.get('tensao_rs','')} | ST: {e.get('tensao_st','')} | TR: {e.get('tensao_tr','')}\n"
    f"R: {e.get('corrente_r','')} | S: {e.get('corrente_s','')} | T: {e.get('corrente_t','')}\n\n"

    f"📊 Potência: {e.get('potencia_kw','')} kW\n"
    f"FP: {e.get('fp','')}\n\n"

    f"👨‍🔧 Técnico: {st.session_state.dados.get('tecnico_nome','')}\n"
    f"📅 {st.session_state.dados.get('data','')}"
)

link_eletrica = f"https://wa.me/55{zap_num}?text={urllib.parse.quote(msg_eletrica)}"

st.link_button("📲 Enviar Laudo Elétrico", link_eletrica, use_container_width=True)
