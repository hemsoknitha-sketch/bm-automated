"""
==============================================================================
🚀 AUTONOMOUS COMMENT & MESSENGER LEAD CONVERSION AGENT
==============================================================================
24/7 AI Customer Engagement & Lead Conversion Hub for Facebook Boosted Posts.
Functions:
1. Scans incoming comments on boosted posts in real-time
2. NLP Intent Classification (Price Inquiry, How to Buy, General Praise, Spam)
3. Immediate friendly public comment reply (within 5 seconds)
4. Instant Private Messenger DM conversion via Meta Graph API
5. Automated Spam Shield (Hides or deletes offensive/scam comments)
==============================================================================
"""

import re
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import joblib

try:
    from .fb_confluence_matrix import FBChatLeadConfluenceMatrix, get_chat_lead_confluence_matrix
except (ImportError, ValueError):
    from fb_confluence_matrix import FBChatLeadConfluenceMatrix, get_chat_lead_confluence_matrix

logger = logging.getLogger("BM_AUTOMATED.CommentAgent")


@dataclass
class CommentActionReport:
    comment_id: str
    post_id: str
    user_name: str
    message: str
    intent: str               # "PRICE_INQUIRY", "HOW_TO_ORDER", "SPAM_OR_SCAM", "GENERAL"
    public_reply_sent: str
    private_dm_sent: bool
    is_hidden_spam: bool
    confluence_analysis: Optional[Dict[str, Any]] = None
    processed_at: float = field(default_factory=time.time)


class AutoCommentResponder:
    """
    Autonomous agent that interacts with Facebook post comments to maximize lead capture
    and conversion rates while maintaining 100% brand safety.
    """

    # Keyword patterns for intent detection (Khmer & English)
    PRICE_PATTERNS = [
        r"តម្លៃ", r"ប៉ុន្មាន", r"ថ្លៃ", r"price", r"cost", r"how\s*much", r"\$", r"តំលៃ"
    ]
    ORDER_PATTERNS = [
        r"ចង់ទិញ", r"inbox", r"ទិញ", r"order", r"buy", r"interested", r"join", r"សុំពត៌មាន", r"ព័ត៌មាន"
    ]
    SPAM_PATTERNS = [
        r"crypto\s*giveaway", r"t\.me/", r"whatsapp", r"free\s*bitcoin", r"hack", r"adult", r"18\+"
    ]

    def __init__(self, api_client=None, business_profile: Optional[Dict[str, Any]] = None):
        self.api_client = api_client
        self.processed_comment_ids = set()
        self.recent_actions: List[CommentActionReport] = []
        self.lead_confluence_matrix = get_chat_lead_confluence_matrix()
        self.intent_model = None
        
        # Default Business Profile for Quick Close
        self.business_profile = {
            "page_name": "Angkor Quant Store",
            "aba_account": "000 888 999 (HEM SINATH)",
            "phone": "012 345 678 / 098 765 432",
            "delivery_info": "Free delivery ភ្នំពេញ (ដឹកជញ្ជូនរហ័ស ២៤ ម៉ោង) | ខេត្ត $1.50",
            "promo_text": "ប្រូម៉ូសិនបញ្ចុះតម្លៃ 20% + ធានាគុណភាព 100% រយៈពេល ៣០ ថ្ងៃ!",
            "order_link": "https://m.me/act_page_khmer_quant"
        }
        if business_profile:
            self.business_profile.update(business_profile)

        model_path = Path(__file__).resolve().parent / "models" / "fb_chat_intent_classifier.pkl"
        if model_path.exists():
            try:
                self.intent_model = joblib.load(model_path)
                logger.info(f"Loaded ML Intent Classifier from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ML Intent Classifier ({e})")

    def update_business_profile(self, new_profile: Dict[str, Any]):
        """Updates live business closing templates."""
        self.business_profile.update(new_profile)
        logger.info(f"Updated Business Profile: {self.business_profile.get('page_name')}")

    def classify_intent(self, comment_text: str) -> str:
        """Determines the user intent from comment text using ML and rule patterns."""
        txt = comment_text.lower().strip()

        # 1. Rule-based spam check (Brand Safety First)
        for pat in self.SPAM_PATTERNS:
            if re.search(pat, txt, re.IGNORECASE):
                return "SPAM_OR_SCAM"

        # 2. ML Intent Classifier inference if available
        if self.intent_model:
            try:
                pred = self.intent_model.predict([txt])[0]
                if pred == "SPAM_SCAM":
                    return "SPAM_OR_SCAM"
                elif pred == "FAST_CHECKOUT":
                    return "HOW_TO_ORDER"
                elif pred == "PRICE_INQUIRY":
                    return "PRICE_INQUIRY"
                elif pred in ("DELIVERY_INQUIRY", "PRODUCT_DETAILS"):
                    return "PRICE_INQUIRY"
            except Exception as e:
                logger.debug(f"ML intent inference fallback: {e}")

        # 3. Rule pattern fallback
        for pat in self.PRICE_PATTERNS:
            if re.search(pat, txt, re.IGNORECASE):
                return "PRICE_INQUIRY"

        for pat in self.ORDER_PATTERNS:
            if re.search(pat, txt, re.IGNORECASE):
                return "HOW_TO_ORDER"

        return "GENERAL"

    def process_comment(self, comment_id: str, post_id: str, user_name: str, message: str) -> CommentActionReport:
        """
        Evaluates a comment, generates smart responses, and triggers Meta Graph API actions.
        """
        intent = self.classify_intent(message)
        public_reply = ""
        private_dm = False
        is_hidden = False

        # 10-Group Confluence Lead Analysis
        mock_history = [{"sender": "user", "text": message, "timestamp": time.time()}]
        confluence_res = self.lead_confluence_matrix.compute_chat_lead_confluence(mock_history)

        if intent == "SPAM_OR_SCAM":
            # Auto-hide spam comments
            is_hidden = True
            if self.api_client and not self.api_client.is_mock:
                self.api_client.hide_comment(comment_id)
            logger.warning(f"🛡️ [SPAM SHIELD] Hidden spam comment from {user_name}: {message}")

        elif intent in ("PRICE_INQUIRY", "HOW_TO_ORDER") or confluence_res.get("lead_score", 0) >= 45.0:
            aba = self.business_profile.get("aba_account", "000 888 999")
            phone = self.business_profile.get("phone", "012 345 678")
            deliv = self.business_profile.get("delivery_info", "Free delivery ភ្នំពេញ")
            promo = self.business_profile.get("promo_text", "បញ្ចុះតម្លៃពិសេស 20%")

            if confluence_res.get("stage") == "HOT_VIP_BUYER" or intent == "HOW_TO_ORDER":
                public_reply = f"សួស្តីបង {user_name}! 🙏 ខ្ញុំបានផ្ញើតម្លៃពិសេស VIP និងទម្រង់កក់ទំនិញ Free សេវាដឹកជូនក្នុង Inbox រួចហើយបាទ! 🚀"
                dm_text = (
                    f"សួស្តីបង {user_name}! 🎉 ឃើញថាបងចាប់អារម្មណ៍ខ្លាំង!\n"
                    f"🎁 {promo}\n"
                    f"🚚 សេវាដឹកជញ្ជូន៖ {deliv}\n"
                    f"💳 លេខកុង ABA វេរប្រាក់៖ {aba}\n"
                    f"📞 ទូរស័ព្ទទាក់ទងបន្ទាន់៖ {phone}\n"
                    f"👉 បងអាចផ្ញើ (ឈ្មោះ + លេខទូរស័ព្ទ + ទីតាំង) មកទីនេះដើម្បីឱ្យក្រុមការងាររៀបចំឥវ៉ាន់ជូនភ្លាមៗបាទ! 📦✨"
                )
            else:
                public_reply = f"សួស្តីបង {user_name}! អរគុណសម្រាប់ការចាប់អារម្មណ៍ 🙏 ខ្ញុំបានផ្ញើព័ត៌មានលម្អិត និងប្រូម៉ូសិនជូនក្នុង Messenger Inbox រួចរាល់ហើយបាទ! 📩"
                dm_text = (
                    f"សួស្តីបង {user_name}! អរគុណសម្រាប់ការចាប់អារម្មណ៍លើផលិតផលយើងខ្ញុំ 🙏\n"
                    f"✨ {promo}\n"
                    f"🚚 សេវាដឹកជញ្ជូន៖ {deliv}\n"
                    f"📞 លេខទូរស័ព្ទ៖ {phone}\n"
                    f"បងអាចសាកសួរព័ត៌មានបន្ថែម ឬសុំរូបភាពផ្ទាល់បានបាទ! 🚀"
                )

            private_dm = True

            if self.api_client:
                # 1. Public Reply
                self.api_client.reply_to_comment(comment_id, public_reply)
                # 2. Private Message
                self.api_client.send_private_reply_to_comment(comment_id, dm_text)

            logger.info(f"⚡ [LEAD CAPTURED] Auto-responded to {user_name} ({intent}, Score: {confluence_res.get('lead_score')})")

        else:
            public_reply = f"សួស្តីបង {user_name}! អរគុណច្រើនសម្រាប់ការគាំទ្រ និងការបញ្ចេញមតិ! សូមជូនពរឱ្យសំណាងល្អ និងជោគជ័យគ្រប់ភារកិច្ច! ❤️✨"
            if self.api_client:
                self.api_client.reply_to_comment(comment_id, public_reply)

        self.processed_comment_ids.add(comment_id)

        report = CommentActionReport(
            comment_id=comment_id,
            post_id=post_id,
            user_name=user_name,
            message=message,
            intent=intent,
            public_reply_sent=public_reply,
            private_dm_sent=private_dm,
            is_hidden_spam=is_hidden,
            confluence_analysis=confluence_res
        )
        self.recent_actions.insert(0, report)
        if len(self.recent_actions) > 50:
            self.recent_actions.pop()

        return report

    def poll_and_respond_comments(self, limit_posts: int = 5) -> List[CommentActionReport]:
        """
        Polls connected Facebook Page for recent comments, identifies unprocessed ones,
        and auto-responds with public replies and private Messenger DMs.
        """
        if not self.api_client:
            logger.warning("No API client available for comment polling.")
            return []

        all_comments = self.api_client.get_recent_page_comments(limit_posts=limit_posts)
        reports = []
        for comm in all_comments:
            c_id = comm.get("id")
            if not c_id or c_id in self.processed_comment_ids:
                continue

            user_name = comm.get("from", {}).get("name", "អតិថិជន")
            msg = comm.get("message", "")
            post_id = comm.get("post_id", "feed_post")
            report = self.process_comment(
                comment_id=c_id,
                post_id=post_id,
                user_name=user_name,
                message=msg
            )
            reports.append(report)

        logger.info(f"🤖 [COMMENT PATROL] Scanned {len(all_comments)} comments, executed {len(reports)} auto-responses.")
        return reports

    def handle_incoming_messenger_message(
        self,
        sender_psid: str,
        sender_name: str,
        message_text: str
    ) -> Dict[str, Any]:
        """
        Autonomous Messenger Chat Closer for 1-on-1 customer conversations.
        Classifies intent, navigates 5-Point Harmonic Buyer Journey, and sends closing response.
        """
        intent = self.classify_intent(message_text)
        mock_history = [{"sender": "user", "text": message_text, "timestamp": time.time()}]
        confluence_res = self.lead_confluence_matrix.compute_chat_lead_confluence(mock_history)
        lead_score = confluence_res.get("lead_score", 50.0)
        stage = confluence_res.get("stage", "STAGE_ENGAGEMENT")

        aba = self.business_profile.get("aba_account", "000 888 999")
        phone = self.business_profile.get("phone", "012 345 678")
        deliv = self.business_profile.get("delivery_info", "Free delivery ភ្នំពេញ")
        promo = self.business_profile.get("promo_text", "បញ្ចុះតម្លៃពិសេស 20%")

        quick_replies = []
        reply_text = ""

        if intent in ("FAST_CHECKOUT", "HOW_TO_ORDER") or stage == "HOT_VIP_BUYER":
            reply_text = (
                f"សួស្តីបង {sender_name}! 🎉 សូមអរគុណសម្រាប់ការសម្រេចចិត្តទិញ!\n\n"
                f"💳 លេខគណនី ABA៖\n👉 *{aba}*\n\n"
                f"📦 បងអាចផ្ញើវិក្កយបត្រវេរប្រាក់ រួមជាមួយ៖\n"
                f"1. ឈ្មោះអ្នកទទួល\n"
                f"2. លេខទូរស័ព្ទ\n"
                f"3. ទីតាំងដឹកជញ្ជូនជាក់លាក់\n\n"
                f"🚚 {deliv}\nក្រុមការងារនឹងខ្ចប់ និងដឹកជូនភ្លាមៗបាទ! 🚀"
            )
            quick_replies = [
                {"title": "ផ្ញើទីតាំងដឹក", "payload": "SEND_LOCATION"},
                {"title": "ទាក់ទងទូរស័ព្ទ", "payload": "CALL_HOTLINE"}
            ]

        elif intent == "PRICE_INQUIRY":
            reply_text = (
                f"សួស្តីបង {sender_name}! 🙏 សម្រាប់តម្លៃពិសេសថ្ងៃនេះ៖\n\n"
                f"🔥 {promo}\n"
                f"🚚 {deliv}\n"
                f"🎁 ធានាគុណភាពពេញចិត្ត ១០០% និងមានការធានារយៈពេល ៣០ ថ្ងៃ!\n\n"
                f"តើបងចង់កក់ទុករៀបចំដឹកជូនថ្ងៃនេះតែម្តងទេបាទ? 😊"
            )
            quick_replies = [
                {"title": "យក ១ ឈុត", "payload": "ORDER_1"},
                {"title": "សុំលេខកុង ABA", "payload": "REQ_ABA"},
                {"title": "សេវាដឹកជញ្ជូន?", "payload": "REQ_DELIVERY"}
            ]

        elif intent == "DELIVERY_INQUIRY":
            reply_text = (
                f"សួស្តីបង {sender_name}! 🚚 {deliv}\n\n"
                f"• ក្នុងរាជធានីភ្នំពេញ៖ ដឹកជញ្ជូនរហ័សក្នុងថ្ងៃតែម្តង (២ ទៅ ៤ ម៉ោង)!\n"
                f"• បណ្តាខេត្តទាំង ២៥៖ ផ្ញើតាមឡានឈ្នួល/វីរៈប៊ុនថាំ រយៈពេល ១-២ ថ្ងៃបានដល់ដៃបង!\n"
                f"តើបងចង់ឱ្យដឹកទៅកាន់ទីតាំងណាដែរទាន? 📍"
            )
            quick_replies = [
                {"title": "ភ្នំពេញ", "payload": "LOC_PHNOM_PENH"},
                {"title": "តាមខេត្ត", "payload": "LOC_PROVINCE"},
                {"title": "កម្ម៉ង់ភ្លាមៗ", "payload": "FAST_ORDER"}
            ]

        elif intent == "SPAM_OR_SCAM":
            reply_text = "សូមអរគុណ! ប្រព័ន្ធបានកត់ត្រាសាររួចរាល់ហើយ។"

        else: # GENERAL
            reply_text = (
                f"សួស្តីបង {sender_name}! 🙏 សូមស្វាគមន៍មកកាន់ {self.business_profile.get('page_name')}!\n\n"
                f"តើខ្ញុំអាចជួយសម្រួលព័ត៌មានអ្វីខ្លះជូនបងដែរទាន? 💡\n"
                f"📞 ផ្នែកបម្រើអតិថិជន៖ {phone}"
            )
            quick_replies = [
                {"title": "សុំមើលតម្លៃ", "payload": "SEE_PRICES"},
                {"title": "ប្រូម៉ូសិនថ្ងៃនេះ", "payload": "SEE_PROMOS"},
                {"title": "កម្ម៉ង់ទំនិញ", "payload": "ORDER_NOW"}
            ]

        # Send via API if available
        if self.api_client:
            self.api_client.send_page_message(sender_psid, reply_text, quick_replies)

        return {
            "sender_psid": sender_psid,
            "sender_name": sender_name,
            "intent": intent,
            "lead_score": lead_score,
            "stage": stage,
            "reply_text": reply_text,
            "quick_replies": quick_replies,
            "timestamp": time.time()
        }

    def evaluate_messenger_thread(self, messages_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates full multi-turn Messenger thread with FBChatLeadConfluenceMatrix."""
        return self.lead_confluence_matrix.compute_chat_lead_confluence(messages_history)

    def get_fibonacci_followup(self, elapsed_hours: float, customer_name: str = "បង") -> Optional[Dict[str, Any]]:
        """Generates automated follow-up at Fibonacci time nodes (1h, 3h, 8h, 21h)."""
        return self.lead_confluence_matrix.get_fibonacci_followup_message(elapsed_hours, customer_name)

