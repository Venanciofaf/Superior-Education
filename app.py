import streamlit as st
import pandas as pd 
from utils import tratamento_nulas , cityfilter , df_Entrantes , graph_Matriculados , graph_EnsinoMedio , barPlot , load_large_database , dict_ies
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(
     layout="wide",
     page_title="DashBoard Cidades e Faculdades"
)

dfCursos , dfMatriculas1 , dfMatriculas2 = load_large_database()
#dfMatriculas1
dfMatriculas2 = dfMatriculas2.loc[dfMatriculas2['Dependência'] == "Privada" , :]
dict_ref = dict_ies()
#dfCursos = tratamento_nulas(dfCursos)

input_ies = st.text_input("Digite o Número de IES da Faculdade que deseja Buscar" , "")
tam_input = len(input_ies)
col1 , col2 = st.columns(2)
categorias = ["Privada com fins lucrativos" , "Privada sem fins lucrativos"]
#print('O Número de Caracteres é: ' , len(input_ies))
if input_ies: 
    #Gráfico de Entrantes

    dfCursos = dfCursos.loc[dfCursos['Modalidade de Ensino'] == 'Presencial ' , :]
    dfCursos = dfCursos.loc[dfCursos['Categoria Administrativa'].isin(categorias)]


    faculdade = dict_ref[int(input_ies)]
    
    SeriesEntrantes , df_city , cidade , dfEntrantes = df_Entrantes(dfCursos , input_ies)
    df_facul = df_city.loc[df_city['Código IES'] == int(input_ies) , :]
    
    #st.dataframe(df_city)
    st.write('A Faculdade desse IES é : ' , faculdade)
    st.write('A Cidade dessa Faculdade é : ' , cidade)
    
    
    SeriesMatriculados , dfMatriculados , SeriesMatriculadosFaculdade , dfMatriculadosFaculdade = graph_Matriculados(df_city , df_facul)
    
    
    #st.dataframe(SeriesMatriculadosFaculdade)
    
    SeriesEnsinoMedio , dfEnsinoMedio = graph_EnsinoMedio(dfMatriculas1 , dfMatriculas2 , cidade)
    
    titles_list = ["Evolução de Entrantes no Ensino Superior" , "Evolução dos Matriculados no Ensino Superior" , "Evolução de Matriculados no Ensino Médio"]
    series_list = [SeriesEntrantes , SeriesMatriculados , SeriesEnsinoMedio]
    
    with st.container(height = 1000):
        st.write('Dados da Cidade de Atuação da Faculdade')
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
            file_name=f"Entrantes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )
    
    
    container2 = st.container(height = 550)
    with container2: 
        
        st.write(f"Dados Específicos de {faculdade}")
        col1 , col2 = st.columns(2)

        col1.write("Número de Matriculados na Faculdade")
        col1.bar_chart(SeriesMatriculadosFaculdade)
        
        #Iniciando o Tratamento de MS 
        MarketShareSeries = SeriesMatriculadosFaculdade * 100 / SeriesMatriculados
        col2.write("Market Share da Faculdade")
        col2.line_chart(MarketShareSeries)


        df_final = {
            "Ano" : [2010 , 2011 , 2012 , 2013 , 2014 , 2015 , 2016 , 2017 , 2018 , 2019 , 2020] , 
            "Matriculados" : SeriesMatriculadosFaculdade,
            "Market Share da Faculdade" : MarketShareSeries,
        }
        df_final = pd.DataFrame(df_final)
        df_final.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)  # Redefinir o ponteiro do arquivo
        st.download_button(
            label="Baixar Base de dados",
            data=excel_buffer,
            file_name=f"Base de dados {faculdade}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

    #Ajustando o Mix de Cursos 
    
    df_cidade_atual = df_city.loc[df_city['Ano Base'] == 2020 , :]
    df_cidade_atual['Matriculados'].fillna(0, inplace=True)
    df_cidade_atual['Matriculados'] = pd.to_numeric(df_cidade_atual['Matriculados'], errors='coerce')
    agroup_courses = df_cidade_atual.groupby('Curso Ajustado 2')['Matriculados'].sum()
    sorted_courses = agroup_courses.sort_values(ascending=False)
    total = df_cidade_atual['Matriculados'].sum()
    #st.write(total)
    dfCursosCidade = pd.DataFrame(sorted_courses)
    top10 = dfCursosCidade.nlargest(15 , 'Matriculados')
    top10_cursos = list(top10.index)
    
    list_cursos = []
    list_ms = []
    list_positions = []

    for curso_ref in top10_cursos:
        df_curso = df_cidade_atual.loc[df_cidade_atual['Curso Ajustado 2'] == curso_ref , :]
        matriculados_total = df_curso['Matriculados'].sum()
        dfMatriculados_facul = df_curso.loc[df_curso['Código IES'] == int(input_ies) , :]
        matriculados_facul = dfMatriculados_facul['Matriculados'].sum()
        marketsharefacul = matriculados_facul * 100 / matriculados_total
        #Pegando o Ranking 
        agrouped_cursos = df_curso.groupby('Código IES')['Matriculados'].sum().reset_index()
        grouped_sorted = agrouped_cursos.sort_values(by='Matriculados' , ascending = False)
        lista_ies_ajustado  = grouped_sorted['Código IES']
        i = 1
        for ies in lista_ies_ajustado:
            if ies == int(input_ies):
                break
            else:
                i += 1
        list_cursos.append(curso_ref)
        list_ms.append(marketsharefacul)
        list_positions.append(i)
    

    
    #list_ms
    #list_positions
    df_positions = pd.DataFrame({
        "Curso": list_cursos,
        "Posição": list_positions,
        "Market Share do Curso" : list_ms
    })
    df_positions
        


    
    

