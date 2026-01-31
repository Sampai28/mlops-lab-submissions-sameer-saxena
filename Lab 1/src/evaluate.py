import joblib
import json
import os
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

x, y = load_digits(return_X_y=True)
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=25
)

os.makedirs("metrics", exist_ok=True)

models = {
    "LogisticRegression": joblib.load("models/LogisticRegression.joblib"),
    "RandomForest": joblib.load("models/RandomForest.joblib"),
    "GradientBoosting": joblib.load("models/GradientBoosting.joblib")
}

results = {}

for name, model in models.items():
    preds = model.predict(x_test)
    acc = accuracy_score(y_test, preds)
    results[name] = {"accuracy": acc}

best_model = None
worst_model = None
best_acc = -1
worst_acc = 1

for name in results:
    acc = results[name]["accuracy"]

    if acc > best_acc:
        best_acc = acc
        best_model = name

    if acc < worst_acc:
        worst_acc = acc
        worst_model = name

                        
summary = {
    "results": results,
    "best_model": best_model,
    "worst_model": worst_model
}

best_preds = models[best_model].predict(x_test)
cm = confusion_matrix(y_test, best_preds).tolist()

results[best_model]["confusion_matrix"] = cm

summary = {
    "results": results,
    "best_model": best_model,
    "worst_model": worst_model
}

with open("metrics/summary.json", "w") as f:
    json.dump(summary, f)

