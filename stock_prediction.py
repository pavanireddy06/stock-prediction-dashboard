import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Step 1: Download data
data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")

print(data.head())

# Step 2: Plot graph
data['Close'].plot(title="Stock Closing Price")
plt.show()

# Step 3: Create lag features
for i in range(1, 6):
    data[f'lag_{i}'] = data['Close'].shift(i)

# Step 4: Target
data['Target'] = (data['Close'] > data['Close'].shift(1)).astype(int)

data.dropna(inplace=True)

# Step 5: Features
X = data[[f'lag_{i}' for i in range(1, 6)]]
y = data['Target']

# Step 6: Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 7: PCA
pca = PCA(n_components=3)
X_pca = pca.fit_transform(X_scaled)

# Step 8: Split
X_train, X_test, y_train, y_test = train_test_split(
    X_pca, y, test_size=0.2, shuffle=False
)

# Step 9: WKNN
model = KNeighborsClassifier(n_neighbors=5, weights='distance')
model.fit(X_train, y_train)

# Step 10: Predict
y_pred = model.predict(X_test)

# Step 11: Accuracy
print("Accuracy:", accuracy_score(y_test, y_pred))

# Extra graph
data['Close'].hist()
plt.title("Histogram")
plt.show()