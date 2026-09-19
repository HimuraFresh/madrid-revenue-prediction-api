from flask import Flask, jsonify, request, render_template
import json
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Se cargan una vez al arrancar, no en cada petición

model = joblib.load("models/modelo_revenue_madrid.pkl")

with open("resources/barrios.json", encoding="utf-8") as f:
    BARRIOS = json.load(f)

with open("resources/defaults.json", encoding="utf-8") as f:
    DEFAULTS = json.load(f)

def construir_fila(data):
    """Combina lo que manda el usuario con los defaults y las derivaciones."""

    barrio = data.get("neighbourhood_cleansed")

    if barrio not in BARRIOS:
        raise ValueError(f"Barrio no reconocido: {barrio}")

    info = BARRIOS[barrio]

    fila = dict(DEFAULTS)

    # Lo que deriva el servidor a partir del barrio
    
    fila["neighbourhood_cleansed"] = barrio
    fila["neighbourhood_group_cleansed"] = info["distrito"]
    fila["latitude"] = info["lat"]
    fila["longitude"] = info["lon"]

    # Lo que pone el usuario, tal cual llega del formulario
    for campo in ["room_type", "accommodates", "bedrooms", "beds", "bathrooms",
                  "price", "n_amenities", "host_is_superhost", "instant_bookable",
                  "bano_compartido", "calculated_host_listings_count"]:
        fila[campo] = data[campo]

    # property_type se deriva de la modalidad elegida
    fila["property_type"] = (
        "Entire rental unit" if data["room_type"] == "Entire home/apt"
        else "Private room in rental unit"
    )

    # Precio por plaza
    fila["precio_por_persona"] = data["price"] / data["accommodates"]

    return fila

# Landing page
@app.route("/", methods=["GET"])
def hello():
    return render_template("index.html")

# Formulario de predicción
@app.route("/api/v1/predict-form", methods=["GET"])
def predict_form():
    return render_template("form.html", barrios=sorted(BARRIOS.keys()))

# Endpoint de predicción
@app.route("/api/v1/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se ha proporcionado un cuerpo JSON"}), 400

    try:
        fila = construir_fila(data)
        prediccion = model.predict(pd.DataFrame([fila]))
        revenue = float(np.expm1(prediccion[0]))

        return jsonify({"prediction": round(revenue, 2), "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
