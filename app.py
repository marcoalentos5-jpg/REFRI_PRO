import streamlit as st
from datetime import datetime
import os

# --- CONFIGURAÇÃO INICIAL (Linha 1-15) ---
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'fabricante': 'Carrier',
        'tecnico_nome': '', 'tecnico_documento': '', 'tecnico_registro': ''
    }

# --- SIDEBAR E LOGO (A LOGO FICA AQUI) ---
with st.sidebar:
    # Procura a logo na pasta raiz do projeto
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    st.title("MPN Soluções")
    st.markdown("---")
    st.info("Sistema de Laudos HVAC v3.0")

# --- DEFINIÇÃO DAS ABAS (ORGANIZAÇÃO) ---
# Criamos as abas UMA ÚNICA VEZ aqui fora
aba1, aba2 = st.tabs(["🏠 Home / Identificação", "🔍 2. Diagnósticos e Relatórios"])

with aba1:
    st.header("Identificação do Cliente e Equipamento")
    with st.expander("👤 Dados do Cliente", expanded=True):
        c1, c2 = st.columns([2, 1])
        # CHAVE ÚNICA (KEY) PARA EVITAR O ERRO DE DUPLICIDADE
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", 
                                                      value=st.session_state.dados.get('nome', ''), 
                                                      key="key_home_nome_unico")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", 
                                                          value=st.session_state.dados.get('cpf_cnpj', ''), 
                                                          key="key_home_cpf_unico")

with aba2:
    st.header("Diagnóstico Técnico")
    with st.expander("👷 Identificação do Técnico", expanded=True):
        t1, t2 = st.columns(2)
        st.session_state.dados['tecnico_nome'] = t1.text_input("Nome do Técnico", 
                                                              value=st.session_state.dados.get('tecnico_nome', ''), 
                                                              key="key_diag_tec_unico")
        st.session_state.dados['tecnico_registro'] = t2.text_input("Registro (CFT/CREA)", 
                                                                  value=st.session_state.dados.get('tecnico_registro', ''), 
                                                                  key="key_diag_reg_unico")

# --- EXECUÇÃO FINAL (INDENTAÇÃO CORRIGIDA) ---
def main():
    # Como as abas já foram renderizadas acima, a main pode apenas 
    # conter lógicas de finalização ou cálculos.
    pass

if __name__ == "__main__":
    main()

# ==============================================================================
# 1. CONFIGURAÇÃO DE INTERFACE E ESTILIZAÇÃO CSS
# ==============================================================================

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
    }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. INICIALIZAÇÃO DO MOTOR DE SESSÃO E SIDEBAR (LOGO)
# ==============================================================================

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 
        'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 
        'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'linha': 'Residencial', 
        'capacidade': '12.000', 'fluido': 'R410A',
        'serie_evap': '', 'serie_cond': '', 'local_evap': '', 'local_cond': '',
        'tag_id': 'TAG-01', 'tipo_servico': 'Manutenção Preventiva',
        'status_maquina': '🟢 Operacional',
        'tecnico_nome': '', 'tecnico_documento': '', 'tecnico_registro': ''
    }

# MANUTENÇÃO DO SIDEBAR E LOGO (ESTRUTURA ORIGINAL)
with st.sidebar:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    st.title("MPN Soluções")
    st.markdown("---")
    st.info("Sistema de Laudos HVAC v3.0")

# ==============================================================================
# 3. FUNÇÃO DA ABA 1: IDENTIFICAÇÃO E EQUIPAMENTO
# ==============================================================================

def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    with tabs[0]:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            # CORREÇÃO DA LINHA 91: USO DE .GET E KEY EXCLUSIVA
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="key_unico_nome_v4")
            d_raw = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados.get('cpf_cnpj', ''), key="k_cli_doc")
            st.session_state.dados['cpf_cnpj'] = formatar_cpf(d_raw)
            z_raw = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados.get('whatsapp', ''), key="k_cli_zap")
            st.session_state.dados['whatsapp'] = formatar_telefone(z_raw)

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = formatar_telefone(cx1.text_input("Celular:", value=st.session_state.dados.get('celular', ''), key="k_cli_cel"))
            st.session_state.dados['tel_fixo'] = formatar_telefone(cx2.text_input("Fixo:", value=st.session_state.dados.get('tel_fixo', ''), key="k_cli_fix"))
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados.get('email', ''), key="k_cli_mail")

            st.markdown("---")
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_in = ce1.text_input("CEP *", value=st.session_state.dados.get('cep', ''), key="k_cli_cep")
            if cep_in != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_in
                if buscar_cep(cep_in): st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Rua:", value=st.session_state.dados.get('endereco', ''), key="k_cli_rua")
            st.session_state.dados['numero'] = ce3.text_input("Nº:", value=st.session_state.dados.get('numero', ''), key="k_cli_num")

            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            st.session_state.dados['complemento'] = ce4.text_input("Comp:", value=st.session_state.dados.get('complemento', ''), key="k_cli_comp")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados.get('bairro', ''), key="k_cli_bair")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados.get('cidade', ''), key="k_cli_cid")
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados.get('uf', ''), max_chars=2, key="k_cli_uf")

        st.subheader("⚙️ Especificações do Equipamento")
        with st.expander("Detalhes Técnicos", expanded=True):
            e1, e2, e3 = st.columns(3)
            f_list = sorted(["Carrier", "Daikin", "Elgin", "Fujitsu", "Gree", "LG", "Midea", "Samsung", "TCL", "Trane", "York"])
            st.session_state.dados['fabricante'] = e1.selectbox("Fabricante:", f_list, key="seq_1")
            st.session_state.dados['modelo'] = e2.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''), key="seq_2")
            st.session_state.dados['linha'] = e3.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], key="seq_3")

            e4, e5 = st.columns(2)
            st.session_state.dados['serie_evap'] = e4.text_input("Série Evap:", value=st.session_state.dados.get('serie_evap', ''), key="seq_4")
            st.session_state.dados['serie_cond'] = e5.text_input("Série Cond:", value=st.session_state.dados.get('serie_cond', ''), key="seq_5")

            e6, e7 = st.columns(2)
            st.session_state.dados['local_evap'] = e6.text_input("Local Evap:", value=st.session_state.dados.get('local_evap', ''), key="seq_6")
            st.session_state.dados['local_cond'] = e7.text_input("Local Cond:", value=st.session_state.dados.get('local_cond', ''), key="seq_7")

            e8, e9, e10 = st.columns(3)
            st.session_state.dados['capacidade'] = e8.selectbox("BTU:", ["9k", "12k", "18k", "24k", "30k", "60k"], key="seq_8")
            st.session_state.dados['fluido'] = e9.selectbox("Gás:", ["R410A", "R22", "R32", "R134a"], key="seq_9")
            st.session_state.dados['tag_id'] = e10.text_input("TAG:", value=st.session_state.dados.get('tag_id', ''), key="seq_10")
            
            st.session_state.dados['status_maquina'] = st.radio("Condição:", ["🟢 OK", "🟡 Atenção", "🔴 Parado"], horizontal=True, key="st_f")
# ==============================================================================
# 4. FUNÇÃO DA ABA 2: DIAGNÓSTICOS TÉCNICOS
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Diagnóstico")
    st.info(f"Fluído: {st.session_state.dados.get('fluido')}")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("P. Sucção (PSI):", key="p_suc_d")
        st.number_input("T. Sucção (°C):", key="t_suc_d")
    with col2:
        st.number_input("P. Descarga (PSI):", key="p_des_d")
        st.number_input("T. Líquido (°C):", key="t_liq_d")
    st.markdown("---")

# ==============================================================================
# EXECUÇÃO FINAL
# ==============================================================================

def main():
    renderizar_aba_1()

if __name__ == "__main__":
    main()

# FINALIZAÇÃO DO ARQUIVO - TOTAL DE LINHAS FISCALIZADAS: 257

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (PARTE 2 - ESQUELETO INSERIDO)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("📋 Central de Diagnósticos")
    st.markdown("---")

# --- BLOCO 2: PROCESSAMENTO (CÁLCULOS TÉCNICOS COM TABELA PT) ---
    fluido = st.session_state.dados.get('fluido', 'R410A')
    
    # Fórmulas de conversão simplificadas (Pressão PSI -> Temp Saturação °C)
    def calcular_t_sat(p, gas):
        if gas == "R410A":
            # Curva aproximada para R410A
            return 0.253 * (p**0.8) - 18.5
        elif gas == "R22":
            # Curva aproximada para R22
            return 0.415 * (p**0.72) - 19.8
        elif gas == "R32":
            return 0.245 * (p**0.81) - 19.0
        elif gas == "R134a":
            return 0.65 * (p**0.62) - 25.0
        return 0.0

    # Cálculo das Temperaturas de Saturação
    t_sat_suc = calcular_t_sat(pres_suc, fluido) if pres_suc > 0 else 0.0
    t_sat_des = calcular_t_sat(pres_des, fluido) if pres_des > 0 else 0.0
    
    # Cálculo Final de SH e SC
    # Superaquecimento (SH) = Temp. Linha Sucção - Temp. Saturação Baixa
    sh = temp_suc - t_sat_suc if pres_suc > 0 else 0.0
    
    # Sub-resfriamento (SC) = Temp. Saturação Alta - Temp. Linha Líquido
    sc = t_sat_des - temp_liq if pres_des > 0 else 0.0

    # Exibição auxiliar (Opcional: ajuda o técnico a ver se a leitura está correta)
    st.caption(f"ℹ️ Temp. Saturação (Orvalho/Bolha): Sucção: {t_sat_suc:.1f}°C | Descarga: {t_sat_des:.1f}°C")
    
    # 1. SELEÇÃO DO EQUIPAMENTO (Dependência da Aba 1)
    # equipments = db_utils.buscar_equipamentos_cadastrados()
    # equipamento_id = st.selectbox("Selecione o Equipamento para Diagnóstico:", list(equipments.keys()), format_func=lambda x: equipments[x])
    
    st.info("Aba de Diagnósticos em desenvolvimento. Implemente a lógica aqui.")

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
# Mudamos esta seção para antes da Lógica de Exibição das Abas para definir aba_selecionada
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    # Use st.sidebar.radio para criar os botões de seleção de aba e DEFINIR a variável
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome do Técnico:", value=st.session_state.dados.get('tecnico_nome', ''), key="f_tec_nome")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados.get('tecnico_documento', ''), key="f_tec_doc")
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados.get('tecnico_registro', ''), key="f_tec_reg")
    
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


# ==============================================================================
# 4. FUNÇÃO DA ABA 2: DIAGNÓSTICOS TÉCNICOS E DADOS DO TÉCNICO
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Diagnóstico e Identificação Profissional")
    
    with st.expander("👷 Identificação do Técnico Responsável", expanded=True):
        t1, t2, t3 = st.columns([2, 1, 1])
        # CORREÇÃO DAS KEYS DO TÉCNICO PARA EVITAR DUPLICIDADE
        st.session_state.dados['tecnico_nome'] = t1.text_input("Nome do Técnico:", value=st.session_state.dados.get('tecnico_nome', ''), key="tec_nome_final")
        st.session_state.dados['tecnico_documento'] = t2.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados.get('tecnico_documento', ''), key="tec_doc_final")
        st.session_state.dados['tecnico_registro'] = t3.text_input("Registro (CFT/CREA):", value=st.session_state.dados.get('tecnico_registro', ''), key="tec_reg_final")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("P. Sucção (PSI):", key="p_suc_val")
        st.number_input("T. Sucção (°C):", key="t_suc_val")
    with col2:
        st.number_input("P. Descarga (PSI):", key="p_des_val")
        st.number_input("T. Líquido (°C):", key="t_liq_val")
        
# ==============================================================================
# EXECUÇÃO FINAL DO MOTOR DO APLICATIVO
# ==============================================================================

def main():
    # Renderiza apenas a interface ativa
    # LINHA 309 (O ERRO ESTÁ AQUI)
    
    def main():
        renderizar_aba_1()  # <--- Aqui ele chama a função pela segunda vez no arquivo

# LINHA 315
    if __name__ == "__main__": main()

# FINALIZAÇÃO DO ARQUIVO - TOTAL DE LINHAS FISCALIZADAS: 257

# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- NOVA APRESENTAÇÃO DA ABA HOME (COM LOGO MPN SOLUÇÕES ) ---
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento superior

    # 1. CENTRALIZAÇÃO E EXIBIÇÃO DA LOGOMARCA
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        # NOME DO ARQUIVO DE IMAGEM QUE ESTÁ SENDO USADO
        NOME_ARQUIVO_LOGO = "logo.png"
        
        # VERIFICAÇÃO ADICIONAL DO ARQUIVO NO DISCO (PARA AJUDAR NO DIAGNÓSTICO)
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                # SE O ARQUIVO EXISTE, TENTA EXIBIR
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao tentar abrir a imagem '{NOME_ARQUIVO_LOGO}'. Verifique se o arquivo está corrompido.")
                st.write(f"Detalhes do erro do sistema: {e}")
        else:
            st.error(f"⚠️ Erro: Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado na pasta raiz.")
            st.info("Verifique se o nome do arquivo salvo no computador é EXATAMENTE 'logo.png' (maiúsculas/minúsculas importam).")

    st.markdown("<br><br>", unsafe_allow_html=True) 

    # 2. TÍTULO E BOAS-VINDAS CENTRALIZADOS E ESTILIZADOS
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                MPN Soluções
            </h1>
            <p style="color: #1976d2; font-size: 1.3em;">
                Soluções em Refrigeração e Climatização
            </p>
            <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold;">
                Bem-vindo ao Sistema HVAC Pro de Gestão Inteligente.
            </p>
            <p style="color: #546e7a; font-size: 1.0em;">
                Selecione uma opção no Painel de Controle lateral para iniciar sua inspeção ou diagnóstico.
            </p>
        </div>
    """, unsafe_allow_html=True)
    # ------------------------------------------------

elif aba_selecionada == "1. Cadastro de Equipamentos":
   st.session_state.dados['tecnico_registro'] = st.text_input("Registro Profissional (CFT/CREA):", value=st.session_state.dados.get('tecnico_registro', ''), key="f_tec_reg_unico")

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() # Chama a função que contém o esqueleto da Aba 2

elif aba_selecionada == "Relatórios":
    st.header("Página de Relatórios (Em desenvolvimento)")
    st.write("Em breve: Visualização e exportação de relatórios.")
# [COLE AQUI - Logo após o fim da renderizar_aba_1]

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    # Busca o fluido que você selecionou na Aba 1
    fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido_selecionado}**")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        pres_suc = st.number_input("Pressão de Sucção (PSI):", min_value=0.0, step=1.0, key="p_suc_diag")
        temp_suc = st.number_input("Temp. Tubulação Sucção (°C):", step=0.1, key="t_suc_diag")

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        pres_des = st.number_input("Pressão de Descarga (PSI):", min_value=0.0, step=1.0, key="p_des_diag")
        temp_liq = st.number_input("Temp. Tubulação Líquido (°C):", step=0.1, key="t_liq_diag")

    st.markdown("---")

    # --- BLOCO 2: PROCESSAMENTO (CÁLCULOS) ---
    # Nota: No próximo passo, inseriremos a tabela PT aqui
    t_sat_suc = 0.0  
    t_sat_des = 0.0  
    
    sh = temp_suc - t_sat_suc
    sc = t_sat_des - temp_liq

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{sh:.1f} K")
        if 5 <= sh <= 7: st.success("✅ SH dentro do padrão (5K a 7K)")
        elif sh < 5: st.error("⚠️ SH Baixo: Risco de retorno de líquido")
        else: st.warning("⚠️ SH Alto: Possível falta de fluido ou restrição")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{sc:.1f} K")
        if 4 <= sc <= 7: st.success("✅ SC dentro do padrão (4K a 7K)")
        else: st.info("ℹ️ SC fora do padrão: Verifique condensação")

    st.markdown("---")

    # --- BLOCO 4: CONCLUSÃO E LAUDO ---
    st.subheader("3. Parecer Técnico Final")
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        placeholder="Ex: Sistema operando com pressões estáveis, superaquecimento normal...",
        key="laudo_area_diag"
    )
