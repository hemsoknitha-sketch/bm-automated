"""
==============================================================================
🚀 AUTONOMOUS AUTO-BOOST ORCHESTRATOR & CAMPAIGN DAEMON
==============================================================================
Central Intelligence Hub for Facebook Page & Business Manager Automation.
Orchestrates:
1. Scheduled / Event-driven scanning of Page posts
2. Real-time Viral Momentum detection
3. AI Copywriting & Policy compliance auditing
4. Machine Learning ROAS & CTR predictive hurdle checks
5. Autonomous Ad creation via Meta Graph API
6. Continuous Multi-Armed Bandit budget scaling & circuit breaker management
==============================================================================
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

from .meta_graph_api import MetaGraphAPIClient, FacebookPost, BoostedAdResult
from .viral_spike_detector import ViralSpikeDetector, PostEngagementVelocity
from .ai_copy_hook_scorer import AICopyHookScorer, HookAnalysisResult
from .ad_performance_predictor import AdPerformancePredictor, PredictionResult
from .smart_budget_bandit import SmartBudgetBandit, BanditAction

logger = logging.getLogger("BM_AUTOMATED.Orchestrator")


@dataclass
class PostEvaluationRecord:
    post_id: str
    message_snippet: str
    post_type: str
    viral_velocity: PostEngagementVelocity
    copy_analysis: HookAnalysisResult
    prediction: PredictionResult
    action_taken: str  # "BOOSTED", "REJECTED_LOW_VIRALITY", "REJECTED_LOW_ROAS", "REJECTED_POLICY_VIOLATION", "ALREADY_ACTIVE"
    boost_result: Optional[BoostedAdResult] = None
    timestamp: float = field(default_factory=time.time)


class AutoBoostOrchestrator:
    """
    Autonomous Engine that monitors Facebook Pages, scores posts, places targeted ads,
    and dynamically optimizes budgets.
    """

    def __init__(
        self,
        api_client: Optional[MetaGraphAPIClient] = None,
        min_viral_score: float = 70.0,
        min_predicted_roas: float = 2.20,
        min_hook_quality: float = 60.0,
        test_daily_budget_usd: float = 5.0,
        max_daily_budget_usd: float = 50.0,
        max_active_boosts: int = 5,
        stop_loss_roas: float = 1.20
    ):
        self.api_client = api_client or MetaGraphAPIClient()
        self.min_viral_score = min_viral_score
        self.min_predicted_roas = min_predicted_roas
        self.min_hook_quality = min_hook_quality
        self.test_daily_budget_usd = test_daily_budget_usd
        self.max_daily_budget_usd = max_daily_budget_usd
        self.max_active_boosts = max_active_boosts

        # Sub-engines
        self.viral_detector = ViralSpikeDetector(min_viral_threshold=min_viral_score)
        self.copy_scorer = AICopyHookScorer()
        self.predictor = AdPerformancePredictor()
        self.bandit = SmartBudgetBandit(
            test_budget_usd=test_daily_budget_usd,
            max_budget_usd=max_daily_budget_usd,
            stop_loss_roas=stop_loss_roas
        )

        # In-memory tracking
        self.active_boosts: Dict[str, BoostedAdResult] = {}
        self.evaluation_history: List[PostEvaluationRecord] = []
        self.bandit_actions_history: List[BanditAction] = []

    def evaluate_and_boost_post(self, post: FacebookPost) -> PostEvaluationRecord:
        """
        Runs comprehensive 360-degree algorithmic evaluation on a single Facebook post.
        """
        # Step 1: Check if already boosted
        if post.post_id in self.active_boosts:
            v_res = self.viral_detector.analyze_post(post)
            c_res = self.copy_scorer.evaluate_copy(post.message)
            features = self.predictor.build_feature_dict(
                viral_score=v_res.viral_score,
                shares_ratio=v_res.shares_ratio,
                comments_ratio=v_res.comments_ratio,
                post_type=post.post_type,
                copy_text=post.message,
                hook_power=c_res.hook_power_score,
                urgency_score=c_res.urgency_score
            )
            p_res = self.predictor.predict(features)
            return PostEvaluationRecord(
                post_id=post.post_id,
                message_snippet=post.message[:80] + "...",
                post_type=post.post_type,
                viral_velocity=v_res,
                copy_analysis=c_res,
                prediction=p_res,
                action_taken="ALREADY_ACTIVE",
                boost_result=self.active_boosts[post.post_id]
            )

        # Step 2: Viral Spike Analysis
        v_res = self.viral_detector.analyze_post(post)

        # Step 3: Copy Hook & Meta Policy Compliance Scan
        c_res = self.copy_scorer.evaluate_copy(post.message)

        # Step 4: Machine Learning CTR & ROAS Prediction
        features = self.predictor.build_feature_dict(
            viral_score=v_res.viral_score,
            shares_ratio=v_res.shares_ratio,
            comments_ratio=v_res.comments_ratio,
            post_type=post.post_type,
            copy_text=post.message,
            hook_power=c_res.hook_power_score,
            urgency_score=c_res.urgency_score
        )
        p_res = self.predictor.predict(features)

        # Step 5: Decision Gatekeeper
        action_taken = "REJECTED"
        boost_res = None

        if not c_res.policy_compliance_pass:
            action_taken = "REJECTED_POLICY_VIOLATION"
            logger.warning(f"Post {post.post_id} rejected: Meta Policy Violation ({c_res.policy_violations})")

        elif v_res.viral_score < self.min_viral_score:
            action_taken = "REJECTED_LOW_VIRALITY"
            logger.info(f"Post {post.post_id} rejected: Viral score ({v_res.viral_score}) < {self.min_viral_score}")

        elif p_res.predicted_roas < self.min_predicted_roas:
            action_taken = "REJECTED_LOW_ROAS"
            logger.info(f"Post {post.post_id} rejected: Predicted ROAS ({p_res.predicted_roas}x) < {self.min_predicted_roas}x")

        elif len(self.active_boosts) >= self.max_active_boosts:
            action_taken = "REJECTED_CAPACITY_FULL"
            logger.warning(f"Post {post.post_id} qualified, but active boosts ({len(self.active_boosts)}) reached maximum capacity.")

        else:
            # QUALIFIED FOR AUTONOMOUS BOOST!
            campaign_name = f"AutoBoost_{post.post_type.upper()}_{post.post_id[-6:]}"
            try:
                boost_res = self.api_client.create_boost_campaign(
                    post_id=post.post_id,
                    campaign_name=campaign_name,
                    daily_budget_usd=self.test_daily_budget_usd
                )
                self.active_boosts[post.post_id] = boost_res
                action_taken = "BOOSTED"
                logger.info(f"🚀 [AUTO-BOOST SUCCESS] Post {post.post_id} boosted with ${self.test_daily_budget_usd}/day! Pred ROAS: {p_res.predicted_roas}x")
            except Exception as e:
                action_taken = f"ERROR_LAUNCHING_{e}"
                logger.error(f"Failed to place boost for {post.post_id}: {e}")

        record = PostEvaluationRecord(
            post_id=post.post_id,
            message_snippet=post.message[:80] + ("..." if len(post.message) > 80 else ""),
            post_type=post.post_type,
            viral_velocity=v_res,
            copy_analysis=c_res,
            prediction=p_res,
            action_taken=action_taken,
            boost_result=boost_res
        )
        self.evaluation_history.append(record)
        return record

    def manage_live_boosts(self) -> List[BanditAction]:
        """
        Audits all currently running boosted ads, pulls real-time insights,
        and applies dynamic budget scaling or circuit breakers.
        """
        actions = []
        for post_id, boost_info in list(self.active_boosts.items()):
            ad_id = boost_info.ad_id
            adset_id = boost_info.adset_id
            curr_budget = boost_info.daily_budget_usd

            insights = self.api_client.get_live_ad_insights(ad_id)
            if not insights:
                continue

            action = self.bandit.evaluate_live_ad(
                ad_id=ad_id,
                adset_id=adset_id,
                current_budget_usd=curr_budget,
                insights=insights
            )
            actions.append(action)
            self.bandit_actions_history.append(action)

            # Execute action
            if action.action_type == "PAUSE_CIRCUIT_BREAKER":
                self.api_client.update_ad_status(ad_id, "PAUSED")
                self.active_boosts.pop(post_id, None)
                logger.warning(f"🛑 [CIRCUIT BREAKER] Paused ad {ad_id} (ROAS: {action.realized_roas}x)")

            elif action.action_type in ("SCALE_UP", "SCALE_DOWN"):
                self.api_client.update_adset_budget(adset_id, action.recommended_budget_usd)
                boost_info.daily_budget_usd = action.recommended_budget_usd
                logger.info(f"📈 [BUDGET UPDATE] AdSet {adset_id} budget updated to ${action.recommended_budget_usd:.2f}/day ({action.action_type})")

        return actions

    def run_single_cycle(self) -> Dict[str, Any]:
        """
        Executes one full scan and optimization cycle across all Page posts and live campaigns.
        """
        posts = self.api_client.get_page_posts(limit=10)
        evaluated_records = []
        for p in posts:
            rec = self.evaluate_and_boost_post(p)
            evaluated_records.append(rec)

        bandit_actions = self.manage_live_boosts()

        return {
            "cycle_timestamp": time.time(),
            "posts_scanned": len(posts),
            "posts_boosted_this_cycle": sum(1 for r in evaluated_records if r.action_taken == "BOOSTED"),
            "total_active_boosts": len(self.active_boosts),
            "bandit_actions_taken": len(bandit_actions),
            "records": evaluated_records,
            "bandit_actions": bandit_actions
        }

