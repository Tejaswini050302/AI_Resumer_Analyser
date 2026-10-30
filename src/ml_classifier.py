import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class JobRoleClassifier:
    """
    Trains, evaluates, compares, and performs inference with 4 ML models:
    - Logistic Regression
    - Support Vector Machine (Calibrated LinearSVC)
    - Random Forest
    - XGBoost
    """

    DEFAULT_ROLES = [
        "Data Scientist",
        "Machine Learning Engineer",
        "Full Stack Developer",
        "Frontend Developer",
        "Backend Developer",
        "DevOps Engineer",
        "Data Analyst",
        "Cybersecurity Analyst",
        "Mobile App Developer",
        "Cloud Solutions Architect"
    ]

    def __init__(self, models_dir: str = None):
        if models_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, "models")
            
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.vectorizer = None
        self.label_encoder = None
        self.models: Dict[str, Any] = {}
        self.best_model_name: str = "Random Forest"
        self.metrics: Dict[str, Any] = {}
        self.confusion_matrices: Dict[str, Any] = {}

    def train_and_compare(self, df: pd.DataFrame, test_size: float = 0.25, random_state: int = 42) -> Dict[str, Any]:
        """
        Train and benchmark all 4 ML models on provided dataset.
        df must have 'text' (resume/profile text) and 'role' (target job role) columns.
        """
        X = df['text'].values
        y_raw = df['role'].values

        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(y_raw)

        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words='english'
        )
        X_vec = self.vectorizer.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_vec, y, test_size=test_size, random_state=random_state, stratify=y
        )

        candidate_models = {
            "Logistic Regression": LogisticRegression(max_iter=1000, C=1.5, random_state=random_state),
            "Support Vector Machine": CalibratedClassifierCV(
                LinearSVC(C=1.0, random_state=random_state, dual="auto")
            ),
            "Random Forest": RandomForestClassifier(
                n_estimators=150, max_depth=15, random_state=random_state, n_jobs=-1
            )
        }

        if XGBOOST_AVAILABLE:
            candidate_models["XGBoost"] = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                eval_metric="mlogloss",
                random_state=random_state
            )

        results = {}
        best_f1 = -1.0

        for name, clf in candidate_models.items():
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)

            acc = float(accuracy_score(y_test, y_pred))
            prec_weighted = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            rec_weighted = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
            f1_weighted = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))

            prec_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
            rec_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
            f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))

            cm = confusion_matrix(y_test, y_pred).tolist()

            results[name] = {
                "accuracy": round(acc * 100, 2),
                "precision_weighted": round(prec_weighted * 100, 2),
                "recall_weighted": round(rec_weighted * 100, 2),
                "f1_score_weighted": round(f1_weighted * 100, 2),
                "precision_macro": round(prec_macro * 100, 2),
                "recall_macro": round(rec_macro * 100, 2),
                "f1_score_macro": round(f1_macro * 100, 2),
            }

            self.confusion_matrices[name] = {
                "matrix": cm,
                "labels": list(self.label_encoder.classes_)
            }
            self.models[name] = clf

            if f1_weighted > best_f1:
                best_f1 = f1_weighted
                self.best_model_name = name

        self.metrics = results
        self.save_artifacts()
        return results

    def save_artifacts(self):
        """Save trained models, encoders, and metrics to disk."""
        model_pack = {
            "models": self.models,
            "vectorizer": self.vectorizer,
            "label_encoder": self.label_encoder,
            "best_model_name": self.best_model_name,
            "roles": list(self.label_encoder.classes_) if self.label_encoder else []
        }
        
        joblib_path = os.path.join(self.models_dir, "job_role_classifier.pkl")
        joblib.dump(model_pack, joblib_path)

        metrics_path = os.path.join(self.models_dir, "model_metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump({
                "metrics": self.metrics,
                "best_model": self.best_model_name,
                "confusion_matrices": self.confusion_matrices
            }, f, indent=2)

    def load_artifacts(self) -> bool:
        """Load trained models from disk if present."""
        joblib_path = os.path.join(self.models_dir, "job_role_classifier.pkl")
        metrics_path = os.path.join(self.models_dir, "model_metrics.json")

        if os.path.exists(joblib_path):
            try:
                pack = joblib.load(joblib_path)
                self.models = pack.get("models", {})
                self.vectorizer = pack.get("vectorizer")
                self.label_encoder = pack.get("label_encoder")
                self.best_model_name = pack.get("best_model_name", "Random Forest")

                if os.path.exists(metrics_path):
                    with open(metrics_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.metrics = data.get("metrics", {})
                        self.confusion_matrices = data.get("confusion_matrices", {})
                return True
            except Exception as e:
                print(f"Error loading model artifacts: {e}")
                return False
        return False

    def predict_roles(self, text: str, model_name: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Predict top suitable job roles for a resume or profile text.
        """
        if not self.models or not self.vectorizer or not self.label_encoder:
            if not self.load_artifacts():
                raise RuntimeError("ML Models are not trained or loaded.")

        target_model_name = model_name or self.best_model_name
        clf = self.models.get(target_model_name) or self.models.get(self.best_model_name)
        if clf is None:
            clf = list(self.models.values())[0]

        vec = self.vectorizer.transform([text])

        # Get probabilities
        if hasattr(clf, "predict_proba"):
            probs = clf.predict_proba(vec)[0]
        else:
            # Fallback for models without predict_proba
            dec = clf.decision_function(vec)[0]
            exp_dec = np.exp(dec - np.max(dec))
            probs = exp_dec / exp_dec.sum()

        top_indices = np.argsort(probs)[::-1][:top_k]

        predictions = []
        for idx in top_indices:
            role_name = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(probs[idx]) * 100
            predictions.append({
                "role": role_name,
                "confidence": round(confidence, 1),
                "model_used": target_model_name
            })

        return predictions
