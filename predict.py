import pickle
import os

# Load trained model
model_path = os.path.join(
    os.path.dirname(__file__),
    "disease_model.pkl"
)

with open(model_path, "rb") as file:
    model = pickle.load(file)


def predict_disease(
    age,
    gender,
    blood_pressure,
    sugar,
    heart_rate,
    symptom_score
):

    prediction = model.predict([[
        age,
        gender,
        blood_pressure,
        sugar,
        heart_rate,
        symptom_score
    ]])[0]

    probabilities = model.predict_proba([[
        age,
        gender,
        blood_pressure,
        sugar,
        heart_rate,
        symptom_score
    ]])[0]

    max_probability = max(probabilities)

    risk_percentage = round(
        max_probability * 100,
        2
    )

    return prediction, risk_percentage


# Test prediction
if __name__ == "__main__":

    disease, risk = predict_disease(
        age=45,
        gender=1,
        blood_pressure=150,
        sugar=150,
        heart_rate=95,
        symptom_score=4
    )

    print("Predicted Disease:", disease)
    print("Risk Percentage:", risk)