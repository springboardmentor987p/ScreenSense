import os
from typing import List
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Dataframes")

# Filenames (adjust if your file names differ)
FILE_1 = "Indian_Kids_Screen_Time_Cleaned.csv"
FILE_2 = "Health_Impacts_df.csv"


def _try_load_csv(filename: str) -> pd.DataFrame:
    """
    Try a few candidate paths to load the CSV:
      1) DATA_DIR/filename
      2) filename (if an absolute or relative path was provided)
    Raises FileNotFoundError if none found.
    """
    candidates = [
        os.path.join(DATA_DIR, filename),
        filename,  # allow absolute path or path provided as-is
    ]
    last_err = None
    for p in candidates:
        try:
            if os.path.exists(p):
                return pd.read_csv(p)
        except Exception as e:
            last_err = e
    # final attempt: try reading filename as given (works for absolute paths)
    try:
        return pd.read_csv(filename)
    except Exception as e:
        raise FileNotFoundError(
            f"Could not load CSV '{filename}'. Tried: {candidates}. Error: {e}"
        ) from e


# Load datasets (will raise helpful FileNotFoundError if not present)
Indian_Kids_Screen_Time_Cleaned = _try_load_csv(FILE_1)
Health_Impacts_count_df = _try_load_csv(FILE_2)

# Provide a copy used earlier in your code
recom_df2 = Indian_Kids_Screen_Time_Cleaned.copy()


# Helper: safe column access with fallback
def _col_value_or_default(row, col, default=0.0):
    try:
        return float(row[col])
    except Exception:
        return default


def _format_diff(diff, pct, label, group_label):
    if diff > 0:
        return f"Your {label} is {diff:.2f} hours ({pct:.1f}%) above the average for {group_label}."
    elif diff < 0:
        return f"Your {label} is {abs(diff):.2f} hours ({abs(pct):.1f}%) below the average for {group_label}."
    else:
        return f"Your {label} matches the average for {group_label}."


def _filter_group(age, gender, device, df):
    match_df = df[
        (df.get("Age") == age) if "Age" in df.columns else (df["Age"] == age)
        if "Age" in df.columns else False
    ]
    # safer: use boolean masks if columns exist
    mask = pd.Series([True] * len(df))
    if "Age" in df.columns:
        mask &= df["Age"] == age
    else:
        return None
    if "Gender" in df.columns:
        mask &= df["Gender"] == gender
    else:
        return None
    if "Primary_Device" in df.columns:
        mask &= df["Primary_Device"] == device
    else:
        return None

    match_df = df[mask]
    return None if match_df.empty else match_df.iloc[0]


def _user_summary(age, gender, device, edu, rec, total):
    return [
        f"Entered Age : {age}",
        f"Entered Gender : {gender}",
        f"Entered Device : {device}",
        f"Entered Edu. Screen Time : {edu}",
        f"Entered Rec. Screen Time : {rec}",
        f"Total Screen Time : {total:.2f} hours",
    ]


def _threshold_analysis(screen_time, row, age, gender):
    msgs = []
    if "Threshold_Limit_hr" not in row:
        msgs.append("Threshold limit data not available for this group.")
        return msgs

    limit = _col_value_or_default(row, "Threshold_Limit_hr", default=None)
    if limit is None:
        msgs.append("Threshold limit data invalid for this group.")
        return msgs

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
    avg_col = "Avg_screen_time_per_criterias"
    if avg_col in row:
        avg = _col_value_or_default(row, avg_col, default=0.0)
    else:
        avg = row.get("Avg_Daily_Screen_Time_per_age_only", 0.0)

    if avg == 0:
        msgs.append("No group average available for comparison.")
        return msgs

    diff = screen_time - avg
    pct = (diff / avg) * 100 if avg else 0
    msgs.append(
        _format_diff(diff, pct, "overall screen time", f"{gender}s aged {age} using {device}")
    )
    return msgs


def _age_only_comparison(screen_time, row, age):
    msgs = []
    col = "Avg_Daily_Screen_Time_per_age_only"
    avg = _col_value_or_default(row, col, default=None) if col in row else None
    if avg is None or avg == 0:
        msgs.append("No age-only average available for comparison.")
        return msgs
    diff = screen_time - avg
    pct = (diff / avg) * 100 if avg else 0
    msgs.append(_format_diff(diff, pct, "screen time", f"children aged {age}"))
    return msgs


def _edu_comparison(edu, row, age, gender, device):
    col = "Avg_Educational_Screen_time"
    if col in row:
        avg = _col_value_or_default(row, col, default=0.0)
    else:
        avg = 0.0
    diff = edu - avg
    pct = (diff / avg) * 100 if avg else 0
    return [
        _format_diff(
            diff, pct, "educational screen time", f"{age}-year-old {gender}s using {device}"
        )
    ]


def _rec_comparison(rec, row, age, gender, device):
    col = "Avg_Recreational_Screen_time"
    if col in row:
        avg = _col_value_or_default(row, col, default=0.0)
    else:
        avg = 0.0
    diff = rec - avg
    pct = (diff / avg) * 100 if avg else 0
    return [
        _format_diff(
            diff, pct, "recreational screen time", f"{age}-year-old {gender}s using {device}"
        )
    ]


def _edu_rec_ratio(edu, rec, age, df):
    msgs = []
    # find row in df matching age for average ratio
    if "Age" not in df.columns or "Educational_to_Recreational_Ratio" not in df.columns:
        msgs.append("No educational/recreational ratio data available.")
        return msgs

    age_rows = df[df["Age"] == age]
    if age_rows.empty:
        msgs.append("No ratio data available for this age.")
        return msgs

    avg_ratio = age_rows["Educational_to_Recreational_Ratio"].iloc[0]
    if rec != 0:
        ratio = edu / rec
        msgs.append(f"Your Educational to Recreational ratio : {ratio:.2f}")
    else:
        ratio = None
        msgs.append("Your Educational to Recreational ratio : Can't be calculated since no recreational time provided")

    msgs.append(f"Average of Educational to Recreational ratio for age {age}  : {avg_ratio:.2f}")

    if ratio is None:
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
    # If Health_Impacts column present, filter; otherwise return message
    if "Health_Impacts" not in df.columns:
        return ["No health impact data available for this dataset."]

    group = df[
        (df["Age"] == age) & (df["Gender"] == gender) & (df["Primary_Device"] == device)
    ]["Health_Impacts"]

    if group.empty:
        return ["No health impact data available for this group."]

    counts = group.value_counts()
    top = counts.head(3)

    msgs.append("Most common health impacts among similar users:")
    for impact, cnt in top.items():
        msgs.append(f"- {impact}")

    top_list = list(top.index)

    if limit is None:
        limit = 0

    if screen_time > limit:
        if len(top_list) == 1:
            msgs.append(f"Exceeding limit is linked to {top_list[0]}.")
        else:
            msgs.append(
                f"Exceeding limit is often linked to {', '.join(top_list[:-1])}, and {top_list[-1]}."
            )
    else:
        if "None" in top_list or "No impacts" in top_list:
            msgs.append("Good news! Most similar users report no health impacts.")

    return msgs


def _risk_level(screen_time, limit):
    if limit is None or limit == 0:
        return ["Risk Level Assessment : Data not available."]
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
    if "Age" not in df_counts.columns or "Health_Impacts_count" not in df_counts.columns or "Primary_Device" not in df_counts.columns:
        return ["No device recommendations available."]
    subset = df_counts[df_counts["Age"] == age]
    if subset.empty:
        return ["No device recommendations available."]
    # use idxmin safely
    try:
        row = subset.loc[subset["Health_Impacts_count"].idxmin()]
        best = row["Primary_Device"]
    except Exception:
        return ["No device recommendation could be computed."]
    if device != best:
        msgs.append(f"DEVICE TYPE ADVICE : Consider switching from '{device}' to '{best}' as it is associated with fewer health impacts for your peer group.")
    else:
        msgs.append(f"'{device}' is already the healthiest choice for your age group.")
    return msgs


def recommendation(age, gender, device, edu_time, rec_time) -> List[str]:
    """
    Main entry point. Returns list of messages.
    """
    try:
        # normalize simple types
        age = int(age)
        gender = str(gender).capitalize()
        device = str(device).title()
        edu_time = float(edu_time)
        rec_time = float(rec_time)
    except Exception as e:
        return [f"Invalid input types: {e}"]

    screen_time = edu_time + rec_time

    # Filter group row
    row = _filter_group(age, gender, device, Indian_Kids_Screen_Time_Cleaned)
    if row is None:
        return [f"No matching data found for given inputs: age={age}, gender={gender}, device={device}."]

    msgs = []
    msgs += _user_summary(age, gender, device, edu_time, rec_time, screen_time)
    msgs += _threshold_analysis(screen_time, row, age, gender)
    msgs += _group_comparison(screen_time, row, age, gender, device)
    msgs += _age_only_comparison(screen_time, row, age)
    msgs += _edu_comparison(edu_time, row, age, gender, device)
    msgs += _rec_comparison(rec_time, row, age, gender, device)
    msgs += _edu_rec_ratio(edu_time, rec_time, age, recom_df2)
    msgs += _health_impacts(age, gender, device, recom_df2, Health_Impacts_count_df, screen_time, _col_value_or_default(row, "Threshold_Limit_hr", default=0))
    msgs += _risk_level(screen_time, _col_value_or_default(row, "Threshold_Limit_hr", default=0))
    msgs += _device_recommendation(age, device, Health_Impacts_count_df)

    return msgs
