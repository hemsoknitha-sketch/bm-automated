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

    def __init__(self, api_client=None):
        self.api_client = api_client
        self.processed_comment_ids = set()
        self.lead_confluence_matrix = get_chat_lead_confluence_matrix()
        self.intent_model = None
        model_path = Path(__file__).resolve().parent / "models" / "fb_chat_intent_classifier.pkl"
        if model_path.exists():
            try:
                self.intent_model = joblib.load(model_path)
                logger.info(f"Loaded ML Intent Classifier from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ML Intent Classifier ({e})")

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
            if confluence_res.get("stage") == "HOT_VIP_BUYER":
                public_reply = f"សួស្តីបង {user_name}! 🙏 ខ្ញុំបានផ្ញើតម្លៃពិសេស VIP និងទម្រង់កក់ទំនិញ Free សេវាដឹកជូនក្នុង Inbox រួចហើយបាទ! 🚀"
                dm_text = f"សួស្តីបង {user_name}! 🎉 ឃើញថាបងចាប់អារម្មណ៍ខ្លាំង ខ្ញុំសូមជូនប្រូម៉ូសិន VIP Free សេវាដឹកជញ្ជូន និងលេខកុង ABA ជូនបងភ្លាមៗបាទ! សូមឆែកមើលព័ត៌មានខាងក្រោម:"
            else:
                public_reply = f"សួស្តីបង {user_name}! អរគុណសម្រាប់ការចាប់អារម្មណ៍ 🙏 ខ្ញុំបានផ្ញើព័ត៌មានលម្អិត និងប្រូម៉ូសិនជូនក្នុង Messenger Inbox រួចរាល់ហើយបាទ! 📩"
                dm_text = f"សួស្តីបង {user_name}! អរគុណសម្រាប់ការចាប់អារម្មណ៍។ សូមចុចតំណភ្ជាប់ខាងក្រោមដើម្បីមើលតម្លៃ និងរបៀបកម្ម៉ង់ភ្លាមៗបាទ! 🚀"

            private_dm = True

            if self.api_client and not self.api_client.is_mock:
                # 1. Public Reply
                self.api_client.reply_to_comment(comment_id, public_reply)
                # 2. Private Message
                self.api_client.send_private_reply_to_comment(comment_id, dm_text)

            logger.info(f"⚡ [LEAD CAPTURED] Auto-responded to {user_name} ({intent}, Score: {confluence_res.get('lead_score')})")

        else:
            public_reply = f"សួស្តីបង {user_name}! អរគុណច្រើនសម្រាប់ការគាំទ្រ និងការបញ្ចេញមតិ! សូមជូនពរឱ្យសំណាងល្អ និងជោគជ័យគ្រប់ភារកិច្ច! ❤️✨"
            if self.api_client and not self.api_client.is_mock:
                self.api_client.reply_to_comment(comment_id, public_reply)

        self.processed_comment_ids.add(comment_id)

        return CommentActionReport(
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

    def evaluate_messenger_thread(self, messages_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates full multi-turn Messenger thread with FBChatLeadConfluenceMatrix."""
        return self.lead_confluence_matrix.compute_chat_lead_confluence(messages_history)

    def get_fibonacci_followup(self, elapsed_hours: float, customer_name: str = "បង") -> Optional[Dict[str, Any]]:
        """Generates automated follow-up at Fibonacci time nodes (1h, 3h, 8h, 21h)."""
        return self.lead_confluence_matrix.get_fibonacci_followup_message(elapsed_hours, customer_name)

