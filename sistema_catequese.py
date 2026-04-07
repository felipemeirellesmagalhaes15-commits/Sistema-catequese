import streamlit as st
import pandas as pd
import psycopg2
from datetime import date

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

    st.title("📖 Sistema da Catequese")
    st.subheader("Paróquia Nossa Senhora da Conceição de Avelar")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        cursor.execute(
            "SELECT usuario FROM usuarios WHERE usuario=%s AND senha=%s",
            (usuario, senha)
        )

        resultado = cursor.fetchone()

        if resultado:

            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    tela_login()
    st.stop()

# ----------------------------
# INTERFACE
# ----------------------------

st.sidebar.success(f"Usuário: {st.session_state['usuario']}")

if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.title("📖 Paróquia Nossa Senhora da Conceição de Avelar")

# ----------------------------
# MENU PRINCIPAL
# ----------------------------

menu_principal = st.sidebar.selectbox(
    "Menu",
    [
        "Selecione",
        "Cadastros",
        "Consultas",
        "Rotinas"
    ]
)

submenu = None

# ----------------------------
# SUBMENUS
# ----------------------------

if menu_principal == "Cadastros":

    submenu = st.sidebar.selectbox(
        "Cadastros",
        [
            "Selecione",
            "Cadastro de Catequizando",
            "Cadastro de Usuários"
        ]
    )

elif menu_principal == "Consultas":

    submenu = st.sidebar.selectbox(
        "Consultas",
        [
            "Selecione",
            "Lista de Catequizandos",
            "Relatório de Faltas"
        ]
    )

elif menu_principal == "Rotinas":

    submenu = st.sidebar.selectbox(
        "Rotinas",
        [
            "Selecione",
            "Registro de Presença"
        ]
    )

# ----------------------------
# TELA INICIAL
# ----------------------------

if menu_principal == "Selecione":

    st.subheader("📊 Painel da Catequese")

    # TOTAL CATEQUIZANDOS
    cursor.execute("SELECT COUNT(*) FROM catequizandos")
    total_catequizandos = cursor.fetchone()[0]

    # TOTAL TURMAS
    cursor.execute("SELECT COUNT(DISTINCT turma) FROM catequizandos")
    total_turmas = cursor.fetchone()[0]

    # TOTAL PRESENÇAS
    cursor.execute("SELECT COUNT(*) FROM presenca WHERE presenca='P'")
    total_presencas = cursor.fetchone()[0]

    # TOTAL FALTAS
    cursor.execute("SELECT COUNT(*) FROM presenca WHERE presenca='F'")
    total_faltas = cursor.fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Catequizandos", total_catequizandos)

    with col2:
        st.metric("Turmas", total_turmas)

    with col3:
        st.metric("Presenças", total_presencas)

    with col4:
        st.metric("Faltas", total_faltas)

    st.divider()

    st.info("Utilize o menu lateral para acessar os cadastros, consultas e rotinas.")

# ----------------------------
# CADASTRO CATEQUIZANDO
# ----------------------------

elif submenu == "Cadastro de Catequizando":

    st.subheader("Cadastro de Catequizando")

    nome = st.text_input("Nome")
    turma = st.text_input("Turma")

    comunidade = st.selectbox(
        "Comunidade",
        ["Avelar", "Granja", "Antonio Joaquim", "Vista Alegre", "Saudade"]
    )

    telefone = st.text_input("Telefone")

    sacramento = st.selectbox(
        "Sacramento",
        ["Primeira Eucaristia", "Crisma"]
    )

    data_cadastro = st.date_input("Data do Cadastro", date.today())

    st.text(f"Data selecionada: {data_cadastro.strftime('%d/%m/%Y')}")

    if st.button("Salvar"):

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
# LISTA CATEQUIZANDOS
# ----------------------------

elif submenu == "Lista de Catequizandos":

    st.subheader("Lista de Catequizandos")

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
# REGISTRO PRESENÇA
# ----------------------------

elif submenu == "Registro de Presença":

    st.subheader("Registro de Presença")

    data_encontro = st.date_input("Data do encontro", date.today())

    st.text(f"Data do encontro: {data_encontro.strftime('%d/%m/%Y')}")

    cursor.execute("SELECT DISTINCT turma FROM catequizandos")

    turmas = [t[0] for t in cursor.fetchall()]

    turma = st.selectbox("Selecione a turma", turmas)

    cursor.execute(
        "SELECT nome FROM catequizandos WHERE turma=%s",
        (turma,)
    )

    alunos = cursor.fetchall()

    presencas = []

    for aluno in alunos:

        presente = st.checkbox(aluno[0])

        presencas.append((aluno[0], "P" if presente else "F"))

    if st.button("Salvar Presença"):

        for nome, status in presencas:

            try:

                cursor.execute(
                    """
                    INSERT INTO presenca
                    (data,nome,turma,presenca)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (data_encontro, nome, turma, status)
                )

            except psycopg2.errors.UniqueViolation:

                conn.rollback()

                st.warning(f"{nome} já possui presença registrada nesta data.")

        conn.commit()

        st.success("Presença registrada!")

# ----------------------------
# CADASTRO USUÁRIOS
# ----------------------------

elif submenu == "Cadastro de Usuários":

    st.subheader("Cadastro de Usuários")

    nome = st.text_input("Nome do usuário")
    usuario = st.text_input("Login")
    senha = st.text_input("Senha", type="password")

    perfil = st.selectbox(
        "Perfil",
        ["admin", "catequista"]
    )

    if st.button("Salvar usuário"):

        cursor.execute(
            """
            INSERT INTO usuarios (usuario, senha, nome, perfil)
            VALUES (%s,%s,%s,%s)
            """,
            (usuario, senha, nome, perfil)
        )

        conn.commit()

        st.success("Usuário cadastrado com sucesso!")

    st.subheader("Usuários cadastrados")

    cursor.execute("""
    SELECT id,nome,usuario,perfil
    FROM usuarios
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "ID",
            "Nome",
            "Usuário",
            "Perfil"
        ]
    )

    st.dataframe(df, use_container_width=True)

# ----------------------------
# RELATÓRIO FALTAS
# ----------------------------

elif submenu == "Relatório de Faltas":

    st.subheader("Relatório de Faltas")

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