"""
==============================================================================
🚀 FB PAGE BM AUTOMATED - CORE PACKAGE
==============================================================================
"""

from .meta_graph_api import MetaGraphAPIClient, FacebookPost, AdCampaignTargeting
from .viral_spike_detector import ViralSpikeDetector, PostEngagementVelocity
from .ai_copy_hook_scorer import AICopyHookScorer, HookAnalysisResult
from .ad_performance_predictor import AdPerformancePredictor, PredictionResult
from .smart_budget_bandit import SmartBudgetBandit, BanditAction
from .auto_boost_orchestrator import AutoBoostOrchestrator
from .dataset_generator import AdDatasetGenerator
from .model_trainer import FBModelTrainer

__all__ = [
    "MetaGraphAPIClient",
    "FacebookPost",
    "AdCampaignTargeting",
    "ViralSpikeDetector",
    "PostEngagementVelocity",
    "AICopyHookScorer",
    "HookAnalysisResult",
    "AdPerformancePredictor",
    "PredictionResult",
    "SmartBudgetBandit",
    "BanditAction",
    "AutoBoostOrchestrator",
    "AdDatasetGenerator",
    "FBModelTrainer",
]

