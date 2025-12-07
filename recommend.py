import pandas as pd
import io

# Global variables to store the dataframes
df = None
threshold_df = None
average_metrics_by_age = None
average_metrics_by_gender = None
average_metrics_by_device = None
average_metrics_by_health_impacts = None

def load_and_preprocess_data(csv_content):
    """
    Load and preprocess the dataset.
    
    Args:
        csv_content: CSV file content (string or bytes)
    
    Returns:
        dict: Contains all processed dataframes
    """
    global df, threshold_df, average_metrics_by_age, average_metrics_by_gender, average_metrics_by_device, average_metrics_by_health_impacts
    
    # Read CSV
    if isinstance(csv_content, bytes):
        df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')))
    else:
        df = pd.read_csv(csv_content)
    
    print(f"Dataset loaded successfully! Shape: {df.shape}")
    
    # 1. Address missing values in Health_Impacts
    df['Health_Impacts'] = df['Health_Impacts'].fillna('None')
    
    # 2. Unify categorical columns
    for col in ['Gender', 'Primary_Device', 'Health_Impacts', 'Urban_or_Rural']:
        if df[col].dtype == 'object':
            df[col] = df[col].str.lower().str.strip()
    
    # 3. Create 'Age_Band' column
    def categorize_age(age):
        if age <= 12:
            return 'Child'
        elif 13 <= age <= 17:
            return 'Teen'
        else:
            return 'Young Adult'
    
    df['Age_Band'] = df['Age'].apply(categorize_age)
    
    # 4. Create threshold_df
    within_limit = df[df['Exceeded_Recommended_Limit'] == False]
    above_limit = df[df['Exceeded_Recommended_Limit'] == True]
    
    ages = sorted(df['Age'].unique())
    genders = df['Gender'].unique()
    threshold_data = []
    
    for age in ages:
        for gender in genders:
            max_False = within_limit.loc[(within_limit['Age'] == age) & (within_limit['Gender'] == gender), 'Avg_Daily_Screen_Time_hr'].max()
            min_True = above_limit.loc[(above_limit['Age'] == age) & (above_limit['Gender'] == gender), 'Avg_Daily_Screen_Time_hr'].min()
            
            if pd.notna(max_False) and pd.notna(min_True):
                threshold = max_False if min_True > max_False else None
            else:
                threshold = None
            
            threshold_data.append({'Age': age, 'Gender': gender, 'Threshold_limit_hr': threshold})
    
    threshold_df = pd.DataFrame(threshold_data).set_index(['Age', 'Gender'])
    
    # 5. Create average metrics
    average_metrics_by_age = df.groupby('Age_Band')[['Avg_Daily_Screen_Time_hr', 'Educational_to_Recreational_Ratio']].mean()
    average_metrics_by_gender = df.groupby('Gender')[['Avg_Daily_Screen_Time_hr', 'Educational_to_Recreational_Ratio']].mean()
    average_metrics_by_device = df.groupby('Primary_Device')[['Avg_Daily_Screen_Time_hr', 'Educational_to_Recreational_Ratio']].mean()
    average_metrics_by_health_impacts = df.groupby('Health_Impacts')[['Avg_Daily_Screen_Time_hr', 'Educational_to_Recreational_Ratio']].mean()
    
    print("Data preprocessing complete!")
    
    return {
        'df': df,
        'threshold_df': threshold_df,
        'average_metrics_by_age': average_metrics_by_age,
        'average_metrics_by_gender': average_metrics_by_gender,
        'average_metrics_by_device': average_metrics_by_device,
        'average_metrics_by_health_impacts': average_metrics_by_health_impacts
    }

def generate_screen_time_recommendation(age, gender, screen_time, primary_device, health_impacts):
    """
    Generates a screen time recommendation based on user input and precalculated data.

    Args:
        age (int): The user's age.
        gender (str): The user's gender ('male' or 'female').
        screen_time (float): The user's average daily screen time in hours.
        primary_device (str): The user's primary device.
        health_impacts (str): The health impacts experienced by the user.

    Returns:
        str: Recommendation message
    """
    if threshold_df is None:
        return "Error: Data not loaded. Please load data first."
    
    recommendation_message = ""
    gender = gender.lower().strip()
    primary_device = primary_device.lower().strip()
    health_impacts = health_impacts.lower().strip()

    # Determine age band
    if age <= 12:
        age_band = 'Child'
    elif 13 <= age <= 17:
        age_band = 'Teen'
    else:
        age_band = 'Young Adult'

    # 1. Look up the recommended screen time limit based on age band and gender
    if age_band == 'Child':
        closest_age_in_threshold = 8
    elif age_band == 'Teen':
        closest_age_in_threshold = 13
    else:  # Young Adult
        closest_age_in_threshold = 18

    try:
        limit = threshold_df.loc[(closest_age_in_threshold, gender), 'Threshold_limit_hr']
    except KeyError:
        recommendation_message += (f"Warning: Could not find a specific threshold for age band {age_band} and gender '{gender}'.\n")
        limit = None

    # 2. Compare user's screen time with the threshold and generate message
    if limit is not None and not pd.isna(limit):
        if screen_time > limit:
            recommendation_message += (f"Your screen time of {screen_time:.2f} hours per day exceeds the recommended limit of {limit:.2f} hours for a {age_band} ({age} years old) {gender}.\n")
        else:
            recommendation_message += (f"Your screen time of {screen_time:.2f} hours per day is within the recommended limit of {limit:.2f} hours for a {age_band} ({age} years old) {gender}.\n")

    # 3. Incorporate average metrics for context
    try:
        avg_screen_time_age = average_metrics_by_age.loc[age_band, 'Avg_Daily_Screen_Time_hr']
        avg_ratio_age = average_metrics_by_age.loc[age_band, 'Educational_to_Recreational_Ratio']
        recommendation_message += (f"The average daily screen time for {age_band}s is {avg_screen_time_age:.2f} hours, with an average educational to recreational ratio of {avg_ratio_age:.2f}.\n")
    except KeyError:
        recommendation_message += (f"Could not find average metrics for {age_band} age band.\n")

    try:
        avg_screen_time_gender = average_metrics_by_gender.loc[gender, 'Avg_Daily_Screen_Time_hr']
        avg_ratio_gender = average_metrics_by_gender.loc[gender, 'Educational_to_Recreational_Ratio']
        recommendation_message += (f"For {gender}s, the average daily screen time is {avg_screen_time_gender:.2f} hours, and the average educational to recreational ratio is {avg_ratio_gender:.2f}.\n")
    except KeyError:
        recommendation_message += (f"Could not find average metrics for gender '{gender}'.\n")

    # 4. Incorporate insights based on primary device
    try:
        avg_screen_time_device = average_metrics_by_device.loc[primary_device, 'Avg_Daily_Screen_Time_hr']
        avg_ratio_device = average_metrics_by_device.loc[primary_device, 'Educational_to_Recreational_Ratio']
        recommendation_message += (f"Users of {primary_device} as their primary device have an average daily screen time of {avg_screen_time_device:.2f} hours and an average educational to recreational ratio of {avg_ratio_device:.2f}.\n")
    except KeyError:
        recommendation_message += (f"Could not find average metrics for primary device '{primary_device}'.\n")

    # 5. Incorporate insights based on health impacts
    if health_impacts != 'none':
        try:
            avg_screen_time_health = average_metrics_by_health_impacts.loc[health_impacts, 'Avg_Daily_Screen_Time_hr']
            avg_ratio_health = average_metrics_by_health_impacts.loc[health_impacts, 'Educational_to_Recreational_Ratio']
            recommendation_message += (f"Individuals experiencing '{health_impacts}' have an average daily screen time of {avg_screen_time_health:.2f} hours and an average educational to recreational ratio of {avg_ratio_health:.2f}.\n")
        except KeyError:
            recommendation_message += (f"Could not find average metrics for health impacts '{health_impacts}'.\n")

    return recommendation_message


def get_analysis_insights(age, gender, screen_time, device):
    """
    Analyze user data against the dataset and return insights.
    
    Args:
        age: User's age
        gender: User's gender (male/female)
        screen_time: Daily screen time in hours
        device: Primary device (smartphone, laptop, tablet, tv)
    
    Returns:
        dict: Insights and statistics for the user's profile
    """
    global df, average_metrics_by_age, average_metrics_by_gender, average_metrics_by_device
    
    if df is None:
        return {"error": "Dataset not loaded"}
    
    try:
        gender = str(gender).lower().strip()
        device = str(device).lower().strip()
        
        # Categorize age
        if age <= 12:
            age_band = 'Child'
        elif 13 <= age <= 17:
            age_band = 'Teen'
        else:
            age_band = 'Young Adult'
        
        # Calculate global statistics
        avg_screen_time = float(df['Avg_Daily_Screen_Time_hr'].mean())
        exceeds_limit_pct = float((df['Exceeded_Recommended_Limit'].sum() / len(df)) * 100)
        
        # Filter for same age, gender, device
        age_gender_filter = df[(df['Age_Band'] == age_band) & (df['Gender'] == gender)]
        age_gender_avg = float(age_gender_filter['Avg_Daily_Screen_Time_hr'].mean()) if len(age_gender_filter) > 0 else avg_screen_time
        
        device_filter = df[df['Primary_Device'] == device]
        device_avg = float(device_filter['Avg_Daily_Screen_Time_hr'].mean()) if len(device_filter) > 0 else avg_screen_time
        
        # Check if user exceeds recommended limit (assuming ~2-3 hours for kids)
        RECOMMENDED_LIMIT = 3.0
        exceeds_limit = screen_time > RECOMMENDED_LIMIT
        
        # Get most common health impacts
        health_impacts = df['Health_Impacts'].value_counts().head(3).to_dict()
        common_health_impacts = ", ".join([k.title() for k in health_impacts.keys()])
        
        # Get most common device
        most_common_device = df['Primary_Device'].value_counts().index[0] if len(df) > 0 else 'Unknown'
        
        # Compare user to peers
        peers = age_gender_filter if len(age_gender_filter) > 0 else df
        percentile = (peers['Avg_Daily_Screen_Time_hr'] < screen_time).sum() / len(peers) * 100 if len(peers) > 0 else 50
        
        return {
            "age_band": age_band,
            "avg_screen_time": round(avg_screen_time, 2),
            "age_gender_avg": round(age_gender_avg, 2),
            "device_avg": round(device_avg, 2),
            "exceeds_limit": exceeds_limit,
            "exceeds_limit_pct": round(exceeds_limit_pct, 1),
            "recommended_limit": RECOMMENDED_LIMIT,
            "percentile": round(percentile, 1),
            "most_common_device": most_common_device.title(),
            "common_health_impacts": common_health_impacts,
            "user_vs_peers": "above average" if screen_time > age_gender_avg else "below average"
        }
    
    except Exception as e:
        print(f"Error in get_analysis_insights: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
