"""import joblib
import os

class MLModel:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        if self._model is None:
            model_path = os.path.join(
                "C:/Users/lenovo/Desktop/fire-detection-web/supervisor/ml_model",
                "xgb_best_model1.pkl"
            )
            self._model = joblib.load(model_path)
        return self._model """
