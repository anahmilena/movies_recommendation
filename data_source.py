import numpy as np
import pandas as pd
import datetime as dt
import ast

DATASET1 = "Dataset/movies_dataset.csv"
DATASET2 = "Dataset/credits.csv"

class DataTransformation():
    def __init__(self):
        self.data = pd.read_csv(DATASET1)
        self.datac = pd.read_csv(DATASET2)

    # data = pd.read_csv("Dataset/movies_dataset.csv")
    def transform(self):
        self.data = self.data[self.data["adult"].isin(["True", "False"])]
        self.data.drop(columns=["video", "imdb_id", "adult", "original_title", "poster_path", "homepage"], inplace=True)
        self.data.dropna(subset="release_date", inplace=True)
        self.data["revenue"] = self.data["revenue"].fillna(0)
        self.data["budget"] = self.data["budget"].fillna(0)
        self.data["budget"] = self.data["budget"].apply(pd.to_numeric)
        self.data["return"] = [x / y if y > 0 else 0 for x, y in zip(self.data["revenue"], self.data["budget"])]
        self.data["release_date"] = pd.to_datetime(self.data["release_date"])
        self.data["release_year"] = self.data["release_date"].dt.strftime('%Y')
        self.data['belongs_to_collection'] = self.data['belongs_to_collection'].apply(lambda x: ast.literal_eval(x)['name'] if pd.notnull(x) else np.nan)
        self.data["production_countries"] = self.data["production_countries"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
        self.data["production_companies"] = self.data["production_companies"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)
        self.data["id"] = self.data["id"].apply(pd.to_numeric)
        self.datac["id"] = self.datac["id"].apply(pd.to_numeric)
        self.data_merge = pd.merge(self.data, self.datac, on="id", how="left")
        self.data_merge["crew"] = self.data_merge["crew"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else np.nan)

    def get_runtime(self, Pelicula):
        runtime = self.data.loc[self.data["title"] == Pelicula]["runtime"][1]
        year_released = self.data.loc[self.data["title"] == Pelicula]["release_year"][1]
        return f"{Pelicula}. Duración: {runtime} min. Año: {year_released}"
    
    def get_movies_by_language(self, Idioma):
        movie_qty = len(self.data.loc[self.data["original_language"] == Idioma].index)
        return f"{movie_qty} películas fueron estrenadas en idioma {Idioma}"
    
    def get_movies_by_collection(self, Franquicia):
        movie_qty = len(self.data.loc[self.data["belongs_to_collection"] == Franquicia].index)
        total_revenue = self.data.loc[self.data["belongs_to_collection"] == Franquicia]["revenue"].sum()
        avg_revenue = self.data.loc[self.data["belongs_to_collection"] == Franquicia]["revenue"].mean()
        return f"La franquicia {Franquicia} posee {movie_qty} peliculas, una ganancia total de {total_revenue} y una ganancia promedio de {avg_revenue}."
    
    def get_movies_by_country(self, Pais):
        self.data["is_country_in"] = self.data["production_countries"].apply(lambda x: sum([1 for n in x if n["name"] == Pais]))
        movie_qty = self.data["is_country_in"].sum()
        return f"Se produjeron {movie_qty} películas en el país {Pais}"
    
    def get_movies_by_company(self, Productora):
        self.data["is_company_in"] = self.data["production_companies"].apply(lambda x: sum([1 for n in x if n["name"] == Productora]))
        movie_qty = self.data["is_company_in"].sum()
        total_revenue = self.data.loc[self.data["is_company_in"] == 1]["revenue"].sum()
        return f"La productora {Productora} ha tenido un revenue de {total_revenue}, con un total de {movie_qty} películas."

    def get_movies_by_director(self, Director):
        # Eliminamos filas con datos nulos y listas vacías.
        self.data_merge.drop(self.data_merge[self.data_merge["crew"].isnull()].index, inplace=True)
        self.data_merge.drop(self.data_merge[self.data_merge['crew'].apply(len) == 0].index, inplace=True)
        # Creamos una columna nueva con un indicador de si se participó como director en dicha película.
        self.data_merge["is_director_in"] = self.data_merge["crew"].apply(lambda x: np.count_nonzero([1 for n in x if (n["job"] == "Director") and (n["name"] == Director)]))
        # Calculamos cantidad de películas en las que participó y retorno general.
        movie_qty = self.data_merge["is_director_in"].sum()
        total_return = self.data_merge.loc[self.data_merge["is_director_in"] == 1]["revenue"].sum() / self.data_merge.loc[self.data_merge["is_director_in"] == 1]["budget"].sum()
        # Obtenemos la lista de películas con la fecha de lanzamiento, retorno individual, costo y ganancia.
        data_draft = self.data_merge.loc[self.data_merge["is_director_in"] == 1]
        movie_list = [{"title": data["title"], "release_date": pd.to_datetime(data["release_date"]).strftime("%Y/%m/%d"), "budget": data["budget"], "revenue": data["revenue"], "return": round(data["return"],2)} for (index, data) in data_draft.iterrows()]
        return f"Message: {Director} ha participado como director en {movie_qty} películas. Con un retorno de {round(total_return,2)}. \n {movie_list}"
