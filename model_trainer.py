"""
==============================================================================
🚀 MODEL TRAINER FOR FB ADS & VIRAL PREDICTION (LIGHTGBM + XGBOOST)
==============================================================================
Trains institutional machine learning models:
1. ROAS Predictor (LightGBM Regressor) -> models/fb_roas_ensemble.pkl
2. CTR Predictor (LightGBM Regressor)  -> models/fb_ctr_ensemble.pkl
3. High-ROAS Classifier (XGBoost)      -> models/fb_profit_classifier.pkl
4. Feature Importance & Validation Metrics
==============================================================================
"""

import os
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score
import lightgbm as lgb
import xgboost as xgb

logger = logging.getLogger("BM_AUTOMATED.Trainer")


class FBModelTrainer:
    """
    Trains and packages predictive models for Facebook Business Manager & Page automation.
    """

    FEATURE_COLS = [
        "organic_velocity_score",
        "organic_shares_ratio",
        "organic_comments_ratio",
        "post_type_video",
        "post_type_reel",
        "post_type_carousel",
        "post_type_image",
        "copy_length_chars",
        "hook_power_score",
        "urgency_score",
        "reading_grade_level",
        "hour_of_day",
        "day_of_week",
        "is_weekend",
        "target_audience_size_m",
        "audience_interest_depth",
        "page_historical_avg_ctr"
    ]

    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes end-to-end model training, validation, and serialization.
        """
        print("⚡ [TRAINING ENGINE] Splitting features and targets...")
        X = df[self.FEATURE_COLS]
        y_roas = df["target_roas"]
        y_ctr = df["target_ctr"]
        y_profit = df["is_profitable"]

        X_train, X_test, y_roas_train, y_roas_test = train_test_split(X, y_roas, test_size=0.20, random_state=42)
        _, _, y_ctr_train, y_ctr_test = train_test_split(X, y_ctr, test_size=0.20, random_state=42)
        _, _, y_profit_train, y_profit_test = train_test_split(X, y_profit, test_size=0.20, random_state=42)

        # 1. Train ROAS Predictor (LightGBM)
        print("🧠 [TRAINING] Training LightGBM ROAS Regression Model...")
        roas_model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=31,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            verbosity=-1
        )
        roas_model.fit(X_train, y_roas_train)
        roas_preds = roas_model.predict(X_test)
        roas_r2 = r2_score(y_roas_test, roas_preds)
        roas_mae = mean_absolute_error(y_roas_test, roas_preds)
        print(f"  └─ ROAS Model R²: {roas_r2:.4f} | MAE: {roas_mae:.4f}")

        # 2. Train CTR Predictor (LightGBM)
        print("🧠 [TRAINING] Training LightGBM CTR Regression Model...")
        ctr_model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=31,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            verbosity=-1
        )
        ctr_model.fit(X_train, y_ctr_train)
        ctr_preds = ctr_model.predict(X_test)
        ctr_r2 = r2_score(y_ctr_test, ctr_preds)
        ctr_mae = mean_absolute_error(y_ctr_test, ctr_preds)
        print(f"  └─ CTR Model R²: {ctr_r2:.4f} | MAE: {ctr_mae:.4f}")

        # 3. Train High-ROAS Classifier (XGBoost)
        print("🧠 [TRAINING] Training XGBoost High-ROAS Classifier...")
        profit_model = xgb.XGBClassifier(
            n_estimators=250,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            eval_metric="logloss"
        )
        profit_model.fit(X_train, y_profit_train)
        profit_prob = profit_model.predict_proba(X_test)[:, 1]
        profit_auc = roc_auc_score(y_profit_test, profit_prob)
        print(f"  └─ High-ROAS Classifier AUC-ROC: {profit_auc:.4f}")

        # 4. Save Models to Disk
        roas_path = self.models_dir / "fb_roas_ensemble.pkl"
        ctr_path = self.models_dir / "fb_ctr_ensemble.pkl"
        profit_path = self.models_dir / "fb_profit_classifier.pkl"

        joblib.dump(roas_model, roas_path)
        joblib.dump(ctr_model, ctr_path)
        joblib.dump(profit_model, profit_path)
        print(f"✅ [SAVED] All models serialized to {self.models_dir}")

        # Extract top feature importances
        feature_importance = pd.DataFrame({
            "feature": self.FEATURE_COLS,
            "importance": roas_model.feature_importances_
        }).sort_values("importance", ascending=False)

        return {
            "roas_r2": round(float(roas_r2), 4),
            "roas_mae": round(float(roas_mae), 4),
            "ctr_r2": round(float(ctr_r2), 4),
            "ctr_mae": round(float(ctr_mae), 4),
            "profit_auc": round(float(profit_auc), 4),
            "top_features": feature_importance.head(5).to_dict(orient="records"),
            "models_saved": [str(roas_path), str(ctr_path), str(profit_path)]
        }

