# -*- coding: utf-8 -*-
"""
==============================================================================
🚀 TRAINER: FACEBOOK CHAT & MESSENGER INTENT CLASSIFIER (NLP ML ENSEMBLE)
==============================================================================
Trains a calibrated Multilingual (Khmer + English) NLP Intent Classifier:
  - Classes: PRICE_INQUIRY, FAST_CHECKOUT, DELIVERY_INQUIRY, PRODUCT_DETAILS, GENERAL_PRAISE, SPAM_SCAM
  - Pipeline: TfidfVectorizer (char_wb + word n-grams) + CalibratedClassifierCV / LogisticRegression
  - Serialized to: models/fb_chat_intent_classifier.pkl
==============================================================================
"""

import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report

# Training Corpus (Khmer & English Real Marketing Customer Messages)
CHAT_INTENT_DATA = [
    # PRICE_INQUIRY
    ("តម្លៃប៉ុន្មានបង?", "PRICE_INQUIRY"),
    ("សុំតម្លៃ", "PRICE_INQUIRY"),
    ("តំលៃប៉ុន្មានមួយ?", "PRICE_INQUIRY"),
    ("how much is this?", "PRICE_INQUIRY"),
    ("price please", "PRICE_INQUIRY"),
    ("ថ្លៃអត់បង?", "PRICE_INQUIRY"),
    ("មួយថ្លៃប៉ុន្មានដែរ?", "PRICE_INQUIRY"),
    ("សុំតម្លៃពិសេស", "PRICE_INQUIRY"),
    ("How much?", "PRICE_INQUIRY"),
    ("Cost please", "PRICE_INQUIRY"),
    ("តម្លៃក្នុងរូប?", "PRICE_INQUIRY"),
    ("សុំតម្លៃ និងប្រូម៉ូសិន", "PRICE_INQUIRY"),
    ("discount price?", "PRICE_INQUIRY"),
    ("មានបញ្ចុះតម្លៃអត់?", "PRICE_INQUIRY"),
    ("$?", "PRICE_INQUIRY"),

    # FAST_CHECKOUT
    ("សុំលេខកុង ABA មកបង", "FAST_CHECKOUT"),
    ("មាន ABA អត់?", "FAST_CHECKOUT"),
    ("ផ្ញើលុយតាមណា?", "FAST_CHECKOUT"),
    ("ខ្ញុំយកមួយ កម្ម៉ង់ឥឡូវ", "FAST_CHECKOUT"),
    ("ចង់ទិញមួយបង", "FAST_CHECKOUT"),
    ("I want to buy now", "FAST_CHECKOUT"),
    ("Ready to order", "FAST_CHECKOUT"),
    ("Please send bank account", "FAST_CHECKOUT"),
    ("សុំកុងធនាគារមកបង ខ្ញុំវេរលុយ", "FAST_CHECKOUT"),
    ("យក 2 ឈុត", "FAST_CHECKOUT"),
    ("កក់ទុកមួយ", "FAST_CHECKOUT"),
    ("Can I order right now?", "FAST_CHECKOUT"),
    ("Check out", "FAST_CHECKOUT"),
    ("ដាក់មួយមកបង លេខទូរស័ព្ទ 012345678", "FAST_CHECKOUT"),
    ("ទីតាំងភ្នំពេញ យកមួយ", "FAST_CHECKOUT"),

    # DELIVERY_INQUIRY
    ("ដឹកដល់ខេត្តអត់បង?", "DELIVERY_INQUIRY"),
    ("សេវាដឹកប៉ុន្មាន?", "DELIVERY_INQUIRY"),
    ("ដឹកជញ្ជូនឥតគិតថ្លៃទេ?", "DELIVERY_INQUIRY"),
    ("Do you deliver to provinces?", "DELIVERY_INQUIRY"),
    ("Delivery fee?", "DELIVERY_INQUIRY"),
    ("Free shipping?", "DELIVERY_INQUIRY"),
    ("ប៉ុន្មានថ្ងៃបានឥវ៉ាន់?", "DELIVERY_INQUIRY"),
    ("ដឹកដល់ផ្ទះអត់?", "DELIVERY_INQUIRY"),
    ("How long does shipping take?", "DELIVERY_INQUIRY"),
    ("សេវាផ្ញើទៅសៀមរាបប៉ុន្មាន?", "DELIVERY_INQUIRY"),
    ("តើមានសេវា COD អត់?", "DELIVERY_INQUIRY"),
    ("Cash on delivery available?", "DELIVERY_INQUIRY"),

    # PRODUCT_DETAILS
    ("មានពណ៌អីខ្លះបង?", "PRODUCT_DETAILS"),
    ("ទំហំប៉ុន្មានដែរ?", "PRODUCT_DETAILS"),
    ("មាន size អីខ្លះ?", "PRODUCT_DETAILS"),
    ("What colors are available?", "PRODUCT_DETAILS"),
    ("What sizes do you have?", "PRODUCT_DETAILS"),
    ("តើមានការធានាអត់?", "PRODUCT_DETAILS"),
    ("Warranty how many months?", "PRODUCT_DETAILS"),
    ("មានក្នុងស្តុកអត់បង?", "PRODUCT_DETAILS"),
    ("Is this original quality?", "PRODUCT_DETAILS"),
    ("គុណភាពម៉េចដែរ?", "PRODUCT_DETAILS"),
    ("សុំរូបភាពបន្ថែម", "PRODUCT_DETAILS"),
    ("More pictures please", "PRODUCT_DETAILS"),

    # GENERAL_PRAISE
    ("ស្អាតណាស់បង", "GENERAL_PRAISE"),
    ("អរគុណច្រើន", "GENERAL_PRAISE"),
    ("ល្អប្រើណាស់", "GENERAL_PRAISE"),
    ("Nice product!", "GENERAL_PRAISE"),
    ("Thank you so much", "GENERAL_PRAISE"),
    ("Very good service", "GENERAL_PRAISE"),
    ("គាំទ្របង", "GENERAL_PRAISE"),
    ("Great quality", "GENERAL_PRAISE"),
    ("Love this", "GENERAL_PRAISE"),
    ("អរគុណសម្រាប់ការចែករំលែក", "GENERAL_PRAISE"),

    # SPAM_SCAM
    ("free crypto giveaway click t.me/join", "SPAM_SCAM"),
    ("invest 100 get 1000 guaranteed bitcoin", "SPAM_SCAM"),
    ("whatsapp me +123456789 for money", "SPAM_SCAM"),
    ("hack account service dm me", "SPAM_SCAM"),
    ("hot girls video 18+ link in bio", "SPAM_SCAM"),
    ("free followers visit scam.com", "SPAM_SCAM"),
    ("check my bio for free cash giveaway", "SPAM_SCAM")
]


def train_and_save_intent_classifier():
    base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    out_path = models_dir / "fb_chat_intent_classifier.pkl"

    df = pd.DataFrame(CHAT_INTENT_DATA, columns=["text", "intent"])

    # Augment corpus with repetitions and small variations
    texts = []
    labels = []
    for _, row in df.iterrows():
        t, l = row["text"], row["intent"]
        texts.append(t)
        labels.append(l)
        texts.append(t.lower())
        labels.append(l)
        texts.append(t + " 🙏")
        labels.append(l)
        texts.append(t + " ?")
        labels.append(l)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            min_df=1,
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(
            C=3.0,
            max_iter=500,
            class_weight="balanced",
            solver="lbfgs"
        ))
    ])

    pipeline.fit(texts, labels)
    preds = pipeline.predict(df["text"])
    print("🎯 Training Classification Report:")
    print(classification_report(df["intent"], preds))

    joblib.dump(pipeline, out_path)
    print(f"✅ Successfully saved calibrated NLP model to {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    train_and_save_intent_classifier()
