
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
# ==============================================================================
# 6. CONFIGURAÇÕES INICIAIS E MEMÓRIA
# ==============================================================================

# PASSO 1: LISTA GLOBAL DE FLUIDOS (Dicionários completos)
LISTA_FLUIDOS = [
    {"nome": "R-22", "tipo": "HCFC", "pressao": "média", "inflamavel": False, "densidade_critica": "523.8 kg/m³"},
    {"nome": "R-32", "tipo": "HFC", "pressao": "alta", "inflamavel": True, "densidade_critica": "447.8 kg/m³"},
    {"nome": "R-134a", "tipo": "HFC", "pressao": "média/baixa", "inflamavel": False, "densidade_critica": "511.9 kg/m³"},
    {"nome": "R-290", "tipo": "HC (Propano)", "pressao": "média", "inflamavel": True, "densidade_critica": "221.0 kg/m³"},
    {"nome": "R-404A", "tipo": "HFC (Mistura)", "pressao": "alta", "inflamavel": False, "densidade_critica": "484.5 kg/m³"},
    {"nome": "R-410A", "tipo": "HFC (Mistura)", "pressao": "alta", "inflamavel": False, "densidade_critica": "459.5 kg/m³"},
    {"nome": "R-600a", "tipo": "HC (Isobutano)", "pressao": "baixa", "inflamavel": True, "densidade_critica": "221.0 kg/m³"}
]

# Ordenação alfabética automática
LISTA_FLUIDOS = sorted(LISTA_FLUIDOS, key=lambda x: x['nome'])

# PASSO 2: DEFINIÇÃO DA ESTRUTURA (Campos Padrão)
# Definimos tudo o que o relatório precisa ter
campos_padrao = {
    'nome': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
    'cpf_cnpj': '', 'endereco': '', 'numero': '', 'bairro': '', 'cidade': '',
    'uf': 'SP', 'cep': '', 'tag_id': 'TAG-01', 'linha': 'Residencial',
    'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000',
    'fluido': 'R-410A', 'serie_evap': '', 'serie_cond': '',
    'local_evap': '', 'local_cond': '', 'tipo_servico': 'Manutenção Preventiva',
    'status_maquina': '🟢 Operacional', 'tecnico_nome': '',
    'tecnico_documento': '', 'tecnico_registro': '', 'tecnico_contato': '',
    'data': datetime.now().strftime("%d/%m/%Y")
}

# PASSO 3: INICIALIZAÇÃO DA MEMÓRIA (SESSION STATE)
# Aqui usamos o campos_padrao que acabamos de criar
if 'dados' not in st.session_state:
    st.session_state.dados = campos_padrao.copy()

# Sincronização de segurança (Garante que campos novos apareçam)
for chave, valor in campos_padrao.items():
    if chave not in st.session_state.dados:
        st.session_state.dados[chave] = valor

# PASSO 4: FUNÇÃO DO CEP (Ferramenta de busca)
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            import requests 
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except Exception as e:
            st.error(f"Erro na conexão com ViaCEP: {e}")
    return False
    
# ==============================================================================
# 7. INICIALIZAÇÃO DO SESSION STATE (O "CÉREBRO" DO APP)
# ==============================================================================

# Isso garante que o técnico não perca os dados ao trocar de aba
if 'dados' not in st.session_state:
    st.session_state.dados = campos_padrao.copy()

# Loop de segurança: Se você criar um campo novo no futuro, ele aparece aqui
for chave, valor in campos_padrao.items():
    if chave not in st.session_state.dados:
        st.session_state.dados[chave] = valor

# ==============================================================================
# 8. ESTILO VISUAL (CSS)
# ==============================================================================
st.markdown("""
    <style>
    /* Estilo para o botão de WhatsApp e botões principais */
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 9. FUNÇÃO DA ABA 1: Identificação e Equipamento (PRIMEIRO DEFINE)
# ==============================================================================
def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            # --- CAMPOS COM FORMATAÇÃO ---
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
            
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
            
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")
            
            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

            st.markdown("---")
            
            # --- SEÇÃO ENDEREÇO ---
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
            if cep_input != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_input
                if buscar_cep(cep_input): st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp_v2")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro_v2")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid_v2")
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf_v2")

# ==============================================================================
# 9A. O INTERRUPTOR (LÓGICA DE NAVEGAÇÃO - AGORA SIM É A ÚLTIMA COISA)
# ==============================================================================

if aba_selecionada == "Home":
    renderizar_aba_home()
elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()  # Agora o Python já leu a função acima e sabe o que fazer!
elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()
elif aba_selecionada == "3. Assistente de Campo":
    st.info("🚧 Aba Assistente em desenvolvimento...")
elif aba_selecionada == "Relatórios":
    st.success("✅ Tudo pronto para gerar o PDF!")
    st.info("Aba de Relatórios em desenvolvimento...")
    
# ==============================================================================
# 9B. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO TÉCNICA REVISADA)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")

    # 1. Recupera o fluido selecionado na Sidebar
    fluido_sel = st.session_state.dados.get('fluido', 'R-410A')
    
    # 2. Busca informações técnicas do fluido na LISTA_FLUIDOS
    # Nota: LISTA_FLUIDOS deve ser uma lista de dicionários definida no topo do arquivo
    info = next((f for f in LISTA_FLUIDOS if f['nome'] == fluido_sel), None)

    st.info(f"❄️ **Fluido Refrigerante em Análise:** {fluido_sel}")

    if info:
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Tipo de Gás", info.get("tipo", "N/A"))
        with col_b:
            st.metric("Pressão de Trabalho", str(info.get("pressao", "N/A")).title())
            
        if fluido_sel in ["R-600a", "R-290", "R-32"]:
            st.warning("⚠️ **Atenção:** Fluido Inflamável ou de Baixo GWP. Cuidado com brasagem e centelhas!")
    
    st.markdown("---")

    # --- 1. MEDIÇÕES DE CAMPO ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAP**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.1f", step=1.0, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.1f", step=0.1, key="ts_final")
        t_ret = st.number_input("T. Retorno (°C)", format="%.1f", step=0.1, key="tr_final")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.1f", step=0.1, key="ti_final")

    with c2:
        st.markdown("🔴 **COND**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.1f", step=1.0, key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.1f", step=0.1, key="tl_final")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", value=220.0, step=1.0, key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", value=220.0, step=1.0, key="vm_final")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (Nominal)", value=0.0, step=0.1, key="rla_final")
        i_med = st.number_input("Corr. Medida (A)", value=0.0, step=0.1, key="im_final")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("C. Nom. (µF)", value=0.0, key="cnc_final")
        cm_c = st.number_input("C. Med. (µF)", value=0.0, key="cmc_final")

    # --- 2. MOTOR DE CÁLCULO (LÓGICA INTERNA) ---
    def calcular_t_sat(p, fluido):
        if p <= 5: return 0.0
        # Fórmulas aproximadas de conversão Pressão -> Temperatura Sat.
        if fluido == "R-410A": return 0.253 * (p**0.8) - 18.5
        if fluido == "R-22": return 0.415 * (p**0.72) - 19.8
        if fluido == "R-32": return 0.245 * (p**0.81) - 19.0
        if fluido == "R-134a": return 0.65 * (p**0.62) - 25.0
        return 0.0

    t_sat_s = calcular_t_sat(p_suc, fluido_sel)
    t_sat_d = calcular_t_sat(p_des, fluido_sel)
    
    sh = (t_suc - t_sat_s) if p_suc > 5 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 5 else 0.0
    dt_ar = (t_ret - t_ins)
    
    st.markdown("---")

    # --- 3. RESULTADOS CALCULADOS ---
    st.subheader("2. Análise de Performance")
    res1, res2, res3, res4 = st.columns(4)

    with res1:
        st.metric("Superaquecimento (SH)", f"{sh:.1f} K")
        if sh < 5 and p_suc > 5:
            st.error("⚠️ SH BAIXO: Risco de golpe de líquido!")
        elif sh > 12:
            st.warning("⚠️ SH ALTO: Baixa eficiência / Carga baixa.")

    with res2:
        st.metric("Sub-resfriamento (SC)", f"{sc:.1f} K")
        if sc < 3 and p_des > 5:
            st.warning("⚠️ SC BAIXO: Falta de fluido ou restrição.")

    with res3:
        st.metric("Delta T (Ar)", f"{dt_ar:.1f} °C")
        if dt_ar < 8 and p_suc > 5:
            st.warning("⚠️ Troca térmica insuficiente.")

    with res4:
        dif_i = rla - i_med
        st.metric("Dif. Corrente", f"{dif_i:.1f} A")
        if i_med > rla and rla > 0:
            st.error("⚠️ SOBRECARGA ELÉTRICA!")

    st.markdown("---")
    st.session_state.dados['laudo_diag'] = st.text_area("Conclusão do Diagnóstico:", key="laudo_final_v4", help="Descreva o que foi encontrado e a solução.")  


# ==============================================================================
# 9C. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO (IA E DIAGNÓSTICO)
# ==============================================================================

def renderizar_aba_ia_diagnostico():
    st.header("🕵️ Assistente de Campo: Diagnóstico Dinâmico")
    
    # --- RESGATE DOS DADOS DA ABA 2 ---
    # Importante: As chaves devem bater exatamente com os inputs da Aba 2 (ps_final, ts_final, etc.)
    # Se você seguiu o código anterior, estas são as variáveis:
    sh = st.session_state.get('sh_val', 0.0) # Valor calculado na Aba 2
    sc = st.session_state.get('sc_val', 0.0) # Valor calculado na Aba 2
    i_med = st.session_state.get('im_final', 0.0)
    rla = st.session_state.get('rla_final', 0.0)

    # Painel de Resumo (O técnico vê o que já preencheu sem precisar voltar de aba)
    st.markdown("### 📊 Monitoramento de Ciclo")
    m1, m2, m3 = st.columns(3)
    m1.metric("Superaquecimento", f"{sh:.1f} K")
    m2.metric("Sub-resfriamento", f"{sc:.1f} K")
    m3.metric("Corrente Real", f"{i_med} A", delta=f"{i_med - rla:.1f} A" if rla > 0 else None, delta_color="inverse")

    st.markdown("---")

    # ==========================================================================
    # 9D. CHECKLIST DE CAMPO (VERIFICAÇÕES FÍSICAS)
    # ==========================================================================
    st.subheader("1. Inspeção Sensorial (O que você vê/ouve?)")
    
    with st.container():
        c1, c2 = st.columns(2)
        
        with c1:
            st.session_state.dados['ia_vibracao'] = st.selectbox(
                "Vibração no compressor?", 
                ["Normal", "Leve (Sentido no tubo)", "Forte (Balanço da base)"], 
                key="ia_vib_final"
            )
            st.session_state.dados['ia_ruido'] = st.selectbox(
                "Ruído mecânico?", 
                ["Normal", "Metálico/Batida", "Sopro/Agudo (Válvula)"], 
                key="ia_ruido_final"
            )
            st.session_state.dados['ia_sujeira'] = st.selectbox(
                "Limpeza da Serpentina?", 
                ["Limpa/Padrão", "Sujeira Leve", "Obstrução Grave (Colmeia tapada)"], 
                key="ia_suj_final"
            )

        with c2:
            st.session_state.dados['ia_ventilador'] = st.selectbox(
                "Motor Ventilador?", 
                ["Normal (Fluxo OK)", "Lento/Capacitor Fraco", "Parado/Travado"], 
                key="ia_fan_final"
            )
            st.session_state.dados['ia_gelo'] = st.selectbox(
                "Presença de Gelo?", 
                ["Não", "Início da Serpentina (Expansão)", "Toda a Sucção/Compressor"], 
                key="ia_gelo_final"
            )
            st.session_state.dados['ia_oleo'] = st.selectbox(
                "Vazamento de Óleo?", 
                ["Não", "Mancha nas Conexões", "Base do Compressor/Cárter"], 
                key="ia_oleo_final"
            )

    st.markdown("---")

    # ==========================================================================
    # 9E. BOTÃO DE ANÁLISE (LÓGICA DE APOIO)
    # ==========================================================================
    if st.button("🚀 Gerar Diagnóstico Assistido", use_container_width=True):
        st.subheader("💡 Conclusão Sugerida")
        
        # Exemplo de lógica automática simples:
        if sh > 12 and sc < 3:
            st.error("🚨 **DIAGNÓSTICO:** Provável **Falta de Fluido Refrigerante** ou Vazamento.")
            st.write("👉 **Ação:** Verificar manchas de óleo e testar estanqueidade.")
            
        elif sh < 5 and sc > 10:
            st.warning("🚨 **DIAGNÓSTICO:** Provável **Excesso de Carga** ou Obstrução de Ar na Condensadora.")
            st.write("👉 **Ação:** Verificar limpeza e rotação do ventilador externo.")
            
        elif st.session_state.dados['ia_sujeira'] == "Obstrução Grave":
            st.warning("🚨 **DIAGNÓSTICO:** **Bloqueio de Troca Térmica.**")
            st.write("👉 **Ação:** Realizar limpeza química pesada antes de prosseguir.")
        
        else:
            st.success("✅ **SISTEMA ESTÁVEL:** Os parâmetros físicos e térmicos estão dentro da normalidade operacional.")

    # ==============================================================================
# 9F. TABELA DE CAUSAS E CONTRAMEDIDAS (LÓGICA IA)
# ==============================================================================
# Esta parte deve estar DENTRO da função renderizar_aba_ia_diagnostico()
    st.subheader("2. Análise de Causas e Contramedidas")
    
    causas_ia = []
    
    # Resgatando variáveis para a lógica (certifique-se que os nomes batem com a Aba 2)
    sh = st.session_state.get('sh_val', 0.0) 
    gelo = st.session_state.dados.get('ia_gelo', 'Não')
    oleo = st.session_state.dados.get('ia_oleo', 'Não')
    sujeira = st.session_state.dados.get('ia_sujeira', 'Limpa')
    ventilador = st.session_state.dados.get('ia_ventilador', 'Normal')
    i_med = st.session_state.get('im_final', 0.0)
    rla = st.session_state.get('rla_final', 0.0)

    # --- MOTOR DE DECISÃO ---
    if sh > 12 and (gelo != "Não" or oleo != "Não"):
        causas_ia.append({
            "Causa": "Vazamento / Carga Insuficiente",
            "Evidência": f"SH Alto ({sh:.1f}K) + Sinais físicos",
            "Ação": "Localizar vazamento e recompor carga por balança."
        })

    if "Obstrução" in sujeira or "Parado" in ventilador:
        causas_ia.append({
            "Causa": "Bloqueio de Troca Térmica",
            "Evidência": "Falha detectada no fluxo de ar",
            "Ação": "Realizar limpeza química e testar capacitor do ventilador."
        })

    if rla > 0 and i_med > rla:
        causas_ia.append({
            "Causa": "Sobrecarga Elétrica",
            "Evidência": f"Corrente ({i_med}A) acima do RLA ({rla}A)",
            "Ação": "Verificar tensão e possível desgaste mecânico."
        })

    if causas_ia:
        st.table(causas_ia)
    else:
        st.success("✅ Parâmetros dentro da normalidade operacional.")

# ==============================================================================
# 9G. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚀 REFRI_PRO")
    
    # A. NAVEGAÇÃO
    opcoes_abas = ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"]
    aba_selecionada = st.radio("Navegação:", opcoes_abas)
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO
    st.subheader("👨‍🔧 Responsável Técnico")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados.get('tecnico_nome', ''))
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados.get('tecnico_registro', ''))
    
    st.markdown("---")
    
    # C. VALIDAÇÃO E ENVIO WHATSAPP
    # Só libera se tiver Nome e WhatsApp preenchidos
    nome_cli = st.session_state.dados.get('nome', '')
    zap_cli = st.session_state.dados.get('whatsapp', '')

    if nome_cli and zap_cli:
        st.success("📋 STATUS: PRONTO")
        
        # Montagem da mensagem (Resumida para o WhatsApp não travar)
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n\n"
            f"👤 *CLIENTE:* {nome_cli}\n"
            f"⚙️ *EQUIPAMENTO:* {st.session_state.dados.get('fabricante', '')} / {st.session_state.dados.get('modelo', '')}\n"
            f"🛠️ *SERVIÇO:* {st.session_state.dados.get('tipo_servico', '')}\n"
            f"👨‍🔧 *TÉCNICO:* {st.session_state.dados.get('tecnico_nome', '')}"
        )
        
        # O link precisa do import urllib.parse no topo do arquivo
        import urllib.parse
        link_final = f"https://wa.me/55{zap_cli.replace('-','').replace(' ','')}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar via WhatsApp", link_final, use_container_width=True)
    else:
        st.warning("⚠️ Preencha Cliente e WhatsApp na Aba 1")

    # D. LIMPAR FORMULÁRIO
    if st.button("🗑️ Resetar Laudo", use_container_width=True):
        # Lista do que NÃO queremos apagar
        manter = ['tecnico_nome', 'tecnico_registro', 'tecnico_documento']
        for key in list(st.session_state.dados.keys()):
            if key not in manter:
                st.session_state.dados[key] = ""
        st.rerun()

# ==============================================================================
# 9H. DEFINIÇÃO DA ABA HOME (VISUAL MPN SOLUÇÕES)
# ==============================================================================

def renderizar_aba_home():
    # Centralização do Logo e Títulos
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tentativa de carregar o logo (se o arquivo existir)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            # Caso não tenha logo, exibe um ícone grande
            st.markdown("<h1 style='text-align: center; font-size: 100px;'>❄️</h1>", unsafe_allow_html=True)

    # Texto de Boas-vindas Estilizado
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #0d47a1; font-family: 'Segoe UI', sans-serif; margin-bottom: 0;">
            MPN Soluções
        </h1>
        <p style="color: #1976d2; font-size: 1.3em; margin-top: 5px;">
            Soluções em Refrigeração e Climatização
        </p>
        <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; display: inline-block; width: 80%;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold; margin-bottom: 10px;">
                Bem-vindo ao Sistema REFRI_PRO
            </p>
            <p style="color: #546e7a; font-size: 1.0em; text-align: left;">
                🚀 <b>Como usar o sistema:</b><br>
                1. <b>Cadastro:</b> Identifique o cliente e o equipamento.<br>
                2. <b>Diagnósticos:</b> Insira pressões, temperaturas e correntes.<br>
                3. <b>Assistente:</b> Use a IA para validar causas e contramedidas.<br>
                4. <b>WhatsApp:</b> Envie o laudo instantâneo pelo painel lateral.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Utilize o menu lateral para navegar entre as etapas do serviço.")

# ==============================================================================
# 9I. LÓGICA DE NAVEGAÇÃO FINAL (O ÚLTIMO BLOCO DO ARQUIVO)
# ==============================================================================

# Este bloco deve vir DEPOIS de todas as funções def e DEPOIS do st.sidebar
if aba_selecionada == "Home":
    renderizar_aba_home()

elif aba_selecionada == "1. Cadastro":
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos()

elif aba_selecionada == "3. Assistente de Campo":
    renderizar_aba_ia_diagnostico()

elif aba_selecionada == "Relatórios":
    st.header("📊 Página de Relatórios")
    st.info("Esta aba está sendo preparada para gerar o seu PDF profissional.")
    # Aqui entrará sua lógica de PDF futuramente
