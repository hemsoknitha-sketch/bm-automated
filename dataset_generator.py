"""
==============================================================================
🚀 FACEBOOK AD & PAGE CAMPAIGN DATASET SYNTHESIZER
==============================================================================
Generates comprehensive, realistic, empirical training datasets for Meta Ads.
Includes:
- Post formats (Video, Reel, Carousel, Image, Status)
- Copy length, Hook power, Urgency index, Reading grade
- Organic velocity, Shares ratio, Comments ratio
- Audience parameters, Time of day, Day of week
- Realistic non-linear CTR, CVR, CPC, CPA, and ROAS target distributions
==============================================================================
"""

import math
import random
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("BM_AUTOMATED.DatasetGenerator")


class AdDatasetGenerator:
    """
    Synthesizes institutional-grade Facebook ad campaign records for machine learning training.
    """

    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

    def generate_dataset(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generates n_samples of historical Facebook Page and Ad Campaign data with rich features.
        """
        logger.info(f"Synthesizing {n_samples} Facebook ad campaign training samples...")

        # 1. Post formats
        format_choices = ["video", "reel", "carousel", "image", "status"]
        format_probs = [0.35, 0.30, 0.15, 0.15, 0.05]
        formats = np.random.choice(format_choices, size=n_samples, p=format_probs)

        # 2. Timing features
        hours = np.random.randint(0, 24, size=n_samples)
        days = np.random.randint(0, 7, size=n_samples)
        is_weekend = (days >= 5).astype(float)

        # 3. Organic engagement features
        # Lognormal distribution for organic velocity
        raw_velocity = np.random.lognormal(mean=2.8, sigma=0.85, size=n_samples)
        organic_velocity = np.clip(raw_velocity * 4.0, 5.0, 100.0)

        shares_ratio = np.random.beta(a=2.0, b=12.0, size=n_samples) # 0.02 to 0.45
        comments_ratio = np.random.beta(a=2.5, b=10.0, size=n_samples)

        # 4. Copywriting and Creative Features
        copy_length = np.random.normal(loc=350, scale=180, size=n_samples)
        copy_length = np.clip(copy_length, 40, 1500)

        hook_power = np.random.beta(a=5.0, b=3.5, size=n_samples) * 100.0
        urgency = np.random.beta(a=3.5, b=4.0, size=n_samples) * 100.0
        reading_grade = np.random.normal(loc=7.5, scale=1.5, size=n_samples)

        # 5. Audience and Target Features
        audience_size = np.random.uniform(0.5, 12.0, size=n_samples) # Millions
        interest_depth = np.random.randint(1, 6, size=n_samples)
        hist_page_ctr = np.random.normal(loc=2.2, scale=0.6, size=n_samples)
        hist_page_ctr = np.clip(hist_page_ctr, 0.8, 4.5)

        # One-hot encoding for format
        post_video = (formats == "video").astype(float)
        post_reel = (formats == "reel").astype(float)
        post_carousel = (formats == "carousel").astype(float)
        post_image = (formats == "image").astype(float)

        # 6. Realistic Non-Linear Target Generation (Ground Truth with Noise)
        # Prime hours (12-14 and 18-22) get engagement boost
        prime_hour_boost = np.where((hours >= 18) & (hours <= 22), 0.35, 0.0) + np.where((hours >= 12) & (hours <= 14), 0.20, 0.0)
        
        # CTR formula with feature interactions
        ctr = (
            hist_page_ctr * 0.70 +
            (hook_power / 100.0) * 1.65 +
            (organic_velocity / 100.0) * 1.10 +
            post_video * 0.75 +
            post_reel * 0.90 +
            post_carousel * 0.45 +
            prime_hour_boost +
            np.random.normal(0, 0.35, size=n_samples)
        )
        ctr = np.clip(ctr, 0.50, 9.50)

        # CPC formula (Inversely related to CTR and audience relevance)
        cpm = 5.50 + np.random.normal(0, 0.8, size=n_samples)
        cpc = np.clip(cpm / (ctr * 10.0), 0.02, 0.80)

        # CVR (Conversion Rate)
        cvr = (
            1.50 +
            (urgency / 100.0) * 1.80 +
            (shares_ratio * 4.50) +
            (hook_power / 100.0) * 0.80 +
            np.random.normal(0, 0.40, size=n_samples)
        )
        cvr = np.clip(cvr, 0.40, 9.0)

        # ROAS (Return On Ad Spend)
        # Direct non-linear multiplier: Viral momentum + High CVR + Low CPC = Huge ROAS
        roas = (
            1.20 +
            (organic_velocity / 100.0) * 2.10 +
            (shares_ratio * 4.0) +
            (hook_power / 100.0) * 1.20 +
            (urgency / 100.0) * 0.70 +
            post_reel * 0.45 +
            post_video * 0.30 -
            (cpc * 1.80) +
            np.random.normal(0, 0.45, size=n_samples)
        )
        roas = np.clip(roas, 0.40, 8.50)

        # Binary label: Was this ad highly profitable? (ROAS >= 2.2x)
        is_profitable = (roas >= 2.20).astype(int)

        df = pd.DataFrame({
            "organic_velocity_score": np.round(organic_velocity, 2),
            "organic_shares_ratio": np.round(shares_ratio, 3),
            "organic_comments_ratio": np.round(comments_ratio, 3),
            "post_type_video": post_video,
            "post_type_reel": post_reel,
            "post_type_carousel": post_carousel,
            "post_type_image": post_image,
            "copy_length_chars": np.round(copy_length, 0),
            "hook_power_score": np.round(hook_power, 2),
            "urgency_score": np.round(urgency, 2),
            "reading_grade_level": np.round(reading_grade, 1),
            "hour_of_day": hours,
            "day_of_week": days,
            "is_weekend": is_weekend,
            "target_audience_size_m": np.round(audience_size, 2),
            "audience_interest_depth": interest_depth,
            "page_historical_avg_ctr": np.round(hist_page_ctr, 2),
            "target_ctr": np.round(ctr, 2),
            "target_cpc": np.round(cpc, 3),
            "target_cvr": np.round(cvr, 2),
            "target_roas": np.round(roas, 2),
            "is_profitable": is_profitable
        })

        return df

    def save_dataset(self, df: pd.DataFrame, output_path: Path):
        """Saves generated dataset to CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset saved to {output_path} ({len(df)} rows).")

