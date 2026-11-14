"""
==============================================================================
🚀 KHMER MASTER / ANGKOR QUANT - FB PAGE BM AUTOMATED
🏛️ STATE-OF-THE-ART META AD MODELS TRAINER (GOOGLE COLAB & LOCAL SUITE)
==============================================================================
Trains institutional machine learning models for Facebook Business Manager
& Page Auto-Boosting:
1. ROAS Predictor (LightGBM Regressor) -> models/fb_roas_ensemble.pkl
2. CTR Predictor (LightGBM Regressor)  -> models/fb_ctr_ensemble.pkl
3. High-ROAS Classifier (XGBoost)      -> models/fb_profit_classifier.pkl
4. Feature Importances & Calibrated Thresholds
==============================================================================
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Auto-install dependencies on Colab environment if missing
REQUIRED_PACKAGES = ["lightgbm", "xgboost", "scikit-learn", "pandas", "numpy", "joblib"]

def verify_and_install_dependencies():
    print("📦 [SETUP] Verifying Python environment packages...")
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            print(f"  └─ Installing missing package: {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pkg], check=True)
    print("✅ [SETUP] All ML dependencies verified!")


verify_and_install_dependencies()

import numpy as np
import pandas as pd

try:
    from fb_bm_core.dataset_generator import AdDatasetGenerator
    from fb_bm_core.model_trainer import FBModelTrainer
except ImportError:
    from dataset_generator import AdDatasetGenerator
    from model_trainer import FBModelTrainer


def main():
    print("=" * 80)
    print("🚀 [FB PAGE BM AUTOMATED] INITIATING COLAB / LOCAL MODEL TRAINING")
    print("=" * 80)

    base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "models"
    data_dir = base_dir / "data"

    models_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dataset Generation
    dataset_csv_path = data_dir / "historical_ads_dataset.csv"
    generator = AdDatasetGenerator(seed=42)
    n_samples = 15000
    print(f"📊 [DATA ENGINE] Generating {n_samples} high-fidelity training records...")
    df = generator.generate_dataset(n_samples=n_samples)
    generator.save_dataset(df, dataset_csv_path)

    print(f"  └─ Dataset Shape: {df.shape}")
    print(f"  └─ Average Target ROAS: {df['target_roas'].mean():.2f}x")
    print(f"  └─ Average Target CTR:  {df['target_ctr'].mean():.2f}%")
    print(f"  └─ High-ROAS Positive Class Ratio: {df['is_profitable'].mean()*100:.1f}%\n")

    # 2. Model Training
    trainer = FBModelTrainer(models_dir=models_dir)
    results = trainer.train_models(df)

    print("\n" + "=" * 80)
    print("🏆 [TRAINING SUMMARY & MODEL BENCHMARKS]")
    print("=" * 80)
    print(f"📈 ROAS Predictor (LightGBM)  -> R²: {results['roas_r2']} | MAE: {results['roas_mae']}")
    print(f"🎯 CTR Predictor (LightGBM)   -> R²: {results['ctr_r2']} | MAE: {results['ctr_mae']}")
    print(f"⚡ High-ROAS Classifier (XGB) -> AUC-ROC: {results['profit_auc']}")
    print("\n🔥 Top 5 Predictive Alpha Features:")
    for f in results['top_features']:
        print(f"   • {f['feature']}: {f['importance']}")

    print("\n💾 Models successfully written to:")
    for m in results['models_saved']:
        print(f"   ✓ {m}")

    print("\n🎉 Model training complete! FB PAGE BM AUTOMATED is ready for live boost deployment.")
    print("=" * 80)


if __name__ == "__main__":
    main()

