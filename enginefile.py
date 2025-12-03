import pandas as pd
import os

# Get backend-fastapi folder path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  

# Construct path to Dataframes/
DATA_PATH = os.path.join(BASE_DIR, "Dataframes")

# Load CSVs
recom_df2 = pd.read_csv(os.path.join(DATA_PATH, "recom_df2.csv"))
Health_Impacts_count_df = pd.read_csv(os.path.join(DATA_PATH, "Health_Impacts_df.csv"))



def _format_diff(diff, pct, label, group_label):
    if diff > 0:
        return f"Your {label} is {diff:.2f} hours ({pct:.1f}%) above the average for {group_label}."
    elif diff < 0:
        return f"Your {label} is {abs(diff):.2f} hours ({abs(pct):.1f}%) below the average for {group_label}."
    else:
        return f"Your {label} matches the average for {group_label}."

def _filter_group(age, gender, device, df):
    match_df = df[
        (df['Age'] == age) &
        (df['Gender'] == gender) &
        (df['Primary_Device'] == device)
    ]
    return None if match_df.empty else match_df.iloc[0]

def _user_summary(age, gender, device, edu, rec, total):
    return [
        #"RECOMMENDATION SYSTEM",
        f"Entered Age : {age}",
        f"Entered Gender : {gender}",
        f"Entered Device : {device}",
        f"Entered Edu. Screen Time : {edu}",
        f"Entered Rec. Screen Time : {rec}",
        f"Total Screen Time : {total:.2f} hours"
    ]

def _threshold_analysis(screen_time, row, age, gender):
    limit = row['Threshold_Limit_hr']
    msgs = []

    if screen_time > limit:
        msgs.append(
            f"For a {age}-year-old {gender}, recommended limit is {limit:.2f} hours. "
            f"You exceeded it by {screen_time - limit:.2f} hours."
        )
    else:
        msgs.append(
            f"You are within the healthy recommended limit range of ({limit:.2f} hours) for a {age}-year-old."
        )

    return msgs

def _group_comparison(screen_time, row, age, gender, device):
    msgs = []
    avg = row['Avg_screen_time_per_criterias']
    diff = screen_time - avg
    pct = (diff / avg) * 100 if avg else 0

    msgs.append(
        _format_diff(diff, pct, "overall screen time", f"{gender}s aged {age} using {device}")
    )
    return msgs

def _age_only_comparison(screen_time, row, age):
    msgs = []
    avg = row['Avg_Daily_Screen_Time_per_age_only']
    diff = screen_time - avg
    pct = (diff / avg) * 100 if avg else 0

    msgs.append(
        _format_diff(diff, pct, "screen time", f"children aged {age}")
    )
    return msgs

def _edu_comparison(edu, row, age, gender, device):
    avg = row['Avg_Educational_Screen_time']
    diff = edu - avg
    pct = (diff / avg) * 100 if avg else 0

    return [
        _format_diff(
            diff, pct,
            "educational screen time",
            f"{age}-year-old {gender}s using {device}"
        )
    ]

def _rec_comparison(rec, row, age, gender, device):
    avg = row['Avg_Recreational_Screen_time']
    diff = rec - avg
    pct = (diff / avg) * 100 if avg else 0

    return [
        _format_diff(
            diff, pct,
            "recreational screen time",
            f"{age}-year-old {gender}s using {device}"
        )
    ]

def _edu_rec_ratio(edu, rec, age, df):
    msgs = []

    avg_ratio = df[df['Age'] == age]['Educational_to_Recreational_Ratio'].iloc[0]

    if rec != 0:
        ratio = edu / rec
        msgs.append(f"Your Educational to Recreational ratio : {ratio:.2f}")
    else:
        ratio = float('inf')
        msgs.append("Your Educational to Recreational ratio : Can't be calculated since ,No recreational time provided")

    msgs.append(f"Average of Educational to Recreational ratio for age {age}  : {avg_ratio:.2f}")

    if ratio == float('inf'):
        return msgs

    diff = ratio - avg_ratio
    if diff > 0:
        msgs.append("You spend more time on educational activities than peers.")
    elif diff < 0:
        msgs.append("Your recreational usage is higher than your age group's average.")
    else:
        msgs.append("Your ratio exactly matches your age group.")

    return msgs

def _health_impacts(age, gender, device, df, df_counts, screen_time, limit):
    msgs = []
    group = df[
        (df['Age'] == age) &
        (df['Gender'] == gender) &
        (df['Primary_Device'] == device)
    ]['Health_Impacts']

    if group.empty:
        return ["No health impact data available for this group."]

    counts = group.value_counts()
    top = counts.head(3)

    msgs.append("Most common health impacts among similar users:")
    for impact, cnt in top.items():
        msgs.append(f"- {impact}")

    top_list = list(top.index)

    if screen_time > limit:
        if len(top_list) == 1:
            msgs.append(f"Exceeding limit is linked to {top_list[0]}.")
        else:
            msgs.append(
                f"Exceeding limit is often linked to {', '.join(top_list[:-1])}, and {top_list[-1]}."
            )
    else:
        if "None" in top_list:
            msgs.append("Good news! Most similar users report no health impacts.")

    return msgs

def _risk_level(screen_time, limit):
    exceed_pct = ((screen_time - limit) / limit) * 100
    if exceed_pct <= 0:
        return ["Risk Level Assessment : Healthy(No Risk)"]
    elif exceed_pct <= 20:
        return ["Risk Level Assessment : Mild Risk"]
    elif exceed_pct <= 50:
        return ["Risk Level Assessment : High Risk"]
    else:
        return ["Risk Level Assessment : Severe Risk"]


def _device_recommendation(age, device, df_counts):
    msgs = []
    subset = df_counts[df_counts['Age'] == age]

    if subset.empty:
        return ["No device recommendations available."]

    row = subset.loc[subset['Health_Impacts_count'].idxmin()]
    best = row['Primary_Device']

    if device != best:
        msgs.append(f'''DEVICE TYPE ADVICE : Consider switching from '{device}' to '{best}' as, {device} has the least number of health impacts linked to it for your peer.''')
    else:
        msgs.append(f"'{device}' is already the healthiest choice for your age group.")

    return msgs


def recommendation(age, gender, device, edu_time, rec_time):
    screen_time = edu_time + rec_time

    # Filter group row
    row = _filter_group(age, gender, device, recom_df2)
    if row is None:
        return ["No matching data found for given inputs."]

    msgs = []

    msgs += _user_summary(age, gender, device, edu_time, rec_time, screen_time)
    msgs += _threshold_analysis(screen_time, row, age, gender)
    msgs += _group_comparison(screen_time, row, age, gender, device)
    msgs += _age_only_comparison(screen_time, row, age)
    msgs += _edu_comparison(edu_time, row, age, gender, device)
    msgs += _rec_comparison(rec_time, row, age, gender, device)
    msgs += _edu_rec_ratio(edu_time, rec_time, age, recom_df2)
    msgs += _health_impacts(age, gender, device, recom_df2, Health_Impacts_count_df, screen_time, row['Threshold_Limit_hr'])
    msgs += _risk_level(screen_time, row['Threshold_Limit_hr'])
    msgs += _device_recommendation(age, device, Health_Impacts_count_df)

    #msgs.append("=============================================================================================")

    # Print OR return 
    return (msgs)
    #return "\n".join(msgs)  #or could just perform the str.join() here

# #USER INPUTS
# age = int(input("Enter your age (8-18) in years: "))
# gender = input("Enter the gender (Male/Female): ").capitalize()
# device = input("Enter your primary screen type ('Smartphone', 'Laptop', 'TV', 'Tablet'): ").capitalize()
# edu_time = float(input("Enter your educational screen time (in hours): "))
# rec_time = float(input("Enter your recreational screen time (in hours): "))

# recommendation(age,gender,device,edu_time,rec_time)