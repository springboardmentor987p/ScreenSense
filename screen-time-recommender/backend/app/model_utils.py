import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")

TARGET_COL = "Avg_Daily_Screen_Time_hr"

def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)

def train_save_model(dataset_path):
    df = load_dataset(dataset_path)

    # Use same columns as API expects
    feature_cols = [
        "Age",
        "Gender",
        "Primary_Device",
        "Educational_to_Recreational_Ratio",
        "Exceeded_Recommended_Limit",
        "Urban_or_Rural",
        "Health_Impacts"
    ]

    X = df[feature_cols]
    y = df[TARGET_COL]

    categorical_cols = ["Gender", "Primary_Device", "Exceeded_Recommended_Limit", 
                        "Urban_or_Rural", "Health_Impacts"]

    numeric_cols = ["Age", "Educational_to_Recreational_Ratio"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", MinMaxScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ]
    )

    model = RandomForestRegressor()

    pipeline = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X, y)

    with open("model.pkl", "wb") as f:
        pickle.dump(pipeline, f)

    print("Model trained and saved as model.pkl")
