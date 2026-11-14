"""
==============================================================================
🚀 VIRAL SPIKE & ORGANIC ENGAGEMENT VELOCITY DETECTOR
==============================================================================
Institutional Real-Time Momentum Engine for Facebook Page Posts.
Mathematically detects viral breakout dynamics within the first 15-120 minutes
after publishing, using weighted engagement velocity, shares-to-likes ratios,
and Hawkes process self-excitation proxies.
==============================================================================
"""

import math
import logging
from dataclasses import dataclass
from typing import Dict, Any
from .meta_graph_api import FacebookPost

logger = logging.getLogger("BM_AUTOMATED.ViralDetector")


@dataclass
class PostEngagementVelocity:
    post_id: str
    elapsed_minutes: float
    raw_engagement_points: float
    velocity_per_minute: float
    shares_ratio: float
    comments_ratio: float
    viral_score: float  # Normalized 0.0 to 100.0
    classification: str  # "VIRAL_EXPLOSION", "STRONG_TRACTION", "NORMAL_ORGANIC", "LOW_MOMENTUM"
    should_boost: bool
    reason: str


class ViralSpikeDetector:
    """
    Evaluates organic Facebook Page posts to detect viral velocity and algorithm favorability.
    Filters out dead posts and isolates high-converting viral winners for ad budget amplification.
    """

    # Engagement weights reflecting Meta's organic algorithm ranking
    WEIGHT_LIKE = 1.0
    WEIGHT_COMMENT = 3.5  # Comments indicate deep discussion and community engagement
    WEIGHT_SHARE = 6.0    # Shares are the #1 catalyst for algorithmic distribution
    WEIGHT_VIDEO_VIEW = 0.05

    def __init__(self, min_viral_threshold: float = 70.0):
        self.min_viral_threshold = min_viral_threshold

    def analyze_post(self, post: FacebookPost) -> PostEngagementVelocity:
        """
        Computes the multi-factor viral momentum score for a given Facebook post.
        """
        elapsed_min = max(5.0, post.elapsed_minutes)

        # 1. Raw weighted engagement points
        raw_pts = (
            post.likes * self.WEIGHT_LIKE +
            post.comments * self.WEIGHT_COMMENT +
            post.shares * self.WEIGHT_SHARE +
            post.video_views * self.WEIGHT_VIDEO_VIEW
        )

        # 2. Velocity per minute (with logarithmic dampening for older posts)
        # Newer posts get higher sensitivity to early acceleration
        time_factor = math.pow(elapsed_min / 60.0 + 1.0, 0.45)
        velocity = (raw_pts / elapsed_min) * (1.0 / time_factor)

        # 3. Structural Viral Ratios
        shares_ratio = post.shares / max(1.0, float(post.likes))
        comments_ratio = post.comments / max(1.0, float(post.likes))

        # 4. Hawkes Process Branching Factor Proxy
        # If shares ratio > 0.15, viral self-excitation is occurring
        branching_boost = 1.0
        if shares_ratio >= 0.30:
            branching_boost += 0.40  # Massive organic compounding
        elif shares_ratio >= 0.15:
            branching_boost += 0.20

        # High comment density boost
        if comments_ratio >= 0.20:
            branching_boost += 0.15

        # 5. Composite Viral Score (0.0 to 100.0)
        # Calibrated so that standard post scores 20-45, strong post 65-79, breakout post 80+
        base_score = 50.0 * (1.0 - math.exp(-velocity * 0.45))
        ratio_score = min(35.0, (shares_ratio * 70.0 + comments_ratio * 30.0))
        reach_efficiency = min(15.0, (raw_pts / max(100.0, float(post.reach))) * 150.0)

        composite_score = (base_score + ratio_score + reach_efficiency) * branching_boost
        composite_score = round(min(100.0, max(0.0, composite_score)), 2)

        # 6. Classification & Decision
        if composite_score >= 80.0:
            classification = "VIRAL_EXPLOSION"
            should_boost = True
            reason = f"Breakout viral velocity ({velocity:.2f}/min) with high share multiplier ({shares_ratio:.2f})."
        elif composite_score >= self.min_viral_threshold:
            classification = "STRONG_TRACTION"
            should_boost = True
            reason = f"Strong organic momentum ({composite_score}/100) exceeding boost threshold."
        elif composite_score >= 45.0:
            classification = "NORMAL_ORGANIC"
            should_boost = False
            reason = "Steady organic engagement but below threshold for paid ad amplification."
        else:
            classification = "LOW_MOMENTUM"
            should_boost = False
            reason = "Low initial traction; paid ad spend would suffer high CPA."

        return PostEngagementVelocity(
            post_id=post.post_id,
            elapsed_minutes=round(elapsed_min, 1),
            raw_engagement_points=round(raw_pts, 1),
            velocity_per_minute=round(velocity, 2),
            shares_ratio=round(shares_ratio, 3),
            comments_ratio=round(comments_ratio, 3),
            viral_score=composite_score,
            classification=classification,
            should_boost=should_boost,
            reason=reason
        )

