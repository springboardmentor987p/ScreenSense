# pylint: disable=unused-import
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Matplotlib imports for chart generation
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for web servers
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import io
import base64
from collections import Counter


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
            return 1.5  # 8-10 years: 1.5 hours
        elif age <= 14:
            return 2.0  # 11-14 years: 2.0 hours
        elif age <= 18:
            return 2.5  # 15-18 years: 2.5 hours
    
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
    def generate_comparison_chart(self, analysis):
        """Generate peer comparison chart and return as base64 image"""
        overall_avg = analysis['comparisons']['Overall Average'][0]
        gender_avg = analysis['comparisons'][f"Gender ({analysis['gender']})"][0]
        device_avg = analysis['comparisons'][f"Device ({analysis['device']})"][0]
        age_group_avg = analysis['comparisons'][f"Age Group ({analysis['age_group']})"][0]
        location_avg = analysis['comparisons'][f"Location ({analysis['location']})"][0]
        screen_time = analysis['screen_time']
    
        categories = [
        "Child's Usage",
        'Overall Avg',
        f'Gender\n({analysis["gender"]})',
        f'Device\n({analysis["device"]})',
        f'Age Group\n({analysis["age_group"]})',
        f'Location\n({analysis["location"]})'
        ]
    
        values = [screen_time, overall_avg, gender_avg, device_avg, age_group_avg, location_avg]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
    
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(categories, values, color=colors, alpha=0.85, 
                   edgecolor='black', linewidth=1.2)
    
        ax.set_title(f'Screen Time Comparison: {analysis["age"]}-year-old {analysis["gender"]} ({analysis["device"]} user)', 
                 fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Daily Screen Time (hours)', fontsize=12)
        ax.set_xlabel('Comparison Categories', fontsize=12)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
    
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.1,
                f'{value:.2f}h', ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
    
        plt.tight_layout()
    
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
        return f"data:image/png;base64,{img_base64}"

    def generate_dashboard_chart(self, analysis):
        """Generate 6-panel dashboard and return as base64 image"""
        df = self.data
    
        fig, axes = plt.subplots(3, 2, figsize=(12, 10))
        fig.suptitle('Screen Time Analysis Dashboard', fontsize=16, fontweight='bold')

        # Panel 1: Peer Comparison
        categories = []
        peer_avgs = []
        for category, (avg, diff) in analysis['comparisons'].items():
            categories.append(category.split('(')[0].strip())
            peer_avgs.append(avg)

        bars1 = axes[0, 0].bar(categories, peer_avgs, alpha=0.6, color='skyblue')
        for bar in bars1:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                       f"{height:.2f}", ha='center', va='bottom',
                       fontweight='bold', fontsize=10)
    
        axes[0, 0].axhline(y=analysis['screen_time'], color='red', linestyle='--', linewidth=2)
        axes[0, 0].axhline(y=analysis['recommended_limit'], color='green', linestyle='--', linewidth=2)
        axes[0, 0].set_title('Peer Group Comparison', fontweight='bold')
        axes[0, 0].set_ylabel('Hours/day')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(axis='y', alpha=0.3)
    
        custom_lines = [
            Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='Child Usage'),
            Line2D([0], [0], color='green', linestyle='--', linewidth=2, label='Usage Limit')
        ]
        axes[0, 0].legend(handles=custom_lines, loc='lower right')
    
        # Panel 2: Usage vs Limit
        labels = ['Current\nUsage', 'Recommended\nLimit', 'Excess']
        values = [analysis['screen_time'], analysis['recommended_limit'], max(0, analysis['exceeds_by'])]
        colors = ['#ff9999', '#66b3ff', '#ffcc99']
    
        bars2 = axes[0, 1].bar(labels, values, color=colors, alpha=0.7)
        for bar in bars2:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width() / 2, height + 0.05,
                       f"{height:.2f}", ha='center', va='bottom',
                       fontweight='bold', fontsize=10)
    
        axes[0, 1].set_title('Usage vs Recommended Limit', fontweight='bold')
        axes[0, 1].set_ylabel('Hours/day')
        axes[0, 1].grid(axis='y', alpha=0.3)
    
        # Panel 3: Severity Gauge
        severity_levels = ['Healthy', 'Moderate', 'High', 'Critical']
        severity_colors = ['#00ff00', '#ffff00', '#ff9900', '#ff0000']
        current_severity = analysis['severity']
        severity_index = severity_levels.index(current_severity)
        current_color = severity_colors[severity_index]
    
        axes[1, 0].barh([current_severity], [1], color=current_color, alpha=0.8, 
                    edgecolor='black', linewidth=2)
        axes[1, 0].set_title('Severity Classification', fontweight='bold')
        axes[1, 0].set_xlabel('Level')
        axes[1, 0].set_xlim(0, 1.2)
        axes[1, 0].text(0.5, 0, current_severity, ha='center', va='center', 
                   fontsize=14, fontweight='bold', color='white')
    
        # Panel 4: Educational to Recreational Ratio
        child_ratio = analysis.get('edu_rec_ratio', 0)
        dataset_avg_ratio = df['Educational_to_Recreational_Ratio'].mean()
        ratio_labels = ['Child\nRatio', 'Dataset Avg\nRatio']
        ratio_values = [child_ratio if child_ratio != 'N/A' else 0, dataset_avg_ratio]
        ratio_colors = ['#2196F3', '#9E9E9E']
    
        bars5 = axes[1, 1].bar(ratio_labels, ratio_values, color=ratio_colors, 
                          alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[1, 1].set_ylabel('Edu/Rec Ratio', fontsize=12, fontweight='bold')
        axes[1, 1].set_title('Educational to Recreational Ratio', fontweight='bold')
        axes[1, 1].axhline(y=1, color='green', linestyle='--', linewidth=2, label='Ideal (1:1)')
        axes[1, 1].legend(loc='upper right')
        axes[1, 1].grid(axis='y', alpha=0.3, linestyle='--')
    
        for bar, val in zip(bars5, ratio_values):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, height + 0.02,
                       f'{val:.2f}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=11)
    
        # Panel 5: Health Impacts
        child_impacts = analysis.get('health_impacts', ['None'])
        if isinstance(child_impacts, str):
            child_impacts = [child_impacts]
    
        all_impacts = []
        for impacts in df['Health_Impacts'].dropna():
            if isinstance(impacts, str):
                all_impacts.extend([i.strip() for i in impacts.split(',')])
    
        impact_counts = Counter(all_impacts)
        top_impacts = dict(impact_counts.most_common(5))
    
        impact_labels = list(top_impacts.keys())
        impact_values = list(top_impacts.values())
        bar_colors = ['#FF6B6B' if label in child_impacts else '#9E9E9E' 
                  for label in impact_labels]
    
        bars = axes[2, 0].barh(impact_labels, impact_values, color=bar_colors, 
                          alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[2, 0].set_title('Health Impacts Frequency', fontweight='bold')
        axes[2, 0].set_xlabel('Number of Children', fontsize=11)
        axes[2, 0].grid(axis='x', alpha=0.3, linestyle='--')
    
        for i, (bar, val) in enumerate(zip(bars, impact_values)):
            width = bar.get_width()
            axes[2, 0].text(width + max(impact_values)*0.02, 
                       bar.get_y() + bar.get_height()/2,
                       f'{val} ({val/len(df)*100:.1f}%)', 
                       ha='left', va='center', fontweight='bold', fontsize=10)
    
        legend_elements = [
            Patch(facecolor='#FF6B6B', edgecolor='black', label="Child's Impacts"),
            Patch(facecolor='#9E9E9E', edgecolor='black', label='Other Impacts')
        ]
        axes[2, 0].legend(handles=legend_elements, loc='lower right', fontsize=10)
    
        # Panel 6: Profile Summary
        axes[2, 1].axis('off')
    
        edu_hours = analysis.get('educational_hours', 'N/A')
        rec_hours = analysis.get('recreational_hours', 'N/A')
        edu_rec_ratio = analysis.get('edu_rec_ratio', 'N/A')
        health_impacts = analysis.get('health_impacts', ['Not specified'])
    
        if isinstance(health_impacts, list):
            health_str = ', '.join(health_impacts)
        else:
            health_str = str(health_impacts)
    
        if edu_hours != 'N/A':
            edu_str = f"{edu_hours:.2f} h/day"
            rec_str = f"{rec_hours:.2f} h/day"
            ratio_str = f"{edu_rec_ratio:.2f}"
        else:
            edu_str = "N/A"
            rec_str = "N/A"
            ratio_str = "N/A"
    
        profile_text = f"""
    USER PROFILE
    ━━━━━━━━━━━━━━━━━━━━
    Age: {analysis['age']} years
    Age Group: {analysis['age_group']}
    Gender: {analysis['gender']}
    Device: {analysis['device']}
    Location: {analysis['location']}

    SCREEN TIME ANALYSIS
    ━━━━━━━━━━━━━━━━━━━━
    Current: {analysis['screen_time']:.2f} h/day
    Recommended: {analysis['recommended_limit']:.2f} h/day
    Difference: {analysis['exceeds_by']:.2f} h/day
    Severity: {analysis['severity']}
    Educational: {edu_str}
    Recreational: {rec_str}
    Edu/Rec Ratio: {ratio_str}

    HEALTH IMPACTS
    ━━━━━━━━━━━━━━━━━━━━
    {health_str}
    """
    
        axes[2, 1].text(0.1, 0.5, profile_text, fontsize=11, family='monospace',
                   verticalalignment='center')
    
        plt.tight_layout()
    
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
    
        return f"data:image/png;base64,{img_base64}"

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
