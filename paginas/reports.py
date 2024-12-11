# streamlit run .\conectividade.py

from io import BytesIO
from datetime import datetime
import pyodbc
import pandas as pd
import streamlit as st
import plotly.express as px

SERVER = '172.22.0.120'
DATABASE = 'eisa_pr2014_vivo_aceitacao_db'
USERNAME = 'qc_minerva'
PASSWORD = 'qc2014minerva'

conexaoBaseQC = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

# conexao = pyodbc.connect(conexaoBaseQC)
# print("Conexao Bem Sucedida")
try:
    conexao = pyodbc.connect(conexaoBaseQC)
    print("Conexão Bem Sucedida")
except pyodbc.Error as e:
    st.error("Erro ao conectar ao banco de dados. Verifique as configurações.")
    st.stop()  # Para a execução do aplicativo

def exibir_tela_reports():

    Consulta_SQL = """
    SELECT
        BG_DETECTION_DATE AS ABERTURA
        ,LEFT(
            BG_USER_01, 
                CHARINDEX('-', BG_USER_01)-1) 
                    AS ID_VIVO
        ,BG_BUG_ID AS ID_EISA
        ,SUBSTRING(
            BG_USER_01, 
                CHARINDEX('-', BG_USER_01, CHARINDEX('-', BG_USER_01) + 1) + 1, 
                    LEN(BG_USER_01)) 
                        AS PROJETO
        ,BG_USER_42 AS BLOCO_REQUISITO
        ,BG_DETECTION_VERSION AS RELEASE
        ,BG_USER_06 AS ESTEIRA
        ,BG_USER_15 AS CNs
        ,BG_USER_10 AS PREVISAO
        ,BG_USER_35 AS COMENTARIOS
        ,BG_USER_08 AS PACKAGE 
        ,BG_SUMMARY AS SUMMARY
        ,BG_RESPONSIBLE AS ASSIGNED_TO
        ,BG_USER_09  AS RESPONSIBLE
        ,BG_USER_20 AS REQUIREMENT
        ,BG_STATUS AS STATUS_EISA
        ,BG_USER_03 AS STATUS_VIVO
        ,BG_USER_13 AS CAUSA_DO_DEFEITO
        ,BG_USER_31 AS MOTIVO_REJEIÇÃO
        ,BG_USER_10 AS ANSWER_DATE
        ,BG_USER_05 AS TYPE
        ,BG_USER_32 AS CONTADOR_REOPEN
        ,BG_USER_34 AS CONTADOR_FIXED
        ,BG_USER_33 AS CONTADOR_REJECTED
        ,BG_USER_41 AS DATA_CORREÇÃO
        ,BG_USER_38 AS DATA_DEVOLUÇÃO_EISA
        ,BG_USER_22 AS SLA
        ,BG_USER_40 AS INTERNAL_FRONT
        ,BG_USER_24 AS SERVIÇO
        ,BG_USER_25 AS AMBIENTE
        ,BG_USER_26 AS MODULO
        ,BG_USER_37 AS SISTEMA_CORRECAO
    FROM TD.BUG 
    WHERE BG_DETECTED_BY IN ('pticketuser')
    AND BG_DETECTION_DATE >= '2024-01-01 00:00:00.000'
    ORDER BY ABERTURA, PROJETO DESC
    """

    # Conteúdo do aplicativo / Titulo da pagina
    st.title("DEP3.1 - Gestão de Defeitos NGIN, Smarts e RM")
    st.write("Aqui você pode visualizar a lista de Bugs sob nossa responsabilidade.")

    # # Verificar se os dados já estão carregados no session_state
    # if "dados" not in st.session_state:
    #     st.session_state.dados = pd.read_sql(Consulta_SQL, conexao)
    
    # # Botão para atualizar os dados no corpo principal
    # if st.button("Atualizar Dados"):
    #     with st.spinner("Atualizando dados..."):
    #         st.session_state.dados = pd.read_sql(Consulta_SQL, conexao)  # Recarrega os dados do banco
    #         st.success("Dados atualizados com sucesso!")

    # Adicionar botão de reexecução
    if st.button("Atualizar Dados"):
        st.rerun()

    # Executando a consulta
    dadosGerais = pd.read_sql(Consulta_SQL, conexao)

    # TRATAMENTOS DOS CAMPOS
    dadosGerais['ABERTURA'] = pd.to_datetime(dadosGerais['ABERTURA']).dt.strftime('%d/%m/%Y') # Converter para datetime e formatar apenas a data no formato DD/MM/YYYY
    dadosGerais['ID_EISA'] = dadosGerais['ID_EISA'].apply(lambda x: f"{x:.0f}")  # Formata sem vírgulas
    dadosGerais = dadosGerais.fillna(' - ') # Antes de qualquer manipulação ou exibição, substitua ou remova valores nulos

    # CONFIGURAÇÃO DOS SIDEBARS - BARRA LATERAL
    st.sidebar.title("Filtros")

    status_vivo = st.sidebar.multiselect(
        "Status VIVO:",
        options=dadosGerais["STATUS_VIVO"].unique(),  # Todos as opções disponíveis
        # default=dadosGerais["STATUS_VIVO"].unique()   # Definir opções como padrão, no momento todas
        default=[status for status in dadosGerais["STATUS_VIVO"].unique() if status != 'A espera de ReTeste']  # Exclui "A espera de reteste" de default

    )

    status_eisa = st.sidebar.multiselect(
        "Status EISA",
        options=dadosGerais[(dadosGerais["STATUS_VIVO"].isin(status_vivo))]["STATUS_EISA"].unique(),  # Apenas opções disponíveis após os filtros anteriores
        default=dadosGerais[(dadosGerais["STATUS_VIVO"].isin(status_vivo))]["STATUS_EISA"].unique()   # Seleciona todas as opções por padrão
    )

    projeto = st.sidebar.multiselect(
        "Projeto:",
        options=dadosGerais[
            (dadosGerais["STATUS_VIVO"].isin(status_vivo)) &  # Opções de Release disponíveis
            (dadosGerais["STATUS_EISA"].isin(status_eisa)) 
            ]
            ["PROJETO"].unique(),
        default=dadosGerais[
            (dadosGerais["STATUS_VIVO"].isin(status_vivo)) &  # Opções de Release disponíveis
            (dadosGerais["STATUS_EISA"].isin(status_eisa)) 
            ]
            ["PROJETO"].unique()
    )

    release = st.sidebar.multiselect(
        "Releases:",
        options=dadosGerais[
            (dadosGerais["STATUS_VIVO"].isin(status_vivo)) &  # Opções de Release disponíveis
            (dadosGerais["STATUS_EISA"].isin(status_eisa)) &
            (dadosGerais["PROJETO"].isin(projeto))
            ]
            ["RELEASE"].unique(),
        default=dadosGerais[
            (dadosGerais["STATUS_VIVO"].isin(status_vivo)) &  # Opções de Release disponíveis
            (dadosGerais["STATUS_EISA"].isin(status_eisa)) &
            (dadosGerais["PROJETO"].isin(projeto))
            ]
            ["RELEASE"].unique()
    )

    # Adicionando o botão de "Sair" na sidebar
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False  # Altera o estado para não logado
        st.session_state.current_page = "login"  # Redireciona para a tela de login
        st.rerun()  # Recarrega a página para ir para o login

    #########################################################################################################################################################################################

    # Filtrar o DataFrame pelas Releases e pelos filtros selecionados
    df_filtro = dadosGerais[
        (dadosGerais["STATUS_VIVO"].isin(status_vivo)) &    # Filtra pelos STATUS_VIVO selecionados
        (dadosGerais["STATUS_EISA"].isin(status_eisa)) &    # Filtra pelos STATUS_EISA selecionados
        (dadosGerais["PROJETO"].isin(projeto)) &            # Filtra pelos FRENTE_VIVO selecionados
        (dadosGerais["RELEASE"].isin(release))              # Filtra pelas Releases selecionadas 
    ].reset_index(drop=True) #### drop=True: Remove o índice antigo do DataFrame.


    #########################################################################################################################################################################################

    # Ajustar o índice para começar de 1
    df_filtro.index = range(1, len(df_filtro) + 1)

    # COLUNAS SELECIONAVEIS
    colunas_disponiveis = ['ABERTURA', 'ID_VIVO', 'ID_EISA', 'PROJETO', 'BLOCO_REQUISITO', 
                        'RELEASE', 'ESTEIRA', 'CNs', 'PREVISAO', 'COMENTARIOS', 'SUMMARY',
                        'ASSIGNED_TO', 'RESPONSIBLE', 'REQUIREMENT', 'STATUS_EISA', 'STATUS_VIVO' , 'CAUSA_DO_DEFEITO',
                        'MOTIVO_REJEIÇÃO', 'ANSWER_DATE', 'TYPE', 'CONTADOR_REOPEN', 'CONTADOR_FIXED',
                        'CONTADOR_REJECTED', 'DATA_CORREÇÃO', 'DATA_DEVOLUÇÃO_EISA', 'SLA',
                        'INTERNAL_FRONT', 'SERVIÇO', 'AMBIENTE', 'MODULO', 'SISTEMA_CORRECAO']

    # Exibição dos dados filtrados
    if df_filtro.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados. Tente ajustar os filtros na barra lateral para visualizar os resultados.")
    else:
        colunas_selecionadas = st.multiselect(              # Multiselect / lista para selecionar as colunas a serem exibidas
            "Selecione as colunas que deseja visualizar:",
            options=colunas_disponiveis,                    # Lista os campos que podem ser selecionados 
            default=['ABERTURA', 'ID_VIVO', 'ID_EISA', 'PROJETO', 'BLOCO_REQUISITO', 'RELEASE', 'ESTEIRA', 'CNs', 'PREVISAO', 'COMENTARIOS']   # Define campos default de exibição
        )        
        # Exibir a contagem de linhas
        st.info(f"No momento temos, {df_filtro.shape[0]} defeitos na nossa chave EISA")
        if colunas_selecionadas:            # Exibir o DataFrame com as colunas selecionadas
            st.dataframe(df_filtro[colunas_selecionadas],use_container_width=True)  # Mostra apenas as colunas escolhidas
        else:
            st.warning("Nenhuma coluna selecionada.")

        st.info("Use o botão abaixo para baixar os dados filtrados em um arquivo EXCEL:")
        
        # # Botão para baixar os dados filtrados como Excel
        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="openpyxl") as writer:
        #     df_filtro[colunas_selecionadas].to_excel(writer, index=False, sheet_name="Reports_Defeitos")
        # processed_data = output.getvalue()

        # Botão para baixar os dados filtrados como Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Para cada projeto na seleção atual, criar uma aba com os dados filtrados
            for projeto in df_filtro["PROJETO"].unique():
                # Filtrar os dados para o projeto atual
                df_projeto = df_filtro[df_filtro["PROJETO"] == projeto]
                
                # Selecionar apenas as colunas desejadas
                df_projeto = df_projeto[colunas_selecionadas]
                
                # Escrever na aba do Excel com o nome do projeto
                abas = projeto[:31]  # Limitar o nome da aba a 31 caracteres (limite do Excel)
                df_projeto.to_excel(writer, index=False, sheet_name=abas)
        
        # Obter os dados processados do arquivo Excel em memória
        processed_data = output.getvalue()

        st.download_button(
            label="Baixar em Excel",
            data=processed_data,               # Dados do arquivo em bytes
            file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",  # Nome do arquivo para download
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # Tipo do arquivo Excel
        )


    #################################################################################################################################################################################################

    # col3, col4 = st.columns(2) # Divide a tela em 2 colunas
    # col5, col6 = st.columns(2)

    #################################################################################################################################################################################################

    count_data = df_filtro.groupby('RESPONSIBLE').size().reset_index(name='Qtd_Defeitos') # Agrupamento os responsaveis ... pelo campo RESPONSIBLE para contagem através do "".size""
                                                                                        # reset_index(name='Qtd_Defeitos'): Entre " " cria um novo DataFrame, e atribui um nome a nova coluna que contém a contagem de defeitos, chamada de 'Qtd_Defeitos'.
    grafico1 = px.bar(
        count_data,
        x='RESPONSIBLE',
        y='Qtd_Defeitos',
        title='Quantidade de Defeitos por Frente EISA',
        color='RESPONSIBLE',
        text='Qtd_Defeitos'
        )
            
            
    grafico1.update_traces(
        textposition='auto',  # Posicionar o texto automaticamente
        insidetextanchor='middle'  # Alinha o texto verticalmente no centro
        )

    grafico1.update_layout(
        legend_title="Responsável EISA",  # Alterar o título da legenda
        xaxis_title=None,  # Remove o título do eixo X
        yaxis_title=None,  # Remove o título do eixo Y
        yaxis=dict(showticklabels=True)  # Exibe os rótulos no eixo Y
        )

    # with col3:
    #     st.plotly_chart(grafico1, use_container_width=True)

    #################################################################################################################################################################################################

    count_data = df_filtro.groupby('PROJETO').size().reset_index(name='Qtd_Defeitos') # Agrupamento os responsaveis ... pelo campo PROJETOS para contagem através do "".size""
                                                                                        # reset_index(name='Qtd_Defeitos'): Entre " " cria um novo DataFrame, e atribui um nome a nova coluna que contém a contagem de defeitos, chamada de 'Qtd_Defeitos'.
    grafico2 = px.pie(
        count_data,
        title='Quantidade de Defeitos por PROJETOS',
        values='Qtd_Defeitos',
        names='PROJETO'
        )
            
            
    grafico2.update_traces(
        textinfo='label + percent',  # Adiciona os valores da contagem como texto
        textposition='auto',       # Posiciona o texto dentro das barras = > ('auto' ou 'inside' ou outside)
        )

    # grafico1.update_layout(
    #     legend_title="PROJETOS",  # Alterar o título da legenda
    #     xaxis_title=None,  # Remove o título do eixo X
    #     yaxis_title=None,  # Remove o título do eixo Y
    #     yaxis=dict(showticklabels=True)  # Exibe os rótulos no eixo Y
    #     )

    # with col4:
    #     st.plotly_chart(grafico2, use_container_width=True)

    #################################################################################################################################################################################################

    count_data = df_filtro.groupby('ESTEIRA').size().reset_index(name='Qtd_Defeitos') # Agrupamento os responsaveis ... pelo campo ESTEIRA para contagem através do "".size""
                                                                                        # reset_index(name='Qtd_Defeitos'): Entre " " cria um novo DataFrame, e atribui um nome a nova coluna que contém a contagem de defeitos, chamada de 'Qtd_Defeitos'.
    grafico3 = px.pie(
        count_data,
        title='Quantidade de Defeitos por ESTEIRA',
        values='Qtd_Defeitos',
        names='ESTEIRA'
        )         
            
    grafico3.update_traces(
        textinfo='label + percent',  # Adiciona os valores da contagem como texto
        textposition='auto',       # Posiciona o texto dentro das barras = > ('auto' ou 'inside' ou outside)
        )

    #################################################################################################################################################################################################

    count_data = df_filtro.groupby('STATUS_EISA').size().reset_index(name='Qtd_Defeitos') # Agrupamento os responsaveis ... pelo campo RESPONSIBLE para contagem através do "".size""
                                                                                        # reset_index(name='Qtd_Defeitos'): Entre " " cria um novo DataFrame, e atribui um nome a nova coluna que contém a contagem de defeitos, chamada de 'Qtd_Defeitos'.
    grafico4 = px.bar(
        count_data,
        x='STATUS_EISA',
        y='Qtd_Defeitos',
        title='Quantidade de Defeitos por STATUS_EISA',
        color='STATUS_EISA',
        text='Qtd_Defeitos'
        )
            
            
    grafico4.update_traces(
        textposition='auto',  # Posicionar o texto automaticamente
        insidetextanchor='middle'  # Alinha o texto verticalmente no centro
        )

    grafico4.update_layout(
        legend_title="STATUS_EISA",  # Alterar o título da legenda
        xaxis_title=None,  # Remove o título do eixo X
        yaxis_title=None,  # Remove o título do eixo Y
        yaxis=dict(showticklabels=True)  # Exibe os rótulos no eixo Y
        )

    # with col6:
    #     st.plotly_chart(grafico4, use_container_width=True)

    with st.container():  # Agrupar gráficos relacionados
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
    with col1:
        st.plotly_chart(grafico1, use_container_width=True)
    with col2:
        st.plotly_chart(grafico2, use_container_width=True)
    with col3:
        st.plotly_chart(grafico3, use_container_width=True)
    with col4:
        st.plotly_chart(grafico4, use_container_width=True)
