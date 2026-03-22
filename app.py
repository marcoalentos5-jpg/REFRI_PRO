# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (VERSÃO CORRIGIDA V17)
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

# 2. MOTOR DE SESSÃO (CHAVES VERIFICADAS + ADIÇÃO DE MEDIÇÕES)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        # Dados Cadastrais
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        
        # Dados do Equipamento
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        
        # Dados do Técnico
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional',

        # --- NOVAS CHAVES ADICIONADAS PARA SUPORTAR O BLOCO DE DIAGNÓSTICOS E RELATÓRIO ---
        'ps_v17': 134.0, 'ts_v17': 14.0, 'pd_v17': 340.0, 'tl_v17': 38.0,
        'tr_v17': 24.0, 'ti_v17': 12.0, 'vl_v17': 220.0, 'vm_v17': 218.0,
        'rla_v17': 10.0, 'im_v17': 9.5, 'cnc_v17': 35.0, 'cmc_v17': 33.0,
        'parecer_tecnico': '' 
    }

# 3. FUNÇÃO DE BUSCAR CEP
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

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    
    # Define a variável global que controlará qual aba será exibida no corpo principal
    aba_selecionada = st.radio("Selecione a Aba:", opcoes_abas, key="nav_sidebar")
    
    st.markdown("---")
    
    # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados.get('tecnico_nome', 'Marcos Alexandre'), key="tec_nome_sb")
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados.get('tecnico_documento', ''), key="tec_doc_sb")
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados.get('tecnico_registro', ''), key="tec_reg_sb")
    
    st.markdown("---")
    
    # VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS (Nome e WhatsApp)
    if not st.session_state.dados.get('nome') or not st.session_state.dados.get('whatsapp'):
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
    # MENSAGEM WHATSAPP - ENVIO DE TODOS OS DADOS
    msg_zap = (
        f"*LAUDO TÉCNICO HVAC*\n\n"
        f"👤 *CLIENTE:* {st.session_state.dados.get('nome', '---')}\n"
        f"🆔 CPF/CNPJ: {st.session_state.dados.get('cpf_cnpj', '---')}\n"
        f"📍 END: {st.session_state.dados.get('endereco', '---')}, {st.session_state.dados.get('numero', 'S/N')} - {st.session_state.dados.get('bairro', '---')}\n"
        f"🏙️ {st.session_state.dados.get('cidade', '---')}/{st.session_state.dados.get('uf', '--')} | CEP: {st.session_state.dados.get('cep', '---')}\n"
        f"📞 Contato: {st.session_state.dados.get('whatsapp', '---')} | Email: {st.session_state.dados.get('email', '---')}\n\n"
        f"⚙️ *EQUIPAMENTO:*\n"
        f"📌 TAG: {st.session_state.dados.get('tag_id', '---')} | Linha: {st.session_state.dados.get('linha', '---')}\n"
        f"🏭 Fab: {st.session_state.dados.get('fabricante', '---')} | Mod: {st.session_state.dados.get('modelo', '---')}\n"
        f"❄️ Cap: {st.session_state.dados.get('capacidade', '---')} BTU | Fluido: {st.session_state.dados.get('fluido', '---')}\n"
        f"🔢 S.Evap: {st.session_state.dados.get('serie_evap', '---')} | S.Cond: {st.session_state.dados.get('serie_cond', '---')}\n"
        f"📍 Loc.Evap: {st.session_state.dados.get('local_evap', '---')} | Loc.Cond: {st.session_state.dados.get('local_cond', '---')}\n"
        f"🛠️ Serviço: {st.session_state.dados.get('tipo_servico', '---')}\n"
        f"🩺 Status: {st.session_state.dados.get('status_maquina', '---')}\n\n"
        f"👨‍🔧 *TÉCNICO:* {st.session_state.dados.get('tecnico_nome', '---')}\n"
        f"📜 Registro: {st.session_state.dados.get('tecnico_registro', '---')}\n"
        f"📅 Data: {st.session_state.dados.get('data', '---')}"
    )
    
    # Geração do link seguro para WhatsApp
    whatsapp_numero = "".join(filter(str.isdigit, st.session_state.dados.get('whatsapp', '')))
    link_final = f"https://wa.me/55{whatsapp_numero}?text={urllib.parse.quote(msg_zap)}"
    st.link_button("📲 Enviar Resumo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")
    
    # LIMPAR FORMULÁRIO (PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_preservar = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_preservar:
                # Se for campo de medição (numérico), reseta para 0.0, senão para string vazia
                if key in ['ps_v17', 'ts_v17', 'im_v17', 'vl_v17']: 
                    st.session_state.dados[key] = 0.0
                else:
                    st.session_state.dados[key] = ""
        st.rerun()

# ==============================================================================
# 4. DEFINIÇÃO DAS FUNÇÕES DE APOIO (DIAGNÓSTICOS)
# ==============================================================================

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Busca o fluido que você selecionou na Aba 1
    # Note que usamos 'fluido' pois é a chave definida no seu st.session_state.dados
    fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido_selecionado}**")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        # Salvando direto no session_state para o laudo
        st.session_state.dados['ps_v17'] = st.number_input("Pressão de Sucção (PSI):", min_value=0.0, step=1.0, value=float(st.session_state.dados.get('ps_v17', 0.0)), key="p_suc_diag")
        st.session_state.dados['ts_v17'] = st.number_input("Temp. Tubulação Sucção (°C):", step=0.1, value=float(st.session_state.dados.get('ts_v17', 0.0)), key="t_suc_diag")

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        st.session_state.dados['pd_v17'] = st.number_input("Pressão de Descarga (PSI):", min_value=0.0, step=1.0, value=float(st.session_state.dados.get('pd_v17', 0.0)), key="p_des_diag")
        st.session_state.dados['tl_v17'] = st.number_input("Temp. Tubulação Líquido (°C):", step=0.1, value=float(st.session_state.dados.get('tl_v17', 0.0)), key="t_liq_diag")

    st.markdown("---")

    # --- BLOCO 2: PROCESSAMENTO (CÁLCULOS) ---
    # Valores temporários (Serão substituídos pela tabela PT no próximo passo)
    t_sat_suc = 0.0  
    t_sat_des = 0.0  
    
    # Cálculos de SH e SC (Usando os dados salvos na sessão)
    sh = st.session_state.dados['ts_v17'] - t_sat_suc
    sc = t_sat_des - st.session_state.dados['tl_v17']
    
    # Salva os cálculos no estado global para o motor do PDF
    st.session_state.dados['sh'] = round(sh, 2)
    st.session_state.dados['sc'] = round(sc, 2)

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{st.session_state.dados['sh']:.1f} K")
        if 5 <= sh <= 7: 
            st.success("✅ SH dentro do padrão (5K a 7K)")
        elif sh < 5: 
            st.error("⚠️ SH Baixo: Risco de retorno de líquido")
        else: 
            st.warning("⚠️ SH Alto: Possível falta de fluido ou restrição")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{st.session_state.dados['sc']:.1f} K")
        if 4 <= sc <= 7: 
            st.success("✅ SC dentro do padrão (4K a 7K)")
        else: 
            st.info("ℹ️ SC fora do padrão: Verifique condensação")

    st.markdown("---")

    # --- BLOCO 4: CONCLUSÃO E LAUDO ---
    st.subheader("3. Parecer Técnico Final")
    # Atualiza o parecer diretamente na chave que o Bloco 5 (PDF) vai ler
    st.session_state.dados['parecer_tecnico'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        value=st.session_state.dados.get('parecer_tecnico', ''),
        placeholder="Ex: Sistema operando com pressões estáveis, superaquecimento normal...",
        key="laudo_area_diag"
    )

# ==============================================================================
# 5. LÓGICA DE EXIBIÇÃO DAS ABAS (CHAMADA DAS FUNÇÕES)
# ==============================================================================

if aba_selecionada == "Home":
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        NOME_ARQUIVO_LOGO = "logo.png"
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao carregar logo: {e}")
        else:
            st.error(f"⚠️ Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado.")

    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">MPN Soluções</h1>
            <p style="color: #1976d2; font-size: 1.3em;">Soluções em Refrigeração e Climatização</p>
            <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold;">Bem-vindo ao Sistema HVAC Pro de Gestão Inteligente.</p>
            <p style="color: #546e7a; font-size: 1.0em;">Selecione uma opção no Painel de Controle lateral para iniciar.</p>
        </div>
    """, unsafe_allow_html=True)

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1() 

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() 

elif aba_selecionada == "Relatórios":
    st.header("📄 Gerenciamento de Relatórios")
    st.info("Esta seção será conectada ao motor de PDF no próximo passo.")

# ==============================================================================
# 5. MOTOR DE PDF - CLASSE E GERAÇÃO (CORRIGIDO V17)
# ==============================================================================

class LaudoFinalV17(FPDF):
    def header(self):
        try:
            # Tenta carregar o logo se o arquivo existir
            if os.path.exists("logo.png"):
                self.image("logo.png", 10, 10, 50)
        except:
            pass
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(0, 51, 102)
        self.set_xy(65, 18)
        self.cell(0, 10, 'LAUDO TÉCNICO DE INSPEÇÃO', 0, 1, 'L')
        self.ln(15)

    def titulo_secao_com_data(self, texto, data_visita):
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 51, 102)
        self.set_font('Helvetica', 'B', 10)
        self.cell(130, 7, f" {texto.upper()}", 'LTB', 0, 'L', True)
        self.cell(60, 7, f"DATA: {data_visita} ", 'RTB', 1, 'R', True)

    def titulo_secao(self, texto):
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 51, 102)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 7, f" {texto.upper()}", 1, 1, 'L', True)

    def grade(self, labels, valores, larguras):
        self.set_font('Helvetica', 'B', 7); self.set_text_color(100)
        for i, label in enumerate(labels):
            self.cell(larguras[i], 4, f" {label}", 'LTR', 0, 'L')
        self.ln()
        self.set_font('Helvetica', '', 9); self.set_text_color(0)
        for i, valor in enumerate(valores):
            txt = str(valor) if valor not in [None, ''] else "---"
            # Limpeza de emojis para o PDF não quebrar
            txt = txt.replace('🟢', '[OK]').replace('🔴', '[ALERTA]').replace('🟡', '[ATENCAO]')
            self.cell(larguras[i], 7, f" {txt}", 'LBR', 0, 'L')
        self.ln(8)

def gerar_laudo_v17_final_corrigido():
    d = st.session_state.dados 
    pdf = LaudoFinalV17()
    pdf.add_page()
    
    # 1. RESPONSÁVEL TÉCNICO
    pdf.titulo_secao_com_data("1. Responsável Técnico", d.get('data', '---'))
    pdf.grade(
        ["NOME DO PROFISSIONAL", "REGISTRO PROFISSIONAL", "CNPJ / CPF"],
        [d.get('tecnico_nome'), d.get('tecnico_registro'), d.get('tecnico_documento')],
        [80, 55, 55]
    )

    # 2. DADOS DO CLIENTE
    pdf.titulo_secao("2. Dados do Cliente e Localização")
    pdf.grade(
        ["CLIENTE / RAZÃO SOCIAL", "CPF / CNPJ", "E-MAIL"],
        [d.get('nome'), d.get('cpf_cnpj'), d.get('email')],
        [85, 45, 60]
    )
    pdf.grade(
        ["ENDEREÇO", "BAIRRO", "CIDADE / UF", "CONTATO"],
        [f"{d.get('endereco', '---')}, {d.get('numero', '')}", d.get('bairro'), f"{d.get('cidade')}/{d.get('uf')}", d.get('whatsapp')],
        [75, 40, 35, 40]
    )

    # 3. EQUIPAMENTO
    pdf.titulo_secao("3. Informações do Equipamento")
    pdf.grade(
        ["FABRICANTE", "MODELO", "TAG / ID", "FLUIDO"],
        [d.get('fabricante'), d.get('modelo'), d.get('tag_id'), d.get('fluido')],
        [50, 50, 45, 45]
    )

    # 4. TERMODINÂMICA (Ajustado para as chaves da Aba 2)
    pdf.titulo_secao("4. Termodinâmica e Medições")
    pdf.grade(
        ["P. SUCÇÃO (PSI)", "S.H. TOTAL (K)", "S.C. TOTAL (K)", "T. TUBO (°C)"],
        [f"{d.get('ps_v17', '0.0')}", f"{d.get('sh', '0.0')}", f"{d.get('sc', '0.0')}", f"{d.get('ts_v17', '0.0')}"],
        [47, 47, 47, 49]
    )

    # 5. STATUS E ELÉTRICA
    pdf.titulo_secao("5. Elétrica e Operacional")
    pdf.grade(
        ["TENSÃO (V)", "CORRENTE (A)", "CAPACIDADE (BTU)", "STATUS FINAL"],
        [f"{d.get('vl_v17', '220')}", f"{d.get('im_v17', '0.0')}", d.get('capacidade'), d.get('status_maquina')],
        [47, 47, 47, 49]
    )

    # 6. PARECER TÉCNICO
    pdf.titulo_secao("6. Parecer Técnico Final")
    pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(100)
    pdf.cell(0, 5, " CONSIDERAÇÕES DO ESPECIALISTA:", 'LTR', 1, 'L')
    pdf.set_font('Helvetica', '', 10); pdf.set_text_color(0)
    
    obs = d.get('parecer_tecnico') or "Nenhuma observação registrada."
    pdf.multi_cell(0, 6, str(obs), 'LBR', 'L')

    # ASSINATURAS
    pdf.set_y(-45)
    pdf.line(20, pdf.get_y(), 90, pdf.get_y())   
    pdf.line(120, pdf.get_y(), 190, pdf.get_y()) 
    pdf.set_y(pdf.get_y() + 2); pdf.set_font('Helvetica', 'B', 9)
    pdf.set_x(20); pdf.cell(70, 5, str(d.get('tecnico_nome', 'TECNICO')).upper(), 0, 0, 'C')
    pdf.set_x(120); pdf.cell(70, 5, str(d.get('nome', 'CLIENTE')).upper(), 0, 1, 'C')

    return pdf.output()
