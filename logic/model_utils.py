import joblib

# Load once and reuse
model = joblib.load("models/lr/best_model.pkl")
vectorizer = joblib.load("models/lr/tfidf_vectorizer.pkl")
vocab = vectorizer.get_feature_names_out()

def get_model():
    return model

def get_vectorizer():
    return vectorizer

def get_vocab():
    return vocab
