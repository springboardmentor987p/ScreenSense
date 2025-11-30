import traceback
from utils import RecommendationEngine

engine = RecommendationEngine('data.csv')
user = {
    'Age': 5,
    'Gender': 'Male',
    'Avg_Daily_Screen_Time_hr': 6.0,
    'Primary_Device': 'Smartphone',
    'Educational_to_Recreational_Ratio': 0.2,
    'Health_Impacts': 'Poor Sleep',
    'Urban_or_Rural': 'Urban',
}

try:
    result = engine.generate_insights(user)
    exceeded, insights, details = result
    print("INSIGHTS:")
    for i, ins in enumerate(insights, 1):
        print(f"  {i}. {ins}")
    print("\nRECOMMENDATIONS:")
    for i, rec in enumerate(details['recommendations'], 1):
        print(f"  {i}. {rec}")
    print(f"\nTotal recommendations: {len(details['recommendations'])}")
except Exception:
    traceback.print_exc()
