from collections import deque
from statistics import mean
from typing import Any, Dict, List
import os
import json

import cv2
import numpy as np


class AgenticDecisionMaker:
    """
    Multi-agent decision orchestrator that fuses specialized risk agents.
    Designed for free-tier/offline operation with deterministic behavior.
    """

    def __init__(self, history_size: int = 12):
        self.risk_history = deque(maxlen=history_size)
        self.person_history = deque(maxlen=history_size)
        self.motion_history = deque(maxlen=history_size)
        self.centroid_history = deque(maxlen=history_size)
        self.prev_gray = None
        self.environment_profile = os.getenv("SAFETY_ENV", "campus").lower()

        # Class-level priors for dangerous objects in public safety monitoring.
        self.object_risk_weights = {
            "knife": 55,
            "scissors": 40,
            "gun": 75,
            "baseball bat": 30,
            "bottle": 18,
        }
        self.profile_thresholds = {
            "campus": {"medium": 42, "high": 62, "critical": 78},
            "workspace": {"medium": 40, "high": 60, "critical": 75},
            "public": {"medium": 45, "high": 65, "critical": 80},
        }
        self._load_calibrated_thresholds()

    def _load_calibrated_thresholds(self) -> None:
        """Load calibrated thresholds from disk if available."""
        calibration_path = os.getenv("SAFETY_THRESHOLDS_FILE", "calibrated_thresholds.json")
        if not os.path.exists(calibration_path):
            return
        try:
            with open(calibration_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for env_name, thresholds in data.items():
                    if not isinstance(thresholds, dict):
                        continue
                    medium = thresholds.get("medium")
                    high = thresholds.get("high")
                    critical = thresholds.get("critical")
                    if all(isinstance(v, (int, float)) for v in [medium, high, critical]):
                        self.profile_thresholds[env_name] = {
                            "medium": float(medium),
                            "high": float(high),
                            "critical": float(critical),
                        }
        except Exception:
            # Fall back to safe defaults when calibration file is malformed.
            pass

    def _object_risk_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        threats: List[str] = context.get("threats", [])
        score = 0.0
        reasons: List[str] = []
        for item in threats:
            weight = self.object_risk_weights.get(item, 20)
            score += weight
            reasons.append(f"object:{item}")
        return {
            "name": "object_risk_agent",
            "score": min(score, 100.0),
            "reasons": reasons,
        }

    def _pose_risk_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        distress_score = float(context.get("distress_score", 0.0))
        distress_signals: List[str] = context.get("distress_signals", [])
        scaled = min(100.0, distress_score * 1.15)
        reasons = [f"pose:{signal}" for signal in distress_signals]
        return {
            "name": "pose_risk_agent",
            "score": scaled,
            "reasons": reasons,
        }

    def _crowd_behavior_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        persons_count = int(context.get("persons_count", 0))
        crowd_score = 0.0
        reasons: List[str] = []
        if persons_count >= 6:
            crowd_score = 35
            reasons.append("crowd:dense")
        elif persons_count >= 4:
            crowd_score = 18
            reasons.append("crowd:group")
        return {
            "name": "crowd_behavior_agent",
            "score": crowd_score,
            "reasons": reasons,
        }

    def _motion_behavior_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        frame = context.get("frame")
        if frame is None:
            return {"name": "motion_behavior_agent", "score": 0.0, "reasons": []}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return {"name": "motion_behavior_agent", "score": 0.0, "reasons": []}

        diff = cv2.absdiff(self.prev_gray, gray)
        self.prev_gray = gray
        motion_energy = float(np.mean(diff))
        normalized = min(100.0, (motion_energy / 35.0) * 100.0)
        self.motion_history.append(normalized)

        reasons: List[str] = []
        if normalized >= 55:
            reasons.append("motion:high_activity")
        elif normalized >= 35:
            reasons.append("motion:elevated")

        return {
            "name": "motion_behavior_agent",
            "score": normalized,
            "reasons": reasons,
        }

    def _trajectory_memory_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        person_boxes = context.get("person_boxes", [])
        if not person_boxes:
            self.centroid_history.clear()
            return {"name": "trajectory_memory_agent", "score": 0.0, "reasons": []}

        centroids = [((x1 + x2) / 2.0, (y1 + y2) / 2.0) for (x1, y1, x2, y2) in person_boxes]
        current_center = (
            sum(c[0] for c in centroids) / len(centroids),
            sum(c[1] for c in centroids) / len(centroids),
        )
        self.centroid_history.append(current_center)
        if len(self.centroid_history) < 3:
            return {"name": "trajectory_memory_agent", "score": 0.0, "reasons": []}

        prev_center = self.centroid_history[-2]
        displacement = float(np.hypot(current_center[0] - prev_center[0], current_center[1] - prev_center[1]))
        # Scale displacement at webcam resolution into a soft risk score.
        score = min(100.0, displacement * 1.6)
        reasons: List[str] = []
        if score >= 40:
            reasons.append("trajectory:rapid_group_shift")
        elif score >= 22:
            reasons.append("trajectory:group_movement")
        return {"name": "trajectory_memory_agent", "score": score, "reasons": reasons}

    def _temporal_consistency_agent(self, current_score: float) -> Dict[str, Any]:
        if len(self.risk_history) < 3:
            return {"name": "temporal_agent", "boost": 0.0, "reasons": []}

        recent_mean = mean(self.risk_history)
        trend_up = current_score >= recent_mean + 10
        sustained_high = recent_mean >= 55
        boost = 0.0
        reasons: List[str] = []

        if trend_up:
            boost += 8.0
            reasons.append("temporal:rising_risk")
        if sustained_high:
            boost += 12.0
            reasons.append("temporal:sustained_high")

        return {"name": "temporal_agent", "boost": boost, "reasons": reasons}

    def _policy_fusion_agent(self, fused_score: float, evidence: List[str]) -> Dict[str, Any]:
        thresholds = self.profile_thresholds.get(self.environment_profile, self.profile_thresholds["campus"])
        medium_thr = thresholds["medium"]
        high_thr = thresholds["high"]
        critical_thr = thresholds["critical"]

        if fused_score >= critical_thr:
            level = "CRITICAL"
            action = "alert"
            threat_type = "violence_or_weapon"
        elif fused_score >= high_thr:
            level = "HIGH"
            action = "alert"
            threat_type = "high_risk_behavior"
        elif fused_score >= medium_thr:
            level = "MEDIUM"
            action = "log"
            threat_type = "suspicious_behavior"
        else:
            level = "LOW"
            action = "ignore"
            threat_type = "none"

        return {
            "threat_detected": level in {"MEDIUM", "HIGH", "CRITICAL"},
            "threat_type": threat_type,
            "threat_level": level,
            "confidence": round(min(max(fused_score, 0.0), 100.0), 2),
            "action": action,
            "summary": ", ".join(evidence[:4]) if evidence else "no significant risk evidence",
            "reason_codes": evidence,
        }

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        object_vote = self._object_risk_agent(context)
        pose_vote = self._pose_risk_agent(context)
        crowd_vote = self._crowd_behavior_agent(context)
        motion_vote = self._motion_behavior_agent(context)
        trajectory_vote = self._trajectory_memory_agent(context)

        # Fusion weights tuned for harassment/violence detection prototype:
        # object signal is strongest, followed by pose, then motion/crowd/trajectory.
        weighted_score = (
            object_vote["score"] * 0.38
            + pose_vote["score"] * 0.28
            + motion_vote["score"] * 0.14
            + crowd_vote["score"] * 0.10
            + trajectory_vote["score"] * 0.10
        )

        temporal_vote = self._temporal_consistency_agent(weighted_score)
        fused_score = min(100.0, weighted_score + temporal_vote["boost"])

        evidence = (
            object_vote["reasons"]
            + pose_vote["reasons"]
            + motion_vote["reasons"]
            + crowd_vote["reasons"]
            + trajectory_vote["reasons"]
            + temporal_vote["reasons"]
        )
        decision = self._policy_fusion_agent(fused_score, evidence)
        decision["agent_scores"] = {
            "object_risk_agent": round(object_vote["score"], 2),
            "pose_risk_agent": round(pose_vote["score"], 2),
            "motion_behavior_agent": round(motion_vote["score"], 2),
            "crowd_behavior_agent": round(crowd_vote["score"], 2),
            "trajectory_memory_agent": round(trajectory_vote["score"], 2),
            "temporal_boost": round(temporal_vote["boost"], 2),
            "weighted_score": round(weighted_score, 2),
            "environment_profile": self.environment_profile,
        }

        self.risk_history.append(decision["confidence"])
        self.person_history.append(int(context.get("persons_count", 0)))
        return decision