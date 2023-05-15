from fastapi import FastAPI
import requests
import calendar
import pandas as pd
import numpy as np
import io

app = FastAPI()

def download_file_from_dropbox(file_path):
    try:
        response = requests.get(f"https://www.dropbox.com/s/{file_path}?dl=1")
        response.raise_for_status()
        file_data = response.content
        return file_data
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from Dropbox: {e}")


file_path = "gccn0wo9tljrbjh/dataset_movies_con_ETL.csv"  # Ruta del archivo en Dropbox
file_data_df = download_file_from_dropbox(file_path)
# Procesa el archivo de datos según tus necesidades

df_expanded_final= pd.read_csv(io.BytesIO(file_data_df))

df_expanded_final['release_date'] = pd.to_datetime(df_expanded_final['release_date'])


@app.get('/cant_peliculas_mes')
def peliculas_mes(mes:str):
    # creo una columna con el mes
    df_expanded_final['mes'] = df_expanded_final['release_date'].dt.month.map(lambda x: calendar.month_name[x])
    # Obtener la cantidad de películas estrenadas ese mes
    respuesta = len(df_expanded_final[df_expanded_final['mes'] == mes])
    return {'mes': mes, 'cantidad': respuesta}

@app.get('/cant_peliculas_dia')
def peliculas_dia(dia:str):
    # creo una columna con el dia
    df_expanded_final['dia_semana'] = df_expanded_final['release_date'].dt.day_name()
    # Obtener la cantidad de películas estrenadas ese dia de la semana
    respuesta = len(df_expanded_final[df_expanded_final['dia_semana'] == dia])
    return {'dia': dia, 'cantidad': respuesta}

@app.get('/datos_por_franquicia')
def franquicia(franquicia:str):
    # Lógica para obtener la cantidad de películas, ganancia total y promedio de una franquicia
    cantidad = len(df_expanded_final[df_expanded_final['name_belongs_to_collection'] == franquicia])
    # se creo la columna ganacia
    df_expanded_final['ganancia']=df_expanded_final['revenue']-df_expanded_final['budget']
    #se realizan los calculos
    filtered_data = df_expanded_final.loc[df_expanded_final['name_belongs_to_collection'] == franquicia]
    ganancia_total = filtered_data['ganancia'].sum()
    ganancia_promedio =filtered_data['ganancia'].mean()
    return {'franquicia': franquicia, 'cantidad de peliculas': cantidad, 'ganancia_total': ganancia_total, 'ganancia_promedio': ganancia_promedio}

@app.get('/peliculas_por_pais')
def peliculas_pais(pais:str):
    # Lógica para obtener la cantidad de películas producidas en un país
    respuesta = len(df_expanded_final[df_expanded_final['name_production_countries'] == pais])
    return {'pais': pais, 'cantidad': respuesta}

@app.get('/datos_por_productora')
def productoras(productora:str):
    # Lógica para obtener la ganancia total y cantidad de películas de una productora
    filtered_data = df_expanded_final.loc[df_expanded_final['name_production_companies'] == productora]
    ganancia_total = filtered_data['ganancia'].sum()
    cantidad = len(df_expanded_final[df_expanded_final['name_production_companies'] == productora])
    return {'productora': productora, 'ganancia_total': ganancia_total, 'cantidad': cantidad}

@app.get('/datos_por_pelicula')
def retorno(pelicula:str):
    # Lógica para obtener la inversión, ganancia, retorno y año de una película
    inversion = df_expanded_final.loc[df_expanded_final['title'] == pelicula, 'budget'].item()
    # se creo la columna ganacia
    df_expanded_final['ganancia']=df_expanded_final['revenue']-df_expanded_final['budget']
    ganancia = df_expanded_final.loc[df_expanded_final['title'] == pelicula, 'ganancia'].item()
    retorno = df_expanded_final.loc[df_expanded_final['title'] == pelicula, 'return'].item()
    anio = df_expanded_final.loc[df_expanded_final['title'] == pelicula, 'release_year'].item()
    return {'pelicula': pelicula, 'inversion': inversion, 'ganancia': ganancia, 'retorno': retorno, 'anio': anio}


