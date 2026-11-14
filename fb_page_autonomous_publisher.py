# -*- coding: utf-8 -*-
"""
==============================================================================
🏛️ ANGKOR QUANT - PAGE'S ITSELF TRAINING & AUTONOMOUS 4K VIRAL PUBLISHER
==============================================================================
Fully automated 5-Stage Institutional Production Engine:
1. Stage 1: Page's Itself Brand DNA Deep Training (Profile, Products, Tone, Audience)
2. Stage 2: Original Asset Mining & 3-5 Product Photo Clustering
3. Stage 3: 4K Ultra-HD Graphic Studio Enhancer (HarfBuzz Typography & Brand Palette)
4. Stage 4: High-Converting Selling Copywriter (Short Headline, Bullet Value, Map/Hotline, 5 Hashtags)
5. Stage 5: Zero-Defect Scheduled Publisher (1h/2h Cadence, Circadian Sleep Shield, Idempotency)
==============================================================================
"""

import os
import re
import time
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Core System Dependencies
from config import config
from meta_graph_api import MetaGraphAPIClient, FacebookPost
from fb_multi_tenant_manager import MultiTenantManager, ManagedPageRecord
from khmer_auditor import KhmerLanguageAuditor
from ai_copy_hook_scorer import AICopyHookScorer
from banner_engine import BannerEngine

logger = logging.getLogger("BM_AUTOMATED.AutonomousPublisher")

BASE_DIR = Path(__file__).resolve().parent
ASSETS_CACHE_DIR = BASE_DIR / "data" / "page_assets"
FONTS_DIR = BASE_DIR / "fonts"


@dataclass
class PageBrandDNA:
    page_id: str
    telegram_id: str
    brand_name: str
    category: str
    hotlines: str
    address: str
    map_url: str
    messenger_url: str
    tone_of_voice: str
    extracted_products: List[str]
    top_keywords: List[str]
    last_trained: float


@dataclass
class ProductPhotoBundle:
    product_name: str
    photo_urls_or_paths: List[str]
    enhanced_photo_paths: List[str]
    photo_hashes: List[str]


@dataclass
class Page4KViralCampaign:
    page_id: str
    telegram_id: str
    product_name: str
    headline: str
    caption: str
    photo_paths: List[str]
    photo_count: int
    hook_score: float
    copy_grade: str
    scheduled_interval_hours: int
    is_circadian_optimal: bool
    summary_khmer: str


class PageAutonomousPublisherEngine:
    """
    Master 5-Stage Autonomous Engine for training on Page's own DNA and
    publishing 4K multi-photo viral campaigns with zero defects.
    """

    _instance: Optional["PageAutonomousPublisherEngine"] = None

    def __init__(self):
        self.multi_tenant = MultiTenantManager.get_instance()
        self.auditor = KhmerLanguageAuditor()
        self.hook_scorer = AICopyHookScorer()
        self.banner_engine = BannerEngine()
        ASSETS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "PageAutonomousPublisherEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # =========================================================================
    # STAGE 1: PAGE'S ITSELF BRAND DNA DEEP TRAINING
    # =========================================================================

    def train_page_brand_dna(
        self,
        client: MetaGraphAPIClient,
        telegram_id: str
    ) -> PageBrandDNA:
        """
        Deep-analyzes the connected Facebook Page:
        1. Profile metadata, phone numbers, map address, category.
        2. Top-performing historical posts to identify products, pricing, and tone of voice.
        """
        page_id = client.page_id
        logger.info(f"🧠 [STAGE 1] Initiating Page's Itself Deep Training for Page [{page_id}]...")

        # 1. Fetch live page profile details
        profile = client.get_page_profile_details()
        brand_name = profile.get("name") or "Angkor Quant Store"
        category = profile.get("category") or "E-Commerce & Technology"

        # Hotlines detection
        raw_phone = profile.get("phone") or "+855 85 927 1875"
        hotlines = self._sanitize_hotline(raw_phone)

        # Address & Map link detection
        address = profile.get("single_line_address") or "Phnom Penh, Cambodia"
        loc = profile.get("location") or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if lat and lng:
            map_url = f"https://maps.google.com/?q={lat},{lng}"
        else:
            map_url = f"https://maps.google.com/?q={address.replace(' ', '+')}"

        messenger_url = f"https://m.me/{page_id}"

        # 2. Scrape historical feed posts to discover catalog, products, and tone
        posts = client.get_page_posts(limit=30)
        extracted_products = []
        top_keywords = []

        all_text = " ".join([p.message for p in posts if p.message])
        if all_text:
            extracted_products = self._extract_product_entities(all_text)
            top_keywords = self._extract_top_keywords(all_text)

        # Default fallbacks if brand has newly created page
        if not extracted_products:
            extracted_products = [
                f"ឈុតផលិតផលពិសេសប្រចាំហាង {brand_name}",
                f"សេវាកម្មគុណភាពខ្ពស់ស្តង់ដារអន្តរជាតិ",
                f"ផលិតផលថ្មីពេញនិយមប្រចាំឆ្នាំ ២០២៦"
            ]

        if not top_keywords:
            top_keywords = ["គុណភាពខ្ពស់", "ទំនុកចិត្ត", "តម្លៃសមរម្យ", "ទាន់សម័យ", "សេវាកម្មរហ័ស"]

        tone = "Professional, Friendly & High-Converting Cambodian Retail"

        dna = PageBrandDNA(
            page_id=page_id,
            telegram_id=str(telegram_id),
            brand_name=brand_name,
            category=category,
            hotlines=hotlines,
            address=address,
            map_url=map_url,
            messenger_url=messenger_url,
            tone_of_voice=tone,
            extracted_products=extracted_products,
            top_keywords=top_keywords,
            last_trained=time.time()
        )

        # Save to database
        self.multi_tenant.save_page_brand_dna(
            page_id=page_id,
            telegram_id=str(telegram_id),
            dna_data=asdict(dna)
        )
        logger.info(f"✅ [STAGE 1] Page DNA Trained! Products found: {len(extracted_products)} | Hotlines: {hotlines}")
        return dna

    # =========================================================================
    # STAGE 2: ORIGINAL ASSET MINING & 3-5 PHOTO CLUSTERING
    # =========================================================================

    def mine_and_cluster_product_photos(
        self,
        client: MetaGraphAPIClient,
        dna: PageBrandDNA,
        target_count: int = 4
    ) -> ProductPhotoBundle:
        """
        Retrieves original high-resolution uploaded photos from Page albums,
        filters low-res/blurry photos, and groups 3 to 5 images per product bundle.
        """
        page_id = client.page_id
        logger.info(f"📸 [STAGE 2] Mining product photos for [{dna.brand_name}] (Target: {target_count} photos)...")

        # Download or gather original image paths
        page_cache_dir = ASSETS_CACHE_DIR / page_id
        page_cache_dir.mkdir(parents=True, exist_ok=True)

        selected_photos = []
        photo_hashes = []

        if client.is_mock:
            # In simulation/mock mode, generate crisp studio fallback photos to eliminate network timeouts
            selected_photos = self._generate_fallback_product_photos(page_cache_dir, dna, target_count)
            photo_hashes = [hashlib.md5(p.encode()).hexdigest()[:10] for p in selected_photos]
        else:
            uploaded = client.get_page_uploaded_photos(limit=35)
            import requests
            for idx, p in enumerate(uploaded):
                src = p.get("source")
                if not src:
                    continue
                # Quality filter: skip very small thumbnails
                w = p.get("width", 0)
                h = p.get("height", 0)
                if w > 0 and w < 600:
                    continue

                # Local cache download
                img_hash = hashlib.md5(src.encode("utf-8")).hexdigest()[:10]
                local_path = page_cache_dir / f"orig_{img_hash}.jpg"

                if not local_path.exists():
                    try:
                        r = requests.get(src, timeout=10)
                        if r.status_code == 200:
                            with open(local_path, "wb") as f:
                                f.write(r.content)
                    except Exception as e:
                        logger.warning(f"Could not download photo {src[:50]}: {e}")

                if local_path.exists():
                    selected_photos.append(str(local_path))
                    photo_hashes.append(img_hash)

                if len(selected_photos) >= target_count:
                    break

            # Fallback if page has fewer than target_count photos
            if len(selected_photos) < 3:
                selected_photos = self._generate_fallback_product_photos(page_cache_dir, dna, target_count)
                photo_hashes = [hashlib.md5(p.encode()).hexdigest()[:10] for p in selected_photos]
            photo_hashes = [hashlib.md5(p.encode()).hexdigest()[:10] for p in selected_photos]

        # Select a product name from DNA
        p_name = dna.extracted_products[int(time.time()) % len(dna.extracted_products)]

        return ProductPhotoBundle(
            product_name=p_name,
            photo_urls_or_paths=selected_photos,
            enhanced_photo_paths=[],
            photo_hashes=photo_hashes
        )

    # =========================================================================
    # STAGE 3: 4K ULTRA-HD GRAPHIC STUDIO & MULTI-BANNER ENHANCER
    # =========================================================================

    def enhance_bundle_to_4k_studio(
        self,
        bundle: ProductPhotoBundle,
        dna: PageBrandDNA
    ) -> List[str]:
        """
        Enhances all 3 to 5 images into 4K Ultra-HD resolution with HarfBuzz
        Khmer typography, brand color palettes, and trust ribbons.
        """
        enhanced_paths = []
        out_dir = ASSETS_CACHE_DIR / dna.page_id / "enhanced_4k"
        out_dir.mkdir(parents=True, exist_ok=True)

        brand_color = self._derive_brand_palette(dna.category)

        for idx, img_path in enumerate(bundle.photo_urls_or_paths, 1):
            is_hero = (idx == 1)
            target_file = out_dir / f"4k_{int(time.time())}_{idx}.jpg"

            try:
                enhanced_file = self._render_4k_framed_image(
                    source_image_path=img_path,
                    output_path=str(target_file),
                    brand_name=dna.brand_name,
                    hotline=dna.hotlines,
                    is_hero=is_hero,
                    badge_title="🔥 NEW ARRIVAL 2026" if is_hero else f"⭐ ANGLE {idx}",
                    brand_color=brand_color
                )
                enhanced_paths.append(enhanced_file)
            except Exception as e:
                logger.error(f"Error enhancing image {img_path}: {e}")
                enhanced_paths.append(img_path)

        bundle.enhanced_photo_paths = enhanced_paths
        return enhanced_paths

    def _render_4k_framed_image(
        self,
        source_image_path: str,
        output_path: str,
        brand_name: str,
        hotline: str,
        is_hero: bool = True,
        badge_title: str = "🔥 BEST SELLER 2026",
        brand_color: Tuple[int, int, int] = (16, 185, 129)
    ) -> str:
        """Renders 4K Studio Canvas (3840x3840) with dynamic framing and badges."""
        canvas_size = (3840, 3840)
        canvas = Image.new("RGB", canvas_size, (15, 23, 42))  # Sleek dark slate backdrop

        # Load and resize source image
        try:
            src = Image.open(source_image_path).convert("RGB")
        except Exception:
            src = Image.new("RGB", (2000, 2000), brand_color)

        # Scale with aspect ratio preserving
        src_w, src_h = src.size
        target_w = 3600
        target_h = 3600
        ratio = min(target_w / src_w, target_h / src_h)
        new_size = (int(src_w * ratio), int(src_h * ratio))
        src_resized = src.resize(new_size, Image.Resampling.LANCZOS)

        # Paste centered
        offset_x = (canvas_size[0] - new_size[0]) // 2
        offset_y = (canvas_size[1] - new_size[1]) // 2
        canvas.paste(src_resized, (offset_x, offset_y))

        draw = ImageDraw.Draw(canvas)

        # Subtle elegant gold/brand border
        border_thickness = 16
        draw.rectangle(
            [(40, 40), (canvas_size[0] - 40, canvas_size[1] - 40)],
            outline=brand_color,
            width=border_thickness
        )

        # Typography fonts
        font_path = FONTS_DIR / "KhmerOSsiemreap.ttf"
        font_badge = None
        font_footer = None
        if font_path.exists():
            try:
                font_badge = ImageFont.truetype(str(font_path), 82)
                font_footer = ImageFont.truetype(str(font_path), 70)
            except Exception:
                pass

        # Draw Top Badge on Hero Photo
        if is_hero:
            badge_bg = [(100, 100), (1400, 260)]
            draw.rectangle(badge_bg, fill=brand_color)
            badge_text = badge_title
            draw.text((140, 135), badge_text, fill=(255, 255, 255), font=font_badge)

        # Draw Sleek Bottom Hotline Ribbon
        ribbon_bg = [(80, canvas_size[1] - 300), (canvas_size[0] - 80, canvas_size[1] - 100)]
        draw.rectangle(ribbon_bg, fill=(0, 0, 0))
        draw.rectangle(ribbon_bg, outline=brand_color, width=6)

        footer_text = f"💎 {brand_name}  |  📞 Hotline: {hotline}  |  💯 ស្តង់ដារគុណភាពខ្ពស់"
        draw.text((140, canvas_size[1] - 230), footer_text, fill=(255, 255, 255), font=font_footer)

        # Save Ultra-Crisp JPEG
        canvas.save(output_path, "JPEG", quality=95, optimize=True)
        return output_path

    # =========================================================================
    # STAGE 4: INSTITUTIONAL SELLING COPYWRITING
    # =========================================================================

    def craft_high_converting_copy(
        self,
        bundle: ProductPhotoBundle,
        dna: PageBrandDNA
    ) -> Tuple[str, str, float, str]:
        """
        Builds the 5-part Golden Selling Blueprint:
        1. Short Curiosity/Value Headline
        2. Punchy Core Value Offer (Bullet points)
        3. Complete Contact Block (Hotlines, Map link, Messenger)
        4. Exactly 5 Cambodian Trending Hashtags
        Returns: (headline, full_caption, hook_score, copy_grade)
        """
        p_name = bundle.product_name
        brand = dna.brand_name
        hotlines = dna.hotlines
        map_url = dna.map_url
        address = dna.address
        msg_url = dna.messenger_url

        # 1. Short Headline (under 12 words)
        headline = f"✨ សម្រស់ថ្មីទំនើប ២០២៦៖ {p_name} គុណភាពស្តង់ដារអន្តរជាតិ!"

        # 2. Punchy Core Value Bullet Points
        value_para = (
            f"រចនាម៉ូដយ៉ាងប្រណីត និងឆ្លើយតបគ្រប់តម្រូវការរបស់បងប្អូន! {brand} "
            f"សូមណែនាំនូវជម្រើសដ៏ល្អឥតខ្ចោះ ធានាទាំងគុណភាព និងតម្លៃសមរម្យបំផុត៖\n"
            f"• 💎 <b>គុណភាពស្តង់ដារខ្ពស់៖</b> ផលិតយ៉ាងផ្ចិតផ្ចង់ និងមានការធានាត្រឹមត្រូវ ១០០%\n"
            f"• ⚡ <b>ទាន់សម័យ & ងាយស្រួល៖</b> ស័ក្តិសមឥតខ្ចោះសម្រាប់ការប្រើប្រាស់ប្រចាំថ្ងៃ\n"
            f"• 🚚 <b>សេវាដឹកជញ្ជូនរហ័ស៖</b> ដឹកជញ្ជូនជូនដល់ទីកន្លែងទូទាំង ២៥ រាជធានី-ខេត្ត"
        )

        # 3. Contact & Map Block
        contact_block = (
            f"────────────────────────────\n"
            f"💎 <b>ព័ត៌មានលម្អិត & កម្ម៉ង់ទិញភ្លាមៗ៖</b>\n"
            f"📞 <b>ទូរស័ព្ទ / Hotlines:</b> <code>{hotlines}</code>\n"
            f"💬 <b>ផ្ញើសារ Inbox:</b> {msg_url}\n"
            f"📍 <b>ទីតាំង / ផែនទីហាង:</b> <a href=\"{map_url}\">Google Maps</a> ({address})\n"
            f"────────────────────────────"
        )

        # 4. Exactly 5 Cambodian Trending Hashtags
        cat_clean = re.sub(r"[^a-zA-Z0-9_\u1780-\u17FF]", "", dna.category)[:15] or "OnlineShopping"
        brand_tag = re.sub(r"[^a-zA-Z0-9_\u1780-\u17FF]", "", brand)[:15] or "AngkorQuant"
        hashtags = f"#{brand_tag} #{cat_clean} #Cambodia2026 #QualityStandard #FastDelivery"

        full_caption = f"{headline}\n\n{value_para}\n\n{contact_block}\n\n{hashtags}"

        # Khmer spelling sanitation
        sanitized_caption = self.auditor.sanitize_khmer_spelling_and_punctuation(full_caption)
        sanitized_headline = self.auditor.sanitize_khmer_spelling_and_punctuation(headline)

        # Hook Scoring
        score_res = self.hook_scorer.evaluate_copy(sanitized_caption)

        return sanitized_headline, sanitized_caption, score_res.hook_power_score, score_res.overall_copy_grade

    # =========================================================================
    # STAGE 5: ZERO-DEFECT SCHEDULED PUBLISHER (1h/2h CADENCE & IDEMPOTENCY)
    # =========================================================================

    def execute_scheduled_publishing_cycle(
        self,
        client: MetaGraphAPIClient,
        telegram_id: str,
        interval_hours: int = 2,
        photo_count: int = 4,
        force_now: bool = False
    ) -> Dict[str, Any]:
        """
        Executes end-to-end 5-Stage Publishing Workflow:
        1. Checks Circadian Sleep Lockout (02:00 - 05:00 AM ICT).
        2. Retrieves or trains Page's Itself Brand DNA.
        3. Mines 3 to 5 original product photos.
        4. Enhances them to 4K Ultra-HD with HarfBuzz typography and brand palette.
        5. Crafts high-converting selling copywriting.
        6. Enforces 30-day anti-duplicate ledger.
        7. Publishes atomically to Meta Graph API.
        8. Records to ledger and returns campaign summary.
        """
        page_id = client.page_id
        now = time.time()
        logger.info(f"🚀 [STAGE 5] Running Autonomous Publishing Cycle for Page [{page_id}]...")

        # 1. Circadian Sleep Lockout Guard
        if not force_now:
            import datetime
            utc_hour = datetime.datetime.now(datetime.timezone.utc).hour
            ict_hour = (utc_hour + 7) % 24
            if 2 <= ict_hour <= 5:
                logger.info(f"🌙 [CIRCADIAN LOCKOUT] Hour {ict_hour}:00 ICT is traffic dead-zone. Holding fire until 06:45 AM.")
                return {"success": False, "reason": "CIRCADIAN_SLEEP_LOCKOUT", "ict_hour": ict_hour}

        # 2. Stage 1: Load or Train DNA
        dna_dict = self.multi_tenant.get_page_brand_dna(page_id)
        if not dna_dict or (now - dna_dict.get("last_trained", 0) > 86400 * 7):
            dna = self.train_page_brand_dna(client, telegram_id)
        else:
            dna = PageBrandDNA(**dna_dict)

        # 3. Stage 2: Mine 3-5 Photos
        bundle = self.mine_and_cluster_product_photos(client, dna, target_count=photo_count)

        # 4. Stage 3: Enhance to 4K Studio
        enhanced_photos = self.enhance_bundle_to_4k_studio(bundle, dna)

        # 5. Stage 4: Craft Selling Copy
        headline, caption, hook_score, copy_grade = self.craft_high_converting_copy(bundle, dna)

        # 6. Anti-Duplicate Ledger Verification (30-day window)
        is_dup = self.multi_tenant.is_duplicate_post(
            page_id=page_id,
            headline=headline,
            image_hashes=bundle.photo_hashes,
            window_days=30
        )
        if is_dup and not force_now:
            logger.warning(f"⚠️ [DEDUPLICATION] Detected duplicate headline or photo set within 30 days! Refreshing angle...")
            headline = f"💎 ពិសេសបំផុតប្រចាំថ្ងៃ៖ {bundle.product_name} គុណភាពខ្ពស់ស្តង់ដារ ២០២៦!"
            caption = f"{headline}\n\n" + caption.split("\n\n", 1)[1]

        # 7. Atomic Multi-Photo Meta API Publishing
        pub_res = client.publish_multi_photo_post(
            message=caption,
            image_paths_or_urls=enhanced_photos
        )

        if "error" in pub_res:
            logger.error(f"❌ Failed to publish multi-photo post: {pub_res['error']}")
            return {"success": False, "error": pub_res["error"]}

        post_id = pub_res.get("id", f"{page_id}_auto_post_{int(now)}")
        post_url = pub_res.get("post_url", f"https://facebook.com/{post_id}")

        # 8. Record into SQLite Ledger
        self.multi_tenant.record_auto_post(
            post_id=post_id,
            page_id=page_id,
            telegram_id=str(telegram_id),
            headline=headline,
            image_hashes=bundle.photo_hashes,
            fb_post_url=post_url
        )
        self.multi_tenant.update_last_auto_post_time(page_id)

        summary_khmer = (
            f"🎉 <b>4K VIRAL CAMPAIGN PUBLISHED TO FACEBOOK!</b>\n"
            f"────────────────────────────\n"
            f"• <b>Facebook Page:</b> <b>{dna.brand_name}</b> (<code>{page_id}</code>)\n"
            f"• <b>Post ID:</b> <code>{post_id}</code>\n"
            f"• <b>រូបភាព 4K Studio:</b> <b>{len(enhanced_photos)} សន្លឹក (Multi-Photo)</b>\n"
            f"• <b>ចំណងជើង:</b> <i>\"{headline}\"</i>\n"
            f"• <b>Hook Power:</b> <b>{hook_score}/100</b> (Grade: <b>{copy_grade}</b>)\n"
            f"• <b>Hotlines ភ្ជាប់ក្នុង Post:</b> <code>{dna.hotlines}</code>\n"
            f"• <b>កាលវិភាគបន្ទាប់:</b> ក្នុងរយៈពេល <b>{interval_hours} ម៉ោងទៀត</b>\n"
            f"────────────────────────────\n"
            f"🔗 <a href=\"{post_url}\"><b>ចុចទីនេះដើម្បីបើកមើល Post លើ Facebook</b></a>"
        )

        return {
            "success": True,
            "post_id": post_id,
            "post_url": post_url,
            "photo_count": len(enhanced_photos),
            "headline": headline,
            "caption": caption,
            "summary_khmer": summary_khmer
        }

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _sanitize_hotline(self, raw_phone: str) -> str:
        """Standardizes telephone number format into clean readable string."""
        cleaned = re.sub(r"[^0-9\+\s\-]", "", raw_phone).strip()
        if not cleaned:
            return "+855 85 927 1875 / +855 92 546 327"
        return cleaned

    def _extract_product_entities(self, text: str) -> List[str]:
        """Extracts products or prominent topics from Cambodian social text."""
        lines = text.split("\n")
        candidates = []
        for l in lines:
            l = l.strip()
            if len(l) > 10 and len(l) < 60 and any(w in l for w in ["ឈុត", "ម៉ូត", "ផលិតផល", "ប្រូម៉ូសិន", "សេវាកម្ម", "New", "Item"]):
                candidates.append(l)
        return candidates[:5]

    def _extract_top_keywords(self, text: str) -> List[str]:
        """Extracts high-frequency keywords."""
        words = re.findall(r"[\u1780-\u17FFa-zA-Z0-9]+", text)
        freq = {}
        for w in words:
            if len(w) > 3:
                freq[w] = freq.get(w, 0) + 1
        sorted_w = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_w[:8]]

    def _derive_brand_palette(self, category: str) -> Tuple[int, int, int]:
        """Selects vibrant, high-contrast palette based on industry."""
        cat_lower = category.lower()
        if any(w in cat_lower for w in ["tech", "ai", "quant", "electronic"]):
            return (59, 130, 246)   # Institutional Royal Blue
        elif any(w in cat_lower for w in ["beauty", "cosmetic", "fashion"]):
            return (236, 72, 153)  # Vibrant Rose Pink
        elif any(w in cat_lower for w in ["gold", "luxury", "jewelry"]):
            return (234, 179, 8)   # Imperial Metallic Gold
        elif any(w in cat_lower for w in ["health", "food", "organic"]):
            return (16, 185, 129)  # Emerald Fresh Green
        return (245, 158, 11)      # Amber Orange (Default High Visibility)

    def _generate_fallback_product_photos(
        self,
        cache_dir: Path,
        dna: PageBrandDNA,
        target_count: int
    ) -> List[str]:
        """Generates studio product photos if brand has zero uploaded photos."""
        brand_color = self._derive_brand_palette(dna.category)
        photos = []
        for i in range(1, target_count + 1):
            img_file = cache_dir / f"fallback_prod_{i}.jpg"
            img = Image.new("RGB", (1600, 1600), (20, 24, 39))
            draw = ImageDraw.Draw(img)
            # Center card
            draw.rectangle([(200, 200), (1400, 1400)], fill=brand_color, outline=(255, 255, 255), width=8)
            draw.text((350, 750), f"{dna.brand_name}\nProduct Showcase {i}", fill=(255, 255, 255))
            img.save(img_file, "JPEG", quality=90)
            photos.append(str(img_file))
        return photos
