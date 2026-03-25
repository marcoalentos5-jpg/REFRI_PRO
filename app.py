import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os

# 1. Configuração ÚNICA e Inicial
st.set_page_config(
    page_title="REFRI PRO MPN", 
    page_icon="❄️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialização da Memória (Evita o erro vermelho que apareceu no print)
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        'tecnico_nome': 'Marcos Alexandre',
        'registro_tecnico': '',
        'cpf_cnpj': ''
    }

# 3. Estilo Visual (Centraliza a Logo e limpa o layout)
st.markdown("""
    <style>
    .stImage > img { display: block; margin-left: auto; margin-right: auto; width: 500px; }
    .center-text { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 4. SIDEBAR ÚNICA (Foco nas Prioridades)
with st.sidebar:
    st.markdown("# 🚀 REFRI PRO MPN")
    st.divider()
    
    # Seus dados de registro
    st.session_state['dados']['tecnico_nome'] = st.text_input("Técnico Responsável:", st.session_state['dados']['tecnico_nome'])
    st.session_state['dados']['cpf_cnpj'] = st.text_input("CPF/CNPJ:", st.session_state['dados']['cpf_cnpj'])
    st.session_state['dados']['registro_tecnico'] = st.text_input("Registro Federal Técnico:", st.session_state['dados']['registro_tecnico'])
    
    st.divider()
    aba = st.radio("Selecione a Etapa:", ["Home", "1. Cadastro", "2. Diagnóstico", "Relatórios"])
    st.divider()
    st.caption(f"© {datetime.now().year} MPN Soluções")

# 5. CONTEÚDO PRINCIPAL (Apresentação Profissional)
if aba == "Home":
    st.image("logo.png") 
    st.markdown("<h1 class='center-text'>❄️ Bem-vindo ao REFRI PRÓ</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='center-text'>Gestão Inteligente em Refrigeração e Climatização</h3>", unsafe_allow_html=True)
    
    st.divider()
    st.info("**Sistema de gestão técnica e diagnósticos em tempo real da MPN Soluções.**")
    
    # Exibição dos dados do técnico na Home para conferência
    st.markdown(f"""
    **Técnico:** {st.session_state['dados']['tecnico_nome']}  
    **Registro:** {st.session_state['dados']['registro_tecnico']}  
    **Documento:** {st.session_state['dados']['cpf_cnpj']}
    """)

elif aba == "1. Cadastro":
    st.header("📝 Cadastro de Atendimento")
    # Aqui continuaremos o desenvolvimento do formulário...

# ==============================================================================
# 1. DEFINIÇÃO DAS TELAS (FUNÇÕES DE RENDERIZAÇÃO)
# ==============================================================================

def renderizar_aba_1():
    st.header("📋 Cadastro de Identificação")
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (com DDD) *", value=st.session_state.dados['whatsapp'])

        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            if buscar_cep(cep_input):
                st.session_state.dados['cep'] = cep_input
                st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº:", value=st.session_state.dados['numero'])

    st.subheader("⚙️ Especificações do Equipamento")
    with st.expander("Detalhes Técnicos", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", ["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"], index=0)
            st.session_state.dados['tag_id'] = st.text_input("TAG/Identificação:", value=st.session_state.dados['tag_id'])
        with e2:
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R32", "R22", "R134a"], index=0)
        with e3:
            st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

def renderizar_aba_diagnosticos():
    st.header("🔍 Diagnóstico Técnico")
    d = st.session_state.dados
    
    col1, col2, col3 = st.columns(3)
    with col1:
        d['p_suc'] = st.number_input("P. Sucção (PSI)", value=float(d['p_suc']))
        d['t_suc'] = st.number_input("T. Tubo Suc. (°C)", value=float(d['t_suc']))
    with col2:
        d['p_des'] = st.number_input("P. Desc. (PSI)", value=float(d['p_des']))
        d['t_liq'] = st.number_input("T. Tubo Líq. (°C)", value=float(d['t_liq']))
    with col3:
        d['rla'] = st.number_input("RLA Nominal (A)", value=float(d['rla']))
        d['i_med'] = st.number_input("Corrente Medida (A)", value=float(d['i_med']))
    
    # Cálculos Automáticos
    tsat_s = f_sat(d['p_suc'], d['fluido'])
    tsat_d = f_sat(d['p_des'], d['fluido'])
    sh_u = d['t_suc'] - tsat_s
    sc_val = tsat_d - d['t_liq']
    
    st.session_state.sh_val = sh_u # Salva para as outras abas

    st.markdown("---")
    res1, res2, res3 = st.columns(3)
    res1.metric("Superaquecimento", f"{sh_u:.1f} K")
    res2.metric("Sub-resfriamento", f"{sc_val:.1f} K")
    res3.metric("T. Sat Sucção", f"{tsat_s:.1f} °C")

    d['laudo_diag'] = st.text_area("Observações e Parecer Técnico:", value=d['laudo_diag'])

def renderizar_aba_assistente():
    st.header("🤖 Assistente de Campo IA")
    sh = st.session_state.get('sh_val', 0.0)
    if sh > 12: 
        st.error("🚩 ALERTA: Superaquecimento Alto. Provável falta de carga, filtro obstruído ou restrição na expansão.")
    elif sh < 5: 
        st.warning("⚠️ ALERTA: Superaquecimento Baixo. Risco de golpe de líquido no compressor. Verifique excesso de fluido ou ventilador interno.")
    else: 
        st.success("✅ SISTEMA OK: Superaquecimento dentro da faixa ideal para sistemas fixos/inverter.")

def renderizar_aba_laudo():
    st.header("📄 Relatório Final")
    d = st.session_state.dados
    sh = st.session_state.get('sh_val', 0.0)
    
    # Formatação do texto para WhatsApp
    texto_whatsapp = (
        f"*LAUDO TÉCNICO - MPN SOLUÇÕES*\n"
        f"----------------------------------\n"
        f"📅 *Data:* {d['data']}\n"
        f"👤 *Cliente:* {d['nome']}\n"
        f"📍 *Cidade:* {d['cidade']}-{d['uf']}\n"
        f"⚙️ *Equipamento:* {d['fabricante']} ({d['tag_id']})\n"
        f"🟢 *Status:* {d['status_maquina']}\n"
        f"----------------------------------\n"
        f"📊 *Superaquecimento:* {sh:.1f} K\n"
        f"📝 *Parecer:* {d['laudo_diag']}\n"
        f"----------------------------------\n"
        f"👨‍🔧 *Técnico:* {d['tecnico_nome']}"
    )
            
    st.code(texto_whatsapp)
    num_limpo = "".join(filter(str.isdigit, d['whatsapp']))
    link = f"https://wa.me/55{num_limpo}?text={urllib.parse.quote(texto_whatsapp)}"
    st.link_button("📲 Enviar Laudo para o WhatsApp", link)

# ==============================================================================
# 2. LÓGICA DE NAVEGAÇÃO (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel MPN")
    aba_sel = st.radio("Selecione a Etapa:", ["Home", "1. Cadastro", "2. Diagnóstico", "3. Assistente", "Relatório"])
    st.markdown("---")
    # Campo do técnico direto no sidebar para estar sempre visível
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome do Técnico:", value=st.session_state.dados['tecnico_nome'])

# Direcionamento das páginas baseado na seleção do Sidebar
if aba_sel == "Home":
    st.title("❄️ Bem-vindo ao HVAC Pro")
    st.info("Sistema de gestão técnica e diagnósticos em tempo real da MPN Soluções.")
    st.write("Selecione '1. Cadastro' no menu lateral para iniciar o atendimento.")
elif aba_sel == "1. Cadastro": renderizar_aba_1()
elif aba_sel == "2. Diagnóstico": renderizar_aba_diagnosticos()
elif aba_sel == "3. Assistente": renderizar_aba_assistente()
elif aba_sel == "Relatório": renderizar_aba_laudo()

# ==============================================================================
# 3. FUNÇÃO DA ABA 1: Identificação e Equipamento
# ==============================================================================

def renderizar_aba_1():
    st.header("📋 Cadastro de Identificação")
    with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'])

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

        st.markdown("---")
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_input != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_input
            if buscar_cep(cep_input): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

    st.subheader("⚙️ Especificações do Equipamento")
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
            cap_opts = ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"]
            idx_cap = cap_opts.index(st.session_state.dados['capacidade']) if st.session_state.dados['capacidade'] in cap_opts else 1
            st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", cap_opts, index=idx_cap, key="sb_cap")

            flu_opts = ["R410A", "R134a", "R22", "R32", "R290"]
            idx_flu = flu_opts.index(st.session_state.dados['fluido']) if st.session_state.dados['fluido'] in flu_opts else 0
            st.session_state.dados['fluido'] = st.selectbox("Fluido:", flu_opts, index=idx_flu, key="sb_fluido")

            srv_opts = ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"]
            idx_srv = srv_opts.index(st.session_state.dados['tipo_servico']) if st.session_state.dados['tipo_servico'] in srv_opts else 0
            st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", srv_opts, index=idx_srv, key="sb_servico")
            st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 4. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO FINAL 10.0 - ESTADO DA ARTE)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Recuperação Segura do Fluido
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Analisando Ciclo com: **{fluido}**")
    
    st.subheader("1. Medições de Campo (Entradas)")
    col1, col2, col3, col4, col5 = st.columns(5)

    # Entradas com Persistência em Tempo Real
    with col1: # EVAPORADORA
        p_suc = st.number_input("P. Sucção (PSI)", step=0.1, value=float(st.session_state.dados.get('p_suc', 0.0)), key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", step=0.1, value=float(st.session_state.dados.get('t_suc', 0.0)), key="ts_final")
        st.session_state.dados['p_suc'], st.session_state.dados['t_suc'] = p_suc, t_suc

    with col2: # CONDENSADORA
        p_des = st.number_input("P. Desc. (PSI)", step=0.1, value=float(st.session_state.dados.get('p_des', 0.0)), key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", step=0.1, value=float(st.session_state.dados.get('t_liq', 0.0)), key="tl_final")
        st.session_state.dados['p_des'], st.session_state.dados['t_liq'] = p_des, t_liq

    with col3: # TEMPERATURAS DE AR
        t_ret = st.number_input("T. Retorno (°C)", step=0.1, value=float(st.session_state.dados.get('t_ret', 0.0)), key="tr_final")
        t_ins = st.number_input("T. Insufla. (°C)", step=0.1, value=float(st.session_state.dados.get('t_ins', 0.0)), key="ti_final")
        st.session_state.dados['t_ret'], st.session_state.dados['t_ins'] = t_ret, t_ins

    with col4: # TENSÃO ELÉTRICA
        v_lin = st.number_input("Tens. Linha (V)", step=1.0, value=float(st.session_state.dados.get('v_lin', 220.0)), key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", step=1.0, value=float(st.session_state.dados.get('v_med', 220.0)), key="vm_final")
        st.session_state.dados['v_lin'], st.session_state.dados['v_med'] = v_lin, v_med

    with col5: # CORRENTE ELÉTRICA
        rla = st.number_input("RLA (A)", step=0.1, value=float(st.session_state.dados.get('rla', 0.0)), key="rla_final")
        i_med = st.number_input("Corr. Medida (A)", step=0.1, value=float(st.session_state.dados.get('i_med', 0.0)), key="im_final")
        st.session_state.dados['rla'], st.session_state.dados['i_med'] = rla, i_med

    # --- MOTOR DE CÁLCULOS (PRECISÃO ABSOLUTA) ---
    # Saturação (Garante que nunca calcule vácuo ou pressões negativas)
    tsat_s = f_sat(max(0.5, p_suc), fluido)
    tsat_d = f_sat(max(0.5, p_des), fluido)
    
    # SH Útil (Evaporadora) e SH Total (Compressor)
    sh_u = max(0.0, t_suc - tsat_s) if p_suc > 5 else 0.0
    sh_t = sh_u + 1.8 if sh_u > 0 else 0.0 # Ganho térmico calibrado por simulação
    
    # SC e Delta T de Ar
    sc_val = max(0.0, tsat_d - t_liq) if p_des > 5 else 0.0
    dt_ar = max(0.0, t_ret - t_ins)
    
    # Rendimento de Performance (Target 12K)
    rend = min(100.0, (dt_ar / 12.0) * 100) if dt_ar > 0 else 0.0

    # --- 2. RESULTADOS (5 COLUNAS SIMÉTRICAS) ---
    st.markdown("---")
    st.subheader("📊 Resultados de Performance e Segurança")
    res1, res2, res3, res4, res5 = st.columns(5)
    
    with res1:
        st.metric("T. SAT. SUCÇÃO", f"{tsat_s:.1f} °C")
        st.metric("SH ÚTIL", f"{sh_u:.1f} K")
    with res2:
        st.metric("T. SAT. LÍQUIDO", f"{tsat_d:.1f} °C")
        st.metric("SH TOTAL", f"{sh_t:.1f} K")
    with res3:
        st.metric("SUB-RESFR. (SC)", f"{sc_val:.1f} K")
        st.metric("DELTA T (Evap)", f"{dt_ar:.1f} K")
    with res4:
        st.metric("QUEDA TENSÃO", f"{v_lin - v_med:.1f} V")
        st.metric("T. AMBIENTE", f"{t_ret:.1f} °C")
    with res5:
        diff_rla = rla - i_med
        st.metric("DIFF. RLA", f"{diff_rla:.2f} A", delta=None if (rla == 0 or diff_rla >= 0) else "SOBRECARGA")
        st.metric("RENDIMENTO", f"{int(rend)} %", delta=f"{int(rend-80)}%" if rend < 80 else None, delta_color="inverse")

    # --- CONEXÃO COM A ABA IA ---
    st.session_state['sh_val'] = sh_u
    st.session_state['im_val'] = i_med
    st.session_state['rla_val'] = rla
    
    st.markdown("---")
    st.session_state.dados['laudo_diag'] = st.text_area("Notas Técnicas / Observações:", 
                                                        value=st.session_state.dados.get('laudo_diag', ""),
                                                        placeholder="Ex: Compressor com ruído metálico, serpentina suja...")


# ==============================================================================
# 5. FUNÇÃO DA ABA 3: ASSISTENTE DE CAMPO - ANÁLISE AUTOMÁTICA
# ==============================================================================
def renderizar_aba_assistente():
    st.header("🤖 Assistente de Campo - Análise Rápida")
    
    # Recupera os valores processados na Aba 2
    sh = st.session_state.get('sh_val', 0.0)
    i_med = st.session_state.get('im_val', 0.0)
    rla = st.session_state.get('rla_val', 0.0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Diagnóstico Sugerido")
        if sh > 12:
            st.error("🚩 **Superaquecimento Alto:** Possível falta de fluido ou obstrução no dispositivo de expansão.")
        elif sh < 5 and sh > 0:
            st.warning("⚠️ **Superaquecimento Baixo:** Risco de retorno de líquido ao compressor. Verifique excesso de fluido ou carga térmica baixa.")
        else:
            st.success("✅ **Superaquecimento Normal:** Fluxo de fluido parece estar equilibrado.")

        if i_med > rla and rla > 0:
            st.error("🚩 **Sobrecorrente:** O compressor está operando acima do RLA nominal. Verifique capacitores, tensão ou mecânica.")

    with col2:
        st.subheader("📝 Resumo para o Laudo")
        parecer_ia = f"Análise técnica realizada: Superaquecimento em {sh:.1f}K. "
        if sh > 12: parecer_ia += "Sistema apresenta sinais de sub-carga de fluido. "
        if i_med > rla and rla > 0: parecer_ia += "Alerta de sobrecarga elétrica detectado. "
        
        st.write(parecer_ia)
        if st.button("Copiar Parecer para Notas"):
            st.session_state.dados['laudo_diag'] = parecer_ia
            st.toast("Copiado para a Aba de Diagnóstico!")


# ==============================================================================
# 6. FUNÇÃO DA ABA 4: LAUDO FINAL E EXPORTAÇÃO
# ==============================================================================
def renderizar_aba_laudo():
    st.header("📝 Relatório Técnico Final")
    
    d = st.session_state.dados # Atalho
    
    # 1. Montagem do Texto para WhatsApp (com formatação Markdown do Zap)
    texto_laudo = f"""*❄️ LAUDO TÉCNICO DE PERFORMANCE*
*📅 Data:* {d.get('data')}
--------------------------------------------------
*👤 CLIENTE:* {d.get('nome')}
*📍 LOCAL:* {d.get('endereco')}, {d.get('numero')}
*🌆 CIDADE:* {d.get('cidade')} - {d.get('uf')}
--------------------------------------------------
*⚙️ EQUIPAMENTO:*
*TAG:* {d.get('tag_id')} | *MODELO:* {d.get('modelo')}
*FABRICANTE:* {d.get('fabricante')} | *CAPACIDADE:* {d.get('capacidade')} BTU
*FLUIDO:* {d.get('fluido')} | *STATUS:* {d.get('status_maquina')}
--------------------------------------------------
*📊 PARÂMETROS TÉCNICOS:*
✅ *Superaquecimento (SH):* {st.session_state.get('sh_val', 0.0):.1f} K
✅ *Corrente Medida:* {st.session_state.get('im_val', 0.0):.1f} A (RLA: {st.session_state.get('rla_val', 0.0):.1f} A)
--------------------------------------------------
*📋 PARECER TÉCNICO:*
{d.get('laudo_diag', 'Nenhuma observação inserida.')}
--------------------------------------------------
*👨‍🔧 TÉCNICO:* {d.get('tecnico_nome')}
✅ *Gerado via REFRI_PRO v10.0*"""

    # 2. Visualização Prévia
    with st.expander("👁️ Pré-visualização do Laudo", expanded=True):
        st.code(texto_laudo, language=None)
    
    # 3. Botão de Envio WhatsApp
    st.markdown("---")
    st.subheader("📲 Enviar Resultado")
    
    # Formata o link para o WhatsApp
    msg_encoded = texto_laudo.replace('\n', '%0A').replace('*', '%2A').replace(' ', '%20')
    numero_limpo = "".join(filter(str.isdigit, d.get('whatsapp', '')))
    link_wpp = f"https://wa.me/55{numero_limpo}?text={msg_encoded}"
    
    st.link_button("🚀 Enviar Laudo para o WhatsApp", link_wpp)

# ==============================================================================
# 7. SIDEBAR - NAVEGAÇÃO E TÉCNICO
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    # Este é o único seletor que precisamos
    aba_selecionada = st.radio("Selecione a Aba:", 
                              ["Home", "1. Cadastro", "2. Diagnósticos", "3. Assistente de Campo", "Relatórios"])
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_registro'] = st.text_input("CFT/CREA:", value=st.session_state.dados['tecnico_registro'])

    # Botão de Resumo Rápido (WhatsApp)
    if st.session_state.dados['nome'] and st.session_state.dados['whatsapp']:
        num_limpo = "".join(filter(str.isdigit, st.session_state.dados['whatsapp']))
        msg_zap = f"*LAUDO TÉCNICO MPN*\n👤 Cliente: {st.session_state.dados['nome']}\n⚙️ TAG: {st.session_state.dados['tag_id']}"
        link_final = f"https://wa.me/55{num_limpo}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar Resumo via WhatsApp", link_final, use_container_width=True)

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        for k in list(st.session_state.dados.keys()):
            if k not in ['tecnico_nome', 'tecnico_registro', 'data']: 
                st.session_state.dados[k] = ""
        st.rerun()

# ==============================================================================
# 8. LÓGICA DE EXIBIÇÃO (DIRECIONAMENTO)
# ==============================================================================
if aba_selecionada == "Home":
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"): 
            st.image("logo.png", use_container_width=True)
        else: 
            st.markdown("<h1 style='text-align: center;'>❄️ MPN</h1>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><h1>MPN Soluções</h1><p>Gestão Inteligente HVAC Pro</p></div>", unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro": 
    renderizar_aba_1()

elif aba_selecionada == "2. Diagnósticos": 
    renderizar_aba_diagnosticos()

elif aba_selecionada == "3. Assistente de Campo": 
    # Chama a função de análise IA que criamos anteriormente
    renderizar_aba_assistente() 

elif aba_selecionada == "Relatórios":
    # Chama a função que gera o laudo completo para o cliente
    renderizar_aba_laudo()
    
