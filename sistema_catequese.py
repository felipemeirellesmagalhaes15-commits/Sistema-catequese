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
# PERMISSÕES
# ----------------------------

cursor.execute("""
SELECT aba, comunidade, turma
FROM permissoes_usuario
WHERE usuario=%s
""",(st.session_state["usuario"],))

permissoes = cursor.fetchall()

abas_permitidas = list(set([p[0] for p in permissoes]))
turmas_permitidas = list(set([p[2] for p in permissoes if p[2] != None]))

# ----------------------------
# MENU LATERAL ORGANIZADO
# ----------------------------

with st.sidebar:

    st.markdown("### 📖 Sistema Catequese")
    st.write(f"Usuário: **{st.session_state['usuario']}**")

    menu = option_menu(
        "Menu",
        [

            "📊 Dashboard",

            "--- CADASTROS ---",
            "Cadastro Turmas",
            "Cadastro Catequizando",
            "Cadastro Usuários",

            "--- PRESENÇA ---",
            "Registro Presença",

            "--- RELATÓRIOS ---",
            "Lista Catequizandos",
            "Lista Catequistas",
            "Relatório Faltas",

            "--- ADMINISTRAÇÃO ---",
            "Gestão de Acesso"

        ],

        icons=[
            "bar-chart",

            None,
            "house",
            "person-plus",
            "people",

            None,
            "check-square",

            None,
            "table",
            "person-badge",
            "exclamation-triangle",

            None,
            "key"
        ],

        default_index=0
    )

    if st.button("🚪 Sair"):
        st.session_state["logado"] = False
        st.rerun()


# Ajuste do nome do menu para o sistema reconhecer

menu = menu.replace("📊 ","")

if "---" in menu:
    menu = "Dashboard"
# ----------------------------
# DASHBOARD
# ----------------------------

if menu == "Dashboard":

    st.title("📊 Painel da Catequese")

    cursor.execute("SELECT COUNT(*) FROM catequizandos")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM turmas")
    total_turmas = cursor.fetchone()[0]

    col1,col2 = st.columns(2)

    col1.metric("Catequizandos",total)
    col2.metric("Turmas",total_turmas)

# ----------------------------
# CADASTRO TURMAS
# ----------------------------

elif menu == "Cadastro Turmas":

    st.header("🏫 Cadastro de Turmas")

    nome = st.text_input("Nome da Turma")

    comunidade = st.selectbox(
        "Comunidade",
        ["Avelar","Granja","Antonio Joaquim","Vista Alegre","Saudade"]
    )

    catequista = st.text_input("Catequista")

    if st.button("Salvar Turma"):

        cursor.execute("""
        INSERT INTO turmas (nome,comunidade,catequista)
        VALUES (%s,%s,%s)
        """,(nome,comunidade,catequista))

        conn.commit()

        st.success("Turma cadastrada!")

    cursor.execute("SELECT id,nome,comunidade,catequista FROM turmas")

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=["ID","Turma","Comunidade","Catequista"]
    )

    st.dataframe(df,use_container_width=True)

# ----------------------------
# CADASTRO CATEQUIZANDO
# ----------------------------

elif menu == "Cadastro Catequizando":

    st.header("👤 Cadastro de Catequizando")

    if st.session_state["perfil"] == "admin":

        cursor.execute("""
        SELECT id,nome,comunidade,catequista
        FROM turmas
        """)

    else:

        cursor.execute("""
        SELECT id,nome,comunidade,catequista
        FROM turmas
        WHERE nome = ANY(%s)
        """,(turmas_permitidas,))

    dados_turmas = cursor.fetchall()

    turmas_dict = {
        f"{t[1]} | Comunidade {t[2]} | Catequista {t[3]}": t[1]
        for t in dados_turmas
    }

    col1,col2 = st.columns(2)

    with col1:

        nome = st.text_input("Nome")

        turma_label = st.selectbox(
            "Turma",
            list(turmas_dict.keys())
        )

        turma = turmas_dict[turma_label]

        telefone = st.text_input("Telefone")
        endereco = st.text_input("Endereço")
        bairro = st.text_input("Bairro")
        cidade = st.text_input("Cidade")

    with col2:

        comunidade = st.selectbox(
            "Comunidade",
            ["Avelar","Granja","Antonio Joaquim","Vista Alegre","Saudade"]
        )

        sacramento = st.selectbox(
            "Sacramento",
            ["Primeira Eucaristia","Crisma"]
        )

        data_cadastro = st.date_input("Data Cadastro", date.today(), format="DD/MM/YYYY")

    if st.button("Salvar"):

        cursor.execute("""
        INSERT INTO catequizandos
        (nome,turma,comunidade,telefone,endereco,bairro,cidade,sacramento,data_cadastro)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,(nome,turma,comunidade,telefone,endereco,bairro,cidade,sacramento,data_cadastro))

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

    perfil = st.selectbox("Perfil", ["admin","catequista"])

    if st.button("Salvar usuário"):

        cursor.execute("""
        INSERT INTO usuarios (usuario,senha,nome,perfil)
        VALUES (%s,%s,%s,%s)
        """,(usuario,senha,nome,perfil))

        conn.commit()

        st.success("Usuário cadastrado!")

# ----------------------------
# REGISTRO PRESENÇA
# ----------------------------

elif menu == "Registro Presença":

    st.header("✅ Registro de Presença")

    data = st.date_input("Data", date.today(), format="DD/MM/YYYY")

    if st.session_state["perfil"] == "admin":
        cursor.execute("SELECT nome FROM turmas")
    else:
        cursor.execute("SELECT nome FROM turmas WHERE nome = ANY(%s)",(turmas_permitidas,))

    turmas = [t[0] for t in cursor.fetchall()]

    turma = st.selectbox("Turma", turmas)

    cursor.execute(
    "SELECT nome FROM catequizandos WHERE turma=%s",
    (turma,)
    )

    alunos = cursor.fetchall()

    presencas=[]

    for aluno in alunos:

        presente = st.checkbox(aluno[0])

        presencas.append((aluno[0],"P" if presente else "F"))

    if st.button("Registrar"):

        for nome,status in presencas:

            cursor.execute("""
            INSERT INTO presenca
            (data,nome,turma,presenca)
            VALUES (%s,%s,%s,%s)
            """,(data,nome,turma,status))

        conn.commit()

        st.success("Presença registrada!")

# ----------------------------
# LISTA CATEQUIZANDOS
# ----------------------------

elif menu == "Lista Catequizandos":

    st.header("📋 Lista de Catequizandos")

    if st.session_state["perfil"] == "admin":

        cursor.execute("""
        SELECT id,nome,turma,comunidade,telefone,endereco,bairro,cidade,sacramento
        FROM catequizandos
        """)

    else:

        cursor.execute("""
        SELECT id,nome,turma,comunidade,telefone,endereco,bairro,cidade,sacramento
        FROM catequizandos
        WHERE turma = ANY(%s)
        """,(turmas_permitidas,))

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "ID","Nome","Turma","Comunidade",
            "Telefone","Endereço","Bairro","Cidade","Sacramento"
        ]
    )

    st.dataframe(df,use_container_width=True)

# ----------------------------
# LISTA CATEQUISTAS
# ----------------------------

elif menu == "Lista Catequistas":

    st.header("👨‍🏫 Lista de Catequistas")

    cursor.execute("""
    SELECT nome,usuario,perfil
    FROM usuarios
    ORDER BY nome
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=["Nome","Usuário","Perfil"]
    )

    st.dataframe(df,use_container_width=True)

# ----------------------------
# RELATÓRIO FALTAS
# ----------------------------

elif menu == "Relatório Faltas":

    st.header("⚠ Relatório de Faltas")

    if st.session_state["perfil"] == "admin":

        cursor.execute("""
        SELECT nome, COUNT(*)
        FROM presenca
        WHERE presenca='F'
        GROUP BY nome
        ORDER BY COUNT(*) DESC
        """)

    else:

        cursor.execute("""
        SELECT nome, COUNT(*)
        FROM presenca
        WHERE presenca='F'
        AND turma = ANY(%s)
        GROUP BY nome
        ORDER BY COUNT(*) DESC
        """,(turmas_permitidas,))

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=["Catequizando","Total de Faltas"]
    )

    st.dataframe(df,use_container_width=True)

# ----------------------------
# GESTÃO DE ACESSO
# ----------------------------

elif menu == "Gestão de Acesso":

    st.header("🔑 Gestão de Acesso")

    cursor.execute("SELECT usuario FROM usuarios ORDER BY usuario")
    usuarios = [u[0] for u in cursor.fetchall()]

    usuario_sel = st.selectbox("Usuário",usuarios)

    cursor.execute("""
    SELECT aba,comunidade,turma
    FROM permissoes_usuario
    WHERE usuario=%s
    """,(usuario_sel,))

    permissoes = cursor.fetchall()

    abas_atuais = list(set([p[0] for p in permissoes if p[0] != None]))
    comunidades_atuais = list(set([p[1] for p in permissoes if p[1] != None]))
    turmas_atuais = list(set([p[2] for p in permissoes if p[2] != None]))

    st.subheader("Permissões atuais")

    if permissoes:
        df_perm = pd.DataFrame(permissoes,columns=["Aba","Comunidade","Turma"])
        st.dataframe(df_perm,use_container_width=True)
    else:
        st.info("Este usuário ainda não possui permissões cadastradas.")

    st.divider()

    st.subheader("Editar permissões")

    abas = [
        "Dashboard",
        "Cadastro Turmas",
        "Cadastro Catequizando",
        "Cadastro Usuários",
        "Registro Presença",
        "Lista Catequizandos",
        "Lista Catequistas",
        "Relatório Faltas"
    ]

    abas_sel = st.multiselect("Abas Permitidas",abas,default=abas_atuais)

    comunidades = [
        "Avelar","Granja","Antonio Joaquim","Vista Alegre","Saudade"
    ]

    comunidades_sel = st.multiselect("Comunidades Permitidas",comunidades,default=comunidades_atuais)

    cursor.execute("SELECT nome FROM turmas ORDER BY nome")
    turmas = [t[0] for t in cursor.fetchall()]

    turmas_sel = st.multiselect("Turmas Permitidas",turmas,default=turmas_atuais)

    if st.button("💾 Salvar Permissões"):

        cursor.execute("DELETE FROM permissoes_usuario WHERE usuario=%s",(usuario_sel,))

        for aba in abas_sel:
            for comunidade in comunidades_sel:
                for turma in turmas_sel:

                    cursor.execute("""
                    INSERT INTO permissoes_usuario
                    (usuario,aba,comunidade,turma)
                    VALUES (%s,%s,%s,%s)
                    """,(usuario_sel,aba,comunidade,turma))

        conn.commit()

        st.success("Permissões atualizadas com sucesso!")