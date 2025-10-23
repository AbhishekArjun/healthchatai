import os, pickle
from pathlib import Path

# Train a simple text classifier mapping symptom descriptions -> disease labels
def train_and_save(model_path, vect_path, data_csv=None):
    try:
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB
    except Exception as e:
        raise RuntimeError("scikit-learn is required. Install with: pip install scikit-learn") from e

    # If data_csv exists, try to load; else use synthetic examples
    texts = []
    labels = []
    if data_csv and Path(data_csv).exists():
        import csv
        with open(data_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'symptoms' in reader.fieldnames and 'disease' in reader.fieldnames:
                for row in reader:
                    texts.append(row['symptoms'])
                    labels.append(row['disease'])
    if not texts:
        samples = [
            ("I have fever and cough and runny nose", "Cold"),
            ("Sneezing, itchy eyes and runny nose", "Allergy"),
            ("Severe headache with nausea and sensitivity to light", "Migraine"),
            ("Sharp chest pain and shortness of breath", "Cardiac issue"),
            ("Stomach pain, vomiting and acidity", "Stomach ache"),
            ("High fever, body aches and chills", "Flu"),
            ("Rash and itchy skin after eating", "Skin allergy"),
            ("My head hurts and I feel a pounding pain", "Headache"),
            ("Chest discomfort and pain radiating to arm", "Cardiac issue"),
            ("Abdominal cramps and gas", "Gas"),
            ("Sore throat and mild fever", "Cold"),
            ("Watery eyes and sneezing", "Allergy"),
            ("Nausea and stomach cramps", "Stomach ache"),
            ("Persistent cough and high fever", "Flu"),
            ("Itchy red bumps on skin", "Skin allergy"),
        ]
        texts = [t for t,_ in samples]
        labels = [l for _,l in samples]

    vect = CountVectorizer()
    X = vect.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(vect_path, "wb") as f:
        pickle.dump(vect, f)
    print("Model trained and saved.")

if __name__ == "__main__":
    model_path = Path(__file__).parent / "model" / "model.pkl"
    vect_path = Path(__file__).parent / "model" / "vect.pkl"
    data_csv = Path(__file__).parent / "data" / "Training.csv"
    train_and_save(model_path, vect_path, data_csv if data_csv.exists() else None)
