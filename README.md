# Proyecto de Recomendación de Películas

Este proyecto en Python implementa un sistema de recomendación de películas utilizando técnicas de procesamiento de texto y algoritmos de vecinos más cercanos (K-Nearest Neighbors). El objetivo principal es proporcionar recomendaciones de películas similares a una película dada.

## Dependencias

El proyecto requiere las siguientes dependencias:

- `numpy`: Biblioteca para realizar cálculos numéricos eficientes.
- `pandas`: Biblioteca para el análisis y manipulación de datos.
- `datetime`: Módulo para trabajar con fechas y tiempos.
- `ast`: Módulo para evaluar literales de sintaxis abstracta.
- `fastapi`: Marco de trabajo para la creación de API web rápidas.
- `string`: Módulo que contiene varias constantes y clases útiles para manipular cadenas de texto.
- `nltk`: Biblioteca de procesamiento del lenguaje natural.
- `sklearn`: Biblioteca de aprendizaje automático con implementaciones eficientes de diversos algoritmos.
  - `TfidfVectorizer`: Clase para convertir una colección de documentos de texto en una matriz TF-IDF.
  - `NearestNeighbors`: Clase para realizar búsquedas de vecinos más cercanos en una matriz.
  - `cosine_similarity`: Calcula el ángulo entre dos vectores para determinar qué tan similares son en términos de dirección y orientación.


## Preparación de datos

El proyecto utiliza un conjunto de datos almacenado en el archivo `data_merge.csv`. Estos datos pasaron previamente por un proceso de transformación que se encuentra en el notebook `transformation.ipynb`, el cual se encuentra en el mismo repositorio. Puedes acceder al notebook y revisar el proceso de transformación allí.

Los archivos originales utilizados en la transformación se encuentran alojados en el siguiente enlace: [Archivos Originales](https://drive.google.com/drive/folders/1Gu3VJ8NGSNpxriCeHdR9q5PCdHFhaJET?usp=sharing). Puedes descargar los archivos originales desde ese enlace y ejecutar el notebook `transformation.ipynb` para obtener el archivo `data_merge.csv` necesario para este proyecto.

Una vez que tengas el archivo `data_merge.csv` generado a partir del proceso de transformación, colócalo en la ubicación especificada por la variable `DATASET` en el código del proyecto.


## Construcción del modelo

El proyecto utiliza TF-IDF (Term Frequency-Inverse Document Frequency) para representar el texto de las películas y calcular la similitud entre ellas. El algoritmo de vecinos más cercanos (K-Nearest Neighbors) se aplica en la matriz TF-IDF para encontrar películas similares.

El código proporcionado realiza las siguientes operaciones para construir el modelo:

1. Crea un objeto `TfidfVectorizer` para convertir el texto en una matriz TF-IDF.
2. Aplica el vectorizador a la columna "main_words_for_rs" del conjunto de datos reducido.
3. Crea un objeto `NearestNeighbors` utilizando la métrica de similitud de coseno.
4. Ajusta el modelo de vecinos más cercanos a la matriz TF-IDF.

## Análisis Exploratorio y Modelos de Aprendizaje Automático

El proyecto incluye un notebook llamado `eda_&_ml.ipynb` que contiene el análisis exploratorio de datos y la implementación de dos modelos diferentes de aprendizaje automático.

En el notebook, se realiza un análisis exploratorio de los datos para comprender mejor las características y distribuciones de las variables relevantes. Además, se prueba la efectividad de dos modelos: uno utilizando el algoritmo de similitud de coseno y otro utilizando el algoritmo de vecinos más cercanos (Nearest Neighbors).

Después de evaluar los dos modelos, se optó por utilizar el modelo basado en Nearest Neighbors debido a su capacidad de rendimiento y su idoneidad para la implementación en el proyecto.

## API Web

El proyecto utiliza el framework FastAPI para construir una API web que proporciona varias funcionalidades relacionadas con las películas. A continuación se describen las rutas de la API y sus respectivas funciones:

- `/`: Ruta raíz que devuelve un mensaje de saludo ("Hello World").
- `/runtime/{Pelicula}`: Recibe el nombre de una película y devuelve su duración y año de lanzamiento.
- `/bylanguage/{Idioma}`: Recibe un idioma y devuelve la cantidad de películas producidas en ese idioma.
- `/collection/{Franquicia}`: Recibe el nombre de una franquicia y devuelve la cantidad de películas, ganancia total y ganancia promedio.
- `/country/{Pais}`: Recibe un país y devuelve la cantidad de películas producidas en ese país.
- `/company/{Productora}`: Recibe el nombre de una productora y devuelve la ganancia total y la cantidad de películas que ha realizado.
- `/director/{Director}`: Recibe el nombre de un director y devuelve información sobre el éxito del director y una lista de películas dirigidas por él.
- `/recommendation/{titulo}`: Recibe el título de una película y devuelve una lista de 5 películas recomendadas similares.

Asegúrate de ejecutar el proyecto y luego puedes acceder a la API web utilizando las rutas mencionadas.

## Uso

El proyecto ha sido alojado en Render, por lo que puedes ir a la siguiente dirección y testear todas las funciones explicadas en el apartado anterior:
https://movies-recommendation-deploy.onrender.com/docs


¡Disfruta utilizando el sistema de recomendación de películas!

