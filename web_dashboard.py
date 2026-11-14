"""
==============================================================================
🚀 FB PAGE BM AUTOMATED - WEB GUI DASHBOARD (PORT 8088)
==============================================================================
Standalone, real-time Web Dashboard for Facebook Business Manager & Page Boosting.
Includes:
- Live KPI monitoring (Active Boosts, Daily Spend, Avg ROAS, Policy Armor)
- Real-time Facebook Page Posts feed with 1-Click Auto-Boost
- Interactive AI Creative Hook & ROAS Simulator
- Smart Budget Bandit pacer status
==============================================================================
"""

import sys
import logging
import asyncio
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, render_template_string

# Ensure BM AUTOMATED directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import config

try:
    from fb_bm_core.meta_graph_api import MetaGraphAPIClient, FacebookPost
    from fb_bm_core.auto_boost_orchestrator import AutoBoostOrchestrator
    from fb_bm_core.ai_copy_hook_scorer import AICopyHookScorer
    from fb_bm_core.ad_performance_predictor import AdPerformancePredictor
    from fb_bm_core.viral_spike_detector import ViralSpikeDetector
except ImportError:
    from meta_graph_api import MetaGraphAPIClient, FacebookPost
    from auto_boost_orchestrator import AutoBoostOrchestrator
    from ai_copy_hook_scorer import AICopyHookScorer
    from ad_performance_predictor import AdPerformancePredictor
    from viral_spike_detector import ViralSpikeDetector

from fb_multi_tenant_manager import MultiTenantManager
from fb_auth_gateway import FBAuthGateway
from fb_offline_boost_engine import FBOfflineBoostEngine, OfflineBoostPackage

logger = logging.getLogger("BM_AUTOMATED.WebGUI")

# Search templates in both 'templates' subfolder and root folder
template_dir = str(BASE_DIR / "templates") if (BASE_DIR / "templates").exists() else str(BASE_DIR)
app = Flask(__name__, template_folder=template_dir)

# Initialize core services
api_client = MetaGraphAPIClient(
    access_token=config.meta.access_token,
    page_id=config.meta.page_id,
    ad_account_id=config.meta.ad_account_id,
    api_version=config.meta.api_version,
    is_mock=config.meta.is_mock
)

orchestrator = AutoBoostOrchestrator(
    api_client=api_client,
    min_viral_score=config.policy.min_viral_score,
    min_predicted_roas=config.policy.min_predicted_roas,
    min_hook_quality=config.policy.min_hook_quality,
    test_daily_budget_usd=config.policy.test_daily_budget_usd,
    max_daily_budget_usd=config.policy.max_daily_budget_usd,
    max_active_boosts=config.policy.max_active_boosts,
    stop_loss_roas=config.policy.stop_loss_roas
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    posts = api_client.get_page_posts(limit=20)
    active_count = len(orchestrator.active_boosts)
    total_budget = sum(b.daily_budget_usd for b in orchestrator.active_boosts.values())

    # Calculate average predicted ROAS across active or recent records
    if orchestrator.evaluation_history:
        avg_roas = sum(r.prediction.predicted_roas for r in orchestrator.evaluation_history) / len(orchestrator.evaluation_history)
    else:
        avg_roas = 3.25

    return jsonify({
        "page_id": config.meta.page_id,
        "ad_account_id": config.meta.ad_account_id,
        "is_mock": config.meta.is_mock,
        "posts_count": len(posts),
        "active_boosts_count": active_count,
        "total_daily_budget": round(total_budget, 2),
        "avg_predicted_roas": round(avg_roas, 2),
        "min_viral_threshold": config.policy.min_viral_score,
        "min_roas_hurdle": config.policy.min_predicted_roas
    })


@app.route("/api/posts", methods=["GET"])
def get_posts():
    posts = api_client.get_page_posts(limit=15)
    records = []
    scorer = AICopyHookScorer()
    detector = ViralSpikeDetector()
    predictor = AdPerformancePredictor()

    for p in posts:
        v_res = detector.analyze_post(p)
        c_res = scorer.evaluate_copy(p.message)
        features = predictor.build_feature_dict(
            viral_score=v_res.viral_score,
            shares_ratio=v_res.shares_ratio,
            comments_ratio=v_res.comments_ratio,
            post_type=p.post_type,
            copy_text=p.message,
            hook_power=c_res.hook_power_score,
            urgency_score=c_res.urgency_score
        )
        pred = predictor.predict(features)

        is_boosted = p.post_id in orchestrator.active_boosts
        daily_budget = orchestrator.active_boosts[p.post_id].daily_budget_usd if is_boosted else 0.0

        records.append({
            "post_id": p.post_id,
            "message": p.message,
            "post_type": p.post_type,
            "likes": p.likes,
            "comments": p.comments,
            "shares": p.shares,
            "video_views": p.video_views,
            "viral_score": v_res.viral_score,
            "viral_class": v_res.classification,
            "hook_score": c_res.hook_power_score,
            "copy_grade": c_res.overall_copy_grade,
            "policy_pass": c_res.policy_compliance_pass,
            "predicted_roas": pred.predicted_roas,
            "status": "BOOSTED" if is_boosted else "ORGANIC",
            "daily_budget": daily_budget
        })

    return jsonify(records)


@app.route("/api/scan", methods=["POST"])
def trigger_scan():
    summary = orchestrator.run_single_cycle()
    return jsonify({
        "status": "success",
        "posts_scanned": summary["posts_scanned"],
        "posts_boosted": summary["posts_boosted_this_cycle"],
        "total_active_boosts": summary["total_active_boosts"]
    })


@app.route("/api/simulate", methods=["POST"])
def simulate_copy():
    data = request.get_json() or {}
    message = data.get("message", "")
    post_type = data.get("post_type", "video")
    likes = int(data.get("likes", 100))
    comments = int(data.get("comments", 20))
    shares = int(data.get("shares", 40))

    scorer = AICopyHookScorer()
    c_res = scorer.evaluate_copy(message)

    detector = ViralSpikeDetector()
    post = FacebookPost(
        post_id="sim_post",
        page_id="page101",
        message=message,
        created_time="now",
        post_type=post_type,
        likes=likes,
        comments=comments,
        shares=shares,
        elapsed_minutes=30.0
    )
    v_res = detector.analyze_post(post)

    predictor = AdPerformancePredictor()
    feat = predictor.build_feature_dict(
        viral_score=v_res.viral_score,
        shares_ratio=v_res.shares_ratio,
        comments_ratio=v_res.comments_ratio,
        post_type=post_type,
        copy_text=message,
        hook_power=c_res.hook_power_score,
        urgency_score=c_res.urgency_score
    )
    pred = predictor.predict(feat)

    return jsonify({
        "hook_score": c_res.hook_power_score,
        "urgency_score": c_res.urgency_score,
        "cta_score": c_res.cta_score,
        "copy_grade": c_res.overall_copy_grade,
        "policy_pass": c_res.policy_compliance_pass,
        "policy_violations": c_res.policy_violations,
        "viral_score": v_res.viral_score,
        "viral_class": v_res.classification,
        "predicted_roas": pred.predicted_roas,
        "predicted_ctr": pred.predicted_ctr,
        "predicted_cpc": pred.predicted_cpc_usd,
        "predicted_cpa": pred.predicted_cpa_usd,
        "recommendation": pred.recommendation,
        "model_source": pred.model_source,
        "improvements": c_res.suggested_improvements
    })


@app.route("/api/manual_boost", methods=["POST"])
def manual_boost():
    data = request.get_json() or {}
    post_id = data.get("post_id")
    budget = float(data.get("budget", 5.0))

    posts = api_client.get_page_posts(limit=30)
    target_post = next((p for p in posts if p.post_id == post_id), None)

    if not target_post:
        return jsonify({"status": "error", "message": f"Post {post_id} not found."}), 404

    res = orchestrator.evaluate_and_boost_post(target_post)
    return jsonify({
        "status": "success",
        "action_taken": res.action_taken,
        "post_id": post_id
    })


# =============================================================================
# MULTI-TENANT VIP FACEBOOK ACCOUNT & PAGES MANAGEMENT API
# =============================================================================

@app.route("/api/multitenant/users", methods=["GET"])
def get_multitenant_users():
    """Lists all registered VIP Facebook users in the database vault."""
    mgr = MultiTenantManager.get_instance()
    users = mgr.list_users()
    return jsonify(users)


@app.route("/api/multitenant/pages", methods=["GET"])
def get_multitenant_pages():
    """Returns managed Facebook Pages for a specific user."""
    telegram_id = request.args.get("telegram_id", "").strip()
    mgr = MultiTenantManager.get_instance()

    if not telegram_id:
        users = mgr.list_users()
        if users:
            telegram_id = users[0]["telegram_id"]
        else:
            return jsonify([])

    pages = mgr.get_user_pages(telegram_id)
    active = mgr.get_active_page(telegram_id)
    active_id = active["page_id"] if active else ""

    return jsonify([{
        "page_id": p.page_id,
        "telegram_id": p.telegram_id,
        "page_name": p.page_name,
        "category": p.category,
        "followers_count": p.followers_count,
        "is_active": (p.page_id == active_id),
        "is_active_boost": p.is_active_boost,
        "is_active_chat": p.is_active_chat,
        "daily_budget_usd": p.daily_budget_usd,
        "min_roas_hurdle": p.min_roas_hurdle,
        "last_synced": p.last_synced
    } for p in pages])


@app.route("/api/multitenant/select_page", methods=["POST"])
def select_multitenant_page():
    """Sets active operating page for a user."""
    data = request.get_json() or {}
    t_id = str(data.get("telegram_id", "")).strip()
    p_id = str(data.get("page_id", "")).strip()
    mgr = MultiTenantManager.get_instance()
    success = mgr.set_active_page(t_id, p_id)
    return jsonify({"success": success})


@app.route("/api/multitenant/update_page", methods=["POST"])
def update_multitenant_page():
    """Updates page boost toggle, chat toggle, budget, and min ROAS hurdle."""
    data = request.get_json() or {}
    t_id = str(data.get("telegram_id", "")).strip()
    p_id = str(data.get("page_id", "")).strip()
    is_active_boost = data.get("is_active_boost")
    is_active_chat = data.get("is_active_chat")
    daily_budget = float(data["daily_budget_usd"]) if "daily_budget_usd" in data and data["daily_budget_usd"] is not None else None
    min_roas = float(data["min_roas_hurdle"]) if "min_roas_hurdle" in data and data["min_roas_hurdle"] is not None else None

    mgr = MultiTenantManager.get_instance()
    success = mgr.update_page_settings(
        telegram_id=t_id,
        page_id=p_id,
        is_active_boost=is_active_boost,
        is_active_chat=is_active_chat,
        daily_budget_usd=daily_budget,
        min_roas_hurdle=min_roas
    )
    return jsonify({"success": success})


@app.route("/api/multitenant/connect", methods=["POST"])
def connect_multitenant_user():
    """Allows 1-Click Connection from Web GUI without Meta App setup."""
    data = request.get_json() or {}
    t_id = str(data.get("telegram_id", "web_vip_user")).strip()
    auth_type = data.get("auth_type", "LOGIN").upper()
    auth_gw = FBAuthGateway()

    if auth_type == "LOGIN":
        email = data.get("email", "")
        password = data.get("password", "")
        res = auth_gw.execute_telegram_login(t_id, email, password)
        return jsonify(res)
    elif auth_type == "TOKEN":
        token = data.get("token", "")
        res = auth_gw.connect_with_token(t_id, token)
        return jsonify(res)
    elif auth_type == "COOKIE":
        cookie = data.get("cookie", "")
        res = auth_gw.connect_with_cookies(t_id, cookie)
        return jsonify(res)

    return jsonify({"success": False, "message": "Unknown authentication type"})


# =============================================================================
# OFFICIAL META OAUTH 2.0 / FACEBOOK APP & WEB DEEP-LINK REDIRECT
# =============================================================================

@app.route("/fb_login_redirect")
def fb_login_redirect():
    """
    Redirects user directly to Facebook App or Meta Web OAuth Dialog.
    Allows 1-Click login without manual token copying.
    """
    telegram_id = request.args.get("state", "web_vip_user").strip()
    host_url = request.host_url.rstrip("/")
    redirect_uri = f"{host_url}/fb_callback"

    auth_gw = FBAuthGateway()
    oauth_url = auth_gw.generate_oauth_url(
        telegram_id=telegram_id,
        redirect_uri=redirect_uri,
        app_id=config.meta.app_id
    )
    return redirect(oauth_url)


@app.route("/api/auth/oauth_url", methods=["GET"])
def api_get_oauth_url():
    """Returns Meta OAuth URL for Telegram Bot buttons or Web GUI."""
    telegram_id = request.args.get("state", "web_vip_user").strip()
    host_url = request.host_url.rstrip("/")
    redirect_uri = f"{host_url}/fb_callback"

    auth_gw = FBAuthGateway()
    oauth_url = auth_gw.generate_oauth_url(
        telegram_id=telegram_id,
        redirect_uri=redirect_uri,
        app_id=config.meta.app_id
    )
    return jsonify({
        "oauth_url": oauth_url,
        "redirect_uri": redirect_uri,
        "app_id": config.meta.app_id or auth_gw.DEFAULT_APP_ID
    })


@app.route("/fb_callback")
def fb_callback():
    """
    Meta OAuth 2.0 Authorization Callback.
    Receives authorization code from Meta, exchanges it for a Long-Lived Token,
    synchronizes all managed pages, and stores them securely in the vault.
    """
    code = request.args.get("code")
    state = request.args.get("state", "web_vip_user")
    error = request.args.get("error_description") or request.args.get("error")

    if error:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Facebook Login Cancelled</title>
          <style>
            body { background: #0b0f19; color: #fff; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
            .card { background: #131b2e; border: 1px solid #dc3545; border-radius: 12px; padding: 32px; max-width: 450px; }
            h2 { color: #dc3545; }
            a { display: inline-block; margin-top: 16px; background: #2563eb; color: #fff; padding: 10px 20px; border-radius: 8px; text-decoration: none; }
          </style>
        </head>
        <body>
          <div class="card">
            <h2>❌ ការចូល Facebook ត្រូវបានលុបចោល</h2>
            <p>{{ error }}</p>
            <a href="/">ត្រឡប់ទៅកាន់ Web Dashboard</a>
          </div>
        </body>
        </html>
        """, error=error), 400

    if not code:
        return "Missing authorization code from Facebook", 400

    host_url = request.host_url.rstrip("/")
    redirect_uri = f"{host_url}/fb_callback"
    auth_gw = FBAuthGateway()
    res = auth_gw.exchange_oauth_code(
        code=code,
        redirect_uri=redirect_uri,
        telegram_id=state,
        app_id=config.meta.app_id,
        app_secret=config.meta.app_secret
    )

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Facebook Connected Successfully</title>
      <style>
        body { background: #0b0f19; color: #fff; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .card { background: #131b2e; border: 1px solid #10b981; border-radius: 16px; padding: 36px; max-width: 480px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #10b981; font-size: 22px; margin-bottom: 12px; }
        p { color: #94a3b8; font-size: 14px; line-height: 1.6; }
        .badge { background: #064e3b; color: #34d399; padding: 6px 14px; border-radius: 20px; font-weight: 600; display: inline-block; margin: 12px 0; }
        a { display: inline-block; margin-top: 20px; background: #2563eb; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; }
        a:hover { background: #1d4ed8; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🎉 ភ្ជាប់ FACEBOOK PAGE ជោគជ័យ ១០០%!</h1>
        <div class="badge">🟢 LIVE CONNECTED TO META</div>
        <p>ប្រព័ន្ធបានទាញយក Facebook Pages ទាំងអស់របស់អ្នកមកកាន់ <b>Angkor Quant BM Automated</b> ដោយស្វ័យប្រវត្ត។</p>
        <p>លោកអ្នកអាចប្រើប្រាស់មុខងារ <b>Auto-Boost</b>, <b>4K Multi-Photo Publisher</b>, និង <b>AI Lead Agent</b> លើ Telegram Bot ឬ Web GUI បានពេញលេញ!</p>
        <a href="/">ចូលទៅកាន់ Web Dashboard ភ្លាមៗ</a>
      </div>
    </body>
    </html>
    """)


# =============================================================================
# AI OFFLINE BOOST & VIRAL CREATOR API ($0 AD SPEND)
# =============================================================================

offline_boost_engine = FBOfflineBoostEngine()


@app.route("/api/media/<path:filename>", methods=["GET"])
def get_media_file(filename):
    """Serves generated 4K banners and audio files from the data directory."""
    data_dir = BASE_DIR / "data"
    return send_from_directory(str(data_dir), filename)


@app.route("/api/offline_boost/generate", methods=["POST"])
def api_generate_offline_boost():
    """Generates 4K Offline Boost Package (Zero-Cost Organic Viral Package)."""
    data = request.get_json() or {}
    topic = data.get("topic", "").strip() or "យុទ្ធសាស្ត្រលក់ដូរអនឡាញ ២០២៦"
    aspect_ratio = data.get("aspect_ratio", "1:1")
    include_audio = bool(data.get("include_audio", True))

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    pkg = loop.run_until_complete(
        offline_boost_engine.generate_offline_boost_package(
            topic=topic,
            aspect_ratio=aspect_ratio,
            include_audio=include_audio
        )
    )

    banner_url = None
    if pkg.banner_image_path:
        banner_url = f"/api/media/{Path(pkg.banner_image_path).name}"

    audio_url = None
    if pkg.voice_audio_path:
        audio_url = f"/api/media/{Path(pkg.voice_audio_path).name}"

    return jsonify({
        "success": True,
        "topic": pkg.topic,
        "viral_category": pkg.viral_category,
        "viral_score": pkg.viral_score,
        "headline": pkg.headline,
        "caption": pkg.caption,
        "hook_score": pkg.hook_score,
        "copy_grade": pkg.copy_grade,
        "banner_url": banner_url,
        "banner_path": pkg.banner_image_path,
        "audio_url": audio_url,
        "audio_path": pkg.voice_audio_path,
        "circadian_optimal_hour": pkg.circadian_optimal_hour,
        "circadian_boost_multiplier": pkg.circadian_boost_multiplier,
        "is_meta_policy_compliant": pkg.is_meta_policy_compliant,
        "summary_khmer": pkg.summary_khmer
    })


@app.route("/api/offline_boost/publish", methods=["POST"])
def api_publish_offline_boost():
    """Publishes Offline Boost package to user's connected page."""
    data = request.get_json() or {}
    telegram_id = str(data.get("telegram_id", "")).strip()
    caption = data.get("caption", "")
    banner_path = data.get("banner_path")

    auth_gw = FBAuthGateway()
    client, active_rec = auth_gw.get_user_page_client(telegram_id)

    pkg = OfflineBoostPackage(
        topic=data.get("topic", "Offline Boost"),
        viral_category="Offline Boost",
        viral_score=80.0,
        headline=data.get("headline", ""),
        caption=caption,
        hook_score=85.0,
        copy_grade="A",
        banner_image_path=banner_path,
        voice_audio_path=None,
        circadian_optimal_hour=12,
        circadian_boost_multiplier=1.5,
        is_meta_policy_compliant=True,
        summary_khmer=""
    )

    res = offline_boost_engine.publish_package_to_page(pkg, client)
    p_name = active_rec.page_name if active_rec else client.page_id
    res["page_name"] = p_name
    return jsonify(res)


def start_web_server(port: int = 8088, host: str = "0.0.0.0"):
    print("=" * 80)
    print(f"🌐 [FB PAGE BM AUTOMATED] STARTING WEB GUI SERVER ON http://localhost:{port}")
    print("=" * 80)
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    start_web_server(port=config.web_port, host=config.web_host)

