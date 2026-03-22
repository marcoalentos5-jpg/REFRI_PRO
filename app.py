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
# 1. FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO COM LAYOUT E MÁSCARAS)
# ==============================================================================
def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            # --- CAMPOS COM FORMATAÇÃO (Máscaras sugeridas via placeholder) ---
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
            
            # Formatação CPF/CNPJ
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
            
            # Formatação WhatsApp
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

            st.markdown("---")
            
            # --- SEÇÃO ENDEREÇO (LINHA 1) ---
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
            if cep_input != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_input
                if buscar_cep(cep_input): st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

            # --- SEÇÃO ENDEREÇO (LINHA 2 - TUDO JUNTO) ---
            # Dividindo em 4 colunas para caber Complemento, Bairro, Cidade e UF
            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp_v2")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro_v2")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid_v2")
            
            # UF com limite de 2 caracteres e alinhado na mesma linha
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf_v2")

        # --- SEÇÃO EQUIPAMENTO ---
        col_titulo, col_data = st.columns([3, 1])
        with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
        with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

        with st.expander("Detalhes Técnicos do Ativo", expanded=True):
            e1, e2, e3 = st.columns(3)
            with e1:
                fab_list = sorted(["Carrier", "Daikin", "Elgin", "Gree", "Fujitsu", "hitachi", "LG", "Midea", "Philco", "Samsung", "TCL", "Trane", "York"])
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
                # 1. CAPACIDADE (COM TRAVA DE MEMÓRIA)
                caps = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
                idx_cap = caps.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in caps else 1
                st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", caps, index=idx_cap, key="cap_fix_v1")

                # 2. FLUIDO (R32 PRIMEIRO + TRAVA DE MEMÓRIA)
                opcoes_fluido = ["R32", "R410A", "R134a", "R22", "R290"]
                idx_f = opcoes_fluido.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in opcoes_fluido else 0
                st.session_state.dados['fluido'] = st.selectbox("Fluido:", opcoes_fluido, index=idx_f, key="gas_fix_v1")

                # 3. TIPO DE SERVIÇO (COM TRAVA DE MEMÓRIA)
                servs = ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"]
                idx_serv = servs.index(st.session_state.dados['tipo_servico']) if st.session_state.dados['tipo_servico'] in servs else 0
                st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", servs, index=idx_serv, key="serv_fix_v1")

                # 4. TAG (COM KEY ÚNICA)
                st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'], key="tag_fix_v1")

                # === FIM DO BLOCO COPIADO ===
                

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO V17 - MATRIZ DE PRECISÃO REAL)
# ==============================================================================

import streamlit as st
import math

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico (Precisão V17)")
    
    # Busca o fluido global. Se não existir, assume R410A
    fluido = st.session_state.dados.get('fluido', 'R410A')

    # --- CSS: ESTILO HI-VIS COM ALERTAS E TEXTO PRETO ---
    st.markdown("""
        <style>
        .res-card { 
            background-color: #ffffff; padding: 15px; border-radius: 10px; 
            text-align: center; min-height: 150px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
            display: flex; flex-direction: column; justify-content: center;
            border-top: 6px solid #1b5e20; 
        }
        .label-res { font-size: 14px; font-weight: 800; color: #333; text-transform: uppercase; margin-bottom: 8px; }
        .valor-res { font-size: 28px; font-weight: 900; color: #1b5e20; margin: 2px 0; }
        .sub-res { font-size: 13px; color: #d32f2f; font-weight: 700; border-top: 2px dotted #eee; padding-top: 8px; margin-top: 5px; }
        
        /* Cores dos Cards */
        .card-bom { border-top-color: #81c784 !important; }
        .card-alerta { border-top-color: #fff176 !important; }
        .card-critico { border-top-color: #e57373 !important; }
        
        /* Ajuste de cor de fonte para alertas específicos */
        .card-alerta .valor-res { color: #fbc02d !important; }
        .card-critico .valor-res { color: #d32f2f !important; }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. MEDIÇÕES DE CAMPO (6 COLUNAS) ---
    st.subheader("1. Medições de Campo")
    
    # Definição dinâmica de valores padrão baseada no Fluido
    if fluido == "R22":
        p_suc_def, p_des_def = 65.0, 210.0
    else:
        p_suc_def, p_des_def = 134.0, 340.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown("🟢 **AR**")
        t_ret = st.number_input("T. Retorno (°C)", value=24.0, step=0.1, key="tr_v17")
        t_ins = st.number_input("T. Insuf. (°C)", value=12.0, step=0.1, key="ti_v17")
    with c2:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", value=p_suc_def, format="%.1f", key="ps_v17")
        t_suc = st.number_input("T. Tubo Suc. (°C)", value=14.0, format="%.1f", key="ts_v17")
    with c3:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", value=p_des_def, format="%.1f", key="pd_v17")
        t_liq = st.number_input("T. Tubo Líq. (°C)", value=38.0, format="%.1f", key="tl_v17")
    with c4:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", value=220.0, key="vl_v17")
        v_med = st.number_input("Tens. Medida (V)", value=218.0, key="vm_v17")
    with c5:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", value=10.0, key="rla_v17")
        i_med = st.number_input("Corr. Medida (A)", value=9.5, key="im_v17")
    with c6:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("Nominal (µF)", value=35.0, key="cnc_v17")
        cm_c = st.number_input("Medida (µF)", value=33.0, key="cmc_v17")

    # --- MOTOR V28: MATRIZ DE PRECISÃO REAL (R22, R32 & R410A) ---
    def f_sat_v17(psi, gas):
        if psi <= 5: return 0.0
        if gas == "R22":
            # Fórmula Polinomial Calibrada R22 (Erro < 0.5 PSI)
            tsat = (-0.0004 * (psi**2)) + (0.453 * psi) - 24.95
        elif gas == "R32":
            tsat = (0.000305 * (psi**2)) + (0.1572 * psi) - 19.64
        else: # R410A
            tsat = (0.000285 * (psi**2)) + (0.15735 * psi) - 18.88
        return round(tsat, 1)

    # Cálculos de Performance
    ts_s = f_sat_v17(p_suc, fluido)
    ts_d = f_sat_v17(p_des, fluido)
    sh = round(t_suc - ts_s, 1)
    sc = round(ts_d - t_liq, 1)
    dt_ar = round(t_ret - t_ins, 1)

    # --- 2. RESULTADOS DO DIAGNÓSTICO (6 COLUNAS) ---
    st.markdown("---")
    st.subheader("2. Resultados do Diagnóstico")
    res_cols = st.columns(6)

    # Lógica de Alerta de SH e Card Status
    cl_sh = "card-bom"
    if fluido == "R22":
        if p_suc < 60.0 or p_suc > 75.0: cl_sh = "card-alerta"
        if p_suc < 55.0 or p_suc > 80.0: cl_sh = "card-critico"
    elif fluido == "R32":
        cl_sh = "card-bom" if 5.5 <= sh <= 7.5 else "card-alerta"
        if sh < 5.0 or sh > 8.0: cl_sh = "card-critico"
    else: # R410A
        cl_sh = "card-bom" if 5.0 <= sh <= 12.0 else "card-critico"

    with res_cols[0]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">ΔT Ar</div><div class="valor-res">{dt_ar} °C</div><div class="sub-res">Troca</div></div>', unsafe_allow_html=True)

    with res_cols[1]:
        st.markdown(f'<div class="res-card {cl_sh}"><div class="label-res">SH Total</div><div class="valor-res">{sh} K</div><div class="sub-res">Sat: {ts_s}°C</div></div>', unsafe_allow_html=True)

    with res_cols[2]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">SC Final</div><div class="valor-res">{sc} K</div><div class="sub-res">Sat: {ts_d}°C</div></div>', unsafe_allow_html=True)

    with res_cols[3]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ Tens.</div><div class="valor-res">{round(v_lin-v_med,1)} V</div><div class="sub-res">Estável</div></div>', unsafe_allow_html=True)

    with res_cols[4]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ RLA</div><div class="valor-res">{round(i_med-rla,2)} A</div><div class="sub-res">Carga</div></div>', unsafe_allow_html=True)

    with res_cols[5]:
        st.markdown(f'<div class="res-card card-bom"><div class="label-res">Δ Cap.</div><div class="valor-res">{round(cm_c-cn_c,1)} µF</div><div class="sub-res">Saúde</div></div>', unsafe_allow_html=True)

    # --- 3. DIAGNÓSTICO INTELIGENTE (TEXTO PRETO + LÓGICA R22 INTEGRADA) ---
    diag_final = "✅ Sistema Operacional em Conformidade"
    bg_diag = "#81c784" 
    
    # LÓGICA DE DIAGNÓSTICO PARA R22 (50-85 PSI)
    if fluido == "R22":
        if p_suc < 55.0:
            diag_final = f"💀 SUPERCRÍTICO BAIXO: {p_suc} PSI. Risco de gelo imediato!"
            bg_diag = "#e57373"
        elif p_suc < 60.0:
            diag_final = f"🔴 CRÍTICO: {p_suc} PSI. Pressão abaixo do limite de projeto."
            bg_diag = "#fff176"
        elif 60.0 <= p_suc <= 75.0:
            diag_final = f"🟢 OPERAÇÃO IDEAL: {p_suc} PSI ({ts_s}°C) dentro da faixa segura."
        elif p_suc <= 80.0:
            diag_final = f"🟡 ALERTA ALTA: {p_suc} PSI. Verifique condensação externa."
            bg_diag = "#fff176"
        else:
            diag_final = f"💀 SUPERCRÍTICO ALTO: {p_suc} PSI. Sobrecarga térmica severa!"
            bg_diag = "#e57373"
            
    # LÓGICA PARA R410A / R32 (Sua lógica original preservada)
    elif p_suc <= 110.0 or p_suc >= 150.0:
        bg_diag = "#fff176"
        diag_final = f"⚠️ ALERTA: Pressão fora dos padrões de funcionamento (110-150 PSI)!"
    
    st.markdown(f"""
        <div style="background-color: {bg_diag}; padding: 18px; border-radius: 10px; color: #000000; text-align: center; font-weight: 800; font-size: 18px; margin-top: 20px; border: 1px solid rgba(0,0,0,0.1);">
            {diag_final}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("4. Parecer Técnico")
    st.text_area("Notas Adicionais:", key="laudo_v17_final", height=100)
    st.info("ℹ️ Medições concluídas. Prossiga para a aba 'Relatórios'.")

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
# --- FIM DA ABA 2 (DIAGNÓSTICOS) ---
    st.info("ℹ️ Medições concluídas. Prossiga para a aba 'Relatórios' para emitir o laudo.")

# ==============================================================================
# BLOCO 5: RELATÓRIOS E LAUDOS (LINHA 495)
# ==============================================================================
elif aba == "Relatórios":
    st.header("Relatório e Parecer Técnico")
    st.markdown("---")

    # 1. CAMPO DE TEXTO DO PARECER (EXCLUSIVO DESTA ABA)
    st.session_state.dados['parecer_tecnico'] = st.text_area(
        "Parecer Técnico Final / Notas Adicionais:",
        value=st.session_state.dados.get('parecer_tecnico', ''),
        height=300,
        placeholder="Descreva aqui o diagnóstico final e recomendações técnicas..."
    )

    # 2. FUNÇÃO DE GERAÇÃO (DEFINIDA DENTRO DO ELIF)
    def gerar_laudo_v17_final_corrigido():
        d = st.session_state.dados 
        pdf = LaudoFinalV17()
        pdf.add_page()
        
        # Estrutura do PDF
        pdf.titulo_secao_com_data("1. Responsável Técnico", d.get('data', '---'))
        pdf.grade(["NOME DO PROFISSIONAL", "REGISTRO PROFISSIONAL", "CONTATO / CNPJ"],
                 [d.get('tecnico_nome'), d.get('tecnico_registro'), d.get('tecnico_documento')], [80, 55, 55])

        pdf.titulo_secao("2. Dados do Cliente")
        pdf.grade(["CLIENTE / RAZÃO SOCIAL", "CPF / CNPJ", "E-MAIL"], 
                 [d.get('nome'), d.get('cpf_cnpj'), d.get('email')], [85, 45, 60])

        pdf.titulo_secao("3. Equipamento")
        pdf.grade(["FABRICANTE", "MODELO", "TAG / ID", "FLUIDO"],
                 [d.get('fabricante'), d.get('modelo'), d.get('tag_id'), d.get('fluido')], [50, 50, 45, 45])

        pdf.titulo_secao("4. Termodinâmica")
        pdf.grade(["P. SUCÇÃO (PSI)", "S.H. TOTAL (K)", "DELTA T AR (°C)", "T. TUBO (°C)"],
                 [d.get('ps_v17', '0.0'), d.get('sh', '0.0'), d.get('dt_ar', '0.0'), d.get('ts_v17', '0.0')], [47, 47, 47, 49])

        pdf.titulo_secao("5. Elétrica")
        pdf.grade(["TENSÃO (V)", "CORRENTE (A)", "CAPACITÂNCIA (uF)", "STATUS"],
                 [d.get('vl_v17', '0.0'), d.get('im_v17', '0.0'), d.get('cmc_v17', '---'), "OPERACIONAL"], [47, 47, 47, 49])

        pdf.titulo_secao("6. Parecer Técnico")
        obs = d.get('parecer_tecnico') or "Nenhuma observação registrada."
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(0, 6, str(obs), 1, 'L')

        # Assinaturas
        pdf.set_y(-45)
        pdf.line(20, pdf.get_y(), 90, pdf.get_y()); pdf.line(120, pdf.get_y(), 190, pdf.get_y())
        pdf.set_y(pdf.get_y() + 2)
        pdf.set_x(20); pdf.cell(70, 5, str(d.get('tecnico_nome', 'TECNICO')).upper(), 0, 0, 'C')
        pdf.set_x(120); pdf.cell(70, 5, str(d.get('nome', 'CLIENTE')).upper(), 0, 1, 'C')

        return bytes(pdf.output(dest='S'))

    # 3. BOTÃO DE GERAÇÃO (UNICO LUGAR DO CÓDIGO)
    st.write("")
    if st.button("🚀 FINALIZAR E GERAR LAUDO COMPLETO", use_container_width=True):
        try:
            pdf_out = gerar_laudo_v17_final_corrigido()
            st.success("✅ Laudo preparado!")
            st.download_button(
                label="📥 Baixar PDF Agora",
                data=pdf_out,
                file_name=f"Laudo_{st.session_state.dados.get('nome', 'Cliente')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao gerar: {e}")
