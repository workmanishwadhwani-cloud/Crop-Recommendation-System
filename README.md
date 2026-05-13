<<<<<<< HEAD
# 🌿 CropAI — Crop Recommendation System Using Machine Learning

An AI-powered web application that recommends the most suitable crops for cultivation based on soil nutrients and climate conditions. Built with Flask and Scikit-learn, with a modern glassmorphism UI.

---

## 🚀 Features

- **Top-3 Crop Recommendations** — Returns the best 3 matching crops ranked by ML model confidence score
- **Crop Details** — Each recommendation includes growing season, water requirements, and a farming tip
- **Prediction History** — All predictions are saved to a local SQLite database and shown in a history table
- **Input Validation** — Graceful error handling for invalid or missing inputs
- **Modern UI** — Dark green glassmorphism design, animated background, fully responsive (mobile/tablet/desktop)
- **AJAX Predictions** — No page reload; results appear instantly via `fetch()` API
- **Print Support** — Clean print stylesheet to export your recommendation
- **REST API** — `/predict` and `/api/history` JSON endpoints for easy integration

---

## 🧠 How It Works

The system takes 7 input parameters:

| Parameter | Unit | Description |
|---|---|---|
| Nitrogen (N) | mg/kg | Nitrogen content in soil |
| Phosphorus (P) | mg/kg | Phosphorus content in soil |
| Potassium (K) | mg/kg | Potassium content in soil |
| Temperature | °C | Average ambient temperature |
| Humidity | % | Relative humidity |
| pH | — | Soil pH level (0–14) |
| Rainfall | mm | Annual rainfall |

These features are scaled using **MinMaxScaler** + **StandardScaler**, then passed to a trained **Random Forest** classifier that predicts from **22 possible crops**.

---

## 🗂️ Project Structure

```
Crop-Recommendation-System/
├── app.py                  # Flask backend (API endpoints, model inference, SQLite)
├── model.pkl               # Trained ML model (Random Forest)
├── standscaler.pkl         # StandardScaler fitted on training data
├── minmaxscaler.pkl        # MinMaxScaler fitted on training data
├── Crop_recommendation.csv # Original dataset
├── requirements.txt        # Python dependencies
├── history.db              # SQLite database (auto-created on first run)
│
├── templates/
│   └── index.html          # Main UI (Jinja2 template)
│
├── static/
│   ├── style.css           # Dark green glassmorphism stylesheet
│   ├── script.js           # AJAX form, result rendering, history loading
│   └── img.jpg             # Crop field image asset
│
└── Crop Classification With Recommendation System.ipynb  # Training notebook
```

---

## 🛠️ Technologies Used

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **ML** | Scikit-learn (Random Forest), NumPy, Pandas |
| **Database** | SQLite (via Python `sqlite3`) |
| **Frontend** | HTML5, Vanilla CSS (Glassmorphism), JavaScript (ES6+) |
| **Fonts** | Google Fonts — Inter |

---

## ⚙️ Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/611noorsaeed/Crop-Recommendation-System-Using-Machine-Learning.git
cd Crop-Recommendation-System-Using-Machine-Learning
```

### 2. Create & activate a virtual environment
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 📡 API Reference

### `POST /predict`
Accepts JSON body and returns top-3 crop recommendations.

**Request:**
```json
{
  "Nitrogen": 90,
  "Phosporus": 42,
  "Potassium": 43,
  "Temperature": 25.5,
  "Humidity": 80.0,
  "Ph": 6.5,
  "Rainfall": 202.0
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "name": "Rice",
      "confidence": 94.2,
      "emoji": "🌾",
      "season": "Kharif (Jun–Nov)",
      "water": "High",
      "tip": "Thrives in flooded fields with high humidity."
    }
  ]
}
```

### `GET /api/history`
Returns the last 10 predictions from the SQLite database.

---

## 🌾 Supported Crops (22)

Rice, Maize, Jute, Cotton, Coconut, Papaya, Orange, Apple, Muskmelon, Watermelon, Grapes, Mango, Banana, Pomegranate, Lentil, Blackgram, Mungbean, Mothbeans, Pigeonpeas, Kidneybeans, Chickpea, Coffee

---

## 🔮 Future Enhancements

- 🌦️ Auto-fetch live weather data via OpenWeatherMap API (temperature, humidity, rainfall by location)
- 📱 Mobile app using React Native or Flutter
- 📊 Crop market price integration for profitability analysis
- 🗺️ Location-based region mapping for automated soil data lookup
- 🔐 User authentication and personal prediction dashboard

---

## 📄 License

This project is open-source and available for educational and research purposes.
=======
# Crop-Recommendation-System
>>>>>>> de1d85dbb48aec193134a46cea8527d3c185068c
