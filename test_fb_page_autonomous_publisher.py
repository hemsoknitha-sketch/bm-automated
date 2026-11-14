# -*- coding: utf-8 -*-
"""
Verification tests for Page's Itself Training & 4K Autonomous Publisher
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from meta_graph_api import MetaGraphAPIClient
from fb_page_autonomous_publisher import PageAutonomousPublisherEngine, PageBrandDNA, ProductPhotoBundle
from fb_multi_tenant_manager import MultiTenantManager


class TestPageAutonomousPublisher(unittest.TestCase):

    def setUp(self):
        self.publisher = PageAutonomousPublisherEngine.get_instance()
        self.client = MetaGraphAPIClient(
            access_token="mock_token",
            page_id="page101_test",
            ad_account_id="act_101",
            api_version="v21.0",
            is_mock=True
        )
        self.telegram_id = "859271875"

    def test_stage_1_train_page_brand_dna(self):
        dna = self.publisher.train_page_brand_dna(self.client, self.telegram_id)
        self.assertIsNotNone(dna)
        self.assertEqual(dna.page_id, "page101_test")
        self.assertGreater(len(dna.extracted_products), 0)
        self.assertTrue("+855" in dna.hotlines or len(dna.hotlines) > 5)

    def test_stage_2_mine_and_cluster_photos(self):
        dna = self.publisher.train_page_brand_dna(self.client, self.telegram_id)
        bundle = self.publisher.mine_and_cluster_product_photos(self.client, dna, target_count=4)
        self.assertIsNotNone(bundle)
        self.assertGreaterEqual(len(bundle.photo_urls_or_paths), 3)

    def test_stage_3_4_5_end_to_end_campaign_cycle(self):
        res = self.publisher.execute_scheduled_publishing_cycle(
            client=self.client,
            telegram_id=self.telegram_id,
            interval_hours=2,
            photo_count=4,
            force_now=True
        )
        self.assertTrue(res.get("success"), f"Campaign failed: {res}")
        self.assertIn("post_id", res)
        self.assertGreaterEqual(res.get("photo_count", 0), 3)
        self.assertIn("សម្រស់ថ្មីទំនើប ២០២៦", res.get("headline", ""))
        self.assertIn("Hotlines", res.get("caption", ""))
        self.assertIn("#", res.get("caption", ""))


if __name__ == "__main__":
    unittest.main()
