---
description: How to run the Crop Recommendation System
---

// turbo-all
1. Ensure the virtual environment exists and is activated.
2. Install dependencies:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install flask numpy pandas scikit-learn
   ```
3. Run the Flask application:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:5000`