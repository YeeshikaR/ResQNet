from pathlib import Path

import pandas as pd

SEVERITY_POINTS = {'low': 20, 'medium': 50, 'high': 75, 'critical': 100}
OUTPUT = Path(__file__).with_name('training_data.csv')

rows = []
for severity, points in SEVERITY_POINTS.items():
    for people in range(1, 51):
        score = min(points + min(people * 2, 30), 100)
        rows.append({'severity_points': points, 'people_affected': people, 'priority_score': score})

pd.DataFrame(rows).to_csv(OUTPUT, index=False)
print(f'Wrote {len(rows)} rows to {OUTPUT}')
