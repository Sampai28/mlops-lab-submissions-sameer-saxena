import joblib
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import os
from sklearn.metrics import accuracy_score, f1_score
import json

x, y = load_digits(return_X_y=True)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=25) # 80% training, 20% testing

models = {
    "LogisticRegression": LogisticRegression(max_iter=500),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=25),
    "GradientBoosting": GradientBoostingClassifier(random_state=25)
}



os.makedirs("models", exist_ok=True)

for name, model in models.items():
    model.fit(x_train, y_train)
    joblib.dump(model, "models/" + name + ".joblib")