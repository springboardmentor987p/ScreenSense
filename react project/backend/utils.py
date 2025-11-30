import os
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
from json import JSONEncoder

logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    return obj


class RecommendationEngine:
    def __init__(self, data_path: Optional[str] = None):
        # Locate CSV: explicit path -> DATA_CSV env var -> ./data.csv
        path = data_path or os.environ.get("DATA_CSV") or "data.csv"
        p = Path(path)
        try:
            self.df = pd.read_csv(p)
        except FileNotFoundError:
            logger.warning("Data file not found at %s — initializing empty DataFrame", p)
            self.df = pd.DataFrame()

    def recommended_limit(self, age: int) -> int:
        return 2 if 8 <= age <= 10 else 3

    def cohort_avg(self, column: str, value):
        if self.df.empty or column not in self.df.columns:
            return None
        filtered = self.df[self.df[column] == value]
        if filtered.empty:
            return None
        return filtered["Avg_Daily_Screen_Time_hr"].mean()

    def device_health_profile(self, health_issue: str):
        if not health_issue or self.df.empty:
            return {}

        profile = {}
        for device in self.df["Primary_Device"].dropna().unique():
            df_device = self.df[self.df["Primary_Device"] == device]
            if df_device.empty:
                continue
            ratio = (df_device["Health_Impacts"].str.contains(health_issue, case=False, na=False)).mean()
            profile[device] = round(ratio, 3)
        return profile

    def recommend_device_switch(self, current_device: str, health_issue: str):
        if not health_issue:
            return None

        profile = self.device_health_profile(health_issue)
        if not profile:
            return None

        best_device = min(profile, key=profile.get)
        if best_device != current_device:
            return f"Consider switching to {best_device}, which shows the lowest rate of '{health_issue}' in the dataset."
        return None

    def generate_insights(self, user: dict):
        age = user["Age"]
        avg_hours = user["Avg_Daily_Screen_Time_hr"]
        device = user["Primary_Device"]
        health = user.get("Health_Impacts", "")

        recommended = self.recommended_limit(age)
        exceeded = avg_hours > recommended
        diff = round(avg_hours - recommended, 2)

        age_avg = self.cohort_avg("Age", age)
        gender_avg = self.cohort_avg("Gender", user["Gender"])
        region_avg = self.cohort_avg("Urban_or_Rural", user["Urban_or_Rural"])
        device_avg = self.cohort_avg("Primary_Device", device)

        insights = []

        if exceeded:
            insights.append(
                f"Your child's average screen time ({avg_hours} hr/day) exceeds the recommended limit "
                f"of {recommended} hr/day by {diff} hours."
            )
        else:
            insights.append(
                f"Your child's screen time ({avg_hours} hr/day) is within the recommended limit of {recommended} hr/day."
            )

        if age_avg is not None:
            insights.append(f"Compared to kids of age {age}, your child watches {round(avg_hours - age_avg, 2)} hrs more/less.")

        if gender_avg is not None:
            insights.append(f"Compared to other {user['Gender']} kids, difference is {round(avg_hours - gender_avg, 2)} hrs.")

        if region_avg is not None:
            insights.append(
                f"Compared to {user['Urban_or_Rural']} kids, difference is {round(avg_hours - region_avg, 2)} hrs."
            )

        if device_avg is not None:
            insights.append(f"Kids using {device} average {round(device_avg, 2)} hrs/day.")

        device_switch = self.recommend_device_switch(device, health)
        if device_switch:
            insights.append(device_switch)

        details = {
            "recommended_limit_hours": recommended,
            "user_avg_daily_hours": avg_hours,
            "exceeded_by_hours": diff if exceeded else 0,
            "peer_averages": {
                "age": age_avg,
                "gender": gender_avg,
                "region": region_avg,
                "device": device_avg,
            },
            "device_health_profile": self.device_health_profile(health),
        }

        # Add detailed recommendations using dataset-aware logic
        details["recommendations"] = self.get_screen_time_recommendations(
            age=age,
            gender=user["Gender"],
            avg_daily_screen_time_hr=avg_hours,
            educational_to_recreational_ratio=user.get("Educational_to_Recreational_Ratio", None),
            primary_device=device,
            health_impacts=health,
        )

        # Convert numpy types to native Python types for JSON serialization
        return exceeded, insights, convert_numpy_types(details)

    def get_screen_time_recommendations(self, age: int, gender: str, avg_daily_screen_time_hr: float,
                                       educational_to_recreational_ratio: Optional[float],
                                       primary_device: str, health_impacts: Optional[str],
                                       detailed: bool = False):
        """Produce 5-6 human-readable recommendations based on the dataset and user inputs."""
        recommendations = []

        if self.df.empty:
            # Without dataset, return comprehensive heuristic recommendations (5-6 items)
            recommended = self.recommended_limit(age)
            if avg_daily_screen_time_hr > recommended:
                pct = ((avg_daily_screen_time_hr - recommended) / recommended) * 100
                recommendations.append(f"Warning: Your screen time is {pct:.1f}% higher than the recommended limit ({recommended} hrs) and may exceed recommended limits.")
                recommendations.append("Consider reducing your overall screen time.")
            
            if educational_to_recreational_ratio is not None and educational_to_recreational_ratio < 0.3:
                recommendations.append("Try to increase the proportion of educational content in your screen time.")
            
            if age <= 10 and avg_daily_screen_time_hr > 2:
                recommendations.append("For younger children, focus on educational and interactive content with parental guidance.")
            elif age > 10 and avg_daily_screen_time_hr > 4:
                recommendations.append("Consider setting screen time limits and encouraging a balance with other activities.")
            
            if primary_device == 'Smartphone':
                recommendations.append("Be mindful of your smartphone usage duration and consider using blue light filters.")
            
            return recommendations

        # ===== Dataset-driven recommendations (5-6 items) =====
        average_screen_time = self.df['Avg_Daily_Screen_Time_hr'].mean()

        # 1. Dataset average comparison
        if avg_daily_screen_time_hr > average_screen_time:
            percentage_higher = ((avg_daily_screen_time_hr - average_screen_time) / average_screen_time) * 100
            recommendations.append(f"Warning: Your screen time is {percentage_higher:.1f}% higher than the average ({average_screen_time:.1f} hrs) and may exceed recommended limits.")
            recommendations.append("Consider reducing your overall screen time.")
        elif avg_daily_screen_time_hr < average_screen_time:
            percentage_lower = ((average_screen_time - avg_daily_screen_time_hr) / average_screen_time) * 100
            recommendations.append(f"Your screen time is {percentage_lower:.1f}% lower than the average ({average_screen_time:.1f} hrs). Keep up the good habits!")

        # 2. Educational ratio recommendation
        if 'Educational_to_Recreational_Ratio' in self.df.columns and educational_to_recreational_ratio is not None:
            average_edu_recre_ratio = self.df['Educational_to_Recreational_Ratio'].mean()
            if educational_to_recreational_ratio < average_edu_recre_ratio * 0.9:
                recommendations.append("Try to increase the proportion of educational content in your screen time.")

        # 3. Device health impacts (most common)
        if 'Primary_Device' in self.df.columns and 'Health_Impacts' in self.df.columns:
            device_health_impacts = self.df[(self.df['Primary_Device'] == primary_device) & (self.df['Health_Impacts'] != 'None')]['Health_Impacts'].value_counts()
            if not device_health_impacts.empty:
                most_common_impact = device_health_impacts.index[0]
                recommendations.append(f"For users of {primary_device}, the most commonly observed health impact is '{most_common_impact}'.")

                # 4. Device switch suggestion (if health impact matches user's)
                if health_impacts and most_common_impact.lower() in health_impacts.lower():
                    recommendations.append(f"Consider trying a different primary device, as '{most_common_impact}' is a common health impact among {primary_device} users.")

        # 5. Device-specific average screen time
        if 'Primary_Device' in self.df.columns:
            average_screen_time_for_device = self.df[self.df['Primary_Device'] == primary_device]['Avg_Daily_Screen_Time_hr'].mean()
            if not pd.isna(average_screen_time_for_device):
                recommendations.append(f"The average daily screen time for users of {primary_device} is approximately {average_screen_time_for_device:.1f} hours.")

        # 6. Age-based suggestions
        if age <= 10 and avg_daily_screen_time_hr > 2:
            recommendations.append("For younger children, focus on educational and interactive content with parental guidance.")
        elif age > 10 and avg_daily_screen_time_hr > 4:
            recommendations.append("Consider setting screen time limits and encouraging a balance with other activities.")

        # 7. Device-specific health tips
        if primary_device == 'Smartphone':
            recommendations.append("Be mindful of your smartphone usage duration and consider using blue light filters.")

        # Remove duplicates while preserving order (keep first occurrence)
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        # Return top 6 recommendations
        return unique_recommendations[:6]
