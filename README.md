# ML Revenue Predictor — API de Predicción de Ingresos de Alquileres en Madrid

API REST desplegada en **Render** que predice el ingreso anual estimado de alojamientos turísticos en Madrid, a partir de un modelo XGBoost entrenado con datos de Airbnb.

**Demo en vivo:** [estimatupiso.onrender.com](https://estimatupiso.onrender.com/)

> Nota: la API está desplegada en el plan gratuito de Render, por lo que la primera petición tras un periodo de inactividad puede tardar unos 30 segundos en responder mientras el servicio se reactiva.

## Estructura del repositorio

```
├── data/
│   └── df_alquileres_original.csv     # Dataset de entrenamiento
├── models/
│   └── modelo_optimizado.pkl          # Modelo entrenado (XGBoost)
├── static/
│   └── style.css
├── templates/
│   ├── index.html                     # Landing page
│   └── form.html                      # Formulario de predicción
├── app_model.py                       # Aplicación Flask (API)
├── model.py                           # Script de entrenamiento del modelo
├── requirements.txt
├── .gitignore
└── README.md
```

## Modelo

- **Algoritmo**: XGBoost (optimizado con RandomizedSearchCV)
- **Target**: `revenue_log = log1p(estimated_revenue_l365d)`
- **Pipeline**: SimpleImputer (mediana) → XGBRegressor
- **Métricas en test**:
  - RMSE (log): 0.058
  - RMSE (€): 5.449,07
  - R²: 0.9998

## Endpoints

### `GET /`
Landing page con información del servicio y enlaces a los demás endpoints.

### `GET /api/v1/predict-form`
Formulario interactivo para introducir variables y obtener una predicción.

### `POST /api/v1/predict`
Endpoint principal de predicción. Recibe un JSON con las features del alojamiento y devuelve la predicción en euros. Los campos faltantes se completan con valores por defecto.

**Ejemplo de petición:**

```python
import requests

data = {
    "host_since": 3000,
    "host_response_rate": 95,
    "host_acceptance_rate": 90,
    "host_is_superhost": 1,
    "host_listings_count": 2,
    "host_total_listings_count": 2,
    "host_verifications": 3,
    "host_has_profile_pic": 1,
    "host_identity_verified": 1,
    "latitude": 40.42,
    "longitude": -3.70,
    "accommodates": 4,
    "bathrooms": 1,
    "bedrooms": 2,
    "beds": 2,
    "price": 80,
    "minimum_nights": 2,
    "maximum_nights": 365,
    "availability_365": 200,
    "number_of_reviews_ltm": 15,
    "estimated_occupancy_l365d": 250,
    "review_scores_rating": 4.5,
    "review_scores_accuracy": 4.6,
    "review_scores_cleanliness": 4.7,
    "review_scores_checkin": 4.8,
    "review_scores_communication": 4.9,
    "review_scores_location": 4.5,
    "review_scores_value": 4.3,
    "instant_bookable": 1,
    "reviews_per_month": 2.5
}

response = requests.post("https://estimatupiso.onrender.com/api/v1/predict", json=data)
print(response.json())
```

**Ejemplo de respuesta:**

```json
{
    "prediction": 24530.75,
    "status": "success",
    "note": "Se usaron valores por defecto para 22 campos faltantes."
}
```

La predicción se devuelve directamente en euros (ingreso anual estimado).

## Reentrenamiento del modelo

```bash
python model.py
```

Ejecuta el pipeline completo de preprocesado, optimización de hiperparámetros y guardado del modelo en `models/modelo_optimizado.pkl`.

## Ejecución local

```bash
pip install -r requirements.txt
python app_model.py
```

La app estará disponible en `http://127.0.0.1:5000`.

## Tecnologías

- **Python** — Flask, pandas, NumPy
- **Machine Learning** — scikit-learn, XGBoost, joblib
- **Despliegue** — Render

## Proyecto relacionado

El modelo servido por esta API se entrenó en [madrid-rental-revenue-prediction](https://github.com/HimuraFresh/madrid-rental-revenue-prediction), donde está todo el proceso de EDA, feature engineering y comparativa de modelos.

## Autores

Proyecto desarrollado en equipo durante el bootcamp de Data Science & IA de The Bridge:

- Nazareth Montero
- Javier Pascual ([@JavierPasAg](https://github.com/JavierPasAg))
- Sara Ruiz
- Román Diaz ([@HimuraFresh](https://github.com/HimuraFresh))