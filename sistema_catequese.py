import streamlit as st
import pandas as pd
import psycopg2
from datetime import date

conn = psycopg2.connect(
    host="aws-1-sa-east-1.pooler.supabase.com",
    database="postgres",
    user="postgres.tepykxeozlbktzjbgzsl",
    password="T4NmeDh8W_M7@-M",
    port=6543
)

cursor = conn.cursor()


st.title("📖 Sistema de Gestão da Catequese")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Cadastrar Catequizando",
        "Lista de Catequizandos",
        "Registrar Presença",
        "Relatório de Faltas"
    ]
)

# CADASTRO
if menu == "Cadastrar Catequizando":

    st.subheader("Cadastro de Catequizando")

    nome = st.text_input("Nome")
    turma = st.text_input("Turma")
    comunidade = st.selectbox(
        "Comunidade",
        ["Avelar", "Granja", "Antonio Joaquim","Vista Alegre"]
    )
    telefone = st.text_input("Telefone")
    sacramento = st.selectbox(
        "Sacramento",
        ["Primeira Eucaristia", "Crisma"]
    )

    if st.button("Salvar"):

        cursor.execute(
            """
            INSERT INTO catequizandos
            (nome,turma,comunidade,telefone,sacramento)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (nome,turma,comunidade,telefone,sacramento)
        )

        conn.commit()

        st.success("Catequizando cadastrado!")

# LISTA
elif menu == "Lista de Catequizandos":

    cursor.execute("SELECT * FROM catequizandos")

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "ID",
            "Nome",
            "Turma",
            "Comunidade",
            "Telefone",
            "Sacramento"
        ]
    )

    st.dataframe(df)

# PRESENÇA
elif menu == "Registrar Presença":

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

        hoje = date.today()

        for nome, status in presencas:

            cursor.execute(
                """
                INSERT INTO presenca
                (data,nome,turma,presenca)
                VALUES (%s,%s,%s,%s)
                """,
                (hoje, nome, turma, status)
            )

        conn.commit()

        st.success("Presença registrada!")

# RELATÓRIO
elif menu == "Relatório de Faltas":

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

    st.dataframe(df)