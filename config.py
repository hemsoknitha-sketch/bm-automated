"""
==============================================================================
🚀 FB PAGE BM AUTOMATED - CONFIGURATION & SETTINGS
==============================================================================
Autonomous Facebook Business Manager & Page AI Boosting Engine
Provides seamless environment parsing, fallback mock modes, targeting presets,
and institutional safety guards.
==============================================================================
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Root directory of BM AUTOMATED
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# Auto-load .env if python-dotenv is present
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass


@dataclass
class MetaAPIConfig:
    app_id: str = os.getenv("META_APP_ID", "")
    app_secret: str = os.getenv("META_APP_SECRET", "")
    access_token: str = os.getenv("META_ACCESS_TOKEN", "")
    page_id: str = os.getenv("FB_PAGE_ID", "act_page_khmer_quant")
    ad_account_id: str = os.getenv("FB_AD_ACCOUNT_ID", "act_10023456789")
    business_id: str = os.getenv("FB_BUSINESS_ID", "biz_987654321")
    api_version: str = os.getenv("META_API_VERSION", "v20.0")
    
    # Auto-fallback to Simulation / Mock Mode if no live access token is provided
    @property
    def is_mock(self) -> bool:
        mock_env = os.getenv("FB_MOCK_MODE", "").lower()
        if mock_env in ("true", "1", "yes"):
            return True
        return not bool(self.access_token and len(self.access_token.strip()) > 15)


@dataclass
class AutoBoostPolicy:
    # Minimum viral momentum score (0-100) before post qualifies for auto-boost
    min_viral_score: float = float(os.getenv("MIN_VIRAL_SCORE", "70.0"))
    
    # Minimum predicted ROAS (Return On Ad Spend) hurdle
    min_predicted_roas: float = float(os.getenv("MIN_PREDICTED_ROAS", "2.2"))
    
    # Minimum AI Copywriting Hook Score (0-100)
    min_hook_quality: float = float(os.getenv("MIN_HOOK_QUALITY", "60.0"))
    
    # Initial exploratory daily test budget ($USD)
    test_daily_budget_usd: float = float(os.getenv("TEST_DAILY_BUDGET_USD", "5.0"))
    
    # Maximum budget cap per boosted ad set ($USD)
    max_daily_budget_usd: float = float(os.getenv("MAX_DAILY_BUDGET_USD", "50.0"))
    
    # Maximum active boosted posts running concurrently
    max_active_boosts: int = int(os.getenv("MAX_ACTIVE_BOOSTS", "5"))
    
    # Auto-Pause circuit breaker: if live ROAS falls below this, pause immediately
    stop_loss_roas: float = float(os.getenv("STOP_LOSS_ROAS", "1.20"))
    
    # Scan cadence for organic page posts in seconds (default: 300s / 5 mins)
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "300"))
    
    # Default targeting options
    target_countries: List[str] = field(default_factory=lambda: ["KH", "US", "SG", "TH"])
    age_min: int = 18
    age_max: int = 65
    genders: List[int] = field(default_factory=lambda: [1, 2]) # 1=Male, 2=Female


@dataclass
class ModelConfig:
    models_dir: Path = MODELS_DIR
    roas_model_path: Path = MODELS_DIR / "fb_roas_ensemble.pkl"
    ctr_model_path: Path = MODELS_DIR / "fb_ctr_ensemble.pkl"
    hook_scorer_path: Path = MODELS_DIR / "fb_hook_scorer.json"
    bandit_policy_path: Path = MODELS_DIR / "fb_bandit_policy.json"
    
    # Feature columns used for tabular training
    feature_columns: List[str] = field(default_factory=lambda: [
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
    ])


@dataclass
class TelegramConfig:
    bot_token: str = os.getenv("BM_TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    admin_id: str = os.getenv("BM_TELEGRAM_ADMIN_ID", os.getenv("TELEGRAM_ADMIN_ID", "859271875"))
    alerts_enabled: bool = os.getenv("BM_TELEGRAM_ALERTS", "true").lower() in ("true", "1", "yes")


@dataclass
class SystemConfig:
    meta: MetaAPIConfig = field(default_factory=MetaAPIConfig)
    policy: AutoBoostPolicy = field(default_factory=AutoBoostPolicy)
    models: ModelConfig = field(default_factory=ModelConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    web_port: int = int(os.getenv("BM_WEB_PORT", "8088"))
    web_host: str = os.getenv("BM_WEB_HOST", "0.0.0.0")
    web_public_url: str = os.getenv("WEB_PUBLIC_URL", "")


# Global singleton instance
config = SystemConfig()

