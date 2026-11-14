# -*- coding: utf-8 -*-
"""
==============================================================================
🧪 TEST SUITE: AI OFFLINE BOOST & VIRAL CREATOR ($0 AD SPEND)
==============================================================================
Validates:
1. SocialViralRadarEngine trend-jacking & category classification
2. KhmerLanguageAuditor Chuon Nath spelling & spam punctuation sanitation
3. BannerEngine 4K graphic banner generation with HarfBuzz/Pillow Khmer font
4. FBOfflineBoostEngine complete package orchestration
5. BMTelegramBot /offline_boost & /viral_creator command processing
6. Flask Web Dashboard /api/offline_boost/generate and /publish REST APIs
==============================================================================
"""

import unittest
import asyncio
from pathlib import Path
import tempfile
import json

from social_viral_radar import SocialViralRadarEngine
from khmer_auditor import KhmerLanguageAuditor
from banner_engine import BannerEngine
from fb_offline_boost_engine import FBOfflineBoostEngine, OfflineBoostPackage
from fb_multi_tenant_manager import MultiTenantManager
from meta_graph_api import MetaGraphAPIClient
from bm_telegram_bot import BMTelegramBot
from web_dashboard import app


class TestFBOfflineBoost(unittest.TestCase):

    def setUp(self):
        self.radar = SocialViralRadarEngine()
        self.auditor = KhmerLanguageAuditor()
        self.banner = BannerEngine()
        self.offline_engine = FBOfflineBoostEngine()
        self.bot = BMTelegramBot()

    def test_01_social_viral_radar(self):
        """Verifies Cambodian social trend-jacking detection."""
        trend = self.radar.analyze_viral_trend(
            "អំពើពុករលួយ និងការឆបោកតាមអនឡាញ",
            "ប្រជាពលរដ្ឋសំណូមពរឱ្យមានវិធានការតឹងរ៉ឹងលើការឆបោក"
        )
        self.assertTrue(trend["is_viral"])
        self.assertGreaterEqual(trend["viral_score"], 45.0)
        self.assertTrue(len(trend["matched_keywords"]) >= 2)

    def test_02_khmer_language_auditor(self):
        """Verifies Chuon Nath dictionary spelling correction & punctuation."""
        raw_text = "ព័ត៏មាន ទាន់ហេតុការណ៍ ៖ អំពើរពុករលួយ និងសន្តិសុខ័ សង្គម !!!"
        sanitized = self.auditor.sanitize_khmer_spelling_and_punctuation(raw_text)
        self.assertIn("ព័ត៌មាន", sanitized)
        self.assertIn("អំពើពុករលួយ", sanitized)
        self.assertIn("សន្តិសុខ", sanitized)
        self.assertNotIn("!!!", sanitized)

    def test_03_banner_engine_generation(self):
        """Verifies 4K graphic banner generation with embedded Khmer TTF font."""
        async def _gen():
            path = await self.banner.generate_banner_image(
                headline="កំពូលយុទ្ធសាស្ត្រ Boost Facebook ឥតគិតថ្លៃ ២០២៦",
                category_title="ទីផ្សារឌីជីថល AI",
                badge_label="⚡ AI OFFLINE BOOST",
                badge_color="amber",
                use_playwright=False
            )
            return path

        banner_path = asyncio.run(_gen())
        self.assertTrue(Path(banner_path).exists())
        self.assertGreater(Path(banner_path).stat().st_size, 5000)

    def test_04_offline_boost_package_orchestration(self):
        """Verifies end-to-end package generation by FBOfflineBoostEngine."""
        async def _gen_pkg():
            return await self.offline_engine.generate_offline_boost_package(
                topic="យុទ្ធសាស្ត្រពាណិជ្ជកម្ម AI Angkor Quant",
                aspect_ratio="1:1",
                include_audio=False
            )

        pkg = asyncio.run(_gen_pkg())
        self.assertIsInstance(pkg, OfflineBoostPackage)
        self.assertTrue(len(pkg.caption) > 100)
        self.assertGreater(pkg.hook_score, 0)
        self.assertTrue(Path(pkg.banner_image_path).exists())
        self.assertIn("AI OFFLINE BOOST", pkg.summary_khmer)

    def test_05_telegram_bot_offline_boost_command(self):
        """Verifies /offline_boost and /viral_creator command handlers."""
        t_id = "tg_offline_user_001"
        self.bot.handle_offline_boost(t_id, "បច្ចេកវិទ្យាទីផ្សារ AI ជំនាន់ថ្មី")
        self.assertIn(t_id, self.bot._last_offline_packages)
        pkg = self.bot._last_offline_packages[t_id]
        self.assertIsNotNone(pkg.banner_image_path)

        # Test posting to page mock
        client = MetaGraphAPIClient(is_mock=True)
        res = self.offline_engine.publish_package_to_page(pkg, client)
        self.assertTrue(res["success"])
        self.assertIn("post_id", res)

    def test_06_web_api_offline_boost_endpoints(self):
        """Verifies Flask Web API endpoints for offline boost generation and publishing."""
        with app.test_client() as client:
            # 1. Generate package
            gen_res = client.post("/api/offline_boost/generate", json={
                "topic": "ស្បែកជើងសុភាពនារី ម៉ូដថ្មី ២០២៦",
                "aspect_ratio": "1:1",
                "include_audio": False
            })
            self.assertEqual(gen_res.status_code, 200)
            data = gen_res.get_json()
            self.assertTrue(data["success"])
            self.assertIsNotNone(data["banner_url"])
            self.assertGreater(data["hook_score"], 0)

            # 2. Publish package
            pub_res = client.post("/api/offline_boost/publish", json={
                "telegram_id": "test_web_user",
                "topic": "ស្បែកជើងសុភាពនារី",
                "headline": data["headline"],
                "caption": data["caption"],
                "banner_path": data["banner_path"]
            })
            self.assertEqual(pub_res.status_code, 200)
            pub_data = pub_res.get_json()
            self.assertTrue(pub_data["success"])


if __name__ == "__main__":
    unittest.main()
