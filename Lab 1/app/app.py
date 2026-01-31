import streamlit as st
import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_digits

st.set_page_config(page_title="MLOps Dashboard")

st.title("Digits Model Comparison Dashboard")

with open("metrics/summary.json") as f:
    summary = json.load(f)

results = summary["results"]
best_model = summary["best_model"]
worst_model = summary["worst_model"]

st.header("Model Performance Table")
df = pd.DataFrame(results).T
st.dataframe(df)

st.success(f"Best Model: {best_model}")
st.error(f"Worst Model: {worst_model}")

st.header("Confusion Matrix (Best Model)")
cm = results[best_model]["confusion_matrix"]

fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
st.pyplot(fig)

st.header("Sample Digit Prediction")

digits = load_digits()
idx = st.slider("Select Digit Index", 0, len(digits.images)-1)

st.image(digits.images[idx] / 16.0, width=150)
st.write("True Label:", digits.target[idx])

model = joblib.load("models/" + best_model + ".joblib")
pred = model.predict([digits.data[idx]])[0]

st.write("Predicted Label:", pred)
