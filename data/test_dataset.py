# test_dataset.py
import pandas as pd
import numpy as np

# Генерируем синтетические данные
np.random.seed(42)
n = 1000

data = {
    'income': np.random.normal(50000, 15000, n),
    'age': np.random.randint(18, 70, n),
    'spend_score': np.random.randint(1, 100, n),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n),
    'loyalty_tier': np.random.choice(['Basic', 'Silver', 'Gold'], n, p=[0.6, 0.3, 0.1]),
    'is_premium': np.random.choice([0, 1], n, p=[0.7, 0.3])  # Целевая переменная
}

# Сделаем так, чтобы income и age коррелировали с is_premium
data['income'] += data['is_premium'] * 20000
data['age'] = data['age'] + data['is_premium'] * 10

df = pd.DataFrame(data)

# Сохраняем
df.to_csv("data/test_data.csv", index=False)
print("✅ Датасет создан: data/test_data.csv")
print(df.head())