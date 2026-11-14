"""
==============================================================================
🚀 FB PAGE BM AUTOMATED - MAIN CONTROLLER & CLI ENTRYPOINT
==============================================================================
Autonomous Facebook Business Manager & Page AI Boosting Engine.
Usage:
  python run_bm_automated.py --scan           # Run 1 scan & optimization cycle
  python run_bm_automated.py --daemon         # Run continuous background daemon
  python run_bm_automated.py --simulate       # Test a custom post copy & predict ROAS
  python run_bm_automated.py --train          # Train / retrain ML models locally
  python run_bm_automated.py --web            # Launch Web GUI Dashboard on Port 8088
==============================================================================
"""

import sys
import time
import argparse
import logging
from pathlib import Path

# Add parent directory to path so relative imports work seamlessly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import config

try:
    from meta_graph_api import MetaGraphAPIClient, FacebookPost
    from auto_boost_orchestrator import AutoBoostOrchestrator
    from ai_copy_hook_scorer import AICopyHookScorer
    from ad_performance_predictor import AdPerformancePredictor
    from viral_spike_detector import ViralSpikeDetector
    from auto_comment_responder import AutoCommentResponder
except ImportError:
    from fb_bm_core.meta_graph_api import MetaGraphAPIClient, FacebookPost
    from fb_bm_core.auto_boost_orchestrator import AutoBoostOrchestrator
    from fb_bm_core.ai_copy_hook_scorer import AICopyHookScorer
    from fb_bm_core.ad_performance_predictor import AdPerformancePredictor
    from fb_bm_core.viral_spike_detector import ViralSpikeDetector
    from fb_bm_core.auto_comment_responder import AutoCommentResponder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BM_AUTOMATED.Main")


def run_scan_cycle(orchestrator: AutoBoostOrchestrator):
    """Executes a single end-to-end scan and optimization cycle."""
    print("\n" + "=" * 80)
    print("🔍 [FB PAGE BM AUTOMATED] SCANNING CONNECTED FACEBOOK PAGE POSTS...")
    print("=" * 80)

    summary = orchestrator.run_single_cycle()
    print(f"📊 Posts Scanned:        {summary['posts_scanned']}")
    print(f"🚀 Posts Boosted:        {summary['posts_boosted_this_cycle']}")
    print(f"⚡ Total Active Boosts:  {summary['total_active_boosts']}")
    print(f"📈 Bandit Adjustments:   {summary['bandit_actions_taken']}")
    print("-" * 80)

    for rec in summary["records"]:
        print(f"\n📌 Post ID:      {rec.post_id} ({rec.post_type.upper()})")
        print(f"   Copy Snippet: \"{rec.message_snippet}\"")
        print(f"   Viral Score:  {rec.viral_velocity.viral_score}/100 [{rec.viral_velocity.classification}]")
        print(f"   Hook Quality: {rec.copy_analysis.hook_power_score}/100 (Grade: {rec.copy_analysis.overall_copy_grade})")
        print(f"   Policy Safe:  {'✅ PASS' if rec.copy_analysis.policy_compliance_pass else '❌ VIOLATION: ' + str(rec.copy_analysis.policy_violations)}")
        print(f"   Pred ROAS:    {rec.prediction.predicted_roas}X (Expected CTR: {rec.prediction.predicted_ctr}%)")
        print(f"   Action:       ▶ {rec.action_taken}")
        if rec.boost_result:
            print(f"   Campaign:     Created ID {rec.boost_result.campaign_id} (${rec.boost_result.daily_budget_usd}/day)")

    if summary["bandit_actions"]:
        print("\n" + "-" * 80)
        print("🧠 [SMART BUDGET BANDIT DECISIONS]")
        for b in summary["bandit_actions"]:
            print(f"   • Ad {b.ad_id} | Action: {b.action_type} | Realized ROAS: {b.realized_roas}X | New Budget: ${b.recommended_budget_usd:.2f}/day")
            print(f"     Reason: {b.reason}")

    # Check incoming page comments and auto-reply
    check_comment_auto_responder(orchestrator.api_client)

    print("=" * 80 + "\n")


def check_autonomous_publishing():
    """Checks and executes scheduled 4K multi-photo publishing for all enabled VIP pages."""
    try:
        from fb_page_autonomous_publisher import PageAutonomousPublisherEngine
        from fb_multi_tenant_manager import MultiTenantManager
        from bm_telegram_bot import BMTelegramBot
        mt_mgr = MultiTenantManager.get_instance()
        pub_engine = PageAutonomousPublisherEngine.get_instance()
        active_auto_pages = mt_mgr.get_active_auto_publish_pages()
        now_ts = time.time()
        for p in active_auto_pages:
            p_tok = p.get("page_token") or config.meta.access_token
            # Strict Isolation Guard: Never auto-publish fake campaigns to mock/unconnected pages in background daemon
            if not p_tok or p_tok.startswith(("MOCK_", "SIM_", "TEST_", "EAA_PAGE_TOKEN_")) or config.meta.is_mock:
                continue

            interval_sec = int(p.get("publish_interval_hours", 2)) * 3600
            last_time = float(p.get("last_auto_post_time", 0))
            if (now_ts - last_time) >= interval_sec:
                p_id = p.get("page_id")
                t_id = str(p.get("telegram_id"))
                p_name = p.get("page_name", p_id)
                logger.info(f"⏰ [DAEMON SCHEDULE] Time to publish for Page [{p_name}] ({p_id})!")
                p_client = MetaGraphAPIClient(
                    access_token=p_tok,
                    page_id=p_id,
                    ad_account_id=config.meta.ad_account_id,
                    api_version=config.meta.api_version,
                    is_mock=False
                )
                res = pub_engine.execute_scheduled_publishing_cycle(
                    client=p_client,
                    telegram_id=t_id,
                    interval_hours=int(p.get("publish_interval_hours", 2)),
                    photo_count=int(p.get("auto_post_photo_count", 4)),
                    force_now=False
                )
                if res.get("success"):
                    logger.info(f"🎉 Successfully published scheduled campaign: {res.get('post_id')}")
                    tbot = BMTelegramBot()
                    if tbot.is_configured and t_id:
                        tbot.send_message(t_id, res["summary_khmer"])
    except Exception as e:
        logger.error(f"Error in autonomous publishing daemon cycle: {e}")


def check_comment_auto_responder(client: MetaGraphAPIClient):
    """
    Patrols comments on connected Facebook Page posts, executes NLP intent classification,
    and deploys public replies, spam hiding, and private Messenger DMs.
    """
    try:
        responder = AutoCommentResponder(api_client=client)
        reports = responder.poll_and_respond_comments(limit_posts=3)
        if reports:
            print("\n" + "-" * 80)
            print(f"🤖 [AI COMMENT & MESSENGER PATROL] Executed {len(reports)} Actions:")
            for r in reports:
                status_icon = "🛡️ HIDDEN SPAM" if r.is_hidden_spam else ("💬 REPLIED + DM" if r.private_dm_sent else "💬 REPLIED")
                print(f"   • {status_icon} | [{r.intent}] User: {r.user_name}")
                print(f"     Comment: \"{r.message}\"")
                if r.public_reply_sent:
                    print(f"     Public:  \"{r.public_reply_sent[:70]}...\"")
            print("-" * 80)
    except Exception as e:
        logger.error(f"Error during comment auto-responder patrol: {e}")


def run_daemon(orchestrator: AutoBoostOrchestrator, interval_seconds: int = 300):
    """Runs continuous background automation loop."""
    print("=" * 80)
    print(f"🚀 [FB PAGE BM AUTOMATED] DAEMON STARTED (INTERVAL: {interval_seconds}s)")
    print(f"🔒 Target Page: {config.meta.page_id} | Mock Mode: {config.meta.is_mock}")
    print("=" * 80)

    try:
        while True:
            run_scan_cycle(orchestrator)
            check_autonomous_publishing()
            check_comment_auto_responder(orchestrator.api_client)
            print(f"⏳ Sleeping for {interval_seconds}s until next scan... (Press Ctrl+C to stop)")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Daemon stopped cleanly by user.")


def run_simulation():
    """Interactive CLI simulator to test copy, hooks, and predict ROAS."""
    print("\n" + "=" * 80)
    print("🧪 [AI COPY & ROAS SIMULATOR]")
    print("=" * 80)

    sample_copy = (
        "🔥 កំពូលយុទ្ធសាស្ត្រ Boost Facebook Page & Ads 2026! 🚀\n"
        "ចង់បង្កើនការលក់ 5X ដោយកាត់បន្ថយថ្លៃ Ad Spend មែនទេ?\n"
        "ចុចទីនេះដើម្បីទទួលបាន AI Quantitative Strategy ភ្លាមៗ! 💡💎 #FacebookAds #AI"
    )

    print(f"Testing default marketing post:\n---\n{sample_copy}\n---")

    scorer = AICopyHookScorer()
    c_res = scorer.evaluate_copy(sample_copy)

    detector = ViralSpikeDetector()
    dummy_post = FacebookPost(
        post_id="test_post_001",
        page_id="page101",
        message=sample_copy,
        created_time="2026-11-11T00:00:00",
        post_type="video",
        likes=350,
        comments=65,
        shares=120,
        video_views=2500,
        reach=6000,
        elapsed_minutes=45.0
    )
    v_res = detector.analyze_post(dummy_post)

    predictor = AdPerformancePredictor()
    feat = predictor.build_feature_dict(
        viral_score=v_res.viral_score,
        shares_ratio=v_res.shares_ratio,
        comments_ratio=v_res.comments_ratio,
        post_type=dummy_post.post_type,
        copy_text=sample_copy,
        hook_power=c_res.hook_power_score,
        urgency_score=c_res.urgency_score
    )
    p_res = predictor.predict(feat)

    print("\n📊 [SIMULATION RESULTS]")
    print(f"   • Hook Power:    {c_res.hook_power_score}/100 (Urgency: {c_res.urgency_score}/100, CTA: {c_res.cta_score}/100)")
    print(f"   • Policy Safe:   {'✅ 100% SAFE' if c_res.policy_compliance_pass else '❌ REJECTED'}")
    print(f"   • Copy Grade:    {c_res.overall_copy_grade}")
    print(f"   • Viral Score:   {v_res.viral_score}/100 [{v_res.classification}]")
    print(f"   • Predicted CTR: {p_res.predicted_ctr}% (Est CPC: ${p_res.predicted_cpc_usd})")
    print(f"   • Predicted CVR: {p_res.predicted_cvr}% (Est CPA: ${p_res.predicted_cpa_usd})")
    print(f"   • Predicted ROAS:{p_res.predicted_roas}X")
    print(f"   • Recommendation:{p_res.recommendation} (Confidence: {p_res.confidence*100:.0f}%)")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="FB Page BM Automated Controller")
    parser.add_argument("--scan", action="store_true", help="Run 1 scan & optimization cycle")
    parser.add_argument("--daemon", action="store_true", help="Run continuous background daemon")
    parser.add_argument("--simulate", action="store_true", help="Run AI copy & ROAS simulator")
    parser.add_argument("--train", action="store_true", help="Run model training locally")
    parser.add_argument("--web", action="store_true", help="Launch Web GUI Dashboard on Port 8088")
    parser.add_argument("--bot", action="store_true", help="Launch Telegram Bot Controller")
    parser.add_argument("--interval", type=int, default=300, help="Daemon scan interval in seconds")

    args = parser.parse_args()

    if args.bot:
        from bm_telegram_bot import main as bot_main
        bot_main()
        return

    if args.train:
        from train_fb_models_colab import main as train_main
        train_main()
        return

    if args.simulate:
        run_simulation()
        return

    if args.web:
        from web_dashboard import start_web_server
        start_web_server(port=config.web_port, host=config.web_host)
        return

    client = MetaGraphAPIClient(
        access_token=config.meta.access_token,
        page_id=config.meta.page_id,
        ad_account_id=config.meta.ad_account_id,
        api_version=config.meta.api_version,
        is_mock=config.meta.is_mock
    )
    orchestrator = AutoBoostOrchestrator(
        api_client=client,
        min_viral_score=config.policy.min_viral_score,
        min_predicted_roas=config.policy.min_predicted_roas,
        min_hook_quality=config.policy.min_hook_quality,
        test_daily_budget_usd=config.policy.test_daily_budget_usd,
        max_daily_budget_usd=config.policy.max_daily_budget_usd,
        max_active_boosts=config.policy.max_active_boosts,
        stop_loss_roas=config.policy.stop_loss_roas
    )

    if args.daemon:
        run_daemon(orchestrator, interval_seconds=args.interval)
    else:
        # Default behavior: run 1 full scan cycle
        run_scan_cycle(orchestrator)


if __name__ == "__main__":
    main()

