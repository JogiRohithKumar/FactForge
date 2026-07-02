# run_evaluation.py
import os
import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc

from xgboost import XGBClassifier
from utils.text_processor import clean_text

# 1. System Setup and Directory Verification
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
DATA_PATH = os.path.join(BASE_DIR, 'data', 'news_combined.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'evaluation_metrics')
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading dataset from path:", DATA_PATH)
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Missing combined dataset at {DATA_PATH}. Please run data_preparation.py first.")

df = pd.read_csv(DATA_PATH)

# Ensure text fields are cleanly cast as strings before processing
df['content'] = df['content'].fillna('').astype(str)

print("Executing text cleaning and synchronization pipeline...")
df['cleaned_content'] = df['content'].apply(clean_text)

# 2. Dataset Splitting
X = df['cleaned_content']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. High-Dimensional TF-IDF Vectorization
print("Extracting statistical feature matrices using TF-IDF...")
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 4. Model Registry Framework Setup
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='logloss', n_jobs=-1)
}

# 5. Stratified Cross-Validation Assessment
print("\nExecuting Stratified K-Fold Cross-Validation (K=5)...")
cv_results = {}
cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    print(f"Evaluating validation boundaries for {name}...")
    scores = cross_val_score(model, X_train_vec, y_train, cv=cv_strategy, scoring='accuracy', n_jobs=-1)
    cv_results[name] = scores
    print(f"{name} CV Mean Accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")

# 6. Full Training and Standard Evaluation Loop
trained_models = {}
predictions = {}
probabilities = {}

print("\nExecuting model training and test-set inference tracking...")
for name, model in models.items():
    print(f"Training architecture: {name}...")
    model.fit(X_train_vec, y_train)
    trained_models[name] = model
    
    # Store metrics for diagnostic comparison
    predictions[name] = model.predict(X_test_vec)
    probabilities[name] = model.predict_proba(X_test_vec)[:, 1]
    
    print(f"\nClassification Report for {name}:")
    print(classification_report(y_test, predictions[name], digits=4))

# 7. Diagnostic Visualization Export: Confusion Matrices
print("\nGenerating and saving multi-model Confusion Matrices...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for idx, (name, pred) in enumerate(predictions.items()):
    cm = confusion_matrix(y_test, pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                xticklabels=['Fake', 'True'], yticklabels=['Fake', 'True'])
    axes[idx].set_title(f'{name}\nConfusion Matrix')
    axes[idx].set_xlabel('Predicted Label')
    axes[idx].set_ylabel('True Label')

plt.tight_layout()
cm_plot_path = os.path.join(OUTPUT_DIR, 'confusion_matrices.png')
plt.savefig(cm_plot_path, dpi=300)
plt.close()
print(f"Confusion Matrix comparison grid exported to: {cm_plot_path}")

# 8. Diagnostic Visualization Export: Receiver Operating Characteristic (ROC) Curves
print("Generating and saving comparative ROC curves...")
plt.figure(figsize=(10, 7))

for name, prob in probabilities.items():
    fpr, tpr, _ = roc_curve(y_test, prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.4f})')

plt.plot([0, 1], [0, 1], color='gray', alpha=0.5, lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve Comparison')
plt.legend(loc="lower right")
plt.grid(True, linestyle=':', alpha=0.6)

roc_plot_path = os.path.join(OUTPUT_DIR, 'roc_curve_comparison.png')
plt.savefig(roc_plot_path, dpi=300)
plt.close()
print(f"ROC curve comparison plot exported to: {roc_plot_path}")

print("\nFactForge Pro Machine Learning Phase 2 Evaluation execution successfully complete.")