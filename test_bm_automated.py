"""
==============================================================================
🧪 COMPREHENSIVE TEST SUITE - FB PAGE BM AUTOMATED
==============================================================================
Validates all sub-modules of the autonomous Facebook Business Manager & Page system:
1. Configuration & Mock Environment
2. Meta Graph & Marketing API Mock Engine
3. Viral Spike & Organic Momentum Detector
4. AI Copy Hook Scorer & Meta Policy Shield (Khmer & English)
5. Machine Learning ROAS & CTR Performance Predictor
6. Smart Budget Bandit & Circuit Breaker Logic
7. End-to-End Autonomous Orchestrator Cycle
8. Dataset Generator & Schema Verification
==============================================================================
"""

import sys
import unittest
from pathlib import Path

# Ensure BM AUTOMATED directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import config

try:
    from fb_bm_core.meta_graph_api import MetaGraphAPIClient, FacebookPost, AdCampaignTargeting
    from fb_bm_core.viral_spike_detector import ViralSpikeDetector
    from fb_bm_core.ai_copy_hook_scorer import AICopyHookScorer
    from fb_bm_core.ad_performance_predictor import AdPerformancePredictor
    from fb_bm_core.smart_budget_bandit import SmartBudgetBandit
    from fb_bm_core.auto_boost_orchestrator import AutoBoostOrchestrator
    from fb_bm_core.dataset_generator import AdDatasetGenerator
    from fb_bm_core.fb_confluence_matrix import FBPostBoostConfluenceMatrix, FBChatLeadConfluenceMatrix
    from fb_bm_core.auto_comment_responder import AutoCommentResponder
except ImportError:
    from meta_graph_api import MetaGraphAPIClient, FacebookPost, AdCampaignTargeting
    from viral_spike_detector import ViralSpikeDetector
    from ai_copy_hook_scorer import AICopyHookScorer
    from ad_performance_predictor import AdPerformancePredictor
    from smart_budget_bandit import SmartBudgetBandit
    from auto_boost_orchestrator import AutoBoostOrchestrator
    from dataset_generator import AdDatasetGenerator
    from fb_confluence_matrix import FBPostBoostConfluenceMatrix, FBChatLeadConfluenceMatrix
    from auto_comment_responder import AutoCommentResponder


class TestFBPagesBMAutomated(unittest.TestCase):

    def setUp(self):
        self.api_client = MetaGraphAPIClient(is_mock=True)
        self.viral_detector = ViralSpikeDetector(min_viral_threshold=70.0)
        self.copy_scorer = AICopyHookScorer()
        self.predictor = AdPerformancePredictor()
        self.bandit = SmartBudgetBandit(test_budget_usd=5.0, max_budget_usd=50.0, stop_loss_roas=1.20)
        self.orchestrator = AutoBoostOrchestrator(api_client=self.api_client)

    def test_01_config_and_mock_environment(self):
        """Verifies system defaults and safe fallback mode."""
        self.assertTrue(self.api_client.is_mock)
        posts = self.api_client.get_page_posts(limit=10)
        self.assertGreaterEqual(len(posts), 3)
        self.assertIn("video", [p.post_type for p in posts])

    def test_02_meta_api_mock_operations(self):
        """Verifies mock campaign, adset, and ad creation."""
        res = self.api_client.create_boost_campaign(
            post_id="post_test_999",
            campaign_name="TestCampaign",
            daily_budget_usd=5.0
        )
        self.assertEqual(res.status, "ACTIVE")
        self.assertEqual(res.daily_budget_usd, 5.0)
        self.assertTrue(res.campaign_id.startswith("mock_camp_"))

        # Test status and budget updates
        self.assertTrue(self.api_client.update_ad_status(res.ad_id, "PAUSED"))
        self.assertTrue(self.api_client.update_adset_budget(res.adset_id, 15.0))

        # Test live insights
        insights = self.api_client.get_live_ad_insights(res.ad_id)
        self.assertIn("purchase_roas", insights)
        self.assertGreater(insights["purchase_roas"], 0)

    def test_03_viral_spike_detector(self):
        """Verifies viral momentum scoring and classification."""
        # High-viral post
        viral_post = FacebookPost(
            post_id="p_viral",
            page_id="page1",
            message="Viral launch!",
            created_time="now",
            post_type="video",
            likes=500,
            comments=120,
            shares=200,
            reach=10000,
            elapsed_minutes=30.0
        )
        res_viral = self.viral_detector.analyze_post(viral_post)
        self.assertGreaterEqual(res_viral.viral_score, 70.0)
        self.assertTrue(res_viral.should_boost)
        self.assertIn(res_viral.classification, ("VIRAL_EXPLOSION", "STRONG_TRACTION"))

        # Low-viral post
        dead_post = FacebookPost(
            post_id="p_dead",
            page_id="page1",
            message="Hello",
            created_time="now",
            post_type="status",
            likes=5,
            comments=0,
            shares=0,
            reach=100,
            elapsed_minutes=120.0
        )
        res_dead = self.viral_detector.analyze_post(dead_post)
        self.assertLess(res_dead.viral_score, 45.0)
        self.assertFalse(res_dead.should_boost)
        self.assertEqual(res_dead.classification, "LOW_MOMENTUM")

    def test_04_ai_copy_hook_scorer_and_policy(self):
        """Verifies copy grading and Meta policy violation interception."""
        # Good marketing copy (Khmer + English)
        good_copy = (
            "🚀 កំពូលយុទ្ធសាស្ត្រ Boost Facebook Ads 2026! 💡\n"
            "បង្កើនការលក់ 5X ដោយកាត់បន្ថយថ្លៃ Ad Spend!\n"
            "ចុចទីនេះដើម្បីទទួលបានដំណោះស្រាយភ្លាមៗ! 💎"
        )
        res_good = self.copy_scorer.evaluate_copy(good_copy)
        self.assertTrue(res_good.policy_compliance_pass)
        self.assertIn(res_good.overall_copy_grade, ("A+", "A", "B"))
        self.assertGreaterEqual(res_good.hook_power_score, 60.0)

        # Policy violating copy (Get rich quick / guaranteed profits)
        bad_copy = "Get rich quick with 100% guaranteed profit today! ធានាចំណេញ ១០០%!"
        res_bad = self.copy_scorer.evaluate_copy(bad_copy)
        self.assertFalse(res_bad.policy_compliance_pass)
        self.assertEqual(res_bad.overall_copy_grade, "F")
        self.assertGreater(len(res_bad.policy_violations), 0)

    def test_05_ad_performance_predictor(self):
        """Verifies CTR, ROAS, and financial metric prediction."""
        feat = self.predictor.build_feature_dict(
            viral_score=85.0,
            shares_ratio=0.25,
            comments_ratio=0.15,
            post_type="video",
            copy_text="Super ad copy",
            hook_power=88.0,
            urgency_score=75.0
        )
        pred = self.predictor.predict(feat)
        self.assertGreaterEqual(pred.predicted_roas, 2.0)
        self.assertGreater(pred.predicted_ctr, 1.5)
        self.assertGreater(pred.confidence, 0.70)
        self.assertIn(pred.recommendation, ("STRONG_BUY_BOOST", "TEST_BUDGET"))

    def test_06_smart_budget_bandit_actions(self):
        """Verifies budget scaling, learning phase, and circuit breaker."""
        # 1. Learning phase (spend < $6)
        act_learn = self.bandit.evaluate_live_ad("ad1", "adset1", 5.0, {"spend": 3.50, "purchase_roas": 1.10})
        self.assertEqual(act_learn.action_type, "MAINTAIN")

        # 2. Scale Up Winner (spend >= $6 and ROAS >= 2.50)
        act_winner = self.bandit.evaluate_live_ad("ad2", "adset2", 5.0, {"spend": 12.0, "purchase_roas": 3.80})
        self.assertEqual(act_winner.action_type, "SCALE_UP")
        self.assertGreater(act_winner.recommended_budget_usd, 5.0)

        # 3. Circuit Breaker (spend >= $8 and ROAS < 1.20)
        act_loss = self.bandit.evaluate_live_ad("ad3", "adset3", 5.0, {"spend": 10.0, "purchase_roas": 0.85})
        self.assertEqual(act_loss.action_type, "PAUSE_CIRCUIT_BREAKER")
        self.assertEqual(act_loss.recommended_budget_usd, 0.0)

    def test_07_orchestrator_end_to_end_cycle(self):
        """Verifies full auto-boost orchestration cycle."""
        summary = self.orchestrator.run_single_cycle()
        self.assertGreaterEqual(summary["posts_scanned"], 1)
        self.assertIsInstance(summary["records"], list)
        self.assertGreaterEqual(len(summary["records"]), 1)

    def test_08_dataset_generator(self):
        """Verifies dataset generation integrity."""
        gen = AdDatasetGenerator(seed=123)
        df = gen.generate_dataset(n_samples=100)
        self.assertEqual(len(df), 100)
        self.assertIn("target_roas", df.columns)
        self.assertIn("target_ctr", df.columns)
        self.assertIn("is_profitable", df.columns)

    def test_09_post_boost_confluence_matrix(self):
        """Verifies 10-dimension Post Boost Confluence Matrix calculations."""
        matrix = FBPostBoostConfluenceMatrix()

        # High-confluence viral video post during peak hour
        history_viral = [
            {"likes": 20, "comments": 5, "shares": 10, "views": 200},
            {"likes": 80, "comments": 25, "shares": 50, "views": 1000},
            {"likes": 250, "comments": 90, "shares": 180, "views": 5000},
            {"likes": 600, "comments": 220, "shares": 450, "views": 15000},
            {"likes": 1200, "comments": 450, "shares": 900, "views": 35000}
        ]
        res_viral = matrix.compute_boost_confluence(
            engagement_history=history_viral,
            caption_hook_score=85.0,
            predicted_roas=3.20,
            post_type="reel",
            current_hour_utc=5.0, # 12:00 ICT Lunch Peak
            policy_pass=True
        )
        self.assertGreaterEqual(res_viral["boost_score"], 70.0)
        self.assertEqual(res_viral["decision"], "STRONG_BOOST")
        self.assertGreater(res_viral["budget_multiplier"], 1.0)
        self.assertGreater(len(res_viral["reasons"]), 0)

        # Policy violation veto test
        res_bad = matrix.compute_boost_confluence(
            engagement_history=history_viral,
            caption_hook_score=90.0,
            predicted_roas=4.0,
            policy_pass=False
        )
        self.assertEqual(res_bad["decision"], "REJECTED_POLICY_VIOLATION")
        self.assertEqual(res_bad["boost_score"], 0.0)
        self.assertEqual(res_bad["budget_multiplier"], 0.0)

    def test_10_chat_lead_confluence_matrix(self):
        """Verifies Messenger Lead Confluence Matrix and Fibonacci follow-ups."""
        chat_matrix = FBChatLeadConfluenceMatrix()

        # Hot VIP Lead inquiring about payment and price
        now = 100000.0
        thread = [
            {"sender": "user", "text": "សួស្តីបង ចង់ដឹងតម្លៃប៉ុន្មានដែរ?", "timestamp": now},
            {"sender": "page", "text": "សួស្តីបង! តម្លៃពិសេស $25 បាទ", "timestamp": now + 15},
            {"sender": "user", "text": "មានសេវាដឹកដល់ផ្ទះអត់? សុំលេខកុង ABA មកបង", "timestamp": now + 35}
        ]
        lead_eval = chat_matrix.compute_chat_lead_confluence(thread)
        self.assertGreaterEqual(lead_eval["lead_score"], 70.0)
        self.assertEqual(lead_eval["stage"], "HOT_VIP_BUYER")
        self.assertEqual(lead_eval["ai_prompt_mode"], "CLOSING_MODE")
        self.assertTrue(lead_eval["harmonic_journey"]["is_pcz_active"])

        # Test Fibonacci Cadence Follow-Up Engine
        f_1h = chat_matrix.get_fibonacci_followup_message(1.05, customer_name="សុខា")
        self.assertIsNotNone(f_1h)
        self.assertEqual(f_1h["fib_hour_node"], 1.0)
        self.assertIn("សុខា", f_1h["followup_text"])

        f_8h = chat_matrix.get_fibonacci_followup_message(8.02, customer_name="តារា")
        self.assertIsNotNone(f_8h)
        self.assertEqual(f_8h["fib_hour_node"], 8.0)

        f_off = chat_matrix.get_fibonacci_followup_message(4.5)
        self.assertIsNone(f_off)

    def test_11_comment_responder_integration(self):
        """Verifies AutoCommentResponder integration with Confluence Lead Scorer."""
        responder = AutoCommentResponder(api_client=self.api_client)
        rep = responder.process_comment(
            comment_id="c_123",
            post_id="p_999",
            user_name="Chan",
            message="សួស្តីបង តម្លៃប៉ុន្មានដែរ? ចង់កម្ម៉ង់"
        )
        self.assertEqual(rep.intent, "PRICE_INQUIRY")
        self.assertTrue(rep.private_dm_sent)
        self.assertIsNotNone(rep.confluence_analysis)
        self.assertGreater(rep.confluence_analysis["lead_score"], 0.0)


if __name__ == "__main__":
    unittest.main()

