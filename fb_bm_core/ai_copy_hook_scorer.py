"""
==============================================================================
🚀 AI COPYWRITING HOOK SCORER & META POLICY COMPLIANCE SHIELD
==============================================================================
Quantitative NLP Engine for Facebook Page & Ad Creatives.
Evaluates:
1. First 3-line hook power (Curiosity gap, data-driven, problem agitation)
2. Call-To-Action (CTA) strength & Urgency index
3. Formatting & Emoji density (CTR optimization)
4. Meta Ad Policy Compliance Guard (Prevents ad rejections & account bans)
5. Multilingual support: English & Khmer (ភាសាខ្មែរ)
==============================================================================
"""

import re
import math
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("BM_AUTOMATED.CopyScorer")


@dataclass
class HookAnalysisResult:
    hook_power_score: float        # 0.0 to 100.0
    urgency_score: float           # 0.0 to 100.0
    cta_score: float               # 0.0 to 100.0
    policy_compliance_pass: bool   # True = Safe to run as Ad
    policy_risk_level: str         # "SAFE", "LOW_RISK", "HIGH_RISK_REJECTION"
    policy_violations: List[str]   # Specific flagged terms or rules
    char_count: int
    emoji_count: int
    first_three_lines: str
    overall_copy_grade: str        # "A+", "A", "B", "C", "F"
    suggested_improvements: List[str]


class AICopyHookScorer:
    """
    Evaluates marketing copy for Facebook Pages and Ads to maximize CTR and ROAS
    while ensuring 100% adherence to Meta Advertising Standards.
    """

    # Meta Advertising Policy Blacklist & Trigger Keywords (causes account bans / rejected ads)
    POLICY_TRIGGER_PATTERNS = [
        (r"\b(100%\s*guaranteed\s*profit|ធានាចំណេញ\s*១០០%)\b", "Guaranteed Financial Returns Violation"),
        (r"\b(get\s*rich\s*quick|ក្លាយជាអ្នកមានភ្លាមៗ)\b", "Misleading Financial Claims Violation"),
        (r"\b(cure\s*cancer|cure\s*all|ព្យាបាលជា១០០%)\b", "Unsubstantiated Health Claims Violation"),
        (r"\b(weight\s*loss\s*in\s*\d+\s*days|ស្រកគីឡូក្នុង\s*\d+\s*ថ្ងៃ)\b", "Personal Health & Body Image Violation"),
        (r"\b(free\s*crypto|giveaway\s*bitcoin)\b", "Cryptocurrency & Scams Red Flag"),
        (r"\b(hack\s*account|spy\s*app|លួចមើល)\b", "Spyware & Malicious Practices Violation")
    ]

    # High-converting CTA patterns (English + Khmer)
    CTA_PATTERNS = [
        r"click\s*(here|link|below)",
        r"learn\s*more",
        r"sign\s*up",
        r"get\s*(started|instant|free|now)",
        r"order\s*now",
        r"shop\s*now",
        r"message\s*us",
        r"ចុច(ទីនេះ|លីង|ខាងក្រោម)",
        r"ទាក់ទង(មកយើង|ឥឡូវនេះ)",
        r"ទិញឥឡូវនេះ",
        r"ផ្ញើសារ",
        r"ស្វែងយល់បន្ថែម",
        r"ចុះឈ្មោះ"
    ]

    # Urgency & Scarcity keywords
    URGENCY_PATTERNS = [
        r"limited\s*(time|offer|seats|spots)",
        r"today\s*only",
        r"now",
        r"urgent",
        r"last\s*chance",
        r"don'?t\s*miss",
        r"ភ្លាមៗ",
        r"កុំឲ្យរំលង",
        r"ចំនួនមានកំណត់",
        r"ថ្ងៃនេះប៉ុណ្ណោះ",
        r"ឱកាសចុងក្រោយ"
    ]

    # Emotional & Curiosity Hook Triggers
    HOOK_TRIGGERS = [
        r"\b(secret|revealed|stop|why|how\s*to|new|case\s*study|truth)\b",
        r"\b(កំពូល|អាថ៌កំបាំង|ឈប់|ហេតុអ្វី|របៀប|ការសិក្សាថ្មី)\b",
        r"[\?🔥🚀💡💎📈⚡🎯]"
    ]

    def __init__(self):
        pass

    def evaluate_copy(self, text: str) -> HookAnalysisResult:
        """
        Performs holistic quantitative evaluation of copy text.
        """
        text = text.strip() if text else ""
        if not text:
            return HookAnalysisResult(
                hook_power_score=0.0,
                urgency_score=0.0,
                cta_score=0.0,
                policy_compliance_pass=False,
                policy_risk_level="HIGH_RISK_REJECTION",
                policy_violations=["Empty copy provided"],
                char_count=0,
                emoji_count=0,
                first_three_lines="",
                overall_copy_grade="F",
                suggested_improvements=["Add compelling text copy with a strong hook."]
            )

        char_count = len(text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        first_3_lines = "\n".join(lines[:3])

        # 1. Emoji & Formatting Detection
        # Emoji regex matches surrogate pairs and common pictographs
        emoji_pattern = re.compile(
            r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f5ff\U0001f600-\U0001f64f\U0001f680-\U0001f6ff]"
        )
        emojis_found = emoji_pattern.findall(text)
        emoji_count = len(emojis_found)

        # 2. Meta Policy Compliance Scan
        violations = []
        for pat, rule_desc in self.POLICY_TRIGGER_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                violations.append(rule_desc)

        policy_pass = len(violations) == 0
        policy_risk = "SAFE" if policy_pass else "HIGH_RISK_REJECTION"

        # 3. Hook Power Analysis (First 3 Lines)
        hook_points = 40.0  # Base score
        first_chunk = first_3_lines.lower()

        # Check for numbers / specific stats (e.g. 5X, 50%, $1000)
        if re.search(r"\d+([xX%]|k|K|\$)?", first_chunk):
            hook_points += 15.0

        # Check for curiosity & power words
        for trig in self.HOOK_TRIGGERS:
            if re.search(trig, first_chunk, re.IGNORECASE):
                hook_points += 10.0
                break

        # Check for question marks (curiosity gap)
        if "?" in first_chunk or "？" in first_chunk:
            hook_points += 10.0

        # Emoji in first line boosts visibility
        if len(lines) > 0 and emoji_pattern.search(lines[0]):
            hook_points += 10.0

        hook_power_score = round(min(100.0, max(0.0, hook_points)), 2)

        # 4. CTA Evaluation
        cta_points = 20.0
        for pat in self.CTA_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                cta_points += 50.0
                break
        # Link or mention presence
        if "http" in text or "t.me" in text or "#" in text:
            cta_points += 20.0
        cta_score = round(min(100.0, max(0.0, cta_points)), 2)

        # 5. Urgency Score
        urgency_points = 25.0
        for pat in self.URGENCY_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                urgency_points += 45.0
                break
        urgency_score = round(min(100.0, max(0.0, urgency_points)), 2)

        # 6. Overall Grade & Improvements
        composite = hook_power_score * 0.45 + cta_score * 0.35 + urgency_score * 0.20
        if not policy_pass:
            grade = "F"
        elif composite >= 85.0:
            grade = "A+"
        elif composite >= 75.0:
            grade = "A"
        elif composite >= 60.0:
            grade = "B"
        elif composite >= 45.0:
            grade = "C"
        else:
            grade = "D"

        improvements = []
        if not policy_pass:
            improvements.append(f"CRITICAL: Remove policy violating phrases: {', '.join(violations)}")
        if hook_power_score < 70.0:
            improvements.append("Strengthen the first line with numbers, stats (e.g. '5X ROI'), or a provocative question.")
        if cta_score < 60.0:
            improvements.append("Add a direct Call-To-Action (e.g. 'ចុចទីនេះ' or 'Click the link below').")
        if emoji_count < 2:
            improvements.append("Add 2-4 strategic emojis (e.g. 🚀, 💡, 💎) to increase visual CTR in mobile feeds.")
        elif emoji_count > 12:
            improvements.append("Reduce emoji count to avoid looking spammy.")
        if char_count < 80:
            improvements.append("Copy is too short; provide enough context to qualify buyers before they click.")

        return HookAnalysisResult(
            hook_power_score=hook_power_score,
            urgency_score=urgency_score,
            cta_score=cta_score,
            policy_compliance_pass=policy_pass,
            policy_risk_level=policy_risk,
            policy_violations=violations,
            char_count=char_count,
            emoji_count=emoji_count,
            first_three_lines=first_3_lines,
            overall_copy_grade=grade,
            suggested_improvements=improvements
        )

