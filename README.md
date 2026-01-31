# Lab 1 MLOps Pipeline with Streamlit Dashboard

## Overview
This project demonstrates a simple end-to-end **MLOps workflow** including model training, evaluation, experiment comparison, and visualization using Streamlit.  
A CI pipeline is implemented using **GitHub Actions** to automatically train and evaluate models on every push.

This implementation uses the **Digits dataset**.

## Project Structure
mlops-lab-submissions-sameer-saxena/
├── Lab 1/
│   ├── src/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── requirements.txt
│   ├── app/
│   │   └── app.py
│   ├── models/
│   ├── metrics/
│   └── .github/workflows/
│       └── pipeline.yml
├── README.md
└── .gitignore

## Components
- **src/**: Contains the Python scripts for model training and evaluation.
- **app/**: Contains the Streamlit application for visualization.
- **models/**: Stores the trained model files.
- **metrics/**: Stores the evaluation metrics and summary.
- **.github/workflows/**: Contains the GitHub Actions workflow definition.

## Workflow
- **train.py**: Trains three different models (Logistic Regression, Random Forest, Gradient Boosting) on the Digits dataset and saves them to the `models/` directory.
- **evaluate.py**: Evaluates the trained models, calculates accuracy and confusion matrices, and saves the results to `metrics/summary.json`.
- **app.py**: A Streamlit application that visualizes the model performance, displays the best and worst models, and allows interactive exploration of digit predictions.
- **pipeline.yml**: A GitHub Actions workflow that automatically triggers the training and evaluation scripts whenever changes are pushed to the `lab-1` branch.

