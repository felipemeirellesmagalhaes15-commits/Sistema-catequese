import streamlit as st
import pandas as pd
import psycopg2
from datetime import date
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="Sistema Catequese",
    page_icon="📖",
    layout="wide"
)

# ----------------------------
# CONEXÃO BANCO
# ----------------------------

conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"],
    port=st.secrets["DB_PORT"]
)

cursor = conn.cursor()

# ----------------------------
# LOGIN
# ----------------------------

def tela_login():

    st.markdown("""
    <div style='text-align:center'>
    <h1>📖 Sistema da Catequese</h1>
    <h3>Paróquia Nossa Senhora da Conceição de Avelar</h3>
    </div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        cursor.execute(
            "SELECT usuario,perfil FROM usuarios WHERE usuario=%s AND senha=%s",
            (usuario, senha)
        )

        resultado = cursor.fetchone()

        if resultado:

            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["perfil"] = resultado[1]

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")


if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    tela_login()
    st.stop()

# ----------------------------
# SIDEBAR
# ----------------------------

with st.sidebar:

    st.markdown("### 📖 Sistema Catequese")
    st.write(f"Usuário: **{st.session_state['usuario']}**")

    menu = option_menu(
        "Menu",
        [
            "Dashboard",
            "Cadastro Turmas",
            "Cadastro Catequizando",
            "Cadastro Usuários",
            "Lista Catequizandos",
            "Lista Catequistas",
            "Registro Presença",
            "Relatório Faltas"
        ],
        icons=[
            "bar-chart",
            "house",
            "person-plus",
            "people",
            "table",
            "person-badge",
            "check-square",
            "exclamation-triangle"
        ],
        default_index=0,
    )

    if st.button("🚪 Sair"):
        st.session_state["logado"] = False
        st.rerun()

# ----------------------------
# DASHBOARD
# ----------------------------

if menu == "Dashboard":

    st.title("📊 Painel da Catequese")

    cursor.execute("SELECT COUNT(*) FROM catequizandos")
    total_catequizandos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM turmas")
    total_turmas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM presenca WHERE presenca='P'")
    total_presencas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM presenca WHERE presenca='F'")
    total_faltas = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Catequizandos", total_catequizandos)
    col2.metric("🏫 Turmas", total_turmas)
    col3.metric("✅ Presenças", total_presencas)
    col4.metric("❌ Faltas", total_faltas)

    st.info("Use o menu lateral para acessar as funcionalidades.")

# ----------------------------
# CADASTRO TURMAS
# ----------------------------

elif menu == "Cadastro Turmas":

    st.header("🏫 Cadastro de Turmas")

    nome = st.text_input("Nome da Turma")

    comunidade = st.selectbox(
        "Comunidade",
        ["Avelar", "Granja", "Antonio Joaquim", "Vista Alegre", "Saudade"]
    )

    catequista = st.text_input("Catequista responsável")

    if st.button("Salvar Turma"):

        cursor.execute(
            """
            INSERT INTO turmas (nome,comunidade,catequista)
            VALUES (%s,%s,%s)
            """,
            (nome, comunidade, catequista)
        )

        conn.commit()

        st.success("Turma cadastrada!")

# ----------------------------
# CADASTRO CATEQUIZANDO
# ----------------------------

elif menu == "Cadastro Catequizando":

    st.header("👤 Cadastro de Catequizando")

    cursor.execute("SELECT nome FROM turmas")
    turmas = [t[0] for t in cursor.fetchall()]

    col1, col2 = st.columns(2)

    with col1:
        nome = st.text_input("Nome")
        turma = st.selectbox("Turma", turmas)
        telefone = st.text_input("Telefone")

    with col2:
        comunidade = st.selectbox(
            "Comunidade",
            ["Avelar", "Granja", "Antonio Joaquim", "Vista Alegre", "Saudade"]
        )

        sacramento = st.selectbox(
            "Sacramento",
            ["Primeira Eucaristia", "Crisma"]
        )

        data_cadastro = st.date_input("Data do Cadastro", date.today())

    if st.button("💾 Salvar"):

        cursor.execute(
            """
            INSERT INTO catequizandos
            (nome,turma,comunidade,telefone,sacramento,data_cadastro)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (nome, turma, comunidade, telefone, sacramento, data_cadastro)
        )

        conn.commit()

        st.success("Catequizando cadastrado!")

# ----------------------------
# CADASTRO USUÁRIOS
# ----------------------------

elif menu == "Cadastro Usuários":

    st.header("🔐 Cadastro de Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Login")
    senha = st.text_input("Senha", type="password")

    perfil = st.selectbox("Perfil", ["admin", "catequista"])

    cursor.execute("SELECT nome FROM turmas")
    turmas = [t[0] for t in cursor.fetchall()]

    turma_permitida = st.selectbox("Turma Permitida", turmas)

    comunidade = st.selectbox(
        "Comunidade Permitida",
        ["Avelar", "Granja", "Antonio Joaquim", "Vista Alegre", "Saudade"]
    )

    if st.button("Salvar usuário"):

        cursor.execute(
            """
            INSERT INTO usuarios
            (usuario,senha,nome,perfil,turma_permitida,comunidade_permitida)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (usuario, senha, nome, perfil, turma_permitida, comunidade)
        )

        conn.commit()

        st.success("Usuário cadastrado!")

# ----------------------------
# LISTA CATEQUIZANDOS
# ----------------------------

elif menu == "Lista Catequizandos":

    st.header("📋 Lista de Catequizandos")

    cursor.execute("""
    SELECT
    id,
    nome,
    turma,
    comunidade,
    telefone,
    sacramento,
    TO_CHAR(data_cadastro,'DD/MM/YYYY')
    FROM catequizandos
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "ID",
            "Nome",
            "Turma",
            "Comunidade",
            "Telefone",
            "Sacramento",
            "Data Cadastro"
        ]
    )

    st.dataframe(df, use_container_width=True)

# ----------------------------
# LISTA CATEQUISTAS
# ----------------------------

elif menu == "Lista Catequistas":

    st.header("👨‍🏫 Lista de Catequistas")

    cursor.execute("""
    SELECT nome,usuario,perfil,comunidade_permitida,turma_permitida
    FROM usuarios
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "Nome",
            "Usuário",
            "Perfil",
            "Comunidade",
            "Turma"
        ]
    )

    st.dataframe(df, use_container_width=True)

# ----------------------------
# REGISTRO PRESENÇA
# ----------------------------

elif menu == "Registro Presença":

    st.header("✅ Registro de Presença")

    data_encontro = st.date_input("Data do encontro", date.today())

    cursor.execute("SELECT nome FROM turmas")
    turmas = [t[0] for t in cursor.fetchall()]

    turma = st.selectbox("Turma", turmas)

    cursor.execute(
        "SELECT nome FROM catequizandos WHERE turma=%s",
        (turma,)
    )

    alunos = cursor.fetchall()

    presencas = []

    for aluno in alunos:

        presente = st.checkbox(aluno[0])

        presencas.append((aluno[0], "P" if presente else "F"))

    if st.button("Registrar"):

        for nome, status in presencas:

            cursor.execute(
                """
                INSERT INTO presenca
                (data,nome,turma,presenca)
                VALUES (%s,%s,%s,%s)
                """,
                (data_encontro, nome, turma, status)
            )

        conn.commit()

        st.success("Presença registrada!")

# ----------------------------
# RELATÓRIO FALTAS
# ----------------------------

elif menu == "Relatório Faltas":

    st.header("⚠ Relatório de Faltas")

    cursor.execute(
        """
        SELECT nome, COUNT(*)
        FROM presenca
        WHERE presenca='F'
        GROUP BY nome
        """
    )

    dados = cursor.fetchall()

    df = pd.DataFrame(dados, columns=["Nome", "Faltas"])

    st.dataframe(df, use_container_width=True)