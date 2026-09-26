from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

DATA_PATH = Path(__file__).with_name('training_data.csv')
MODEL_PATH = Path(__file__).with_name('priority_model.joblib')

if not DATA_PATH.exists():
    raise SystemExit(f'Missing {DATA_PATH}. Run generate_simulation_data.py first or provide your own CSV.')

data = pd.read_csv(DATA_PATH)
required = {'severity_points', 'people_affected', 'priority_score'}
if not required.issubset(data.columns):
    raise SystemExit(f'CSV must contain columns: {sorted(required)}')

features = data[['severity_points', 'people_affected']]
target = data['priority_score']
train_features, test_features, train_target, test_target = train_test_split(features, target, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(train_features, train_target)
error = mean_absolute_error(test_target, model.predict(test_features))
joblib.dump(model, MODEL_PATH)
print(f'Model saved to {MODEL_PATH}')
print(f'Test mean absolute error: {error:.3f}')
