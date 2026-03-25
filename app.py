
# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np
import urllib.parse


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

# 1.1. MOTOR DE SESSÃO (CHAVES VERIFICADAS)

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
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO FINAL BLINDADA)
# ==============================================================================
def renderizar_aba_1():
    st.subheader("📋 Cadastro de Cliente e Ativo")

    # --- SEÇÃO CLIENTE ---
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados.get('nome', ''), key="cli_nome_f")
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados.get('cpf_cnpj', ''), key="cli_doc_f")
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp *", value=st.session_state.dados.get('whatsapp', ''), key="cli_zap_f")

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados.get('celular', ''), key="cli_cel_f")
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados.get('tel_fixo', ''), key="cli_fixo_f")
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados.get('email', ''), key="cli_email_f")

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados.get('cep', ''), key="cli_cep_f")
        
        # Busca de CEP com Rerun para atualizar campos automaticamente
        if cep_input != st.session_state.dados.get('cep', ''):
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): 
                st.rerun()

        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados.get('endereco', ''), key="cli_end_f")
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados.get('numero', ''), key="cli_num_f")

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados.get('complemento', ''), key="cli_comp_f")
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados.get('bairro', ''), key="cli_bair_f")
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados.get('cidade', ''), key="cli_cid_f")
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados.get('uf', ''), max_chars=2, key="cli_uf_f")

    # --- SEÇÃO EQUIPAMENTO ---
    st.markdown("### ⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos do Ativo", expanded=True):
        e1, e2, e3 = st.columns(3)
        
        with e1:
            fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
            fab_val = st.session_state.dados.get('fabricante', 'Carrier')
            fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx, key="fab_f")
            st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados.get('modelo', ''), key="mod_f")
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], key="stat_f")

        with e2:
            st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados.get('serie_evap', ''), key="sevap_f")
            st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados.get('serie_cond', ''), key="scond_f")
            st.session_state.dados['local_evap'] = st.text_input("Local Evaporadora:", value=st.session_state.dados.get('local_evap', ''), key="levap_f")

        with e3:
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "60.000"], index=1, key="cap_f")
            
            # --- FIX: O CAMPO FLUIDO QUE NÃO RESETA ---
            lista_fluidos = ["R410A", "R134a", "R22", "R32", "R290"]
            f_atual = st.session_state.dados.get('fluido', 'R410A')
            f_idx = lista_fluidos.index(f_atual) if f_atual in lista_fluidos else 0
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", lista_fluidos, index=f_idx, key="fluid_f")
            
            st.session_state.dados['tipo_servico'] = st.selectbox("Serviço:", ["Preventiva", "Corretiva", "Instalação"], key="serv_f")
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados.get('tag_id', ''), key="tag_f")

def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    
    # Dados baseados em tabelas PT de precisão (Danfoss/RefTools)
    tabelas = {
        "R410A": {
            "xp": [90.0, 100.0, 110.0, 122.7, 130.9, 141.7, 150.0, 350.0, 450.0],
            "fp": [-3.50, -0.29, 2.36, 5.50, 7.40, 9.80, 11.50, 41.50, 54.00]
        },
        "R32": {
            "xp": [90.0, 100.0, 115.0, 140.0, 170.0, 380.0, 480.0],
            "fp": [-3.66, -0.87, 3.00, 8.50, 14.80, 44.00, 56.50]
        },
        "R22": {
            "xp": [50.0, 60.0, 70.0, 80.0, 100.0, 200.0, 250.0],
            "fp": [-3.00, 1.50, 5.80, 9.70, 16.50, 38.50, 48.00]
        },
        "R134a": {
            "xp": [20.0, 30.0, 40.0, 50.0, 70.0, 150.0, 200.0],
            "fp": [-8.00, 1.50, 9.50, 16.20, 27.50, 53.00, 65.50]
        },
        "R290": {
            "xp": [40.0, 50.0, 65.0, 80.0, 100.0, 150.0, 190.0],
            "fp": [-10.5, -4.2, 3.50, 10.20, 17.50, 32.50, 42.00]
        }
    }

    if g not in tabelas: return 0.0
    
    xp = tabelas[g]["xp"]
    fp = tabelas[g]["fp"]

    # Interpolação Linear para precisão decimal
    return float(np.interp(p, xp, fp))

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO FINAL CONSOLIDADA E ESTILIZADA)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # --- CONFIGURAÇÃO DE ESTILO (DESTAQUE VERDE) ---
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.markdown("""
        <style>
        /* Estilo para números grandes e destacados */
        div[data-testid="stMetricValue"] > div {
            font-size: 2rem !important;
            color: #00e676 !important;
            font-weight: bold;
        }
        /* Alerta para Superaquecimento crítico */
        .sh-alerta {
            background-color: #ff1744; color: white; padding: 10px;
            border-radius: 8px; text-align: center; font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. ENTRADA DE DADOS (MEDIÇÕES) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", key="ps_v3")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", key="ts_v3")
    with c2:
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", key="pd_v3")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", key="tl_v3")
    with c3:
        v_lin = st.number_input("Tens. Linha (V)", value=220.0, key="vl_v3")
        v_med = st.number_input("Tens. Medida (V)", value=220.0, key="vm_v3")
    with c4:
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", key="tr_v3")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", key="ti_v3")
        rla = st.number_input("RLA (A)", value=0.0, key="rla_v3")
        i_med = st.number_input("Corr. Medida (A)", value=0.0, key="im_v3")
    with c5:
        cn_c = st.number_input("C. Nom. Comp", value=0.0, key="cnc_v3")
        cm_c = st.number_input("C. Lido Comp", value=0.0, key="cmc_v3")
        cn_f = st.number_input("C. Nom. Fan", value=0.0, key="cnf_v3")
        cm_f = st.number_input("C. Lido Fan", value=0.0, key="cmf_v3")

    # --- 2. PROCESSAMENTO DOS CÁLCULOS ---
    t_sat_s = f_sat_precisao(p_suc, fluido)
    t_sat_d = f_sat_precisao(p_des, fluido)
    
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dif_v = v_lin - v_med
    dt_ar = (t_ret - t_ins) if (t_ret > 0 and t_ins > 0) else 0.0
    dif_i = i_med - rla
    d_comp = cm_c - cn_c
    d_fan = cm_f - cn_f

    # --- 3. RESULTADOS CALCULADOS (ORDEM DO RASCUNHO) ---
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    
    # --- PRIMEIRA LINHA ---
    l1 = st.columns(5)
    with l1[0]: # SH TOTAL
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div class="sh-alerta">SH: {sh:.1f} K<br>⚠️ RISCO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH TOTAL", f"{sh:.1f} K")
    l1[1].metric("SAT. BAIXA", f"{t_sat_s:.1f} °C")
    l1[2].metric("Δ TENSÃO", f"{dif_v:.1f} V")
    l1[3].metric("ΔT (AR)", f"{dt_ar:.2f} °C")
    l1[4].metric("Δ CAP. COMP", f"{d_comp:.1f} µF")

    # --- SEGUNDA LINHA ---
    l2 = st.columns(5)
    l2[0].metric("SC FINAL", f"{sc:.1f} K")
    l2[1].metric("SAT. ALTA", f"{t_sat_d:.1f} °C")
    l2[2].metric("Δ CORRENTE", f"{dif_i:.2f} A")
    l2[3].metric("COP", "0.00") # Espaço para cálculo de eficiência
    l2[4].metric("Δ FAN", f"{d_fan:.1f} µF")

    # --- 4. PARECER TÉCNICO ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.text_area("Diagnóstico Final:", value=st.session_state.dados.get('laudo_diag', ''), key="laudo_final_v3")

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


# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================
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
    renderizar_aba_1() # Chama a função que contém todo o código da Aba 1

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
