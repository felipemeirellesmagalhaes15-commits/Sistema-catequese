import streamlit as st
import pandas as pd
from datetime import date
import os

ARQ_CATEQUIZANDOS = "catequizandos.xlsx"
ARQ_PRESENCA = "presenca.xlsx"

def carregar_catequizandos():
    if os.path.exists(ARQ_CATEQUIZANDOS):
        return pd.read_excel(ARQ_CATEQUIZANDOS)
    else:
        df = pd.DataFrame(columns=[
            "Nome",
            "Turma",
            "Comunidade",
            "Telefone",
            "Sacramento"
        ])
        df.to_excel(ARQ_CATEQUIZANDOS, index=False)
        return df

def salvar_catequizandos(df):
    df.to_excel(ARQ_CATEQUIZANDOS, index=False)

def carregar_presenca():
    if os.path.exists(ARQ_PRESENCA):
        return pd.read_excel(ARQ_PRESENCA)
    else:
        df = pd.DataFrame(columns=[
            "Data",
            "Nome",
            "Turma",
            "Presenca"
        ])
        df.to_excel(ARQ_PRESENCA, index=False)
        return df

def salvar_presenca(df):
    df.to_excel(ARQ_PRESENCA, index=False)

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

df_cate = carregar_catequizandos()

if menu == "Cadastrar Catequizando":

    st.subheader("Cadastro de Catequizando")

    nome = st.text_input("Nome")
    turma = st.text_input("Turma")
    comunidade = st.text_input("Comunidade")
    telefone = st.text_input("Telefone")
    sacramento = st.selectbox(
        "Sacramento",
        ["Primeira Eucaristia", "Crisma"]
    )

    if st.button("Salvar"):

        novo = pd.DataFrame([[nome, turma, comunidade, telefone, sacramento]],
        columns=df_cate.columns)

        df_cate = pd.concat([df_cate, novo], ignore_index=True)

        salvar_catequizandos(df_cate)

        st.success("Catequizando cadastrado!")

elif menu == "Lista de Catequizandos":

    st.subheader("Lista Geral")

    st.dataframe(df_cate)

elif menu == "Registrar Presença":

    st.subheader("Registro de Presença")

    turma = st.selectbox(
        "Selecione a turma",
        df_cate["Turma"].unique()
    )

    lista = df_cate[df_cate["Turma"] == turma]

    presencas = []

    for nome in lista["Nome"]:

        presente = st.checkbox(nome)

        presencas.append((nome, "P" if presente else "F"))

    if st.button("Salvar Presença"):

        df_pres = carregar_presenca()

        for nome, status in presencas:

            nova = pd.DataFrame(
                [[date.today(), nome, turma, status]],
                columns=df_pres.columns
            )

            df_pres = pd.concat([df_pres, nova], ignore_index=True)

        salvar_presenca(df_pres)

        st.success("Presença registrada!")

elif menu == "Relatório de Faltas":

    st.subheader("Relatório de Faltas")

    df_pres = carregar_presenca()

    faltas = df_pres[df_pres["Presenca"] == "F"]

    relatorio = faltas["Nome"].value_counts()

    st.write(relatorio)