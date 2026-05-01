"""import os
import joblib
from django.conf import settings

class FWIPredictor:
    def __init__(self):
        model_path = os.path.join(settings.BASE_DIR, 'supervisor', 'ml_model', 'xgb_best_model1.pkl')
        self.model = joblib.load(model_path)

    def predict(self, features):
        return self.model.predict([features])[0]"""
