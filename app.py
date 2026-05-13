from flask import Flask, request, render_template, jsonify
import numpy as np
import pickle
import sqlite3
import os
from datetime import datetime

# ── Load models ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model = pickle.load(open(os.path.join(BASE_DIR, 'model.pkl'), 'rb'))
    # Correct order: StandardScaler is applied FIRST, MinMaxScaler SECOND
    sc    = pickle.load(open(os.path.join(BASE_DIR, 'standscaler.pkl'), 'rb'))  # step 1
    ms    = pickle.load(open(os.path.join(BASE_DIR, 'minmaxscaler.pkl'), 'rb'))  # step 2
except FileNotFoundError as e:
    raise SystemExit(f"[ERROR] Model file not found: {e}. "
                     "Make sure model.pkl, standscaler.pkl, and minmaxscaler.pkl exist.")

app = Flask(__name__)
DB_PATH = os.path.join(BASE_DIR, 'history.db')

# ── Crop metadata ─────────────────────────────────────────────────────────────
CROP_DICT = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut",
    6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon",
    11: "Grapes", 12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil",
    16: "Blackgram", 17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas",
    20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

CROP_INFO = {
    "Rice":        {"emoji": "🌾", "season": "Kharif (Jun–Nov)",  "water": "High",        "tip": "Thrives in flooded fields with high humidity and warm temperatures."},
    "Maize":       {"emoji": "🌽", "season": "Kharif & Rabi",    "water": "Medium",      "tip": "Versatile crop; grows well in well-drained loamy soil."},
    "Jute":        {"emoji": "🌿", "season": "Kharif (Mar–Jun)", "water": "High",        "tip": "Thrives in warm humid climate with heavy rainfall."},
    "Cotton":      {"emoji": "🌸", "season": "Kharif (Apr–Jun)", "water": "Medium",      "tip": "Requires long frost-free periods with plenty of sunshine."},
    "Coconut":     {"emoji": "🥥", "season": "Year-round",       "water": "Medium",      "tip": "Coastal crop; tolerates saline-sandy soils."},
    "Papaya":      {"emoji": "🍈", "season": "Year-round",       "water": "Medium",      "tip": "Fast-growing; sensitive to waterlogging and frost."},
    "Orange":      {"emoji": "🍊", "season": "Winter (Nov–Feb)", "water": "Medium",      "tip": "Requires well-drained soil and full sun exposure."},
    "Apple":       {"emoji": "🍎", "season": "Summer (Jun–Sep)", "water": "Medium",      "tip": "Needs cold winters for proper dormancy and fruiting."},
    "Muskmelon":   {"emoji": "🍈", "season": "Summer (Feb–May)", "water": "Low-Medium",  "tip": "Warm-season crop; requires well-drained sandy loam soil."},
    "Watermelon":  {"emoji": "🍉", "season": "Summer (Feb–May)", "water": "Medium",      "tip": "Needs long warm season; very sensitive to frost."},
    "Grapes":      {"emoji": "🍇", "season": "Winter (Nov–Mar)", "water": "Medium",      "tip": "Prefers well-drained soil and hot, dry summers."},
    "Mango":       {"emoji": "🥭", "season": "Summer (Mar–Jun)", "water": "Low-Medium",  "tip": "Tropical fruit tree; needs a dry season during flowering."},
    "Banana":      {"emoji": "🍌", "season": "Year-round",       "water": "High",        "tip": "Thrives in tropical climate with uniform rainfall."},
    "Pomegranate": {"emoji": "🍹", "season": "Summer (Mar–May)", "water": "Low",         "tip": "Drought-tolerant; grows best in hot, dry climates."},
    "Lentil":      {"emoji": "🫘", "season": "Rabi (Oct–Mar)",   "water": "Low",         "tip": "Cool-season legume; tolerates drought conditions."},
    "Blackgram":   {"emoji": "🫘", "season": "Kharif (Jun–Sep)", "water": "Low-Medium",  "tip": "Thrives in tropical regions with moderate rainfall."},
    "Mungbean":    {"emoji": "🫘", "season": "Kharif (Jun–Sep)", "water": "Low-Medium",  "tip": "Short-duration crop; tolerates semi-arid conditions."},
    "Mothbeans":   {"emoji": "🫘", "season": "Kharif (Jun–Sep)", "water": "Low",         "tip": "Drought-resistant; grows in arid and semi-arid regions."},
    "Pigeonpeas":  {"emoji": "🫘", "season": "Kharif (Jun–Oct)", "water": "Low",         "tip": "Drought-tolerant perennial; fixes atmospheric nitrogen."},
    "Kidneybeans": {"emoji": "🫘", "season": "Kharif (Jun–Sep)", "water": "Medium",      "tip": "Prefers cool temperatures especially during pod development."},
    "Chickpea":    {"emoji": "🫘", "season": "Rabi (Oct–Feb)",   "water": "Low",         "tip": "Cool-season legume; thrives in well-drained soil."},
    "Coffee":      {"emoji": "☕", "season": "Year-round",       "water": "Medium-High", "tip": "Shade-loving; grows best at high altitudes with rich soil."},
}


# ── Database helpers ──────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                N           REAL,
                P           REAL,
                K           REAL,
                temperature REAL,
                humidity    REAL,
                ph          REAL,
                rainfall    REAL,
                result      TEXT,
                confidence  REAL,
                timestamp   TEXT
            )
        ''')
        conn.commit()


# Run DB init once (guarded so the debug reloader doesn't run it twice)
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    init_db()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/predict", methods=['POST'])
def predict():
    # ── Parse & validate input ─────────────────────────────────────────
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No JSON body received.'}), 400

        N        = float(data['Nitrogen'])
        P        = float(data['Phosporus'])
        K        = float(data['Potassium'])
        temp     = float(data['Temperature'])
        humidity = float(data['Humidity'])
        ph       = float(data['Ph'])
        rainfall = float(data['Rainfall'])
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {e}. Please enter valid numeric values.'}), 400

    # ── Predict ────────────────────────────────────────────────────────
    features = np.array([[N, P, K, temp, humidity, ph, rainfall]])
    try:
        # Correct pipeline: StandardScaler first, then MinMaxScaler
        scaled = sc.transform(features)  # step 1: StandardScaler
        final  = ms.transform(scaled)    # step 2: MinMaxScaler
    except Exception as e:
        return jsonify({'error': f'Scaling error: {e}'}), 500

    recommendations = []
    try:
        proba        = model.predict_proba(final)[0]
        top3_idx     = np.argsort(proba)[::-1][:3]
        for idx in top3_idx:
            label = int(model.classes_[idx])
            name  = CROP_DICT.get(label, f"Crop {label}")
            info  = CROP_INFO.get(name, {})
            recommendations.append({
                'name':       name,
                'confidence': round(float(proba[idx]) * 100, 1),
                'emoji':      info.get('emoji', '🌱'),
                'season':     info.get('season', 'N/A'),
                'water':      info.get('water', 'N/A'),
                'tip':        info.get('tip', ''),
            })
    except AttributeError:
        # Model does not support predict_proba – fall back to plain predict
        try:
            label = int(model.predict(final)[0])
            name  = CROP_DICT.get(label, "Unknown")
            info  = CROP_INFO.get(name, {})
            recommendations = [{
                'name':       name,
                'confidence': 100.0,
                'emoji':      info.get('emoji', '🌱'),
                'season':     info.get('season', 'N/A'),
                'water':      info.get('water', 'N/A'),
                'tip':        info.get('tip', ''),
            }]
        except Exception as e:
            return jsonify({'error': f'Prediction failed: {e}'}), 500
    except Exception as e:
        return jsonify({'error': f'Prediction error: {e}'}), 500

    if not recommendations:
        return jsonify({'error': 'Could not determine a suitable crop.'}), 400

    # ── Save to history ────────────────────────────────────────────────
    try:
        with get_db() as conn:
            conn.execute(
                '''INSERT INTO predictions
                   (N, P, K, temperature, humidity, ph, rainfall,
                    result, confidence, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (N, P, K, temp, humidity, ph, rainfall,
                 recommendations[0]['name'],
                 recommendations[0]['confidence'],
                 datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
            conn.commit()
    except sqlite3.Error as e:
        # Log but don't fail the request
        app.logger.warning("DB insert failed: %s", e)

    return jsonify({'recommendations': recommendations})


@app.route("/api/history")
def history():
    try:
        with get_db() as conn:
            rows = conn.execute(
                '''SELECT id, N, P, K, temperature, humidity, ph, rainfall,
                          result, confidence, timestamp
                   FROM predictions
                   ORDER BY id DESC
                   LIMIT 10'''
            ).fetchall()
        return jsonify({'history': [dict(r) for r in rows]})
    except sqlite3.Error as e:
        app.logger.error("History fetch failed: %s", e)
        return jsonify({'history': [], 'error': str(e)}), 500


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_production = os.environ.get("ENVIRONMENT") == "production"
    app.run(debug=not is_production, host="0.0.0.0", port=port, use_reloader=False)