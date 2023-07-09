import numpy as np
import pandas as pd
import datetime as dt
import json
import ast
from fastapi import FastAPI, Depends

DATASET1 = "Dataset/movies_dataset.csv"
DATASET2 = "Dataset/credits.csv"

data = pd.read_csv(DATASET1)
datac = pd.read_csv(DATASET2)

# Transformaciones:
data = data[data["adult"].isin(["True", "False"])]
data.drop(columns=["video", "imdb_id", "adult", "original_title", "poster_path", "homepage"], inplace=True)
data.dropna(subset=["release_date"], inplace=True)
data["revenue"] = data["revenue"].fillna(0)
data["budget"] = data["budget"].fillna(0)
data["budget"] = data["budget"].apply(pd.to_numeric)
data["return"] = [x / y if y > 0 else 0 for x, y in zip(data["revenue"], data["budget"])]
data["release_date"] = pd.to_datetime(data["release_date"])
data["release_year"] = data["release_date"].dt.strftime('%Y')
data['belongs_to_collection'] = data['belongs_to_collection'].apply(lambda x: ast.literal_eval(x)['name'] if pd.notnull(x) else np.nan)
data["production_countries"] = data["production_countries"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
data["production_companies"] = data["production_companies"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
data["id"] = data["id"].apply(pd.to_numeric)
datac["id"] = datac["id"].apply(pd.to_numeric)
data_merge = pd.merge(data, datac, on="id", how="left")
data_merge["crew"] = data_merge["crew"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)

#Funciones en FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Message": "Hello World"}

@app.get("/runtime/{Pelicula}")
# Se ingresa una pelicula. Debe devolver la duracion y el año.
def peliculas_duracion(Pelicula: str):
    indexes = data.loc[data["title"] == Pelicula].index
    movies = []
    for i in indexes:
        element = {"Pelicula": Pelicula, 
                    "Año": data.loc[data["title"] == Pelicula]["release_year"][i],
                    "Duración": data.loc[data["title"] == Pelicula]["runtime"][i]}
        movies.append(element)
    return movies

@app.get("/bylanguage/{Idioma}")
# Se ingresa un idioma (como están escritos en el dataset). Debe devolver la cantidad de películas producidas en ese idioma.
def peliculas_idioma(Idioma: str):
    movie_qty = len(data.loc[data["original_language"] == Idioma].index)
    return {"Idioma": Idioma, "Cantidad_Peliculas": movie_qty}

@app.get("/collection/{Franquicia}")
# Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio.
def franquicia(Franquicia: str): 
    movie_qty = len(data.loc[data["belongs_to_collection"] == Franquicia].index)
    total_revenue = data.loc[data["belongs_to_collection"] == Franquicia]["revenue"].sum()
    avg_revenue = data.loc[data["belongs_to_collection"] == Franquicia]["revenue"].mean()
    return {"Franquicia": Franquicia, "Cantidad_Peliculas": movie_qty, "Ganancia total": total_revenue, "Ganancia promedio": avg_revenue}

@app.get("/country/{Pais}")
# Se ingresa un país (como están escritos en el dataset), retornando la cantidad de peliculas producidas en el mismo.
def peliculas_pais(Pais: str): 
    data["is_country_in"] = data["production_countries"].apply(lambda x: sum([1 for n in x if n["name"] == Pais]))
    movie_qty = data["is_country_in"].sum()
    return {"País": Pais, "Cantidad_Peliculas": movie_qty}

@app.get("/company/{Productora}")
# Se ingresa la productora, entregandote el revunue total y la cantidad de peliculas que realizó.
def productoras_exitosas(Productora: str):
    data["is_company_in"] = data["production_companies"].apply(lambda x: sum([1 for n in x if n["name"] == Productora]))
    movie_qty = data["is_company_in"].sum()
    total_revenue = data.loc[data["is_company_in"] == 1]["revenue"].sum()
    return {"Productora": Productora, "Ganancia": total_revenue, "Cantidad_Peliculas": movie_qty}

@app.get("/director/{Director}")
# Se ingresa el nombre de un director que se encuentre dentro del dataset debiendo devolver el éxito del mismo 
# medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, 
# retorno individual, costo y ganancia de la misma, en formato lista.
def get_director(Director: str):
    # Eliminamos filas con datos nulos y listas vacías.
    data_merge.drop(data_merge[data_merge["crew"].isnull()].index, inplace=True)
    data_merge.drop(data_merge[data_merge['crew'].apply(len) == 0].index, inplace=True)
    # Creamos una columna nueva con un indicador de si se participó como director en dicha película.
    data_merge["is_director_in"] = data_merge["crew"].apply(lambda x: sum([1 for n in x if (n["job"] == "Director") and (n["name"] == Director)]))
    # Calculamos cantidad de películas en las que participó y retorno general.
    movie_qty = sum(data_merge["is_director_in"])
    total_return = data_merge.loc[data_merge["is_director_in"] == 1]["revenue"].sum() / data_merge.loc[data_merge["is_director_in"] == 1]["budget"].sum()
    # Obtenemos la lista de películas con la fecha de lanzamiento, retorno individual, costo y ganancia.
    data_draft = data_merge.loc[data_merge["is_director_in"] == 1]
    movie_list = [{"title": data["title"], "release_date": pd.to_datetime(data["release_date"]).strftime("%Y/%m/%d"), "budget": data["budget"], "revenue": data["revenue"], "return": round(data["return"],2)} for (index, data) in data_draft.iterrows()]
    return {"Director": Director, "Cantidad_Peliculas": movie_qty, "Retorno": round(float(total_return),2), "Listado_peliculas": movie_list}
