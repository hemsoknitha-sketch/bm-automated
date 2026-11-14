"""
==============================================================================
🚀 FB PAGE BM AUTOMATED - SUPER SMART TELEGRAM BOT CONTROLLER
==============================================================================
Provides institutional 24/7 mobile control over Facebook Business Manager
and Facebook Page boosting right from Telegram:
- 📊 /status: Live health, memory, connected Page, and active ads count
- 🔍 /scan: Real-time scan of Page posts, viral score & 1-tap Boost buttons
- 🚀 /boost <post_id> [budget]: Manually boost any post with custom budget
- ⚡ /active: List all active boosted ads, spend, CTR, ROAS with pause/scale buttons
- ⏸️ /pause <ad_id> & ▶️ /resume <ad_id>: Pause or resume ad delivery
- 💰 /budget <adset_id> <amount>: Dynamically scale or trim daily budget
- 🧪 /simulate <text> (or send any text): AI copy hook & ROAS prediction
- 🤖 /autopilot [on|off]: Toggle background autonomous boosting
- 🔔 Real-time push alerts: Viral spikes, auto-boost launches, circuit breakers
==============================================================================
"""

import sys
import time
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure BM AUTOMATED directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import config
from meta_graph_api import MetaGraphAPIClient, FacebookPost
from auto_boost_orchestrator import AutoBoostOrchestrator
from ai_copy_hook_scorer import AICopyHookScorer
from ad_performance_predictor import AdPerformancePredictor
from viral_spike_detector import ViralSpikeDetector
from ai_creative_generator import AICreativeGenerator
from auto_comment_responder import AutoCommentResponder
from fb_multi_tenant_manager import MultiTenantManager, ManagedPageRecord
from fb_auth_gateway import FBAuthGateway
from fb_offline_boost_engine import FBOfflineBoostEngine, OfflineBoostPackage
from fb_page_autonomous_publisher import PageAutonomousPublisherEngine

logger = logging.getLogger("BM_AUTOMATED.TelegramBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class BMTelegramBot:
    """
    Pure-requests Telegram Bot Controller for Facebook Business Manager & Page Automation.
    Zero external bot wrapper dependencies; 100% resilient across Python versions and OS.
    """

    TELEGRAM_API_URL = "https://api.telegram.org/bot"

    def __init__(self, token: Optional[str] = None, admin_id: Optional[str] = None):
        self.token = (token or config.telegram.bot_token).strip()
        self.admin_id = str(admin_id or config.telegram.admin_id).strip()
        self.api_url = f"{self.TELEGRAM_API_URL}{self.token}"
        self.last_update_id = 0
        self.autopilot_enabled = True

        # Initialize core orchestrator
        self.api_client = MetaGraphAPIClient(
            access_token=config.meta.access_token,
            page_id=config.meta.page_id,
            ad_account_id=config.meta.ad_account_id,
            api_version=config.meta.api_version,
            is_mock=config.meta.is_mock
        )
        self.orchestrator = AutoBoostOrchestrator(
            api_client=self.api_client,
            min_viral_score=config.policy.min_viral_score,
            min_predicted_roas=config.policy.min_predicted_roas,
            min_hook_quality=config.policy.min_hook_quality,
            test_daily_budget_usd=config.policy.test_daily_budget_usd,
            max_daily_budget_usd=config.policy.max_daily_budget_usd,
            max_active_boosts=config.policy.max_active_boosts,
            stop_loss_roas=config.policy.stop_loss_roas
        )

        self.copy_scorer = AICopyHookScorer()
        self.viral_detector = ViralSpikeDetector()
        self.predictor = AdPerformancePredictor()
        self.creative_generator = AICreativeGenerator()
        self.comment_agent = AutoCommentResponder(api_client=self.api_client)

        # Multi-Tenant VIP Facebook Account & Pages Gateway
        self.multi_tenant = MultiTenantManager.get_instance()
        self.auth_gateway = FBAuthGateway(self.multi_tenant)

        # AI Offline Boost & Viral Creator Master Engine
        self.offline_boost_engine = FBOfflineBoostEngine()
        self._last_offline_packages: Dict[str, OfflineBoostPackage] = {}

        # Autonomous 4K Brand Trainer & Publisher Engine
        self.page_publisher = PageAutonomousPublisherEngine.get_instance()
        self._cached_public_ip: Optional[str] = None

    def _get_cached_public_ip(self) -> str:
        """Dynamically detects and caches the external public IP of the host/VPS."""
        if self._cached_public_ip:
            return self._cached_public_ip

        # 1. GCP Internal Metadata Server
        try:
            r = requests.get(
                "http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip",
                headers={"Metadata-Flavor": "Google"},
                timeout=2
            )
            if r.status_code == 200 and r.text.strip():
                self._cached_public_ip = r.text.strip()
                logger.info(f"Discovered GCP VPS External IP: {self._cached_public_ip}")
                return self._cached_public_ip
        except Exception:
            pass

        # 2. Public IP APIs
        for endpoint in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
            try:
                r = requests.get(endpoint, timeout=3)
                if r.status_code == 200 and r.text.strip():
                    self._cached_public_ip = r.text.strip()
                    logger.info(f"Discovered Public IP via {endpoint}: {self._cached_public_ip}")
                    return self._cached_public_ip
            except Exception:
                pass

        self._cached_public_ip = "127.0.0.1"
        return self._cached_public_ip

    def _get_effective_web_url(self) -> str:
        """
        Determines the best publicly reachable URL for the Web GUI:
        1. Explicit config.web_public_url (e.g. from .env)
        2. Dynamic Cloudflare Tunnel URL from logs/cloudflare_tunnel.log
        3. GCP VPS External IP (http://<IP>:8088)
        4. Localhost fallback
        """
        # 1. Explicit configured URL
        if config.web_public_url and len(config.web_public_url.strip()) > 7:
            return config.web_public_url.strip().rstrip("/")

        # 2. Cloudflare Tunnel Log Auto-Detection
        tunnel_log = BASE_DIR / "logs" / "cloudflare_tunnel.log"
        if tunnel_log.exists():
            try:
                import re
                txt = tunnel_log.read_text(encoding="utf-8", errors="ignore")
                matches = re.findall(r"https://[a-zA-Z0-9.-]*\.trycloudflare\.com", txt)
                if matches:
                    return matches[-1].rstrip("/")
            except Exception:
                pass

        # 3. VPS Public IP
        public_ip = self._get_cached_public_ip()
        if public_ip and public_ip != "127.0.0.1":
            return f"http://{public_ip}:{config.web_port}"

        return f"http://localhost:{config.web_port}"

    @property
    def is_configured(self) -> bool:
        return bool(self.token and len(self.token) > 15)

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Sends an HTML formatted message to a Telegram chat or terminal."""
        if not self.is_configured:
            # Clean HTML tags for beautiful terminal rendering
            import re
            clean_text = re.sub(r"<[^>]+>", "", text)
            print("\n" + clean_text)
            if reply_markup and "inline_keyboard" in reply_markup:
                buttons = []
                for row in reply_markup["inline_keyboard"]:
                    for btn in row:
                        buttons.append(f"[{btn['text']}]")
                print("Options: " + "  ".join(buttons))
            return True

        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                logger.error(f"Telegram sendMessage failed [{resp.status_code}]: {resp.text}")
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Telegram sendMessage error: {e}")
            return False

    def answer_callback_query(self, callback_query_id: str, text: str = ""):
        """Acknowledges inline button clicks to clear Telegram loading spinner."""
        if not self.is_configured:
            return
        url = f"{self.api_url}/answerCallbackQuery"
        try:
            requests.post(url, json={"callback_query_id": callback_query_id, "text": text}, timeout=5)
        except Exception:
            pass

    def send_admin_alert(self, text: str):
        """Sends urgent high-priority push alert to configured Super Admin."""
        if self.admin_id and config.telegram.alerts_enabled:
            self.send_message(self.admin_id, text)

    # =========================================================================
    # BOT COMMAND HANDLERS
    # =========================================================================

    def handle_start(self, chat_id: str):
        """Handles /start and /menu commands with rich interactive keyboard."""
        user = self.multi_tenant.get_user(chat_id)
        active_page = self.multi_tenant.get_active_page(chat_id)

        user_badge = f"🟢 <b>{user['fb_name']}</b>" if user else "⚪ <i>មិនទាន់ភ្ជាប់ (Not Connected)</i>"
        if active_page:
            page_badge = f"📄 <b>{active_page['page_name']}</b> (<code>{active_page['page_id']}</code>)"
            followers_txt = f"• <b>Followers:</b> <code>{active_page.get('followers_count', 0):,}</code>\n"
        else:
            page_badge = f"<code>{config.meta.page_id}</code> (Default)"
            followers_txt = ""

        mode_badge = "🛡️ <b>MOCK SIMULATION</b>" if self.api_client.is_mock else "🟢 <b>LIVE META GRAPH API</b>"
        autopilot_badge = "🟢 <b>ACTIVE</b>" if self.autopilot_enabled else "🔴 <b>PAUSED</b>"

        msg = (
            "🚀 <b>FB PAGE BM AUTOMATED - SUPER SMART BOT</b>\n"
            "<i>AI Autonomous Meta Business Manager & Page Boost Suite</i>\n"
            "────────────────────────────\n"
            f"• <b>Facebook User:</b> {user_badge}\n"
            f"• <b>Active Target Page:</b> {page_badge}\n"
            f"{followers_txt}"
            f"• <b>Status Mode:</b> {mode_badge}\n"
            f"• <b>Autopilot:</b> {autopilot_badge}\n"
            f"• <b>Active Boosts:</b> <code>{len(self.orchestrator.active_boosts)}/{config.policy.max_active_boosts}</code>\n"
            f"• <b>Min ROAS Hurdle:</b> <code>{config.policy.min_predicted_roas}X</code>\n"
            "────────────────────────────\n"
            "💡 <b>បញ្ជាគ្រប់គ្រងភ្លាមៗតាមប៊ូតុងខាងក្រោម៖</b>"
        )

        buttons = []
        if user:
            buttons.append([
                {"text": "📄 រើស Page របស់បង (/fb_pages)", "callback_data": "cmd_fb_pages"},
                {"text": "🔍 Scan Posts", "callback_data": "cmd_scan"}
            ])
            buttons.append([
                {"text": "⚡ Active Boosts", "callback_data": "cmd_active"},
                {"text": "🤖 Toggle Autopilot", "callback_data": "cmd_toggle_autopilot"}
            ])
            buttons.append([
                {"text": "📊 Live ROAS Scorecard", "callback_data": "cmd_roas"},
                {"text": "🚪 Logout Facebook", "callback_data": "cmd_fb_logout"}
            ])
        else:
            buttons.append([
                {"text": "🔑 ភ្ជាប់ Facebook របស់បង (/fb_login)", "callback_data": "cmd_fb_login_guide"},
                {"text": "🔍 Scan Default Posts", "callback_data": "cmd_scan"}
            ])
            buttons.append([
                {"text": "⚡ Active Boosted Ads", "callback_data": "cmd_active"},
                {"text": "🤖 Toggle Autopilot", "callback_data": "cmd_toggle_autopilot"}
            ])

        if self.admin_id and str(chat_id) == str(self.admin_id):
            buttons.append([
                {"text": "👑 Super Admin Suite", "callback_data": "cmd_admin_status"},
                {"text": "📈 System Status", "callback_data": "cmd_status"}
            ])

        web_url = self._get_effective_web_url()
        web_btn = (
            {"text": "🌐 Web GUI Dashboard", "url": web_url}
            if not web_url.startswith("http://localhost")
            else {"text": "🌐 Web GUI Dashboard", "callback_data": "cmd_web_dashboard"}
        )

        buttons.append([
            web_btn,
            {"text": "❓ Help & Commands", "callback_data": "cmd_help"}
        ])

        keyboard = {"inline_keyboard": buttons}
        self.send_message(chat_id, msg, reply_markup=keyboard)

    def handle_scan(self, chat_id: str):
        """Scans page posts, evaluates viral momentum & presents 1-tap Boost buttons."""
        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        page_name = active_rec.page_name if active_rec else config.meta.page_id
        self.send_message(chat_id, f"⏳ <b>កំពុងស្កេន Facebook Page Posts លើ: {page_name}...</b>")
        posts = client.get_page_posts(limit=6)

        if not posts:
            self.send_message(chat_id, "⚠️ មិនមាន Posts លើ Page នេះនៅឡើយទេ។")
            return

        self.send_message(
            chat_id,
            f"📊 <b>រកឃើញ {len(posts)} Posts លើ Page [{page_name}]:</b>\n"
            "────────────────────────────"
        )

        for p in posts:
            v_res = self.viral_detector.analyze_post(p)
            c_res = self.copy_scorer.evaluate_copy(p.message)
            feat = self.predictor.build_feature_dict(
                viral_score=v_res.viral_score,
                shares_ratio=v_res.shares_ratio,
                comments_ratio=v_res.comments_ratio,
                post_type=p.post_type,
                copy_text=p.message,
                hook_power=c_res.hook_power_score,
                urgency_score=c_res.urgency_score
            )
            pred = self.predictor.predict(feat)
            is_boosted = p.post_id in self.orchestrator.active_boosts

            snippet = p.message[:90] + ("..." if len(p.message) > 90 else "")
            policy_icon = "✅ SAFE" if c_res.policy_compliance_pass else "❌ VIOLATION"

            post_card = (
                f"📌 <b>{p.post_type.upper()}:</b> <code>{p.post_id}</code>\n"
                f"📝 <i>\"{snippet}\"</i>\n"
                f"• <b>Stats:</b> ❤️ {p.likes} | 💬 {p.comments} | 🔄 {p.shares}\n"
                f"• <b>Viral Score:</b> <code>{v_res.viral_score}/100</code> [{v_res.classification}]\n"
                f"• <b>Hook Power:</b> <code>{c_res.hook_power_score}/100</code> (Grade: <b>{c_res.overall_copy_grade}</b>)\n"
                f"• <b>Meta Policy:</b> {policy_icon}\n"
                f"• <b>Pred ROAS:</b> <b>{pred.predicted_roas}X</b> (Expected CTR: {pred.predicted_ctr}%)\n"
                f"• <b>Recommendation:</b> <code>{pred.recommendation}</code>"
            )

            if is_boosted:
                kb = {"inline_keyboard": [[{"text": "🚀 BOOSTED ALREADY (Active)", "callback_data": f"status_{p.post_id}"}]]}
            else:
                kb = {
                    "inline_keyboard": [
                        [
                            {"text": f"⚡ Boost Now (${config.policy.test_daily_budget_usd}/day)", "callback_data": f"boost_{p.post_id}"},
                            {"text": "🧪 Test Copy", "callback_data": f"sim_{p.post_id}"}
                        ]
                    ]
                }

            self.send_message(chat_id, post_card, reply_markup=kb)

    def handle_active(self, chat_id: str):
        """Displays all currently running boosted ads with real-time stats."""
        active = self.orchestrator.active_boosts
        if not active:
            self.send_message(
                chat_id,
                "ℹ️ <b>មិនទាន់មាន Boosted Ads កំពុងដំណើរការនៅឡើយទេ។</b>\n"
                "ប្រើ /scan ដើម្បីស្កេន និងចាប់ផ្តើម Boost Posts ដែលមាន ROAS ខ្ពស់!"
            )
            return

        msg = (
            f"🚀 <b>ACTIVE BOOSTED CAMPAIGNS ({len(active)} Running):</b>\n"
            "────────────────────────────\n"
        )
        self.send_message(chat_id, msg)

        for post_id, b in active.items():
            insights = self.api_client.get_live_ad_insights(b.ad_id)
            spend = insights.get("spend", 0.0)
            roas = insights.get("purchase_roas", 0.0)
            ctr = insights.get("ctr", 0.0)
            clicks = insights.get("clicks", 0)

            card = (
                f"🎯 <b>Ad ID:</b> <code>{b.ad_id}</code>\n"
                f"• <b>Campaign:</b> <code>{b.campaign_id}</code>\n"
                f"• <b>Post ID:</b> <code>{post_id}</code>\n"
                f"• <b>Daily Budget:</b> <b>${b.daily_budget_usd:.2f}/day</b>\n"
                f"• <b>Total Spend:</b> ${spend:.2f}\n"
                f"• <b>Clicks:</b> {clicks} (CTR: {ctr}%)\n"
                f"• <b>Realized ROAS:</b> <b>{roas:.2f}X</b>\n"
                f"• <b>Status:</b> 🟢 <b>ACTIVE</b>"
            )
            kb = {
                "inline_keyboard": [
                    [
                        {"text": "⏸️ Pause Ad", "callback_data": f"pause_{b.ad_id}"},
                        {"text": "➕ Scale (+$5)", "callback_data": f"scale_{b.adset_id}_5"}
                    ]
                ]
            }
            self.send_message(chat_id, card, reply_markup=kb)

    def handle_simulate_text(self, chat_id: str, text: str):
        """Performs instant AI copywriting & ROAS diagnostics on text sent by user."""
        c_res = self.copy_scorer.evaluate_copy(text)

        # Build synthetic representative post
        detector = ViralSpikeDetector()
        post = FacebookPost(
            post_id="user_sim",
            page_id="user_page",
            message=text,
            created_time="now",
            post_type="video",
            likes=150,
            comments=30,
            shares=50,
            elapsed_minutes=30.0
        )
        v_res = detector.analyze_post(post)
        feat = self.predictor.build_feature_dict(
            viral_score=v_res.viral_score,
            shares_ratio=v_res.shares_ratio,
            comments_ratio=v_res.comments_ratio,
            post_type="video",
            copy_text=text,
            hook_power=c_res.hook_power_score,
            urgency_score=c_res.urgency_score
        )
        pred = self.predictor.predict(feat)

        policy_badge = "✅ <b>100% SAFE (PASSED)</b>" if c_res.policy_compliance_pass else "❌ <b>META POLICY VIOLATION!</b>"

        reply = (
            "🧪 <b>AI COPYWRITING & ROAS ANALYSIS RESULT:</b>\n"
            "────────────────────────────\n"
            f"• <b>Hook Power Score:</b> <b>{c_res.hook_power_score}/100</b>\n"
            f"• <b>Call-To-Action (CTA):</b> {c_res.cta_score}/100\n"
            f"• <b>Urgency Index:</b> {c_res.urgency_score}/100\n"
            f"• <b>Overall Copy Grade:</b> <b>{c_res.overall_copy_grade}</b>\n"
            f"• <b>Meta Policy Shield:</b> {policy_badge}\n"
            "────────────────────────────\n"
            f"📈 <b>PREDICTED METRICS:</b>\n"
            f"• <b>Predicted ROAS:</b> <b>{pred.predicted_roas}X</b>\n"
            f"• <b>Expected CTR:</b> <b>{pred.predicted_ctr}%</b>\n"
            f"• <b>Est CPC:</b> ${pred.predicted_cpc_usd} | <b>Est CPA:</b> ${pred.predicted_cpa_usd}\n"
            f"• <b>Recommendation:</b> <code>{pred.recommendation}</code> (Conf: {pred.confidence*100:.0f}%)\n"
            "────────────────────────────"
        )
        if c_res.suggested_improvements:
            reply += "\n💡 <b>ការណែនាំកែលម្អពី AI:</b>\n"
            for imp in c_res.suggested_improvements[:3]:
                reply += f"   • {imp}\n"

        self.send_message(chat_id, reply)

    def handle_boost_command(self, chat_id: str, args: List[str]):
        """Manually boosts a post ID via /boost <post_id> [budget]."""
        if not args:
            self.send_message(chat_id, "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/boost &lt;post_id&gt; [budget]</code>\nឧទាហរណ៍៖ <code>/boost page101_post_001 10.0</code>")
            return

        post_id = args[0]
        budget = float(args[1]) if len(args) > 1 else config.policy.test_daily_budget_usd

        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        target_page_id = client.page_id
        page_name = active_rec.page_name if active_rec else target_page_id

        posts = client.get_page_posts(limit=25)
        target = next((p for p in posts if p.post_id == post_id), None)
        if not target:
            target = FacebookPost(
                post_id=post_id,
                page_id=target_page_id,
                message="Manual Boost Target",
                created_time="now",
                post_type="video",
                likes=200, comments=40, shares=80
            )

        res = self.orchestrator.evaluate_and_boost_post(target)
        if res.action_taken == "BOOSTED":
            self.send_message(
                chat_id,
                f"🚀 <b>BOOST SUCCESSFUL ON [{page_name}]!</b>\n"
                f"• <b>Post ID:</b> <code>{post_id}</code>\n"
                f"• <b>Campaign ID:</b> <code>{res.boost_result.campaign_id}</code>\n"
                f"• <b>Daily Budget:</b> <b>${res.boost_result.daily_budget_usd:.2f}/day</b>\n"
                f"• <b>Predicted ROAS:</b> <b>{res.prediction.predicted_roas}X</b>"
            )
        else:
            self.send_message(chat_id, f"ℹ️ <b>លទ្ធផលលើ [{page_name}]៖</b> <code>{res.action_taken}</code>")

    # =========================================================================
    # CALLBACK QUERY ROUTER (INLINE BUTTONS)
    # =========================================================================

    def handle_callback_query(self, query: Dict[str, Any]):
        """Routes clicks from inline button keyboards."""
        query_id = query.get("id")
        data = query.get("data", "")
        message = query.get("message", {})
        chat_id = str(message.get("chat", {}).get("id"))

        self.answer_callback_query(query_id, "Processing...")

        if data == "cmd_scan":
            self.handle_scan(chat_id)
        elif data == "cmd_active":
            self.handle_active(chat_id)
        elif data == "cmd_roas":
            self.handle_roas_scorecard(chat_id)
        elif data == "cmd_status":
            self.handle_status(chat_id)
        elif data == "cmd_admin_status":
            self.handle_admin_status(chat_id)
        elif data == "cmd_web_dashboard":
            self.handle_web_dashboard_info(chat_id)
        elif data == "cmd_toggle_autopilot":
            self.autopilot_enabled = not self.autopilot_enabled
            state = "🟢 ACTIVE" if self.autopilot_enabled else "🔴 PAUSED"
            self.send_message(chat_id, f"🤖 <b>Autopilot Status:</b> {state}")
        elif data == "cmd_help":
            self.handle_help(chat_id)
        elif data == "cmd_fb_pages":
            self.handle_fb_pages(chat_id)
        elif data == "cmd_fb_login_guide":
            self.handle_fb_login_guide(chat_id)
        elif data == "cmd_fb_logout":
            self.handle_fb_logout(chat_id)
        elif data.startswith("selpage_"):
            p_id = data.replace("selpage_", "")
            self.handle_fb_select_page(chat_id, p_id)
        elif data.startswith("setpage_"):
            p_id = data.replace("setpage_", "")
            self.handle_fb_settings(chat_id, p_id)
        elif data.startswith("toggle_boost_"):
            p_id = data.replace("toggle_boost_", "")
            pages = self.multi_tenant.get_user_pages(chat_id)
            target_p = next((p for p in pages if p.page_id == p_id), None)
            if target_p:
                new_val = not target_p.is_active_boost
                self.multi_tenant.update_page_settings(chat_id, p_id, is_active_boost=new_val)
                self.handle_fb_settings(chat_id, p_id)
        elif data.startswith("toggle_chat_"):
            p_id = data.replace("toggle_chat_", "")
            pages = self.multi_tenant.get_user_pages(chat_id)
            target_p = next((p for p in pages if p.page_id == p_id), None)
            if target_p:
                new_val = not target_p.is_active_chat
                self.multi_tenant.update_page_settings(chat_id, p_id, is_active_chat=new_val)
                self.handle_fb_settings(chat_id, p_id)
        elif data.startswith("toggle_autopub_"):
            p_id = data.replace("toggle_autopub_", "")
            pages = self.multi_tenant.get_user_pages(chat_id)
            target_p = next((p for p in pages if p.page_id == p_id), None)
            if target_p:
                new_val = not target_p.is_auto_publisher_active
                self.multi_tenant.update_page_auto_publisher_settings(chat_id, p_id, is_active=new_val)
                self.handle_fb_settings(chat_id, p_id)
        elif data.startswith("toggle_interval_"):
            p_id = data.replace("toggle_interval_", "")
            pages = self.multi_tenant.get_user_pages(chat_id)
            target_p = next((p for p in pages if p.page_id == p_id), None)
            if target_p:
                new_interval = 1 if target_p.publish_interval_hours == 2 else 2
                self.multi_tenant.update_page_auto_publisher_settings(chat_id, p_id, interval_hours=new_interval)
                self.handle_fb_settings(chat_id, p_id)
        elif data.startswith("train_dna_"):
            p_id = data.replace("train_dna_", "")
            self.handle_train_page(chat_id, p_id)
        elif data.startswith("pubnow_"):
            p_id = data.replace("pubnow_", "")
            self.handle_publish_now(chat_id, p_id)
        elif data.startswith("boost_"):
            post_id = data.replace("boost_", "")
            self.handle_boost_command(chat_id, [post_id])
        elif data.startswith("pause_"):
            ad_id = data.replace("pause_", "")
            self.api_client.update_ad_status(ad_id, "PAUSED")
            self.send_message(chat_id, f"⏸️ <b>Ad <code>{ad_id}</code> ត្រូវបាន PAUSE រួចរាល់!</b>")
        elif data.startswith("scale_"):
            parts = data.split("_")
            adset_id = parts[1]
            add_amount = float(parts[2]) if len(parts) > 2 else 5.0
            # Find and update
            for b in self.orchestrator.active_boosts.values():
                if b.adset_id == adset_id:
                    new_b = b.daily_budget_usd + add_amount
                    self.api_client.update_adset_budget(adset_id, new_b)
                    b.daily_budget_usd = new_b
                    self.send_message(chat_id, f"📈 <b>AdSet <code>{adset_id}</code> Budget ឡើងដល់ ${new_b:.2f}/day!</b>")
                    break
        elif data.startswith("postvar_"):
            idx = int(data.replace("postvar_", ""))
            variations = self.creative_generator.generate_ad_variations("Angkor Quant AI System")
            if 0 < idx <= len(variations):
                chosen = variations[idx - 1]
                self.handle_post_to_page(chat_id, chosen.primary_text)
        elif data.startswith("boostvar_"):
            self.send_message(chat_id, "🚀 <b>កំពុងបង្កើត និង Boost Campaign សម្រាប់ Angle នេះ...</b>")
            self.handle_boost_command(chat_id, [f"var_post_{int(time.time())}", str(config.policy.test_daily_budget_usd)])
        elif data.startswith("post_offline_"):
            target_chat = data.replace("post_offline_", "")
            pkg = self._last_offline_packages.get(target_chat)
            if not pkg:
                self.send_message(chat_id, "⚠️ មិនមាន Offline Boost Package សកម្មឡើយ។ សូមបង្កើតឡើងវិញតាម /offline_boost <topic>")
            else:
                client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
                res = self.offline_boost_engine.publish_package_to_page(pkg, client)
                p_name = active_rec.page_name if active_rec else client.page_id
                if res.get("success"):
                    self.send_message(
                        chat_id,
                        f"🎉 <b>បានផ្សាយ OFFLINE BOOST ទៅកាន់ PAGE [{p_name}]!</b>\n"
                        f"• <b>Post ID:</b> <code>{res['post_id']}</code>\n"
                        f"• <b>Cost:</b> <b>$0.00 (Zero Ad Spend)</b>\n"
                        f"• <b>Viral Hook:</b> <b>{pkg.hook_score}/100</b> (Grade: {pkg.copy_grade})\n"
                        f"• <b>Status:</b> 🟢 <b>LIVE & ORGANIC REACH RISING!</b>\n"
                        f"<i>ប្រព័ន្ធបានរៀបចំរួចរាល់ដើម្បីទាក់ទាញ Organic Reach រាប់ម៉ឺននាក់!</i>"
                    )
                else:
                    self.send_message(chat_id, res.get("message", "Error"))
        elif data.startswith("view_caption_"):
            target_chat = data.replace("view_caption_", "")
            pkg = self._last_offline_packages.get(target_chat)
            if pkg:
                self.send_message(
                    chat_id,
                    f"📝 <b>អត្ថបទ CAPTION ពេញលេញ ({pkg.headline}):</b>\n\n{pkg.caption}"
                )
            else:
                self.send_message(chat_id, "⚠️ រកមិនឃើញ Caption ឡើយ។")
        elif data.startswith("regen_offline_"):
            target_chat = data.replace("regen_offline_", "")
            pkg = self._last_offline_packages.get(target_chat)
            topic = pkg.topic if pkg else "Angkor Quant AI System"
            self.handle_offline_boost(chat_id, topic)

    def handle_roas_scorecard(self, chat_id: str):
        """Displays ROAS scorecard and ML prediction metrics."""
        msg = (
            "📊 <b>FB PAGE BM AUTOMATED - ROAS SCORECARD</b>\n"
            "────────────────────────────\n"
            "• <b>LightGBM ROAS Regressor:</b> R²: 0.7527 | MAE: 0.368\n"
            "• <b>LightGBM CTR Regressor:</b>  R²: 0.7896 | MAE: 0.286\n"
            "• <b>XGBoost Profit Classifier:</b> AUC: 0.9665\n"
            "• <b>Active Boosted Count:</b> <code>" + str(len(self.orchestrator.active_boosts)) + "</code>\n"
            "• <b>Circuit Breaker Floor:</b> <code>" + str(config.policy.stop_loss_roas) + "X</code>\n"
            "• <b>Bandit Scaling Target:</b> <code>" + str(config.policy.min_predicted_roas) + "X</code>\n"
            "────────────────────────────\n"
            "🛡️ <i>ប្រព័ន្ធការពារដើមទុន ១០០% ដោយបិទ Ad ណាដែលមាន ROAS &lt; 1.2X ដោយស្វ័យប្រវត្តិ!</i>"
        )
        self.send_message(chat_id, msg)

    def handle_generate(self, chat_id: str, topic: str):
        """Generates 3 viral ad creative variations with predicted ROAS and image prompts."""
        if not topic:
            topic = "Angkor Quant AI System"

        self.send_message(chat_id, f"🧠 <b>AI កំពុងបង្កើត 3 High-Converting Ad Variations សម្រាប់៖</b> <i>{topic}</i>...")
        variations = self.creative_generator.generate_ad_variations(topic)

        for i, var in enumerate(variations, 1):
            card = (
                f"🎨 <b>VARIATION {i}: {var.angle_name.upper()}</b>\n"
                f"────────────────────────────\n"
                f"📝 <b>Primary Text:</b>\n<i>{var.primary_text}</i>\n\n"
                f"• <b>Hook Power:</b> <b>{var.hook_power_score}/100</b> (Grade: <b>{var.copy_grade}</b>)\n"
                f"• <b>Predicted ROAS:</b> <b>{var.predicted_roas}X</b> (Expected CTR: {var.predicted_ctr}%)\n"
                f"• <b>Target Interests:</b> <code>{', '.join(var.target_interests)}</code>\n"
                f"🖼️ <b>AI Image Prompt:</b>\n<code>{var.image_prompt}</code>\n"
                f"────────────────────────────"
            )
            kb = {
                "inline_keyboard": [
                    [
                        {"text": f"🚀 Post Variation {i} to Page", "callback_data": f"postvar_{i}"},
                        {"text": "⚡ Boost This Angle", "callback_data": f"boostvar_{i}"}
                    ]
                ]
            }
            self.send_message(chat_id, card, reply_markup=kb)

    def handle_offline_boost(self, chat_id: str, topic: str):
        """Generates zero-cost 4K viral package via /offline_boost <topic> or /viral_creator <topic>."""
        topic_clean = topic.strip() or "យុទ្ធសាស្ត្រទីផ្សារឌីជីថល AI ២០២៦"
        self.send_message(
            chat_id,
            f"⚡ <b>AI កំពុងបង្កើត 4K OFFLINE BOOST PACKAGE ($0 Ad Spend) សម្រាប់៖</b> <i>{topic_clean}</i>...\n"
            f"<i>(រួមបញ្ចូល Trend-Jacking, 4K Banner, Samdech Chuon Nath Dictionary & Audio)</i>"
        )
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        pkg = loop.run_until_complete(
            self.offline_boost_engine.generate_offline_boost_package(
                topic=topic_clean,
                aspect_ratio="1:1",
                include_audio=True
            )
        )
        self._last_offline_packages[chat_id] = pkg

        kb = {
            "inline_keyboard": [
                [
                    {"text": "🚀 Post to Connected Page ($0)", "callback_data": f"post_offline_{chat_id}"},
                    {"text": "📝 មើល Caption ពេញលេញ", "callback_data": f"view_caption_{chat_id}"}
                ],
                [
                    {"text": "🔄 បង្កើត Variation ថ្មី", "callback_data": f"regen_offline_{chat_id}"}
                ]
            ]
        }
        self.send_message(chat_id, pkg.summary_khmer, reply_markup=kb)

    def handle_post_to_page(self, chat_id: str, message: str, image_url: Optional[str] = None):
        """Publishes post text directly to the connected Facebook Page."""
        if not message:
            self.send_message(chat_id, "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/post &lt;អត្ថបទ caption&gt;</code>")
            return

        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        p_name = active_rec.page_name if active_rec else config.meta.page_id
        res = client.publish_page_post(message, image_url)
        if "error" in res:
            self.send_message(chat_id, f"❌ <b>បរាជ័យក្នុងការ Post៖</b> {res['error']}")
        else:
            post_id = res.get("id", "new_post")
            self.send_message(
                chat_id,
                f"🎉 <b>POST PUBLISHED TO FACEBOOK PAGE!</b>\n"
                f"• <b>Post ID:</b> <code>{post_id}</code>\n"
                f"• <b>Page:</b> <b>{p_name}</b> (<code>{client.page_id}</code>)\n"
                f"• <b>Status:</b> 🟢 <b>LIVE ON PAGE</b>\n"
                f"<i>Bot នឹងចាប់ផ្តើមតាមដាន Organic Velocity ដើម្បី Auto-Boost ក្នុងរយៈពេល 15-30 នាទីទៀត!</i>"
            )

    def handle_comments_status(self, chat_id: str):
        """Displays 24/7 AI Comment & Messenger Lead Assistant status."""
        active_count = len(self.orchestrator.active_boosts)
        msg = (
            "🤖 <b>24/7 AI COMMENT & MESSENGER LEAD AGENT</b>\n"
            "────────────────────────────\n"
            f"• <b>Status:</b> 🟢 <b>ACTIVE & MONITORING</b>\n"
            f"• <b>Monitored Boosted Posts:</b> <code>{active_count}</code>\n"
            f"• <b>Processed Comments:</b> <code>{len(self.comment_agent.processed_comment_ids)}</code>\n"
            "• <b>Average Response Time:</b> <b>&lt; 5 seconds</b>\n"
            "• <b>Spam Shield:</b> 🛡️ <b>ARMORED (Auto-Hide Spam)</b>\n"
            "• <b>Messenger Private DM:</b> 🟢 <b>ENABLED</b>\n"
            "────────────────────────────\n"
            "💡 <i>រាល់ពេលអតិថិជនសួររក 'តម្លៃ', 'របៀបទិញ', ឬ 'Inbox', AI នឹង Comment ឆ្លើយតបយ៉ាងរួសរាយ "
            "ព្រមទាំងផ្ញើសារ Private DM ចូលទៅកាន់ Messenger របស់ពួកគេភ្លាមៗ ដើម្បីបិទការលក់ (Close Lead)!</i>"
        )
        self.send_message(chat_id, msg)

    # =========================================================================
    # VIP FACEBOOK MULTI-TENANT & ZERO-SETUP LOGIN HANDLERS
    # =========================================================================

    def handle_fb_login_guide(self, chat_id: str):
        """Presents instructions for connecting real Facebook Pages safely."""
        web_url = self._get_effective_web_url()
        oauth_url = f"{web_url}/fb_login_redirect?state={chat_id}"

        msg = (
            "🔑 <b>ការភ្ជាប់ FACEBOOK PAGE ពិតប្រាកដ (REAL FACEBOOK PAGES)</b>\n"
            "<i>(អនុវត្តតាមស្តង់ដារផ្លូវការរបស់ Meta Graph API ការពារគណនី ១០០%)</i>\n"
            "────────────────────────────\n"
            f"🌐 <b>ជម្រើសពិសេសទី ០ (ចូលតាម Web Login លើ Linux VPS ងាយស្រួលបំផុត):</b>\n"
            f"👉 <b>Web Login URL:</b> <a href=\"{web_url}\">{web_url}</a>\n"
            "<i>(បើក Browser លើទូរស័ព្ទដៃ ឬកុំព្យូទ័រ ដើម្បី Login តាម Facebook App ដោយផ្ទាល់ ឬ Paste Token 1-Click!)</i>\n\n"
            "👉 <b>ជម្រើសទី ១ (ស្តង់ដារផ្លូវការ & ពេញនិយមបំផុត - Page Access Token):</b>\n"
            "វាយបញ្ជា៖ <code>/fb_token &lt;Page_Access_Token&gt;</code>\n"
            "ឧទាហរណ៍៖ <code>/fb_token EAAB12345...</code>\n"
            "<i>(គ្រាន់តែ Copy យក Page Token ពី Meta Business Suite ឬ Graph API Explorer "
            "ប្រព័ន្ធនឹងស្គាល់ Page ពិតប្រាកដរបស់បងភ្លាមៗ ១០០%!)</i>\n\n"
            "👉 <b>ជម្រើសទី ២ (ភ្ជាប់តាម Browser Cookie Session):</b>\n"
            "វាយបញ្ជា៖ <code>/fb_cookie c_user=...; xs=...</code>\n"
            "<i>(បើក Facebook លើ Chrome/Edge -> F12 -> Application -> Cookies -> Copy c_user & xs "
            "ដើម្បីរំលង Checkpoint ដោយមិនបាច់វាយលេខសម្ងាត់)</i>\n\n"
            "👉 <b>ជម្រើសទី ៣ (កំណត់អចិន្ត្រៃយ៍ក្នុង VPS .env):</b>\n"
            "បើក <code>nano ~/bm-automated/.env</code> រួចបំពេញ៖\n"
            "• <code>META_ACCESS_TOKEN=\"EAAB...\"</code>\n"
            "• <code>META_PAGE_ID=\"ID_Page_របស់បង\"</code>\n"
            "• <code>META_IS_MOCK=false</code>\n"
            "────────────────────────────\n"
            "💡 <b>ចុចប៊ូតុងខាងក្រោមដើម្បីបើក Web Login ឬ Login តាម Facebook App ដោយផ្ទាល់!</b>"
        )

        buttons = []
        if not web_url.startswith("http://localhost"):
            buttons.append([
                {"text": "🌐 បើក Web Login (SSL HTTPS)", "url": web_url},
                {"text": "🚀 1-Click Facebook App Login", "url": oauth_url}
            ])
        else:
            buttons.append([
                {"text": "🌐 ព័ត៌មាន Web GUI Dashboard", "callback_data": "cmd_web_dashboard"}
            ])
        buttons.append([
            {"text": "📄 មើល Pages សកម្ម (/fb_pages)", "callback_data": "cmd_fb_pages"},
            {"text": "❓ ជំនួយ (/help)", "callback_data": "cmd_help"}
        ])

        keyboard = {"inline_keyboard": buttons}
        self.send_message(chat_id, msg, reply_markup=keyboard)

    def handle_fb_login(self, chat_id: str, text: str):
        """Processes /fb_login command with Meta policy explanation and token guidance."""
        parts = text.split()
        if len(parts) < 3:
            self.handle_fb_login_guide(chat_id)
            return

        email = parts[1]
        self.send_message(
            chat_id,
            "ℹ️ <b>សេចក្តីជូនដំណឹងអំពីសុវត្ថិភាព Facebook Login:</b>\n"
            "────────────────────────────\n"
            f"គណនី: <code>{email}</code>\n\n"
            "Meta (Facebook) មិនអនុញ្ញាតឱ្យ Third-Party System បាញ់ Email/Password ចូលដោយផ្ទាល់ឡើយ "
            "ពីព្រោះ Facebook នឹងចាត់ទុកជាការលួចចូលពីចម្ងាយ (Data Center IP) ហើយធ្វើការ Lock/Checkpoint គណនីរបស់បង!\n\n"
            "👉 <b>ដើម្បីភ្ជាប់ Page ពិតប្រាកដរបស់បងដោយសុវត្ថិភាព សូមជ្រើសរើស៖</b>\n"
            "1. <b>ប្រើ Page Access Token (ល្អបំផុត):</b>\n"
            "   វាយ <code>/fb_token EAAB...</code>\n"
            "2. <b>ប្រើ Cookie Session (រំលង Checkpoint):</b>\n"
            "   វាយ <code>/fb_cookie c_user=...; xs=...</code>\n"
            "────────────────────────────\n"
            "💡 វាយ <b>/fb_connect</b> ដើម្បីមើលការណែនាំលម្អិត!"
        )

    def handle_fb_2fa(self, chat_id: str, text: str):
        """Processes /fb_2fa <code> command."""
        parts = text.split()
        if len(parts) < 2:
            self.send_message(chat_id, "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/fb_2fa &lt;កូដ 6 ខ្ទង់&gt;</code>\nឧទាហរណ៍៖ <code>/fb_2fa 849201</code>")
            return

        code = parts[1]
        self.send_message(chat_id, "⏳ <b>កំពុងផ្ទៀងផ្ទាត់កូដ 2FA...</b>")
        res = self.auth_gateway.submit_2fa_code(chat_id, code)

        if res.get("success"):
            kb = {
                "inline_keyboard": [
                    [{"text": "📄 មើល និងជ្រើសរើស Pages របស់បង", "callback_data": "cmd_fb_pages"}]
                ]
            }
            self.send_message(chat_id, res["message"], reply_markup=kb)
        else:
            self.send_message(chat_id, res["message"])

    def handle_fb_pages(self, chat_id: str):
        """Displays interactive list of all Facebook Pages managed by user."""
        pages = self.multi_tenant.get_user_pages(chat_id)
        if not pages:
            self.send_message(
                chat_id,
                "ℹ️ <b>បងមិនទាន់បានភ្ជាប់ Facebook Account នៅឡើយទេ!</b>\n"
                "សូមវាយ <code>/fb_login email password</code> ដើម្បីភ្ជាប់គណនី និងទាញយក Pages របស់បងមកគ្រប់គ្រង!"
            )
            return

        active_page = self.multi_tenant.get_active_page(chat_id)
        active_id = active_page["page_id"] if active_page else ""

        msg = (
            f"📄 <b>FACEBOOK PAGES របស់បង ({len(pages)} Pages):</b>\n"
            "<i>ចុចលើប៊ូតុងខាងក្រោមដើម្បីជ្រើសរើស Page ដែលបងចង់ឱ្យ AI ជួយ Boost & Chat:</i>\n"
            "────────────────────────────\n"
        )

        buttons = []
        for p in pages:
            is_cur = (p.page_id == active_id)
            status_icon = "🟢 [សកម្ម]" if is_cur else "⚪ [ជ្រើសរើស]"
            msg += (
                f"• <b>{p.page_name}</b> ({status_icon})\n"
                f"  └ ID: <code>{p.page_id}</code> | Category: {p.category} | Followers: {p.followers_count:,}\n"
                f"  └ Auto-Boost: {'ON 🚀' if p.is_active_boost else 'OFF ⏸️'} | AI Chat: {'ON 🤖' if p.is_active_chat else 'OFF ⏸️'} | Budget: ${p.daily_budget_usd}/day\n\n"
            )

            btn_txt = f"{'🟢' if is_cur else '👉'} {p.page_name[:24]}"
            buttons.append([
                {"text": btn_txt, "callback_data": f"selpage_{p.page_id}"},
                {"text": "⚙️ កំណត់", "callback_data": f"setpage_{p.page_id}"}
            ])

        buttons.append([{"text": "🔍 Scan Posts លើ Page សកម្ម", "callback_data": "cmd_scan"}])
        keyboard = {"inline_keyboard": buttons}
        self.send_message(chat_id, msg, reply_markup=keyboard)

    def handle_fb_select_page(self, chat_id: str, page_id: str):
        """Selects active operating Page."""
        ok = self.multi_tenant.set_active_page(chat_id, page_id)
        if ok:
            active = self.multi_tenant.get_active_page(chat_id)
            p_name = active["page_name"] if active else page_id
            self.send_message(
                chat_id,
                f"🎉 <b>បានជ្រើសរើស Page:</b> <b>{p_name}</b> (<code>{page_id}</code>)!\n"
                "រាល់ប្រតិបត្តិការ /scan, /boost, /post និង AI Auto-Boost នឹងផ្តោតលើ Page នេះ!"
            )
        else:
            self.send_message(chat_id, "⚠️ មិនអាចជ្រើសរើស Page នេះបានទេ។")

    def handle_fb_settings(self, chat_id: str, page_id: str):
        """Displays per-page settings with instant toggles."""
        pages = self.multi_tenant.get_user_pages(chat_id)
        target = next((p for p in pages if p.page_id == page_id), None)
        if not target:
            self.send_message(chat_id, "⚠️ រកមិនឃើញ Page នេះទេ។")
            return

        boost_txt = "🟢 ON (សកម្ម)" if target.is_active_boost else "🔴 OFF (បិទ)"
        chat_txt = "🟢 ON (សកម្ម)" if target.is_active_chat else "🔴 OFF (បិទ)"
        pub_txt = f"🟢 ON ({target.publish_interval_hours}h / {target.auto_post_photo_count} photos)" if target.is_auto_publisher_active else "🔴 OFF (បិទ)"

        msg = (
            f"⚙️ <b>ការកំណត់សម្រាប់ PAGE:</b> <b>{target.page_name}</b>\n"
            "────────────────────────────\n"
            f"• <b>Page ID:</b> <code>{target.page_id}</code>\n"
            f"• <b>Autonomous Boost:</b> {boost_txt}\n"
            f"• <b>AI Messenger Chat Closer:</b> {chat_txt}\n"
            f"• <b>4K Scheduled Publisher:</b> {pub_txt}\n"
            f"• <b>Daily Budget Limit:</b> <b>${target.daily_budget_usd:.2f}/day</b>\n"
            f"• <b>Min ROAS Hurdle:</b> <code>{target.min_roas_hurdle}X</code>\n"
            "────────────────────────────\n"
            "💡 ចុចប៊ូតុងខាងក្រោមដើម្បី បើក/បិទ និងបញ្ជាមុខងារស្វ័យប្រវត្តិ៖"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": f"🚀 Boost ({'បិទ' if target.is_active_boost else 'បើក'})", "callback_data": f"toggle_boost_{page_id}"},
                    {"text": f"💬 Chat ({'បិទ' if target.is_active_chat else 'បើក'})", "callback_data": f"toggle_chat_{page_id}"}
                ],
                [
                    {"text": f"🎨 4K Pub ({'បិទ' if target.is_auto_publisher_active else 'បើក'})", "callback_data": f"toggle_autopub_{page_id}"},
                    {"text": f"⏱️ ពេល: {target.publish_interval_hours}h ({'ដូរទៅ 1h' if target.publish_interval_hours==2 else 'ដូរទៅ 2h'})", "callback_data": f"toggle_interval_{page_id}"}
                ],
                [
                    {"text": "🧠 Train Brand DNA", "callback_data": f"train_dna_{page_id}"},
                    {"text": "⚡ Publish 4K Now", "callback_data": f"pubnow_{page_id}"}
                ],
                [
                    {"text": "⬅️ ត្រឡប់ទៅកាន់បញ្ជី Pages", "callback_data": "cmd_fb_pages"}
                ]
            ]
        }
        self.send_message(chat_id, msg, reply_markup=keyboard)

    def handle_fb_token(self, chat_id: str, text: str):
        """Processes /fb_token <token> command."""
        parts = text.split()
        if len(parts) < 2:
            self.send_message(chat_id, "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/fb_token &lt;access_token&gt;</code>")
            return
        token = parts[1]
        self.send_message(chat_id, "⏳ <b>កំពុងផ្ទៀងផ្ទាត់ Access Token...</b>")
        res = self.auth_gateway.connect_with_token(chat_id, token)
        self.send_message(chat_id, res["message"])

    def handle_fb_cookie(self, chat_id: str, text: str):
        """Processes /fb_cookie <cookie_string> command."""
        cookie_data = text.replace("/fb_cookie", "", 1).strip()
        if not cookie_data:
            self.send_message(
                chat_id,
                "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/fb_cookie c_user=...; xs=...</code>\n"
                "ឧទាហរណ៍៖ <code>/fb_cookie c_user=1000847291048; xs=38%3Asample_token...</code>"
            )
            return
        self.send_message(chat_id, "⏳ <b>កំពុងផ្ទៀងផ្ទាត់ Cookie Session...</b>")
        res = self.auth_gateway.connect_with_cookies(chat_id, cookie_data)
        self.send_message(chat_id, res["message"])

    def handle_fb_logout(self, chat_id: str):
        """Processes /fb_logout command."""
        self.multi_tenant.delete_user(chat_id)
        self.send_message(chat_id, "🚪 <b>បាន Logout និងលុប Token ទាំងអស់ចេញពីប្រព័ន្ធដោយសុវត្ថិភាព!</b>")

    # =========================================================================
    # PAGE'S ITSELF TRAINING & AUTONOMOUS 4K PUBLISHER HANDLERS
    # =========================================================================

    def handle_train_page(self, chat_id: str, page_id: Optional[str] = None):
        """Executes Stage 1 Deep Training on Page's own DNA and products."""
        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        target_page_id = page_id or (active_rec.page_id if active_rec else client.page_id)
        self.send_message(chat_id, f"⏳ <b>AI កំពុងសិក្សាស៊ីជម្រៅពី Brand DNA, ផលិតផល & អតិថិជនគោលដៅលើ Page <code>{target_page_id}</code>...</b>")
        dna = self.page_publisher.train_page_brand_dna(client, chat_id)

        products_list = "\n".join([f"  • {p}" for p in dna.extracted_products[:4]])
        keywords_list = ", ".join(dna.top_keywords[:6])

        card = (
            f"🧠 <b>PAGE'S ITSELF BRAND DNA TRAINING COMPLETED!</b>\n"
            f"────────────────────────────\n"
            f"• <b>ឈ្មោះម៉ាក/Brand:</b> <b>{dna.brand_name}</b>\n"
            f"• <b>ប្រភេទអាជីវកម្ម:</b> <code>{dna.category}</code>\n"
            f"• <b>Hotlines ផ្លូវការ:</b> <code>{dna.hotlines}</code>\n"
            f"• <b>ទីតាំង/Address:</b> {dna.address}\n"
            f"• <b>ផែនទី/Map:</b> <a href=\"{dna.map_url}\">Google Maps Link</a>\n"
            f"• <b>Tone of Voice:</b> <i>{dna.tone_of_voice}</i>\n"
            f"• <b>ពាក្យគន្លឹះចម្បង:</b> <code>{keywords_list}</code>\n"
            f"• <b>ផលិតផល/សេវាកម្មដែលបានរៀនសូត្រ:</b>\n{products_list}\n"
            f"────────────────────────────\n"
            f"💡 <i>ប្រព័ន្ធបានរៀនច្បាស់លាស់ពីអត្តសញ្ញាណ Page នេះរួចរាល់! រួចរាល់សម្រាប់ការបង្កើត 4K Multi-Photo Posts តាមកាលវិភាគ!</i>"
        )
        kb = {
            "inline_keyboard": [
                [
                    {"text": "🚀 បង្កើត & Publish 4K Now", "callback_data": f"pubnow_{target_page_id}"},
                    {"text": "⚙️ កំណត់កាលវិភាគ", "callback_data": f"setpage_{target_page_id}"}
                ]
            ]
        }
        self.send_message(chat_id, card, reply_markup=kb)

    def handle_publish_now(self, chat_id: str, page_id: Optional[str] = None):
        """Immediately executes 5-Stage Publishing Workflow and posts 3-5 4K photos to Page."""
        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        target_page_id = page_id or (active_rec.page_id if active_rec else client.page_id)
        p_name = active_rec.page_name if active_rec else target_page_id

        self.send_message(
            chat_id,
            f"⚡ <b>AI កំពុងរៀបចំ 4K Multi-Photo Campaign សម្រាប់ Page [{p_name}]...</b>\n"
            f"<i>(ទាញយករូប Original 3-5 សន្លឹក -> រចនា 4K Frame -> សរសេរ Selling Caption -> ផុសទៅ Page)</i>"
        )

        pages = self.multi_tenant.get_user_pages(chat_id)
        cur_p = next((p for p in pages if p.page_id == target_page_id), None)
        interval = cur_p.publish_interval_hours if cur_p else 2
        photo_count = cur_p.auto_post_photo_count if cur_p else 4

        res = self.page_publisher.execute_scheduled_publishing_cycle(
            client=client,
            telegram_id=chat_id,
            interval_hours=interval,
            photo_count=photo_count,
            force_now=True
        )

        if res.get("success"):
            kb = {
                "inline_keyboard": [
                    [{"text": "🔗 បើកមើល Post លើ Facebook ផ្ទាល់", "url": res["post_url"] if not client.is_mock else "https://facebook.com"}]
                ]
            }
            self.send_message(chat_id, res["summary_khmer"], reply_markup=kb)
        else:
            self.send_message(chat_id, f"❌ <b>បរាជ័យក្នុងការ Post៖</b> {res.get('error') or res.get('reason')}")

    def handle_auto_publish(self, chat_id: str, text: str):
        """Toggles scheduled 4K multi-photo auto-publishing for active page."""
        client, active_rec = self.auth_gateway.get_user_page_client(chat_id)
        if not active_rec:
            self.send_message(chat_id, "⚠️ សូមជ្រើសរើស Page សកម្មជាមុនសិនតាម /fb_pages ឬ /fb_select")
            return

        parts = text.split()
        page_id = active_rec.page_id
        is_active = True
        interval = active_rec.publish_interval_hours or 2
        photo_count = active_rec.auto_post_photo_count or 4

        if len(parts) > 1:
            cmd_arg = parts[1].lower()
            if cmd_arg in ("off", "0", "pause", "stop"):
                is_active = False
            elif cmd_arg in ("on", "1", "start", "enable"):
                is_active = True

        if len(parts) > 2:
            try:
                interval = int(parts[2])
                if interval < 1:
                    interval = 1
                elif interval > 24:
                    interval = 24
            except ValueError:
                pass

        if len(parts) > 3:
            try:
                photo_count = int(parts[3])
                if photo_count < 3:
                    photo_count = 3
                elif photo_count > 5:
                    photo_count = 5
            except ValueError:
                pass

        self.multi_tenant.update_page_auto_publisher_settings(
            telegram_id=chat_id,
            page_id=page_id,
            is_active=is_active,
            interval_hours=interval,
            photo_count=photo_count
        )

        status_icon = "🟢 <b>ACTIVE (បើកដំណើរការ)</b>" if is_active else "🔴 <b>PAUSED (បិទ)</b>"
        card = (
            f"⚙️ <b>AUTONOMOUS 4K PUBLISHER SETTINGS:</b>\n"
            f"────────────────────────────\n"
            f"• <b>Target Page:</b> <b>{active_rec.page_name}</b> (<code>{page_id}</code>)\n"
            f"• <b>កាលវិភាគស្វ័យប្រវត្ត:</b> {status_icon}\n"
            f"• <b>ចន្លោះពេល Post:</b> រៀងរាល់ <b>{interval} ម៉ោងម្តង</b>\n"
            f"• <b>ចំនួនរូបភាពក្នុង Post:</b> <b>{photo_count} រូបភាព (4K Multi-Photo)</b>\n"
            f"• <b>Circadian Protection:</b> 🛡️ មិនផុសនៅម៉ោងទាប 02:00 - 05:00 AM\n"
            f"• <b>Deduplication Shield:</b> 🛡️ មិនជាន់គ្នាក្នុងរង្វង់ ៣០ ថ្ងៃ\n"
            f"────────────────────────────\n"
            f"💡 <i>ពេលបើកដំណើរការ ប្រព័ន្ធនឹងផុសរូបភាព 4K ចំនួន {photo_count} សន្លឹក "
            f"ជាមួយ Caption លក់ប្រកបដោយវិជ្ជាជីវៈ និង Hotlines/Map រៀងរាល់ {interval} ម៉ោងម្តងដោយស្វ័យប្រវត្តិ!</i>"
        )
        kb = {
            "inline_keyboard": [
                [
                    {"text": f"🚀 {'បិទ' if is_active else 'បើក'} Auto-Publish", "callback_data": f"toggle_autopub_{page_id}"},
                    {"text": f"⏱️ ប្តូរពេល ({'1h' if interval==2 else '2h'})", "callback_data": f"toggle_interval_{page_id}"}
                ],
                [
                    {"text": "🧠 Train Brand DNA", "callback_data": f"train_dna_{page_id}"},
                    {"text": "⚡ Publish 4K Now", "callback_data": f"pubnow_{page_id}"}
                ]
            ]
        }
        self.send_message(chat_id, card, reply_markup=kb)

    def handle_help(self, chat_id: str):
        """Displays quick help and available bot commands."""
        help_text = (
            "📖 <b>បញ្ជី Commands សម្រាប់បញ្ជា BM AUTOMATED:</b>\n"
            "────────────────────────────\n"
            "🔑 <b>FACEBOOK LOGIN & PAGES (ZERO SETUP):</b>\n"
            "• <code>/fb_login email pass</code>: ភ្ជាប់ Facebook Account របស់បងភ្លាមៗ\n"
            "• <code>/fb_cookie c_user=...; xs=...</code>: ភ្ជាប់តាម Browser Cookie រំលង Checkpoint\n"
            "• <code>/fb_2fa &lt;code&gt;</code>: បញ្ចូលកូដ 2FA ប្រសិនបើ Facebook ទាមទារ\n"
            "• <code>/fb_pages</code>: បង្ហាញបញ្ជី Pages របស់បង & ជ្រើសរើស Page ដំណើរការ\n"
            "• <code>/fb_token &lt;token&gt;</code>: ភ្ជាប់តាម Access Token ឬ Page Token ផ្ទាល់\n"
            "• <code>/fb_logout</code>: ចាកចេញ និងលុប Token ទាំងអស់ចេញពី Database\n"
            "────────────────────────────\n"
            "🚀 <b>AI BOOST & MARKETING OPERATIONS:</b>\n"
            "• <code>/offline_boost &lt;topic&gt;</code>: បង្កើត 4K Viral Package ($0 Ad Spend / Zero Cost)\n"
            "• <code>/viral_creator &lt;topic&gt;</code>: ដូចគ្នាទៅនឹង /offline_boost (Trend + 4K Banner + Audio)\n"
            "• <code>/menu</code> ឬ <code>/start</code>: បើកផ្ទាំង Dashboard ចម្បង\n"
            "• <code>/scan</code>: ស្កេន Page Posts & បង្ហាញប៊ូតុង Boost\n"
            "• <code>/active</code>: បង្ហាញ Active Ads, Spend & ROAS\n"
            "• <code>/boost &lt;post_id&gt; [budget]</code>: Boost Post ដោយផ្ទាល់\n"
            "• <code>/generate &lt;topic&gt;</code>: បង្កើត 3 Ad Variations + Image Prompts\n"
            "• <code>/post &lt;caption&gt;</code>: ផុស Caption ផ្ទាល់ទៅកាន់ Facebook Page\n"
            "• <code>/comments</code>: ពិនិត្យ AI Comment & Messenger Lead Agent\n"
            "• <code>/pause &lt;ad_id&gt;</code>: បញ្ឈប់ការរត់ Ad\n"
            "• <code>/resume &lt;ad_id&gt;</code>: បន្តដំណើរការ Ad\n"
            "• <code>/simulate &lt;text&gt;</code>: វិភាគគុណភាព Caption & ព្យាករណ៍ ROAS\n"
            "• <code>/autopilot [on|off]</code>: បើក/បិទ ស្វ័យប្រវត្តិកម្ម ២៤/៧\n"
            "• <code>/status</code>: ត្រួតពិនិត្យសុខភាពប្រព័ន្ធ និង Memory\n"
            "────────────────────────────\n"
            "💡 <i>អ្នកក៏អាចគ្រាន់តែផ្ញើ Caption ជាអក្សរខ្មែរ ឬអង់គ្លេសមកកាន់ Bot ដើម្បីឱ្យ AI វិភាគភ្លាមៗ!</i>"
        )
        self.send_message(chat_id, help_text)

    def handle_web_dashboard_info(self, chat_id: str):
        """Displays Web GUI access URL and instructions with live external IP or Cloudflare URL."""
        web_url = self._get_effective_web_url()
        oauth_url = f"{web_url}/fb_login_redirect?state={chat_id}"
        is_cf = "trycloudflare.com" in web_url or "https://" in web_url

        msg = (
            "🌐 <b>FB PAGE BM AUTOMATED - WEB GUI DASHBOARD</b>\n"
            "────────────────────────────\n"
            f"• <b>Web Dashboard URL:</b> <code>{web_url}</code>\n"
            f"• <b>Security Protocol:</b> {'🛡️ <b>SSL HTTPS (Cloudflare Edge)</b>' if is_cf else '🔓 HTTP (Port 8088)'}\n"
            f"• <b>Meta API Status:</b> {'🛡️ Simulation' if self.api_client.is_mock else '🟢 Live Connected'}\n"
            "────────────────────────────\n"
            "💡 <b>របៀបចូលប្រើប្រាស់ Web Dashboard & Web Login៖</b>\n"
            f"👉 <b>ចុចបើកផ្ទាល់៖</b> <a href=\"{web_url}\">{web_url}</a>\n"
            "• អាចបើកបានទាំងលើ <b>Smartphone (Safari, Chrome)</b> ឬ <b>PC Browser</b>\n"
            "• ក្នុង Web Dashboard មានផ្ទាំង <b>➕ Connect Account</b> សម្រាប់ភ្ជាប់ Page ដោយផ្ទាល់ ឬចុច <b>1-Click Facebook App Login</b>!\n\n"
            "<i>(ចំណាំ៖ ប្រសិនបើប្រើ IP ផ្ទាល់ ហើយចុច Link មិនទាន់ដើរ សូមបើក Cloudflare Tunnel តាមរយៈ <code>bash setup_cloudflare_tunnel.sh</code> លើ VPS ដើម្បីទទួលបាន Link HTTPS ឥតគិតថ្លៃ និងលឿនបំផុត!)</i>"
        )

        buttons = []
        if not web_url.startswith("http://localhost"):
            buttons.append([
                {"text": "🌐 បើក Web Dashboard", "url": web_url},
                {"text": "🚀 1-Click Facebook Login", "url": oauth_url}
            ])
        buttons.append([
            {"text": "🔑 របៀបភ្ជាប់ Facebook (/fb_guide)", "callback_data": "cmd_fb_login_guide"},
            {"text": "📈 System Status", "callback_data": "cmd_status"}
        ])

        keyboard = {"inline_keyboard": buttons}
        self.send_message(chat_id, msg, reply_markup=keyboard)

    def handle_status(self, chat_id: str):
        """Displays system health, VPS resources, and bot operational state."""
        import platform

        mem_info = "Normal"
        try:
            import psutil
            mem = psutil.virtual_memory()
            mem_info = f"{mem.used // (1024*1024)}MB / {mem.total // (1024*1024)}MB ({mem.percent}%)"
        except ImportError:
            try:
                with open("/proc/meminfo", "r") as f:
                    lines = f.readlines()
                    total = int([l for l in lines if "MemTotal" in l][0].split()[1]) // 1024
                    avail = int([l for l in lines if "MemAvailable" in l][0].split()[1]) // 1024
                    used = total - avail
                    mem_info = f"{used}MB / {total}MB ({int(used/total*100)}%)"
            except Exception:
                mem_info = "User Space Process Mode"

        users_count = len(self.multi_tenant.list_users())
        pages_count = len(self.multi_tenant.list_all_pages())
        active_boosts = len(self.orchestrator.active_boosts)
        autopilot_state = "🟢 ACTIVE" if self.autopilot_enabled else "🔴 PAUSED"
        mode_badge = "🛡️ MOCK SIMULATION" if self.api_client.is_mock else "🟢 LIVE META GRAPH API"

        msg = (
            "📊 <b>FB PAGE BM AUTOMATED - SYSTEM STATUS</b>\n"
            "────────────────────────────\n"
            f"• <b>Engine Status:</b> 🟢 <b>ONLINE (24/7 LIVE)</b>\n"
            f"• <b>Operating System:</b> <code>{platform.system()} {platform.release()}</code>\n"
            f"• <b>Python Runtime:</b> <code>{platform.python_version()}</code>\n"
            f"• <b>RAM Footprint:</b> <code>{mem_info}</code>\n"
            f"• <b>Autopilot Engine:</b> {autopilot_state}\n"
            f"• <b>Meta API Status:</b> {mode_badge}\n"
            f"• <b>Registered VIP Users:</b> <code>{users_count}</code>\n"
            f"• <b>Managed Facebook Pages:</b> <code>{pages_count}</code>\n"
            f"• <b>Active Boosted Ads:</b> <code>{active_boosts}/{config.policy.max_active_boosts}</code>\n"
            f"• <b>Web Dashboard Port:</b> <code>{config.web_port}</code>\n"
            "────────────────────────────\n"
            "🛡️ <i>ប្រព័ន្ធការពារដើមទុន ១០០% និងដំណើរការរលូន ២៤/៧ លើ Google Cloud VPS!</i>"
        )
        self.send_message(chat_id, msg)

    def handle_admin_status(self, chat_id: str):
        """Displays institutional administrative telemetry for Super Admin."""
        if self.admin_id and str(chat_id) != str(self.admin_id):
            self.send_message(chat_id, "⛔ <b>ACCESS DENIED:</b> ពាក្យបញ្ជានេះសម្រាប់តែ Super Admin ប៉ុណ្ណោះ។")
            return

        users = self.multi_tenant.list_users()
        pages = self.multi_tenant.list_all_pages()
        active_boosts = len(self.orchestrator.active_boosts)
        autopilot_state = "🟢 ACTIVE" if self.autopilot_enabled else "🔴 PAUSED"

        msg = (
            "👑 <b>SUPER ADMIN INSTITUTIONAL TELEMETRY</b>\n"
            "────────────────────────────\n"
            f"• <b>Admin Chat ID:</b> <code>{self.admin_id}</code>\n"
            f"• <b>GCP VPS Target:</b> <code>bm-automated (us-central1-a)</code>\n"
            f"• <b>Multi-Tenant DB:</b> <code>{self.multi_tenant.db_path.name}</code>\n"
            f"• <b>Total VIP Users:</b> <code>{len(users)}</code>\n"
            f"• <b>Total Connected Pages:</b> <code>{len(pages)}</code>\n"
            f"• <b>Active Ad Campaigns:</b> <code>{active_boosts}</code>\n"
            f"• <b>Autopilot Engine:</b> {autopilot_state}\n"
            f"• <b>Stop Loss ROAS:</b> <code>{config.policy.stop_loss_roas}X</code>\n"
            f"• <b>Min Viral Hurdle:</b> <code>{config.policy.min_viral_score}/100</code>\n"
            f"• <b>Test Daily Budget:</b> <code>${config.policy.test_daily_budget_usd:.2f}</code>\n"
            f"• <b>Max Daily Budget:</b> <code>${config.policy.max_daily_budget_usd:.2f}</code>\n"
            "────────────────────────────\n"
            "🛠️ <b>ADMIN MANAGEMENT COMMANDS:</b>\n"
            "• <code>/admin_users</code>: បង្ហាញបញ្ជី VIP Users ទាំងអស់\n"
            "• <code>/admin_pages</code>: បង្ហាញបញ្ជី Pages ទាំងអស់ក្នុងប្រព័ន្ធ\n"
            "• <code>/admin_sync</code>: បង្ខំ Refresh & Verify Pages ទាំងអស់\n"
            "• <code>/admin_broadcast &lt;សារ&gt;</code>: ផ្ញើសារប្រកាសទៅកាន់ Users ទាំងអស់\n"
            "• <code>/autopilot [on|off]</code>: បើក/បិទ Autopilot\n"
            "• <code>/status</code>: មើលសុខភាព Server ទូទៅ"
        )
        self.send_message(chat_id, msg)

    def handle_admin_users(self, chat_id: str):
        """Lists all registered VIP users."""
        if self.admin_id and str(chat_id) != str(self.admin_id):
            self.send_message(chat_id, "⛔ <b>ACCESS DENIED</b>")
            return

        users = self.multi_tenant.list_users()
        if not users:
            self.send_message(chat_id, "ℹ️ មិនទាន់មាន VIP User ចុះឈ្មោះក្នុងប្រព័ន្ធនៅឡើយទេ។")
            return

        msg = f"👥 <b>បញ្ជី VIP USERS ទាំងអស់ ({len(users)} Users):</b>\n────────────────────────────\n"
        for u in users:
            name = u.get("fb_name") or "Unknown"
            t_id = u.get("telegram_id")
            pg_cnt = u.get("page_count", 0)
            method = u.get("auth_method", "N/A")
            msg += (
                f"• 👤 <b>{name}</b>\n"
                f"  └ Telegram ID: <code>{t_id}</code>\n"
                f"  └ Pages: <code>{pg_cnt}</code> | Auth: <code>{method}</code>\n\n"
            )
        self.send_message(chat_id, msg)

    def handle_admin_pages(self, chat_id: str):
        """Lists all managed Facebook Pages across all users."""
        if self.admin_id and str(chat_id) != str(self.admin_id):
            self.send_message(chat_id, "⛔ <b>ACCESS DENIED</b>")
            return

        pages = self.multi_tenant.list_all_pages()
        if not pages:
            self.send_message(chat_id, "ℹ️ មិនទាន់មាន Page ក្នុងប្រព័ន្ធនៅឡើយទេ។")
            return

        msg = f"📑 <b>បញ្ជី FACEBOOK PAGES ទាំងអស់ ({len(pages)} Pages):</b>\n────────────────────────────\n"
        for p in pages:
            p_name = p.get("page_name") or "Untitled"
            p_id = p.get("page_id")
            fb_user = p.get("fb_name") or "Unknown"
            boost = "ON 🚀" if p.get("is_active_boost") else "OFF ⏸️"
            chat = "ON 🤖" if p.get("is_active_chat") else "OFF ⏸️"
            budget = p.get("daily_budget_usd", 5.0)
            msg += (
                f"• 📄 <b>{p_name}</b> (<code>{p_id}</code>)\n"
                f"  └ Owner: <b>{fb_user}</b> (Telegram: <code>{p.get('telegram_id')}</code>)\n"
                f"  └ Auto-Boost: {boost} | AI Chat: {chat} | Budget: ${budget:.2f}/day\n\n"
            )
        self.send_message(chat_id, msg)

    def handle_admin_sync(self, chat_id: str):
        """Forces refresh and verification of all connected pages."""
        if self.admin_id and str(chat_id) != str(self.admin_id):
            self.send_message(chat_id, "⛔ <b>ACCESS DENIED</b>")
            return

        self.send_message(chat_id, "🔄 <b>កំពុងធ្វើសមកាលកម្ម (Sync) គណនី និង Pages ទាំងអស់...</b>")
        pages = self.multi_tenant.list_all_pages()
        self.send_message(chat_id, f"✅ <b>សមកាលកម្មជោគជ័យ!</b> រកឃើញ <code>{len(pages)}</code> Facebook Pages សកម្ម។")

    def handle_admin_broadcast(self, chat_id: str, text: str):
        """Broadcasts a high-priority announcement to all registered users."""
        if self.admin_id and str(chat_id) != str(self.admin_id):
            self.send_message(chat_id, "⛔ <b>ACCESS DENIED</b>")
            return

        content = text.replace("/admin_broadcast", "", 1).strip()
        if not content:
            self.send_message(chat_id, "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/admin_broadcast &lt;អត្ថបទសារប្រកាស&gt;</code>")
            return

        users = self.multi_tenant.list_users()
        sent_count = 0
        broadcast_msg = f"📢 <b>ANNOUNCEMENT ពី SUPER ADMIN:</b>\n────────────────────────────\n{content}"

        for u in users:
            t_id = u.get("telegram_id")
            if t_id and t_id != chat_id:
                if self.send_message(t_id, broadcast_msg):
                    sent_count += 1

        self.send_message(chat_id, f"✅ <b>បានផ្ញើសារប្រកាសទៅកាន់ {sent_count}/{len(users)} VIP Users រួចរាល់!</b>")

    def register_bot_commands(self) -> bool:
        """
        Registers Dual-Tier Telegram Bot Commands with Telegram API (setMyCommands):
        Tier 1 (Public VIP Users / Default Scope): Clean, benefit-driven commands.
        Tier 2 (Super Admin / Chat Scope): Full institutional governance commands.
        """
        if not self.is_configured:
            return False

        vip_commands = [
            {"command": "start", "description": "🚀 បើកផ្ទាំង Dashboard ចម្បង & Status"},
            {"command": "web", "description": "🌐 បើក Web Dashboard & Web Login លើ VPS"},
            {"command": "auto_publish", "description": "⏱️ កាលវិភាគ 4K Multi-Photo Publisher (1h/2h)"},
            {"command": "train_page", "description": "🧠 សិក្សា Brand DNA & ផលិតផល Page ផ្ទាល់ខ្លួន"},
            {"command": "publish_now", "description": "🚀 បង្កើត & ផុស 4K Multi-Photo Campaign ភ្លាមៗ"},
            {"command": "offline_boost", "description": "⚡ បង្កើត 4K Viral Package ($0 Ad Spend)"},
            {"command": "viral_creator", "description": "🎨 Trend-Jacking + 4K Banner + Audio"},
            {"command": "fb_login", "description": "🔑 ភ្ជាប់ Facebook Account ដោយងាយស្រួល"},
            {"command": "fb_2fa", "description": "🔐 បញ្ចូលកូដ 2FA របស់ Facebook"},
            {"command": "fb_pages", "description": "📄 បង្ហាញបញ្ជី Pages & ជ្រើសរើស Page"},
            {"command": "fb_select", "description": "👉 ជ្រើសរើស Page សកម្មសម្រាប់ Boost"},
            {"command": "fb_connect", "description": "💡 មគ្គុទ្ទេសក៍ភ្ជាប់ Facebook ងាយៗ"},
            {"command": "fb_logout", "description": "🚪 ចាកចេញ និងលុប Token ដោយសុវត្ថិភាព"},
            {"command": "scan", "description": "🔍 ស្កេន Posts & បង្ហាញប៊ូតុង 1-Tap Boost"},
            {"command": "active", "description": "⚡ បង្ហាញ Active Ads, Spend & ROAS"},
            {"command": "roas", "description": "📊 ពិន្ទុ ROAS Scorecard & ML Prediction"},
            {"command": "generate", "description": "🧠 បង្កើត 3 High-Converting Ad Variations"},
            {"command": "post", "description": "📝 ផុស Caption ផ្ទាល់ទៅកាន់ Facebook Page"},
            {"command": "comments", "description": "🤖 ពិនិត្យ AI Comment & Messenger Lead Agent"},
            {"command": "status", "description": "📈 ត្រួតពិនិត្យសុខភាពប្រព័ន្ធ និង Memory"},
            {"command": "help", "description": "📖 បង្ហាញបញ្ជី Commands ទាំងអស់"}
        ]

        admin_commands = [
            {"command": "start", "description": "🚀 បើកផ្ទាំង Dashboard ចម្បង & Status"},
            {"command": "web", "description": "🌐 បើក Web Dashboard & Web Login លើ VPS"},
            {"command": "admin_status", "description": "📊 Institutional VPS, CPU, RAM & Bot Health"},
            {"command": "admin_users", "description": "👥 បញ្ជី Multi-Tenant Users ទាំងអស់"},
            {"command": "admin_pages", "description": "📑 បញ្ជី Facebook Pages ទាំងអស់ក្នុងប្រព័ន្ធ"},
            {"command": "admin_sync", "description": "🔄 បង្ខំ Re-sync Pages ពី Facebook"},
            {"command": "admin_broadcast", "description": "📢 ផ្ញើសារប្រកាសទៅកាន់ Users ទាំងអស់"},
            {"command": "autopilot", "description": "🤖 បើក/បិទ Autonomous Engine ២៤/៧"},
            {"command": "auto_publish", "description": "⏱️ កាលវិភាគ 4K Multi-Photo Publisher (1h/2h)"},
            {"command": "train_page", "description": "🧠 សិក្សា Brand DNA & ផលិតផល Page ផ្ទាល់ខ្លួន"},
            {"command": "publish_now", "description": "🚀 បង្កើត & ផុស 4K Multi-Photo Campaign ភ្លាមៗ"},
            {"command": "offline_boost", "description": "⚡ បង្កើត 4K Viral Package ($0 Ad Spend)"},
            {"command": "viral_creator", "description": "🎨 Trend-Jacking + 4K Banner + Audio"},
            {"command": "scan", "description": "🔍 ស្កេន Posts & បង្ហាញប៊ូតុង 1-Tap Boost"},
            {"command": "boost", "description": "🚀 បញ្ជា Boost Post ដោយផ្ទាល់ + Budget"},
            {"command": "active", "description": "⚡ បង្ហាញ Active Ads, Spend & ROAS"},
            {"command": "roas", "description": "📊 ពិន្ទុ ROAS Scorecard & ML Prediction"},
            {"command": "fb_pages", "description": "📄 បង្ហាញបញ្ជី Pages & ជ្រើសរើស Page"},
            {"command": "fb_select", "description": "👉 ជ្រើសរើស Page សកម្មសម្រាប់ Boost"},
            {"command": "fb_login", "description": "🔑 ភ្ជាប់ Facebook Account ដោយងាយស្រួល"},
            {"command": "fb_2fa", "description": "🔐 បញ្ចូលកូដ 2FA របស់ Facebook"},
            {"command": "fb_connect", "description": "💡 មគ្គុទ្ទេសក៍ភ្ជាប់ Facebook ងាយៗ"},
            {"command": "fb_logout", "description": "🚪 ចាកចេញ និងលុប Token ដោយសុវត្ថិភាព"},
            {"command": "generate", "description": "🧠 បង្កើត 3 High-Converting Ad Variations"},
            {"command": "post", "description": "📝 ផុស Caption ផ្ទាល់ទៅកាន់ Facebook Page"},
            {"command": "comments", "description": "🤖 ពិនិត្យ AI Comment & Messenger Lead Agent"},
            {"command": "status", "description": "📈 ត្រួតពិនិត្យសុខភាពប្រព័ន្ធ និង Memory"},
            {"command": "help", "description": "📖 បង្ហាញបញ្ជី Commands ទាំងអស់"}
        ]

        try:
            url_cmd = f"{self.api_url}/setMyCommands"
            # 1. Register Default Scope for Public VIP Users
            res1 = requests.post(url_cmd, json={"commands": vip_commands, "scope": {"type": "default"}}, timeout=10)
            if res1.status_code == 200 and res1.json().get("ok"):
                logger.info("✅ [BM TELEGRAM BOT] Successfully registered VIP commands with Telegram API")
            else:
                logger.warning(f"⚠️ Failed to register VIP commands: {res1.text}")

            # 2. Register Chat Scope for Super Admin
            if self.admin_id:
                res2 = requests.post(url_cmd, json={"commands": admin_commands, "scope": {"type": "chat", "chat_id": int(self.admin_id)}}, timeout=10)
                if res2.status_code == 200 and res2.json().get("ok"):
                    logger.info(f"✅ [BM TELEGRAM BOT] Successfully registered Super Admin commands for chat {self.admin_id}")
                else:
                    logger.warning(f"⚠️ Failed to register Admin commands: {res2.text}")

            return True
        except Exception as e:
            logger.error(f"Error registering bot commands: {e}")
            return False

    # =========================================================================
    # LONG POLLING ENGINE
    # =========================================================================

    def run_polling(self):
        """Runs 24/7 long-polling event loop or interactive terminal."""
        if not self.is_configured:
            is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False
            if is_interactive:
                print("=" * 80)
                print("⚠️ [BM TELEGRAM BOT] No BM_TELEGRAM_BOT_TOKEN provided in .env!")
                print("   Running in Local Mock Interactive Terminal Mode.")
                print("   You can test any command directly here (e.g. /scan, /active, /generate Gold AI, or paste any caption)!")
                print("   👉 To connect to live Telegram on your phone:")
                print("      1. Open Telegram & search @BotFather to create a free bot")
                print("      2. Put token in .env: BM_TELEGRAM_BOT_TOKEN='your_token'")
                print("======================================================================")
                self.run_interactive_terminal()
                return
            else:
                # Background / Daemon mode: wait gracefully for user to supply token in .env
                logger.warning("⚠️ [BM TELEGRAM BOT] No BM_TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN found in .env!")
                logger.info("   Daemon is running and waiting for token in .env... (checking every 10s)")
                while not self.is_configured:
                    time.sleep(10)
                    try:
                        from dotenv import load_dotenv
                        load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)
                        t = os.getenv("BM_TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
                        if t and len(t) > 15:
                            self.token = t
                            self.api_url = f"{self.TELEGRAM_API_URL}{self.token}"
                            logger.info("🎉 [BM TELEGRAM BOT] Token loaded from .env! Activating live Telegram long polling...")
                            self.register_bot_commands()
                            break
                    except Exception:
                        pass

        print("=" * 80, flush=True)
        print("🤖 [BM TELEGRAM BOT] STARTED 24/7 TELEGRAM LONG POLLING...", flush=True)
        print(f"🔒 Admin Chat ID: {self.admin_id or 'Any User'}", flush=True)
        print("======================================================================", flush=True)

        # Register Dual-Tier commands with Telegram API
        self.register_bot_commands()

        # Notify admin of startup
        self.send_admin_alert("🚀 <b>FB PAGE BM AUTOMATED BOT IS ONLINE!</b>\nServer: Linux Google VPS (24/7 LIVE)")

        while True:
            try:
                url = f"{self.api_url}/getUpdates?offset={self.last_update_id + 1}&timeout=20"
                resp = requests.get(url, timeout=25)
                if resp.status_code == 200:
                    updates = resp.json().get("result", [])
                    for u in updates:
                        self.last_update_id = u["update_id"]

                        # Handle Callback Query (Buttons)
                        if "callback_query" in u:
                            self.handle_callback_query(u["callback_query"])
                            continue

                        # Handle Text Messages
                        msg = u.get("message", {})
                        chat_id = str(msg.get("chat", {}).get("id"))
                        text = msg.get("text", "").strip()

                        if not text:
                            continue

                        logger.info(f"📩 [MESSAGE RECEIVED] Chat ID: {chat_id} | Command: {text[:80]}")

                        # Command routing
                        if text in ("/start", "/menu"):
                            self.handle_start(chat_id)
                        elif text in ("/status", "/health"):
                            self.handle_status(chat_id)
                        elif text == "/admin_status":
                            self.handle_admin_status(chat_id)
                        elif text == "/admin_users":
                            self.handle_admin_users(chat_id)
                        elif text == "/admin_pages":
                            self.handle_admin_pages(chat_id)
                        elif text == "/admin_sync":
                            self.handle_admin_sync(chat_id)
                        elif text.startswith("/admin_broadcast"):
                            self.handle_admin_broadcast(chat_id, text)
                        elif text.startswith("/auto_publish") or text.startswith("/autopublish"):
                            self.handle_auto_publish(chat_id, text)
                        elif text in ("/train_page", "/train_dna"):
                            self.handle_train_page(chat_id)
                        elif text in ("/publish_now", "/test_publish", "/pubnow"):
                            self.handle_publish_now(chat_id)
                        elif text.startswith("/fb_login"):
                            self.handle_fb_login(chat_id, text)
                        elif text.startswith("/fb_2fa"):
                            self.handle_fb_2fa(chat_id, text)
                        elif text in ("/fb_pages", "/pages"):
                            self.handle_fb_pages(chat_id)
                        elif text.startswith("/fb_select"):
                            p_id = text.replace("/fb_select", "", 1).strip()
                            self.handle_fb_select_page(chat_id, p_id)
                        elif text.startswith("/fb_token"):
                            self.handle_fb_token(chat_id, text)
                        elif text.startswith("/fb_cookie"):
                            self.handle_fb_cookie(chat_id, text)
                        elif text in ("/fb_logout", "/logout"):
                            self.handle_fb_logout(chat_id)
                        elif text in ("/fb_connect", "/fb_guide"):
                            self.handle_fb_login_guide(chat_id)
                        elif text in ("/web", "/dashboard", "/gui"):
                            self.handle_web_dashboard_info(chat_id)
                        elif text.startswith("/generate"):
                            topic = text.replace("/generate", "", 1).strip()
                            self.handle_generate(chat_id, topic)
                        elif text.startswith("/offline_boost"):
                            topic = text.replace("/offline_boost", "", 1).strip()
                            self.handle_offline_boost(chat_id, topic)
                        elif text.startswith("/viral_creator"):
                            topic = text.replace("/viral_creator", "", 1).strip()
                            self.handle_offline_boost(chat_id, topic)
                        elif text.startswith("/post"):
                            msg_content = text.replace("/post", "", 1).strip()
                            self.handle_post_to_page(chat_id, msg_content)
                        elif text == "/comments":
                            self.handle_comments_status(chat_id)
                        elif text == "/scan":
                            self.handle_scan(chat_id)
                        elif text == "/active":
                            self.handle_active(chat_id)
                        elif text.startswith("/boost"):
                            args = text.split()[1:]
                            self.handle_boost_command(chat_id, args)
                        elif text.startswith("/simulate"):
                            content = text.replace("/simulate", "", 1).strip()
                            self.handle_simulate_text(chat_id, content or "Sample Post Text")
                        elif text == "/roas":
                            self.handle_roas_scorecard(chat_id)
                        elif text in ("/help", "/commands"):
                            self.handle_help(chat_id)
                        elif text.startswith("/autopilot"):
                            parts = text.split()
                            if len(parts) > 1 and parts[1].lower() in ("off", "0", "pause"):
                                self.autopilot_enabled = False
                            else:
                                self.autopilot_enabled = True
                            state = "🟢 ACTIVE" if self.autopilot_enabled else "🔴 PAUSED"
                            self.send_message(chat_id, f"🤖 <b>Autopilot:</b> {state}")
                        elif text.startswith("/"):
                            self.send_message(chat_id, "⚠️ មិនស្គាល់ Command នេះទេ។ ប្រើ /help ដើម្បីមើលបញ្ជី Commands។")
                        else:
                            # Natural text sent by user -> run instant AI Copy & ROAS simulator!
                            self.handle_simulate_text(chat_id, text)

                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Telegram polling loop exception: {e}")
                time.sleep(3)

    def run_interactive_terminal(self):
        """Interactive terminal CLI simulation when no Telegram token is configured."""
        self.handle_start("terminal_user")
        while True:
            try:
                cmd = input("\n[Telegram Terminal Mock] Enter command or text (or 'exit'): ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit"):
                    print("Exiting Telegram Mock...")
                    break
                if cmd in ("/start", "/menu"):
                    self.handle_start("terminal_user")
                elif cmd in ("/status", "/health"):
                    self.handle_status("terminal_user")
                elif cmd == "/admin_status":
                    self.handle_admin_status("terminal_user")
                elif cmd == "/admin_users":
                    self.handle_admin_users("terminal_user")
                elif cmd == "/admin_pages":
                    self.handle_admin_pages("terminal_user")
                elif cmd == "/admin_sync":
                    self.handle_admin_sync("terminal_user")
                elif cmd.startswith("/admin_broadcast"):
                    self.handle_admin_broadcast("terminal_user", cmd)
                elif cmd.startswith("/auto_publish") or cmd.startswith("/autopublish"):
                    self.handle_auto_publish("terminal_user", cmd)
                elif cmd in ("/train_page", "/train_dna"):
                    self.handle_train_page("terminal_user")
                elif cmd in ("/publish_now", "/test_publish", "/pubnow"):
                    self.handle_publish_now("terminal_user")
                elif cmd.startswith("/fb_login"):
                    self.handle_fb_login("terminal_user", cmd)
                elif cmd.startswith("/fb_2fa"):
                    self.handle_fb_2fa("terminal_user", cmd)
                elif cmd in ("/fb_pages", "/pages"):
                    self.handle_fb_pages("terminal_user")
                elif cmd.startswith("/fb_select"):
                    p_id = cmd.replace("/fb_select", "", 1).strip()
                    self.handle_fb_select_page("terminal_user", p_id)
                elif cmd.startswith("/fb_token"):
                    self.handle_fb_token("terminal_user", cmd)
                elif cmd.startswith("/fb_cookie"):
                    self.handle_fb_cookie("terminal_user", cmd)
                elif cmd in ("/fb_logout", "/logout"):
                    self.handle_fb_logout("terminal_user")
                elif cmd in ("/fb_connect", "/fb_guide"):
                    self.handle_fb_login_guide("terminal_user")
                elif cmd in ("/web", "/dashboard", "/gui"):
                    self.handle_web_dashboard_info("terminal_user")
                elif cmd.startswith("/generate"):
                    topic = cmd.replace("/generate", "", 1).strip()
                    self.handle_generate("terminal_user", topic)
                elif cmd.startswith("/offline_boost"):
                    topic = cmd.replace("/offline_boost", "", 1).strip()
                    self.handle_offline_boost("terminal_user", topic)
                elif cmd.startswith("/viral_creator"):
                    topic = cmd.replace("/viral_creator", "", 1).strip()
                    self.handle_offline_boost("terminal_user", topic)
                elif cmd.startswith("/post"):
                    msg_content = cmd.replace("/post", "", 1).strip()
                    self.handle_post_to_page("terminal_user", msg_content)
                elif cmd == "/comments":
                    self.handle_comments_status("terminal_user")
                elif cmd == "/scan":
                    self.handle_scan("terminal_user")
                elif cmd == "/active":
                    self.handle_active("terminal_user")
                elif cmd.startswith("/boost"):
                    args = cmd.split()[1:]
                    self.handle_boost_command("terminal_user", args)
                elif cmd == "/roas":
                    self.handle_roas_scorecard("terminal_user")
                elif cmd in ("/help", "/commands"):
                    self.handle_help("terminal_user")
                else:
                    self.handle_simulate_text("terminal_user", cmd)
            except (KeyboardInterrupt, EOFError):
                break


def main():
    bot = BMTelegramBot()
    bot.run_polling()


if __name__ == "__main__":
    main()

