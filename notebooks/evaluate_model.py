import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

def run_diagnostic_suite():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("🛰️ Loading Combined Datasets and Evaluation Weights...")
    df = pd.read_csv(os.path.join(base_dir, 'data', 'news_combined.csv')).dropna()
    
    # Re-verify and unpack the serialized feature matrices
    vectorizer = joblib.load(os.path.join(base_dir, 'model', 'tfidf_vectorizer.pkl'))
    model = joblib.load(os.path.join(base_dir, 'model', 'fake_news_model.pkl'))
    
    print("✨ Transforming strings to vectorized token matrices...")
    X = vectorizer.transform(df['content'])
    y = df['label'].values
    
    # 1. Compute Stratified K-Fold Cross Validation
    print("🧮 Calculating 5-Fold Stratified Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
    print(f"-> Cross-Validation Accuracy Iterations: {cv_scores}")
    print(f"-> Stable Cross-Validated Accuracy Mean: {np.mean(cv_scores)*100:.2f}%")
    
    # 2. Extract Precision-Recall & Local Confidence Metrics
    y_pred = model.predict(X)
    y_probs = model.predict_proba(X)[:, 1]
    
    print("\n📊 Micro-Level Precision & Recall Statistics:")
    print(classification_report(y, y_pred, target_names=['Class 0: Fake', 'Class 1: True']))
    
    # 3. Compute Confusion Matrix Elements
    print("📐 Matrix Configuration Profile:")
    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
    print(f"True Negatives: {tn}  ||  False Positives: {fp}")
    print(f"False Negatives: {fn}  ||  True Positives: {tp}")
    
    # 4. Area Under the ROC Curve Telemetry
    auc_score = roc_auc_score(y, y_probs)
    print(f"\n📈 Receiver Operating Characteristic Area Under Curve Score: {auc_score:.4f}")

if __name__ == "__main__":
    run_diagnostic_suite()