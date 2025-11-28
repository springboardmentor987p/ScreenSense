import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class ScreenTimeRecommendationSystem:
    
    def __init__(self, csv_path='Indian_Kids_Screen_Time.csv'):
        print("="*70)
        print("INITIALIZING SCREEN TIME RECOMMENDATION SYSTEM")
        print("="*70)
        
        # Load dataset
        print("\n📂 Loading dataset...")
        self.data = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(self.data)} records")
        
        # Data cleaning
        print("\n🧹 Cleaning data...")
        original_size = len(self.data)
        self.data = self.data.drop_duplicates()
        print(f"✓ Removed {original_size - len(self.data)} duplicates")
        
        # Create age groups
        self.data['Age_Group'] = self.data['Age'].apply(self._get_age_group)
        
        # Calculate baseline statistics
        print("\n📊 Calculating baseline statistics...")
        self.overall_avg = self.data['Avg_Daily_Screen_Time_hr'].mean()
        self.gender_stats = self.data.groupby('Gender')['Avg_Daily_Screen_Time_hr'].mean().to_dict()
        self.device_stats = self.data.groupby('Primary_Device')['Avg_Daily_Screen_Time_hr'].mean().to_dict()
        self.age_group_stats = self.data.groupby('Age_Group')['Avg_Daily_Screen_Time_hr'].mean().to_dict()
        self.location_stats = self.data.groupby('Urban_or_Rural')['Avg_Daily_Screen_Time_hr'].mean().to_dict()
        
        print(f"✓ Overall Average: {self.overall_avg:.2f} hours/day")
        print("\n✅ System ready!")
        print("="*70)
    
    def get_recommended_limit(self, age):
        if age <= 10:
            return 2.0  # 8-10 years: 2 hours
        elif age <= 14:
            return 2.5  # 11-14 years: 2.5 hours
        else:
            return 3.0  # 15-18 years: 3 hours
    
    def _get_age_group(self, age):
        if age <= 10:
            return '8-10 years'
        elif age <= 14:
            return '11-14 years'
        else:
            return '15-18 years'
    
    def _classify_severity(self, exceeds_by, limit):
        if exceeds_by <= 0:
            return 'Healthy'
        elif exceeds_by <= limit * 0.5:
            return 'Moderate'
        elif exceeds_by <= limit:
            return 'High'
        else:
            return 'Critical'
    
    def analyze_user_input(self, age, gender, device, location, screen_time):
        
        age_group = self._get_age_group(age)
        recommended_limit = self.get_recommended_limit(age)
        
        # Get peer group averages
        gender_avg = self.gender_stats.get(gender, self.overall_avg)
        device_avg = self.device_stats.get(device, self.overall_avg)
        age_avg = self.age_group_stats.get(age_group, self.overall_avg)
        location_avg = self.location_stats.get(location, self.overall_avg)
        
        # Calculate differences
        comparisons = {
            'Overall Average': (self.overall_avg, screen_time - self.overall_avg),
            f'Gender ({gender})': (gender_avg, screen_time - gender_avg),
            f'Device ({device})': (device_avg, screen_time - device_avg),
            f'Age Group ({age_group})': (age_avg, screen_time - age_avg),
            f'Location ({location})': (location_avg, screen_time - location_avg)
        }
        
        # Determine severity
        exceeds_by = screen_time - recommended_limit
        severity = self._classify_severity(exceeds_by, recommended_limit)
        
        return {
            'age': age,
            'age_group': age_group,
            'gender': gender,
            'device': device,
            'location': location,
            'screen_time': screen_time,
            'recommended_limit': recommended_limit,
            'exceeds_by': exceeds_by,
            'severity': severity,
            'comparisons': comparisons
        }
    
    def generate_recommendations(self, analysis):
        recommendations = []
        severity = analysis['severity']
        exceeds_by = analysis['exceeds_by']
        age = analysis['age']
        device = analysis['device']
        
        # Health-based recommendations
        if severity == 'Healthy':
            recommendations.append("✅ Great job! Your screen time is within healthy limits.")
            recommendations.append("💡 Continue maintaining a balanced digital lifestyle.")
        elif severity == 'Moderate':
            recommendations.append(f"⚠️ Your screen time exceeds recommendations by {exceeds_by:.1f} hours/day.")
            recommendations.append("💡 Try reducing screen time gradually by 15-30 minutes per week.")
        elif severity == 'High':
            recommendations.append(f"⚠️ WARNING: Screen time significantly exceeds recommendations by {exceeds_by:.1f} hours/day.")
            recommendations.append("💡 Immediate action needed: Reduce screen time by at least 1 hour daily.")
        else:  # Critical
            recommendations.append(f"🚨 CRITICAL: Screen time is {exceeds_by:.1f} hours ABOVE recommendations!")
            recommendations.append("💡 URGENT: Reduce screen time by 2-3 hours immediately and seek professional guidance.")
        
        # Device-specific recommendations
        device_tips = {
            'Smartphone': [
                "📱 Enable screen time limits using built-in features",
                "📱 Move distracting apps to folders or remove from home screen",
                "📱 Use grayscale mode to reduce appeal"
            ],
            'Laptop': [
                "💻 Use website blockers during study/work hours",
                "💻 Practice the 20-20-20 rule: Every 20 mins, look 20 feet away for 20 seconds",
                "💻 Set specific time blocks for laptop use"
            ],
            'TV': [
                "📺 Avoid binge-watching; set episode limits",
                "📺 Remove TV from bedroom to improve sleep",
                "📺 Plan viewing schedule in advance"
            ],
            'Tablet': [
                "📋 Use parental controls to limit usage time",
                "📋 Encourage educational apps over games",
                "📋 Keep tablets in common areas, not bedrooms"
            ]
        }
        
        recommendations.extend(device_tips.get(device, []))
        
        # Age-specific recommendations
        if age <= 10:
            recommendations.extend([
                "👶 Prioritize outdoor play and physical activities",
                "👶 Encourage creative activities like drawing and building",
                "👶 Co-view content with parents when possible"
            ])
        elif age <= 14:
            recommendations.extend([
                "👦 Balance screen time with hobbies and sports",
                "👦 Set homework completion before recreational screen time",
                "👦 Discuss online safety and digital citizenship"
            ])
        else:
            recommendations.extend([
                "👨 Practice self-regulation and time management",
                "👨 Use productivity apps to track and limit usage",
                "👨 Engage in social activities without screens"
            ])
        
        # General health recommendations
        recommendations.extend([
            "🏥 HEALTH TIPS:",
            "• Follow the 20-20-20 rule to prevent eye strain",
            "• Maintain proper posture while using devices",
            "• Avoid screens 1 hour before bedtime",
            "• Stay physically active for at least 60 minutes daily",
            "• Ensure adequate sleep (8-10 hours for children)"
        ])
        
        return recommendations
    def get_statistics(self):
        stats = {
            'Total Records': len(self.data),
            'Overall Average': f"{self.overall_avg:.2f} hours/day",
            'By Gender': self.gender_stats,
            'By Device': self.device_stats,
            'By Age Group': self.age_group_stats,
            'By Location': self.location_stats
        }
        return stats
    def display_analysis(self, analysis, recommendations):
        print("="*70)
        print("📊 PERSONALIZED SCREEN TIME ANALYSIS REPORT")
        print("="*70)
        
        print(f"👤 User Profile:")
        print(f"   Age: {analysis['age']} years ({analysis['age_group']})")
        print(f"   Gender: {analysis['gender']}")
        print(f"   Primary Device: {analysis['device']}")
        print(f"   Location: {analysis['location']}\n")
        
        print(f"📱 Screen Time Analysis:")
        print(f"   Current Usage: {analysis['screen_time']:.2f} hours/day")
        print(f"   Recommended Limit: {analysis['recommended_limit']:.2f} hours/day\n")
        
        if analysis['exceeds_by'] > 0:
            print(f"   ⚠️  Exceeds by: {analysis['exceeds_by']:.2f} hours/day")
        else:
            print(f"   ✅ Within limit by: {abs(analysis['exceeds_by']):.2f} hours/day")
        
        print(f"   Severity Level: {analysis['severity']}")
        
        print(f"📈 Peer Group Comparisons:")
        for category, (avg, diff) in analysis['comparisons'].items():
            symbol = "↑" if diff > 0 else "↓"
            print(f"   {category}: {avg:.2f}h (You: {symbol} {abs(diff):.2f}h)\n")
        
        print(f"💡 PERSONALIZED RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
        print("\n")
        print("="*70)
