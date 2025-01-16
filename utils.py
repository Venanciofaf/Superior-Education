import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import streamlit as st
import os
import glob
import requests
import gdown
def tratamentoBases(df1 , df2 ,df3): 
    df2 = df2.iloc[9603:]
    df3 = df3.iloc[11039,:]
    df1['NO_MUNICIPIO'] = df1['NO_MUNICIPIO'].str.encode('latin1').str.decode('utf-8')
    df2['NO_MUNICIPIO'] = df2['NO_MUNICIPIO'].str.encode('latin1').str.decode('utf-8')
    df3['NO_MUNICIPIO'] = df3['NO_MUNICIPIO'].str.encode('latin1').str.decode('utf-8')
    
    return df1 , df2 , df3

def tratamento_nulas(df): 
    nulls = df.isna().sum()
    nulls = nulls.sort_values(ascending=False)
    dict_nulls = dict(nulls)

    droped_columns = []
    for column in dict_nulls.keys(): 
        #print(dict_nulls[column])
        if dict_nulls[column] > 100000:
            droped_columns.append(column)
            df.drop(column , axis = 1 , inplace=True)
    nulls = df.isna().sum().sort_values(ascending=False)

    #print(nulls)

    return df

def cityfilter(dfFaculdadeDesejada , dfCursos): 
    dict_cidade = dict(dfFaculdadeDesejada['Cidade do Curso'].value_counts())
    num_cidades = len(dict_cidade)
    print(dict_cidade)
    cidade = list(dict_cidade.keys())[0]
    estado =  list(dict(dfFaculdadeDesejada['UF do Curso'].value_counts()).keys())[0]
    df_cidade = dfCursos.loc[dfCursos['Cidade do Curso'] == cidade , : ]
    return df_cidade , cidade

def EntrantesCidade(dfCidade , cidade): 
    agrouped_entrantes = dfCidade.groupby('Ano Base')['Ingressantes'].sum()
    anos , entrantes = (list(dict(agrouped_entrantes).keys()) , list(dict(agrouped_entrantes).values()))
    #anos.pop()
    #entrantes.pop()
    SeriesEntrantes = pd.Series(entrantes , index=anos)
    dfEntrantes = pd.DataFrame({
        "Ano": anos,
        "Número de Entrantes no Ensino Superior": entrantes,
    }
        
    )
    return SeriesEntrantes , dfEntrantes

def df_Entrantes(dfEntrantes , input_ies):
    df_filtered = dfEntrantes.loc[dfEntrantes['Código IES'] == int(input_ies) , :]
    df_city , city = cityfilter(df_filtered , dfEntrantes)
    df_city = df_city.loc[df_city['Ano Base'] != '2010' , :]
    #Gráfico de Entrantes 
    SeriesEntrantes , dfEntrantes = EntrantesCidade(df_city , city)
    
    return SeriesEntrantes , df_city , city , dfEntrantes

def graph_Matriculados(df_city , dfFaculdades):
    df_city = df_city.loc[df_city['Ano Base'] != '2010' , :]

    agrouped_matriculados = df_city.groupby('Ano Base')['Matriculados'].sum()
    anos , matriculados = (list(dict(agrouped_matriculados).keys()) , list(dict(agrouped_matriculados).values()))
    


    SeriesMatriculados = pd.Series(matriculados , index=anos)
    dfMatriculados = pd.DataFrame({
        "Ano": anos,
        "Número de Matriculados no Ensino Superior": matriculados,
    }

    )
    agrouped_faculdade = dfFaculdades.groupby('Ano Base')['Matriculados'].sum()    
    anos , matriculados = (list(dict(agrouped_faculdade).keys()) , list(dict(agrouped_faculdade).values()))

    SeriesMatriculadosFaculdade = pd.Series(matriculados , index=anos)

    dfMatriculadosFaculdade = pd.DataFrame({
        "Ano": anos,
        "Matriculados na Faculdade": matriculados,
    })

    return SeriesMatriculados , dfMatriculados , SeriesMatriculadosFaculdade , dfMatriculadosFaculdade


def graph_EnsinoMedio(df1 , df2 , cidade):
    df_escolas_cidade = df1.loc[df1['Município'] == cidade , : ]
    df_EM = df_escolas_cidade.loc[df_escolas_cidade['Classificação JK'] == 'Ensino Médio' , :]
    df_EM['SomaDeQT_MATRICULAS'] = df_EM['SomaDeQT_MATRICULAS'].astype(float)
    
    matriculados_agrouped = df_EM.groupby('Ano')['SomaDeQT_MATRICULAS'].sum()
    
    df_escolas_cidade2 = df2.loc[df2['NO_MUNICIPIO'] == cidade , : ]
    df_EM2 = df_escolas_cidade2.loc[df_escolas_cidade2['Classificação'] == 'Ensino Médio' , :]
    matriculados_agrouped2 = df_EM2.groupby('Ano')['QT_MAT_MED'].sum()
  
    anos1 , matriculados1 = (list(dict(matriculados_agrouped).keys()) , list(dict(matriculados_agrouped).values()))
    anos2 , matriculados2 = (list(dict(matriculados_agrouped2).keys()) , list(dict(matriculados_agrouped2).values()))

    anos = anos1 + anos2
    matriculados = matriculados1 + matriculados2
   
    SeriesEM = pd.Series(matriculados , index=anos)
    dfFinal =  pd.DataFrame({
        "Ano": anos,
        "Número de Matriculados no Ensino Médio": matriculados,
    }
        
    )
    return SeriesEM , dfFinal


def barPlot(series1 , series2 , título , titulo_eixoX , titulo_EixoY , width=8 , height=5):
    fig , ax = plt.subplots(figsize=(width , height))
    bars = ax.bar(series1 ,series2 , color = "#00008B")
    for bar in bars:
        altura = bar.get_height()  # Altura da barra (valor no eixo Y)
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # Posição no centro da barra
            altura,  # Posição logo acima da barra
            f"{int(altura)}",  # Valor a ser exibido
            ha="center",  # Alinhamento horizontal
            va="bottom",  # Alinhamento vertical
            fontsize=6  # Tamanho da fonte
        )
    ax.set_title(título)
    ax.set_xlabel(titulo_eixoX, fontsize=12)
    ax.set_ylabel( titulo_EixoY , fontsize=12)
    ax.set_xticks(series1)
    ax.tick_params(axis="x", labelsize=8)  # Reduz o tamanho dos ticks no eixo X
    ax.tick_params(axis="y", labelsize=8)  # Reduz o tamanho dos ticks no eixo Y
    return fig

def clear_csv_files(folder_path):
    """
    Apaga todos os arquivos CSV em uma pasta específica.

    :param folder_path: Caminho para a pasta onde os arquivos CSV serão apagados.
    """
    # Localizar todos os arquivos CSV na pasta
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    # Apagar cada arquivo encontrado
    for file in csv_files:
        try:
            os.remove(file)
            print(f"Arquivo removido: {file}")
        except Exception as e:
            print(f"Erro ao remover {file}: {e}")

def read_csv_from_google_drive(file_id, output_file="temp.csv"):
    """
    Baixa um arquivo CSV do Google Drive usando gdown e retorna um DataFrame.

    :param file_id: ID do arquivo no Google Drive.
    :param output_file: Nome do arquivo temporário para salvar o CSV.
    :return: DataFrame com os dados do arquivo CSV.
    """
    # Construir o URL de download do Google Drive
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    
    # Fazer o download do arquivo
    gdown.download(url, output_file, quiet=False)
    
    # Ler o arquivo CSV e retornar como DataFrame
    df = pd.read_csv(output_file)
    return df

@st.cache_data
def load_large_database():
    path = 'dados2'

    ids = ['1zerQCYbiJp7JbnZYfNWA6OMlGmaTraIt',
       '1xv6GP7iam84WcXpUGesjCdpdNHdkJEb5',
       '1wtRNOU7cNmgQzGomeb1iK3Sy-Q17ZE10',
       '1Ccb1ptFODCiSqr5nGGDIKVvD0xldMJ6Y'
       ]

    outputs = ['dados2/CursosDB.csv',
           'dados2/EBMATRICULAS.csv',
           'dados2/EBMATRICULAS20-23.csv',
           'dados2/MICRODADOS_ED_SUP_IES_2023.CSV']
    

    clear_csv_files(path)

    # Substitua pelo seu método de carregamento de dados2
    df1= read_csv_from_google_drive(ids[0] , outputs[0])
    df2 = read_csv_from_google_drive(ids[1] , outputs[1])
    df3 = read_csv_from_google_drive(ids[2] , outputs[2])
    return df1 , df2 , df3

@st.cache_data
def dict_ies():
    df_atualizado = pd.read_csv('dados3/MICRODADOS_ED_SUP_IES_2023.CSV', encoding='ISO-8859-1', sep=';')
    nomes_faculdades = df_atualizado.drop_duplicates(subset='NO_IES')
    final_dict = nomes_faculdades.set_index('CO_IES')['NO_IES'].to_dict()
    faculdades_dict = {k: v for k, v in sorted(final_dict.items(), key=lambda item: item[0])}
    return faculdades_dict

