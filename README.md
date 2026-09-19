# API de estimación de ingresos de alojamientos turísticos en Madrid

API REST en Flask que estima el ingreso anual de un alojamiento
turístico en Madrid a partir de doce datos del inmueble.

**Demo:** [estimatupiso.onrender.com](https://estimatupiso.onrender.com/)

> La API corre en el plan gratuito de Render, así que la primera
> petición tras un rato de inactividad tarda unos 30 segundos
> mientras el servicio se reactiva.

---

## Qué pide y qué completa el servidor

El modelo espera 29 variables, pero el formulario solo pide doce:
barrio, modalidad, plazas, habitaciones, camas, baños, baño
compartido, precio por noche, servicios ofrecidos, reserva
inmediata, superhost y número de alojamientos gestionados.

El resto lo completa el servidor:

**Derivadas del barrio.** El distrito y las coordenadas salen de una
tabla de centroides, construida como la mediana de latitud y longitud
de los anuncios de cada barrio.

**Derivadas de otros campos.** El precio por plaza y el tipo de
propiedad, que se deduce de la modalidad elegida.

**Valores por defecto.** Los campos del anfitrión (tasas de respuesta
y aceptación, antigüedad, verificación) se rellenan con la mediana o
la moda del conjunto de entrenamiento, no con ceros.

Ese reparto viene del caso de uso: quien consulta está proyectando un
alojamiento que todavía no ha publicado, así que solo puede aportar
lo que sabe del inmueble.

---

## Modelo

Pipeline de XGBoost con el preprocesado dentro, entrenado en
[madrid-rental-revenue-prediction](https://github.com/HimuraFresh/madrid-rental-revenue-prediction).
La API carga un único objeto y no replica ninguna transformación.

El target se modela en escala logarítmica y la predicción se devuelve
en euros aplicando `expm1`.

| Métrica (test) | Valor |
|---|---|
| RMSE (log) | 0,838 |
| R² (log) | 0,584 |
| MAE | 8.037 € |
| Error porcentual mediano | 43,3 % |

El modelo no usa reseñas, ocupación ni valoraciones: son datos que un
alojamiento sin publicar no tiene.

---

## Endpoints

### `GET /`
Landing page.

### `GET /api/v1/predict-form`
Formulario interactivo con los doce campos.

### `POST /api/v1/predict`
Recibe un JSON con los doce campos y devuelve el ingreso anual
estimado en euros.

```python
import requests

data = {
    "neighbourhood_cleansed": "Sol",
    "room_type": "Entire home/apt",
    "accommodates": 4,
    "bedrooms": 2,
    "beds": 3,
    "bathrooms": 1,
    "bano_compartido": 0,
    "price": 120,
    "n_amenities": 29,
    "instant_bookable": 1,
    "host_is_superhost": 0,
    "calculated_host_listings_count": 1
}

r = requests.post("https://estimatupiso.onrender.com/api/v1/predict", json=data)
print(r.json())
```

Respuesta:

```json
{
    "prediction": 18889.04,
    "status": "success"
}
```

Si el barrio no está entre los 127 reconocidos, devuelve un error
indicándolo en lugar de predecir sobre datos inventados.

---

## Ejecución local

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python app_model.py
```

Disponible en `http://127.0.0.1:5000`.

Las versiones del `requirements.txt` están fijadas a las de
entrenamiento: cargar el modelo bajo otras produce avisos de
compatibilidad y puede alterar las predicciones.

---

## Estructura del repositorio

```text
├── models/
│   └── modelo_revenue_madrid.pkl   pipeline completo
├── resources/
│   ├── barrios.json                centroides y distrito por barrio
│   └── defaults.json               valores por defecto del anfitrión
├── static/
│   └── css/style.css
├── templates/
│   ├── index.html
│   └── form.html
├── app_model.py
├── requirements.txt
└── README.md
```

El `.pkl` y los dos JSON se generan en el repo del modelo y se copian
aquí. Este repo no entrena, solo sirve.

---

## Stack

Flask, pandas, numpy, scikit-learn, xgboost, joblib y Render.

---

## Autoría

Trabajo original desarrollado en equipo durante el bootcamp de Data
Science e IA de The Bridge por Nazareth Montero, Javier Pascual
([@JavierPasAg](https://github.com/JavierPasAg)), Sara Ruiz y Román
Diaz ([@HimuraFresh](https://github.com/HimuraFresh)).

El rediseño de la API y el modelo que sirve actualmente son trabajo
individual de Román Diaz.