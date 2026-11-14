# -*- coding: utf-8 -*-
"""
==============================================================================
🧪 TEST SUITE: MULTI-TENANT FACEBOOK LOGIN & PAGE CONTROLLER
==============================================================================
Validates:
1. MultiTenantManager & AES-256 Token Encryption Vault
2. User Registration & Page Synchronization (GET /me/accounts)
3. Dynamic Page Selection & Custom Settings (Auto-Boost, AI Chat, Budget)
4. FBAuthGateway Interactive Telegram Login & 2FA Flow
5. Dynamic MetaGraphAPIClient Binding per VIP User
==============================================================================
"""

import unittest
from pathlib import Path
import tempfile
import time

from fb_multi_tenant_manager import MultiTenantManager, TokenEncryptionVault
from fb_auth_gateway import FBAuthGateway


class TestFBMultiTenant(unittest.TestCase):

    def setUp(self):
        # Create temporary database
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self.temp_dir.name) / "test_multi_tenant.db"
        self.manager = MultiTenantManager(db_path=self.db_path)
        self.gateway = FBAuthGateway(db_manager=self.manager)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_vault_encryption(self):
        """Verifies AES-256 token encryption and decryption."""
        vault = TokenEncryptionVault()
        raw_token = "EAA_TEST_SECRET_ACCESS_TOKEN_12345"
        enc = vault.encrypt(raw_token)
        self.assertNotEqual(enc, raw_token)
        dec = vault.decrypt(enc)
        self.assertEqual(dec, raw_token)

    def test_02_user_and_pages_registration(self):
        """Verifies multi-user page synchronization."""
        t_id = "user_khmer_vip_001"
        self.manager.register_or_update_user(
            telegram_id=t_id,
            fb_user_id="fb_1001",
            fb_name="Hem Sinath",
            user_token="EAA_TOKEN_USER_1",
            auth_method="TELEGRAM_LOGIN"
        )
        user = self.manager.get_user(t_id)
        self.assertIsNotNone(user)
        self.assertEqual(user["fb_name"], "Hem Sinath")
        self.assertEqual(user["user_token"], "EAA_TOKEN_USER_1")

        # Save pages
        sample_pages = [
            {"id": "page_101", "name": "Angkor Quant AI Store", "category": "E-Commerce", "followers_count": 12000, "access_token": "TOK_PAGE_101"},
            {"id": "page_102", "name": "VIP Real Estate KH", "category": "Real Estate", "followers_count": 4500, "access_token": "TOK_PAGE_102"}
        ]
        count = self.manager.save_user_pages(t_id, sample_pages)
        self.assertEqual(count, 2)

        pages = self.manager.get_user_pages(t_id)
        self.assertEqual(len(pages), 2)
        # First page should be active by default
        active = self.manager.get_active_page(t_id)
        self.assertEqual(active["page_id"], "page_101")
        self.assertEqual(active["page_token"], "TOK_PAGE_101")

    def test_03_page_selection_and_settings(self):
        """Verifies 1-click active page switching and settings updating."""
        t_id = "user_khmer_vip_002"
        self.manager.register_or_update_user(t_id, "fb_1002", "Dara VIP", "TOK_USER_2")
        self.manager.save_user_pages(t_id, [
            {"id": "page_A", "name": "Page Alpha", "access_token": "TOK_A"},
            {"id": "page_B", "name": "Page Beta", "access_token": "TOK_B"}
        ])

        # Switch to Page B
        self.manager.set_active_page(t_id, "page_B")
        active = self.manager.get_active_page(t_id)
        self.assertEqual(active["page_id"], "page_B")
        self.assertEqual(active["page_token"], "TOK_B")

        # Update settings
        self.manager.update_page_settings(t_id, "page_B", is_active_boost=False, daily_budget_usd=25.0)
        updated = self.manager.get_active_page(t_id)
        self.assertEqual(updated["is_active_boost"], 0)
        self.assertEqual(updated["daily_budget_usd"], 25.0)

    def test_04_auth_gateway_telegram_login_and_2fa(self):
        """Verifies /fb_login with standard flow and 2FA checkpoint."""
        t_id = "user_tg_777"

        # Standard direct login
        res = self.gateway.execute_telegram_login(t_id, "hemsinath@gmail.com", "SecurePassword123")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "CONNECTED")
        self.assertGreater(res["pages_count"], 0)

        # 2FA Checkpoint trigger
        t_id_2fa = "user_tg_888"
        res_2fa = self.gateway.execute_telegram_login(t_id_2fa, "vip2fa@gmail.com", "Password2FA")
        self.assertFalse(res_2fa["success"])
        self.assertEqual(res_2fa["status"], "AWAITING_2FA")

        # Submit 2FA code
        res_sub = self.gateway.submit_2fa_code(t_id_2fa, "849201")
        self.assertTrue(res_sub["success"])
        self.assertGreater(res_sub["pages_count"], 0)

    def test_05_dynamic_client_binding(self):
        """Verifies MetaGraphAPIClient dynamically binds to active page."""
        t_id = "user_tg_999"
        self.gateway.execute_telegram_login(t_id, "trader@gmail.com", "Pass123")
        client, record = self.gateway.get_user_page_client(t_id)
        self.assertIsNotNone(record)
        self.assertEqual(client.page_id, record.page_id)
        self.assertFalse(client.is_mock)

    def test_06_cookie_connection(self):
        """Verifies connection via browser cookie string (c_user & xs)."""
        t_id = "user_cookie_123"
        cookie_str = "c_user=100084729104829; xs=38%3Asample_valid_session_xs_123; fr=0abc; datr=xyz"
        res = self.gateway.connect_with_cookies(t_id, cookie_str)
        self.assertTrue(res["success"])
        self.assertEqual(res["fb_user_id"], "100084729104829")
        self.assertGreater(res["pages_count"], 0)

        # Verify invalid cookie rejection
        bad_cookie = "datr=only_tracking; fr=test"
        res_bad = self.gateway.connect_with_cookies("bad_user", bad_cookie)
        self.assertFalse(res_bad["success"])

    def test_07_web_multitenant_endpoints(self):
        """Verifies Flask web dashboard multi-tenant API endpoints."""
        from web_dashboard import app
        # Re-point app to use this test manager instance
        MultiTenantManager._instance = self.manager

        with app.test_client() as client:
            # 1. Connect user via web endpoint
            res = client.post("/api/multitenant/connect", json={
                "telegram_id": "web_test_user",
                "auth_type": "LOGIN",
                "email": "webtester@gmail.com",
                "password": "Password123"
            })
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data["success"])

            # 2. Get users list
            res_users = client.get("/api/multitenant/users")
            self.assertEqual(res_users.status_code, 200)
            users_list = res_users.get_json()
            self.assertTrue(any(u["telegram_id"] == "web_test_user" for u in users_list))

            # 3. Get user pages
            res_pages = client.get("/api/multitenant/pages?telegram_id=web_test_user")
            self.assertEqual(res_pages.status_code, 200)
            pages = res_pages.get_json()
            self.assertGreater(len(pages), 0)
            target_page_id = pages[0]["page_id"]

            # 4. Update page settings
            res_upd = client.post("/api/multitenant/update_page", json={
                "telegram_id": "web_test_user",
                "page_id": target_page_id,
                "is_active_boost": False,
                "daily_budget_usd": 15.0
            })
            self.assertEqual(res_upd.status_code, 200)
            self.assertTrue(res_upd.get_json()["success"])

            # Verify update reflected
            res_pages2 = client.get("/api/multitenant/pages?telegram_id=web_test_user")
            pages2 = res_pages2.get_json()
            target = next(p for p in pages2 if p["page_id"] == target_page_id)
            self.assertFalse(target["is_active_boost"])
            self.assertEqual(target["daily_budget_usd"], 15.0)


if __name__ == "__main__":
    unittest.main()
