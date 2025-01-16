import streamlit as st
import pandas as pd 
from utils import tratamentoBases , tratamento_nulas , cityfilter , df_Entrantes , graph_Matriculados , graph_EnsinoMedio , barPlot ,  load_large_database , dict_ies , EntrantesCidade
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(
     layout="wide",
     page_title="DashBoard Cidades e Faculdades"
)

dfCursos , dfMatriculas1 , dfMatriculas2 = load_large_database()
dfMatriculas2 = dfMatriculas2.loc[dfMatriculas2['Dependência'] == "Privada" , :]
dict_ref = dict_ies()
cidade = st.text_input("Digite o Nome da Cidade que deseja Buscar" , "")
#dfCursos['Cidade do Curso']
categorias = ["Privada com fins lucrativos" , "Privada sem fins lucrativos"]

if cidade:

    df_cidade = dfCursos.loc[dfCursos['Cidade do Curso'] == cidade , : ]
    df_cidade = df_cidade.loc[df_cidade['Ano Base'] != '2010' , :]
    df_cidade = df_cidade.loc[df_cidade['Modalidade de Ensino'] == 'Presencial ' , :]
    df_cidade = df_cidade[df_cidade['Categoria Administrativa'].isin(categorias)]

    
    #st.dataframe(df_cidade)
    #df_cidade['Nome IES']
    agrouped_entrantes = df_cidade.groupby('Ano Base')['Ingressantes'].sum()
    SeriesEntrantes , dfEntrantes = EntrantesCidade(df_cidade , cidade)
   

    SeriesMatriculados , dfMatriculados  , inutil1 , inutil2 = graph_Matriculados(df_cidade , df_cidade)
   

    SeriesEnsinoMedio , dfEnsinoMedio = graph_EnsinoMedio(dfMatriculas1 , dfMatriculas2 , cidade)
    
    

    titles_list = ["Evolução de Entrantes no Ensino Superior" , "Evolução dos Matriculados no Ensino Superior" , "Evolução de Matriculados no Ensino Médio"]
    series_list = [SeriesEntrantes , SeriesMatriculados , SeriesEnsinoMedio]
    
    container1 = st.container(height = 900)
    with container1:
        col1 , col2 = st.columns(2)
        col1.write(titles_list[0])
        col1.bar_chart(series_list[0])    
        col2.write(titles_list[1])
        col2.bar_chart(series_list[1])  
        st.write(titles_list[2])
        st.bar_chart(series_list[2])

        df_final = dfEnsinoMedio
        df_final['Número de Entrantes no Ensino Superior'] = dfEntrantes['Número de Entrantes no Ensino Superior']
        df_final['Número de Matriculados no Ensino Superior'] = dfMatriculados['Número de Matriculados no Ensino Superior']
        
        excel_buffer = BytesIO()
        df_final.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)  # Redefinir o ponteiro do arquivo
        st.download_button(
            label="Baixar Base de dados",
            data=excel_buffer,
            file_name=f"Cidade+.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )
    
    #Iniciando o Processo de Criação do Gráfico de Market Share
    df_cidade_atual = df_cidade.loc[df_cidade['Ano Base'] == 2020 , :]
    df_cidade_atual['Matriculados'].fillna(0, inplace=True)
    df_cidade_atual['Matriculados'] = pd.to_numeric(df_cidade_atual['Matriculados'], errors='coerce')
    #df_cidade_atual.dtypes
    agroup_courses = df_cidade_atual.groupby('Curso Ajustado 2')['Matriculados'].sum()
    sorted_courses = agroup_courses.sort_values(ascending=False)
    total = df_cidade_atual['Matriculados'].sum()
    #st.write(total)
    dfCursosCidade = pd.DataFrame(sorted_courses)
    dfCursosCidade['MarketShareCurso'] = (dfCursosCidade['Matriculados'] * 100 / total).round(2)
    top10 = dfCursosCidade.nlargest(10 , 'Matriculados')
    #st.write('Soma de Share dos 10 maiores é : ' , top10['MarketShareCurso'].sum().round(2))
    #top10
    container2 = st.container(height = 480)

    with container2:
        col1 , col2 = st.columns(2)
        col1.write('Número de Matriculados entre os 10 maiores cursos')
        col1.bar_chart(top10['Matriculados'])
        col2.write('Percentual de MarketShare  por Curso')
        col2.line_chart(top10['MarketShareCurso'])


        excel_buffer = BytesIO()
        dfCursosCidade['Curso'] = list(dfCursosCidade.index)
        dfCursosCidade.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)  # Redefinir o ponteiro do arquivo
        st.download_button(
            label="Baixar Base de dados",
            data=excel_buffer,
            file_name=f"MixCursos{cidade}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

    #3. Processo de Criação da Tabela de Market Share 
     
    df_marktshare = df_cidade.groupby(['Nome da IES Ajustado' , 'Ano Base' , 'Código IES'])['Matriculados'].sum().reset_index()
    df_marktshare_oordenado = df_marktshare.sort_values(by=['Ano Base', 'Matriculados'])
    dfMatriculados.rename(columns={'Ano' : 'Ano Base'} , inplace=True)
    df_ms = pd.merge(df_marktshare_oordenado , dfMatriculados , on='Ano Base' , how='right')
    df_ms['Market Share'] = df_ms['Matriculados'] * 100 / df_ms['Número de Matriculados no Ensino Superior']
    del df_ms['Número de Matriculados no Ensino Superior']
    
    session3 = st.container(height=400)
    with session3:
        st.write("Tabela de Informações de Market Share da cidade. Você pode clicar nela para baixar")
        session3.dataframe(df_ms)
    
    # df_marktshare_oordenado
    
    
    



    
    