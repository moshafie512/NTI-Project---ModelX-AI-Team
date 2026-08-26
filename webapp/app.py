import json
import os

import pandas as pd
import streamlit as st
from catboost import CatBoostRegressor

st.set_page_config(page_title="AI/DS Salary Predictor", page_icon="💰", layout="centered")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_model():
    model = CatBoostRegressor()
    model.load_model(os.path.join(BASE_DIR, "catboost_model.cbm"))
    return model


@st.cache_data
def load_metadata():
    with open(os.path.join(BASE_DIR, "model_metadata.json"), "r", encoding="utf-8") as f:
        return json.load(f)

model = load_model()
meta = load_metadata()

st.title("💰 AI / Data Science Salary Predictor")
st.write("Fill in the job details and get an estimated annual salary in USD.")

with st.form("prediction_form"):
    inputs = {}

    # Categorical fields -> dropdowns
    for col in meta["categorical_cols"]:
        options = meta["categorical_options"][col]
        label = col.replace("_", " ").title()
        inputs[col] = st.selectbox(label, options)

    # Numeric fields -> number inputs (except the yes/no field below)
    for col in meta["numeric_cols"]:
        if col == "uses_ai_tools_daily":
            continue
        rng = meta["numeric_ranges"][col]
        label = col.replace("_", " ").title()
        inputs[col] = st.number_input(
            label,
            min_value=float(rng["min"]),
            max_value=float(rng["max"]) * 2,  # allow some headroom above observed max
            value=float(rng["default"]),
        )

    # uses_ai_tools_daily -> yes/no checkbox instead of a raw 0/1 number
    if "uses_ai_tools_daily" in meta["numeric_cols"]:
        uses_ai = st.checkbox("Uses AI tools daily?")
        inputs["uses_ai_tools_daily"] = int(uses_ai)

    submitted = st.form_submit_button("Predict Salary")

if submitted:
    # Build a single-row dataframe with columns in the exact order the model was trained on
    row = {col: inputs[col] for col in meta["columns"]}
    X_input = pd.DataFrame([row], columns=meta["columns"])

    prediction = model.predict(X_input)[0]

    st.success(f"Estimated annual salary: **${prediction:,.0f}**")
