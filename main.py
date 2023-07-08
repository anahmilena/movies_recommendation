from fastapi import FastAPI, Depends
from data_source import DataTransformation
from typing import Annotated, Any

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/runtime/{Pelicula}")
def peliculas_duracion(Pelicula: str, commons: Annotated[Any, Depends(DataTransformation)]):
    # Se ingresa una pelicula. Debe devolver la duracion y el año.
    commons.transform()
    return commons.get_runtime(Pelicula)

@app.get("/bylanguage/{Idioma}")
def peliculas_idioma(Idioma: str, commons: Annotated[Any, Depends(DataTransformation)]):
    # Se ingresa un idioma (como están escritos en el dataset). Debe devolver la cantidad de películas producidas en ese idioma.
    commons.transform()
    return commons.get_movies_by_language(Idioma)

@app.get("/collection/{Franquicia}")
def franquicia(Franquicia: str, commons: Annotated[Any, Depends(DataTransformation)]): 
    # Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio.
    commons.transform()
    return commons.get_movies_by_collection(Franquicia)

@app.get("/country/{Pais}")
def peliculas_pais(Pais: str, commons: Annotated[Any, Depends(DataTransformation)]): 
    # Se ingresa un país (como están escritos en el dataset), retornando la cantidad de peliculas producidas en el mismo.
    commons.transform()
    return commons.get_movies_by_country(Pais)

@app.get("/company/{Productora}")
def productoras_exitosas(Productora: str, commons: Annotated[Any, Depends(DataTransformation)]):
    # Se ingresa la productora, entregandote el revunue total y la cantidad de peliculas que realizó.
    commons.transform()
    return commons.get_movies_by_company(Productora)

@app.get("/director/{Director}")
def get_director(Director, commons: Annotated[Any, Depends(DataTransformation)]):
    # Se ingresa el nombre de un director que se encuentre dentro del dataset debiendo devolver el éxito del mismo 
    # medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, 
    # retorno individual, costo y ganancia de la misma, en formato lista.
    commons.transform()
    return commons.get_movies_by_director(Director)