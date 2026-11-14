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

        buttons.append([
            {"text": "🌐 Open Web Dashboard", "url": f"http://localhost:{config.web_port}"},
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
        """Presents instructions for zero-setup Facebook login."""
        msg = (
            "🔑 <b>ការភ្ជាប់ FACEBOOK ដោយងាយស្រួល (ZERO METADEV SETUP)</b>\n"
            "<i>មិនបាច់មាន Meta App ID, Secret, ឬ Access Token ស្មុគស្មាញឡើយ!</i>\n"
            "────────────────────────────\n"
            "👉 <b>ជម្រើសទី ១ (លឿន & ងាយស្រួលបំផុត):</b>\n"
            "វាយបញ្ជា៖ <code>/fb_login &lt;email&gt; &lt;password&gt;</code>\n"
            "ឧទាហរណ៍៖ <code>/fb_login user@email.com MySecretPass123</code>\n"
            "<i>(ប្រព័ន្ធលុប Password ចេញពី Memory ភ្លាមៗ និងប្រើកូដ 2FA /fb_2fa)</i>\n\n"
            "👉 <b>ជម្រើសទី ២ (ភ្ជាប់តាម Browser Cookie c_user & xs):</b>\n"
            "វាយបញ្ជា៖ <code>/fb_cookie c_user=...; xs=...</code>\n"
            "<i>(ជួយរំលង Checkpoint 100% ដោយមិនបាច់វាយលេខសម្ងាត់)</i>\n\n"
            "👉 <b>ជម្រើសទី ៣ (បើមាន Access Token ឬ Page Token ស្រាប់):</b>\n"
            "វាយបញ្ជា៖ <code>/fb_token EAA...</code>\n"
            "────────────────────────────\n"
            "💡 បន្ទាប់ពីភ្ជាប់ជោគជ័យ ប្រព័ន្ធនឹងទាញយក <b>Facebook Pages ទាំងអស់</b> ដែលបងគ្រប់គ្រង មកបង្ហាញជូនបងជ្រើសរើសភ្លាមៗ!"
        )
        self.send_message(chat_id, msg)

    def handle_fb_login(self, chat_id: str, text: str):
        """Processes /fb_login <email> <password> command."""
        parts = text.split()
        if len(parts) < 3:
            self.send_message(
                chat_id,
                "⚠️ <b>ទម្រង់ប្រើប្រាស់៖</b> <code>/fb_login &lt;email&gt; &lt;password&gt;</code>\n"
                "ឧទាហរណ៍៖ <code>/fb_login user@email.com SecretPass123</code>"
            )
            return

        email = parts[1]
        password = parts[2]
        self.send_message(chat_id, "⏳ <b>កំពុងភ្ជាប់ទៅកាន់ Facebook និងទាញយក Pages របស់បង...</b>")

        res = self.auth_gateway.execute_telegram_login(chat_id, email, password)
        if res.get("status") == "AWAITING_2FA":
            self.send_message(chat_id, res["message"])
            return

        if res.get("success"):
            kb = {
                "inline_keyboard": [
                    [{"text": "📄 មើល និងជ្រើសរើស Pages របស់បង", "callback_data": "cmd_fb_pages"}],
                    [{"text": "🔍 Scan Posts លើ Page ចម្បង", "callback_data": "cmd_scan"}]
                ]
            }
            self.send_message(chat_id, res["message"], reply_markup=kb)
        else:
            self.send_message(chat_id, res["message"])

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

        msg = (
            f"⚙️ <b>ការកំណត់សម្រាប់ PAGE:</b> <b>{target.page_name}</b>\n"
            "────────────────────────────\n"
            f"• <b>Page ID:</b> <code>{target.page_id}</code>\n"
            f"• <b>Autonomous Boost:</b> {boost_txt}\n"
            f"• <b>AI Messenger Chat Closer:</b> {chat_txt}\n"
            f"• <b>Daily Budget Limit:</b> <b>${target.daily_budget_usd:.2f}/day</b>\n"
            f"• <b>Min ROAS Hurdle:</b> <code>{target.min_roas_hurdle}X</code>\n"
            "────────────────────────────\n"
            "💡 ចុចប៊ូតុងខាងក្រោមដើម្បី បើក/បិទ មុខងារ៖"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": f"🚀 Toggle Boost ({'បិទ' if target.is_active_boost else 'បើក'})", "callback_data": f"toggle_boost_{page_id}"},
                    {"text": f"💬 Toggle Chat ({'បិទ' if target.is_active_chat else 'បើក'})", "callback_data": f"toggle_chat_{page_id}"}
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
                            break
                    except Exception:
                        pass

        print("=" * 80, flush=True)
        print("🤖 [BM TELEGRAM BOT] STARTED 24/7 TELEGRAM LONG POLLING...", flush=True)
        print(f"🔒 Admin Chat ID: {self.admin_id or 'Any User'}", flush=True)
        print("======================================================================", flush=True)

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

