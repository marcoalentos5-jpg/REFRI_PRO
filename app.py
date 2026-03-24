# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema

# 1. CONFIGURAÇÃO INICIAL (TESTADA)
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# 2. MOTOR DE SESSÃO (CHAVES MESTRAS)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional', 'laudo_diag': ''
    }

# LISTA GLOBAL DE FLUIDOS (Para garantir consistência de índice)
LISTA_FLUIDOS = ["R410A", "R134a", "R22", "R32", "R290"]

# ==============================================================================
# 1. FUNÇÃO DA ABA 1: IDENTIFICAÇÃO E EQUIPAMENTO
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Identificação e Equipamento")
    
    # --- DADOS DO CLIENTE (Resumido para foco no erro) ---
    with st.expander("👤 Dados do Cliente", expanded=False):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados['whatsapp'], key="cli_zap")

    # --- ESPECIFICAÇÕES DO EQUIPAMENTO (ONDE ESTAVA O ERRO) ---
    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung"], key="fab_aba1")
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)
        
        with e3:
            # CORREÇÃO: Usamos a mesma KEY que será usada na Aba 2 para "travar" o valor
            idx_f = LISTA_FLUIDOS.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in LISTA_FLUIDOS else 0
            st.session_state.dados['fluido'] = st.selectbox(
                "Fluido Refrigerante:", 
                LISTA_FLUIDOS, 
                index=idx_f, 
                key="shared_fluido_key" 
            )
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva"], key="serv_aba1")

# ==============================================================================
# 2. FUNÇÃO DA ABA 2: DIAGNÓSTICOS
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # RECUPERAÇÃO DO FLUIDO SINCRONIZADO
    # Ao usar a "shared_fluido_key", o Streamlit mantém o valor escolhido na Aba 1
    fluido = st.session_state.shared_fluido_key
    st.session_state.dados['fluido'] = fluido # Sincroniza com o dicionário de dados
    
    st.info(f"❄️ Fluido em Análise: **{fluido}** (Sincronizado)")

    st.subheader("1. Medições de Campo")
    c1, c2 = st.columns(2)
    with c1:
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_diag")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_diag")
    with c2:
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="pd_diag")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="tl_diag")

    # MOTOR DE CÁLCULO
    def f_sat(p, g):
        if p <= 5: return 0.0
        if g == "R410A": return 0.253 * (p**0.8) - 18.5
        if g == "R22": return 0.415 * (p**0.72) - 19.8
        if g == "R32": return 0.245 * (p**0.81) - 19.0
        if g == "R134a": return 0.65 * (p**0.62) - 25.0
        return 0.0

    t_sat_s = f_sat(p_suc, fluido)
    t_sat_d = f_sat(p_des, fluido)
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0

    # EXIBIÇÃO
    res1, res2 = st.columns(2)
    res1.metric("Superaquecimento (SH)", f"{sh:.2f} K")
    res2.metric("Sub-resfriamento (SC)", f"{sc:.2f} K")

# ==============================================================================
# 4. SIDEBAR E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel REFRI_PRO")
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO DAS ABAS
# ==============================================================================
if aba_selecionada == "Home":
    st.markdown("<h1 style='text-align: center;'>MPN Soluções</h1>", unsafe_allow_html=True)
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()
elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO FINAL BLINDADA - R32/RLA/ΔT)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # --- CORREÇÃO CRÍTICA: SINCRONIZAÇÃO DO FLUIDO ---
    # Criamos uma lista idêntica à da Aba 1 para manter os índices íntegros
    lista_fluidos = ["R410A", "R134a", "R22", "R32", "R290"]
    
    # Recuperamos o que está salvo no estado global
    fluido_atual = st.session_state.dados.get('fluido', 'R410A')
    
    # Garantimos que o índice seja localizado corretamente para não resetar para o R410A
    try:
        idx_fluido = lista_fluidos.index(fluido_atual)
    except ValueError:
        idx_fluido = 0

    # Exibimos o seletor na Aba 2 também, mas AMARRADO ao session_state.dados['fluido']
    st.session_state.dados['fluido'] = st.selectbox(
        "❄️ Confirme o Fluido Refrigerante para Cálculo:", 
        lista_fluidos, 
        index=idx_fluido,
        key="fluido_diag_sync" # Chave única para evitar conflito de widgets
    )
    
    fluido = st.session_state.dados['fluido']
    st.info(f"⚙️ Calculando pressões baseadas no fluido: **{fluido}**")

    # --- 1. MEDIÇÕES DE CAMPO ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        # Usamos chaves específicas para as entradas numéricas para não perder dados ao trocar de aba
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="p_suc_val")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="t_suc_val")
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", step=0.1, key="t_ret_val")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", step=0.1, key="t_ins_val")

    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="p_des_val")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="t_liq_val")

    # ... (Restante das colunas c3, c4, c5 permanecem iguais)

    # --- 2. MOTOR DE CÁLCULO (R32 CORRIGIDO) ---
    def f_sat(p, g):
        if p <= 5: return 0.0
        # Fórmulas de conversão Pressão -> Temperatura de Saturação (Curva PxT)
        if g == "R410A": return 0.253 * (p**0.8) - 18.5
        if g == "R22": return 0.415 * (p**0.72) - 19.8
        if g == "R32": return 0.245 * (p**0.81) - 19.0
        if g == "R134a": return 0.65 * (p**0.62) - 25.0
        return 0.0

    t_sat_s = f_sat(p_suc, fluido)
    t_sat_d = f_sat(p_des, fluido)
    
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0

    # --- SALVAMENTO PARA O ASSISTENTE (ABA 3) ---
    st.session_state['sh_val'] = sh
    st.session_state['sc_val'] = sc
    # ... (restante do código de exibição)

# ==============================================================================
# 3. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO (IA E DIAGNÓSTICO)
# ==============================================================================

def renderizar_aba_ia_diagnostico():
    st.header("🕵️ Assistente de Campo: Diagnóstico Dinâmico")
    
    # --- RESGATE DOS DADOS DA ABA 2 (VIA SESSION STATE) ---
    sh = st.session_state.get('sh_val', 0.0)
    sc = st.session_state.get('sc_val', 0.0)
    i_med = st.session_state.get('im_val', 0.0)
    rla = st.session_state.get('rla_val', 0.0)

    # Painel de Monitoramento Rápido
    st.info(f"📊 **Dados Recebidos:** SH: {sh:.1f}K | SC: {sc:.1f}K | Corrente: {i_med}A")

    # ==========================================================================
    # 1. CHECKLIST DE CAMPO (PERGUNTAS DO ASSISTENTE)
    # ==========================================================================
    st.subheader("1. Verificações Físicas (Checklist)")
    c1, c2 = st.columns(2)
    
    with c1:
        vibracao = st.selectbox("Vibração no compressor?", ["Normal", "Leve", "Forte"], key="ia_vib")
        ruido = st.selectbox("Ruído mecânico?", ["Normal", "Metálico", "Sopro/Agudo"], key="ia_ruido")
        sujeira = st.selectbox("Limpeza da Serpentina?", ["Limpa", "Sujeira Leve", "Obstrução Grave"], key="ia_suj")

    with c2:
        ventilador = st.selectbox("Motor Ventilador?", ["Normal", "Lento", "Parado/Travado"], key="ia_fan")
        gelo = st.selectbox("Presença de Gelo?", ["Não", "Linha de Expansão", "Sucção/Compressor"], key="ia_gelo")
        oleo = st.selectbox("Vazamento de Óleo?", ["Não", "Conexões", "Base do Compressor"], key="ia_oleo")

    st.markdown("---")

    # ==========================================================================
    # 2. TABELA DE CAUSAS E CONTRAMEDIDAS (LÓGICA IA)
    # ==========================================================================
    st.subheader("2. Análise de Causas e Contramedidas")
    
    causas_ia = []

    # --- MOTOR DE DECISÃO (LOGICA CRUZADA) ---
    
    # Caso 1: Falta de Fluido
    if sh > 12 and (gelo == "Linha de Expansão" or oleo == "Conexões"):
        causas_ia.append({
            "Causa": "Vazamento / Carga Insuficiente",
            "Evidência": f"SH Alto ({sh}K) + Gelo/Óleo detectado",
            "Ação": "Localizar vazamento com nitrogênio e recompor carga por balança."
        })

    # Caso 2: Falha de Troca Térmica
    if sujeira == "Obstrução Grave" or ventilador == "Parado/Travado":
        causas_ia.append({
            "Causa": "Bloqueio de Condensação",
            "Evidência": "Checklist indica falha no fluxo de ar",
            "Ação": "Realizar limpeza química e testar capacitor do ventilador."
        })

    # Caso 3: Risco de Quebra Mecânica
    if i_med > rla and rla > 0:
        causas_ia.append({
            "Causa": "Sobrecarga Elétrica",
            "Evidência": f"Corrente ({i_med}A) acima do RLA ({rla}A)",
            "Ação": "Verificar tensão de rede e possível desgaste mecânico interno."
        })

    # EXIBIÇÃO FINAL
    if causas_ia:
        st.table(causas_ia)
    else:
        st.success("✅ Parâmetros normais. Continue o monitoramento.")

# ==============================================================================
# 4. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO
# ==============================================================================
# Mudamos esta seção para antes da Lógica de Exibição das Abas para definir aba_selecionada
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"]
    
    # Use st.sidebar.radio para criar os botões de seleção de aba e DEFINIR a variável
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
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
    
    # Importante: urllib.parse deve estar no topo do arquivo (import urllib.parse)
    link_final = f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    # LIMPAR FORMULÁRIO (PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in list(st.session_state.dados.keys()):
            if key not in chaves_tecnico:
                st.session_state.dados[key] = ""
        st.rerun()

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================

# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- APRESENTAÇÃO DA ABA HOME ---
    st.markdown("<br>", unsafe_allow_html=True) 

    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        NOME_ARQUIVO_LOGO = "logo.png"
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao abrir a imagem: {e}")
        else:
            st.error(f"⚠️ Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado.")

    st.markdown("<br><br>", unsafe_allow_html=True) 

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

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1() 

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() 

elif aba_selecionada == "3. Assistente de Campo":
    renderizar_aba_ia_diagnostico()

elif aba_selecionada == "Relatórios":
    st.header("📊 Página de Relatórios")
    st.write("Em breve: Visualização e exportação de relatórios.")
