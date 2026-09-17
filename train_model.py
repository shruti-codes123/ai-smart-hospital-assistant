import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# =========================================================
# Training Dataset
# =========================================================

data = {
    "age": [
        25, 30, 45, 50, 35, 60, 40, 28, 55, 65,
        22, 32, 48, 52, 38, 58, 42, 27, 62, 34
    ],

    "gender": [
        0, 1, 1, 0, 1, 0, 1, 0, 1, 0,
        1, 0, 1, 0, 1, 0, 1, 0, 1, 0
    ],

    "blood_pressure": [
        120, 130, 150, 160, 125, 170, 145, 118, 155, 165,
        115, 135, 148, 158, 128, 175, 140, 122, 162, 132
    ],

    "sugar": [
        90, 100, 150, 180, 110, 200, 160, 85, 170, 190,
        80, 105, 145, 175, 115, 210, 155, 88, 185, 108
    ],

    "heart_rate": [
        72, 78, 95, 100, 75, 105, 92, 70, 98, 102,
        68, 80, 90, 96, 76, 108, 88, 71, 101, 79
    ],

    "symptom_score": [
        1, 2, 4, 5, 2, 6, 4, 1, 5, 6,
        1, 2, 4, 5, 2, 6, 3, 1, 5, 2
    ],

    "disease": [
        "Healthy",
        "Healthy",
        "Hypertension",
        "Diabetes",
        "Healthy",
        "Heart Disease",
        "Hypertension",
        "Healthy",
        "Heart Disease",
        "Diabetes",
        "Healthy",
        "Healthy",
        "Hypertension",
        "Diabetes",
        "Healthy",
        "Heart Disease",
        "Hypertension",
        "Healthy",
        "Diabetes",
        "Healthy"
    ]
}


# =========================================================
# Create DataFrame
# =========================================================

df = pd.DataFrame(data)


# =========================================================
# Features and Target
# =========================================================

X = df[
    [
        "age",
        "gender",
        "blood_pressure",
        "sugar",
        "heart_rate",
        "symptom_score"
    ]
]

y = df["disease"]


# =========================================================
# Train Test Split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# =========================================================
# Random Forest Model
# =========================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# =========================================================
# Accuracy
# =========================================================

accuracy = model.score(X_test, y_test)

print("Model trained successfully!")
print("Model Accuracy:", accuracy)


# =========================================================
# Save Model
# =========================================================

with open("disease_model.pkl", "wb") as file:

    pickle.dump(model, file)


print("Model saved as disease_model.pkl")