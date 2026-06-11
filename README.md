# 📰 Detecting Misinformation Through Machine Learning

A simple yet effective machine learning application that detects whether a news article is **fake** or **real** based on its content. Built with Python, Scikit-learn, and Streamlit for an interactive web interface.

---
## explore it here: 
https://try-fake-news-detector.streamlit.app/
---

## 🚀 Features

- Combines real and fake news datasets
- Cleans and vectorizes text using TF-IDF
- Trains a Logistic Regression classifier
- Saves trained model and vectorizer using `joblib`
- Provides a Streamlit web interface to classify news articles in real-time

---

## 🧠 Dataset

- **Source:** [Kaggle Fake and Real News Dataset](https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset)
- Two CSV files:
  - `Fake.csv`: Contains fake news articles
  - `True.csv`: Contains real news articles

---

## 🛠️ Folder Structure

```
FakeNewsDetection/
├── app/
│   └── streamlit_app.py       # Streamlit frontend
├── data/
│   ├── Fake.csv
│   ├── True.csv
│   └── news_combined.csv      # Combined + cleaned data
├── model/
│   ├── fake_news_model.pkl    # Trained model
│   └── tfidf_vectorizer.pkl   # Fitted TF-IDF vectorizer
├── model_training.py          # Model training + saving
├── data_preparation.py        # Dataset preprocessing
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

---

## ⚙️ How to Run

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/FakeNewsDetection.git
cd FakeNewsDetection
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Prepare Data

```bash
python data_preparation.py
```

### 4️⃣ Train the Model

Make sure `model/` folder exists:
```bash
mkdir model
```

Then run:
```bash
python model_training.py
```

### 5️⃣ Launch the App

Navigate to the `app/` folder and run:

```bash
streamlit run streamlit_app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💻 Tech Stack

- Python 🐍
- Scikit-learn
- Pandas
- NLTK
- Joblib
- Streamlit 🚀

---

## 📌 To-Do / Future Ideas

- Improve model with more advanced NLP (BERT, LSTM)
- Deploy on Streamlit Cloud or HuggingFace Spaces
- Add drag-and-drop PDF/news URL input
- Add confidence/probability score

---

## 🙌 Acknowledgements

- Dataset by [Clément Bisaillon](https://www.kaggle.com/clmentbisaillon)
- Streamlit for UI
- Scikit-learn and NLTK for ML and preprocessing

---

## 📜 License

MIT License – feel free to use and modify!

---

## 🌐 Connect

Made with Jogi RohithKumar 
🔗 [LinkedIn](https://www.linkedin.com/in/rohith-kumar-jogi-747a782b8/)
```
