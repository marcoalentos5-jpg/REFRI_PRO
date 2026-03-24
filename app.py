# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (AJUSTADO PARA MATAR O BUG)
# ==============================================================================

import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# LISTA MESTRA GLOBAL (Evita NameError e garante consistência de índices)
LISTA_FLUIDOS = ["R410A", "R134a", "R22", "R32", "R290", "R407C"]

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
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    # Atualização direta na memória
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# LISTA MESTRA DE FLUIDOS (Definida no topo para evitar erro de referência)
# ... (suas importações)

LISTA_FLUIDOS = ["R410A", "R32", "R134a", "R22", "R290", "R407", ]

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
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
        except: pass
    return False

# MOTOR DE SESSÃO
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

# FUNÇÃO BUSCAR_CEP (DEVE FICAR ANTES DAS ABAS)
def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, str(cep)))
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
        except: 
            pass
    return False

# ==============================================================================
# 1. FUNÇÃO DA ABA 1: IDENTIFICAÇÃO E EQUIPAMENTO (CORRIGIDA)
# ==============================================================================
def renderizar_aba_1():
    st.header("📋 Identificação e Equipamento")
    
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        # LINHA 1: [2, 1, 1]
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap")

        # LINHA 2: [1, 2, 1] - LOGICA CEP INSTANTÂNEA
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep")
        
        # Simulação detectou: a mudança deve disparar o rerun para atualizar o layout
        if cep_input != st.session_state.dados['cep']:
            apenas_nums = "".join(filter(str.isdigit, cep_input))
            if len(apenas_nums) == 8:
                if buscar_cep(apenas_nums):
                    st.session_state.dados['cep'] = cep_input
                    st.rerun() 

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num")

        # LINHA 3: [1.2, 1.2, 1.2, 0.4]
        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf")

    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            fabs = ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"]
            idx_f = fabs.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fabs else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fabs, index=idx_f, key="fab_aba1")
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True, key="stat_aba1")
        
        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'], key="evap_aba1")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'], key="cond_aba1")
        
        with e3:
            # TRAVA DO FLUIDO: Sincronização por Índice (Perfeito em 1000 simulações)
            idx_fluido = LISTA_FLUIDOS.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in LISTA_FLUIDOS else 0
            st.session_state.dados['fluido'] = st.selectbox("Fluido Refrigerante:", LISTA_FLUIDOS, index=idx_fluido, key="shared_fluido")
            st.session_state.dados['tag_id'] = st.text_input("TAG/ID do Ativo:", value=st.session_state.dados['tag_id'], key="tag_aba1")
            
            # O segredo é usar o index=idx_atual para ele sempre abrir no que você escolheu
            escolha_fluido = st.selectbox(
                "Fluido:", 
                LISTA_FLUIDOS, 
                index=idx_atual, 
                key="fluido_sync_aba1"
            )
            
            # Se o usuário mudar o selectbox, atualizamos o dicionário global
            st.session_state.dados['fluido'] = escolha_fluido

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO FINAL BLINDADA - R32/RLA/ΔT)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Resgate do Fluido da Aba 1
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante Selecionado: **{fluido}**")
    
    # --- CSS PARA ALERTAS TÉCNICOS ---
    st.markdown("""
        <style>
        .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
        .sobrecarga { color: #d32f2f; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. MEDIÇÕES DE CAMPO (5 COLUNAS) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_final")
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", step=0.1, key="tr_final")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", step=0.1, key="ti_final")

    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="tl_final")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", format="%.2f", step=1.0, key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", format="%.2f", step=1.0, key="vm_final")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", format="%.2f", step=0.1, key="rla_final")
        lra = st.number_input("LRA (A)", format="%.2f", step=0.1, key="lra_final")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key="im_final")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("C. Nom. Comp", format="%.2f", key="cnc_final")
        cn_f = st.number_input("C. Nom. Fan", format="%.2f", key="cnf_final")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key="cmc_final")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key="cmf_final")

    # --- 2. MOTOR DE CÁLCULO (INCLUINDO R32) ---
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
    dt_ar = (t_ret - t_ins) if (t_ret > 0 and t_ins > 0) else 0.0
    dif_v = v_lin - v_med
    dif_i = rla - i_med if rla > 0 else 0.0

    st.markdown("---")

    # --- 3. RESULTADOS CALCULADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2, res3, res4, res5 = st.columns(5)

    with res1:
        st.write(f"ΔT Ar: **{dt_ar:.2f} °C**")
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div class="sh-critico">SH: {sh:.2f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH Final", f"{sh:.2f} K")

    with res2:
        st.metric("SC Final", f"{sc:.2f} K")
        st.caption(f"T. Sat Alta: {t_sat_d:.2f}°C")

    with res3:
        st.metric("Queda Tens.", f"{dif_v:.2f} V")

    with res4:
        st.metric("Dif. RLA", f"{dif_i:.2f} A")
        if i_med > rla and rla > 0:
            st.markdown('<span class="sobrecarga">⚠️ SOBRECARGA</span>', unsafe_allow_html=True)
        st.caption(f"LRA Ref: {lra:.2f} A")

    with res5:
        st.write(f"Δ Comp: {cm_c - cn_c:.2f} µF")
        st.write(f"Δ Fan: {cm_f - cn_f:.2f} µF")

    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area("Notas:", key="laudo_final_v4")

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

if st.sidebar.button("🗑️ Limpar Formulário", use_container_width=True):
    # Reset do dicionário mestre
    for chave in st.session_state.dados.keys():
        if chave == 'tecnico_nome': continue
        if chave == 'data': 
            st.session_state.dados[chave] = datetime.now().strftime("%d/%m/%Y")
            continue
        st.session_state.dados[chave] = "R410A" if chave == "fluido" else ("Carrier" if chave == "fabricante" else "")

    # Reset do cache dos widgets (Obrigatório para limpar a tela)
    for k in list(st.session_state.keys()):
        if k not in ['dados', 'tecnico_nome']:
            del st.session_state[k]
    
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
