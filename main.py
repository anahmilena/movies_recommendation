import numpy as np
import pandas as pd
import datetime as dt
import ast
from fastapi import FastAPI
import string
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Creamos una función para filtrar del texto que ingresemos los signos de puntuación y los stopwords, y para pasar todo a minúsculas.
nltk.download('stopwords') # Descargamos el conjunto de stopwords en inglés
nltk.download('punkt') # Descargamos los datos requeridos para el tokenizador de oraciones en inglés
stop_words = set(stopwords.words('english'))  # Creamos un set de stopwords en inglés

def transform_sentence(sentence):
    sentence_new = sentence.translate(str.maketrans("", "", string.punctuation)).lower() # Remove punctuation and convert to lowercase

    words = nltk.word_tokenize(sentence_new) # Utilizamos este método para dividir la oración en palabras individuales
    filtered_sentence = " ".join([word for word in words if word.lower() not in stop_words]) # Utilizamos list comprehension para filtrar las palabras de la lista words y lo regresamos a string

    return filtered_sentence
#---------------------------------------------------------------------

DATASET = "Dataset/data_merge.csv"

data = pd.read_csv(DATASET)

# Reducimos el número de registros para evitar que se muera el computador
data_reduced = data[data["vote_count"] > 50]
data_reduced = data_reduced[data_reduced["vote_average"] > 5]
data_reduced.dropna(subset=["overview", "title"], inplace=True)
#----------------------------------------------------------------------

# Aplicamos la función de filtrado de texto a overview y title y las concateno en una sola columna.
data_reduced["overview_main_words"] = data_reduced["overview"].apply(lambda x: transform_sentence(x) if pd.notnull(x) else np.nan)
data_reduced["title_main_words"] = data_reduced["title"].apply(lambda x: transform_sentence(x) if pd.notnull(x) else np.nan)
data_reduced["main_words_for_rs"] = data_reduced["title_main_words"] + " " + data_reduced["overview_main_words"]
data_reduced.drop(columns=["overview_main_words", "title_main_words"], inplace=True)
#----------------------------------------------------------------------

# Creamos TF-IDF vectors y calculamos similaridad con Cosine Similarity
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(data_reduced["main_words_for_rs"])
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
#----------------------------------------------------------------------

app = FastAPI()

#Funciones en FastAPI
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
                    "Año": str(data.loc[data["title"] == Pelicula]["release_year"][i]),
                    "Duración": int(data.loc[data["title"] == Pelicula]["runtime"][i])}
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
    data["production_countries"] = data["production_countries"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
    data["is_country_in"] = data["production_countries"].apply(lambda x: np.sum([1 for n in x if n["name"] == Pais]))
    movie_qty = data["is_country_in"].sum()
    return {"País": Pais, "Cantidad_Peliculas": movie_qty}

@app.get("/company/{Productora}")
# Se ingresa la productora, entregandote el revunue total y la cantidad de peliculas que realizó.
def productoras_exitosas(Productora: str):
    data["production_companies"] = data["production_companies"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
    data["is_company_in"] = data["production_companies"].apply(lambda x: np.sum([1 for n in x if n["name"] == Productora]))
    movie_qty = data["is_company_in"].sum()
    total_revenue = data.loc[data["is_company_in"] == 1]["revenue"].sum()
    return {"Productora": Productora, "Ganancia": total_revenue, "Cantidad_Peliculas": movie_qty}

@app.get("/director/{Director}")
# Se ingresa el nombre de un director que se encuentre dentro del dataset debiendo devolver el éxito del mismo 
# medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, 
# retorno individual, costo y ganancia de la misma, en formato lista.
def get_director(Director: str):
    # Creamos una columna nueva con un indicador de si se participó como director en dicha película.
    data_draft = data.drop(data[data["director"].isnull()].index)
    data_draft = data_draft.drop(data_draft[data_draft['director'].apply(len) == 0].index)
    data_draft["is_director_in"] = data_draft["director"].apply(lambda x: x.count(Director))
    # Calculamos cantidad de películas en las que participó y retorno general.
    movie_qty = sum(data_draft["is_director_in"])
    total_return = data_draft.loc[data_draft["is_director_in"] == 1]["revenue"].sum() / data_draft.loc[data_draft["is_director_in"] == 1]["budget"].sum()
    # Obtenemos la lista de películas con la fecha de lanzamiento, retorno individual, costo y ganancia.
    data_draft = data_draft.loc[data_draft["is_director_in"] == 1]
    movie_list = [{"title": data["title"], "release_date": pd.to_datetime(data["release_date"]).strftime("%Y/%m/%d"), "budget": data["budget"], "revenue": data["revenue"], "return": round(data["return"],2)} for (index, data) in data_draft.iterrows()]
    return {"Director": Director, "Cantidad_Peliculas": movie_qty, "Retorno": round(float(total_return),2), "Listado_peliculas": movie_list}

@app.get("/recommendation/{titulo}")
def recomendacion(titulo: str): 
# Se ingresa el nombre de una película y te recomienda las similares en una lista de 5 valores.
    index_id = data_reduced[data_reduced["title"] == titulo].index[0]  # Index of the movie you want to find similar movies for
    similar_movies_indices = similarity_matrix[index_id].argsort()[::-1][1:6]  # Exclude the movie itself, take top 10
    similar_movies = data_reduced.iloc[similar_movies_indices][['title']].to_dict(orient='list')
    return similar_movies