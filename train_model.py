import pandas as pd
import joblib

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

# Load Dataset
data = pd.read_csv(
    "dataset_combined.csv",
    header=None
)

X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Model
model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# Train
model.fit(
    X_train,
    y_train
)

# Predict
y_pred = model.predict(
    X_test
)

acc = accuracy_score(
    y_test,
    y_pred
)

print("\nAccuracy:", acc)

print(
    classification_report(
        y_test,
        y_pred
    )
)

# Save
joblib.dump(
    model,
    "csi_model.pkl"
)

print("\nModel Saved")