import re
import string
import math

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    return text

def get_confidence(model, vect):
    try:
        if hasattr(model, "predict_proba"):
            return model.predict_proba(vect)[0][1] * 100
        else:
            margin = model.decision_function(vect)[0]
            return 1 / (1 + math.exp(-margin)) * 100
    except:
        return None
