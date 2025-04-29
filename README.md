# Trtl Profitability Calculator

This is a Streamlit app to replace the manual profitability Excel sheet.
It allows configuration of products, COGS, RRPs, and calculates profitability, partner income, and margins.

---

## 🛠 How to Set Up

### 1. Create a GitHub Repository

- Go to [github.com](https://github.com/)
- Create a new repository (e.g., `trtl-profitability-calculator`)
- Do NOT initialize with a README (you already have one)
- Clone the repo to your local machine (if you have Git installed)
- OR upload files directly via GitHub web interface

**Upload these files into your repo:**
- `app.py`
- `utils.py`
- `config.json`
- `requirements.txt`
- `.streamlit/config.toml`
- `README.md`

Also create a folder called `/calculations/` (this will automatically fill when you save calculations).

---

### 2. Deploy on Streamlit Cloud

- Go to [streamlit.io/cloud](https://streamlit.io/cloud)
- Create a free Streamlit account
- Click **"New app"**
- Connect your GitHub account
- Choose your GitHub repository
- Select `app.py` as the entry point
- Deploy!

✅ Your app will automatically install from `requirements.txt`
✅ Your app will load using the settings in `.streamlit/config.toml`

---

## 📝 Configuring Products
- Go to the **Configuration** tab in the app
- You can add or edit products (name, COGS Sea/Air, Default RRP USD)
- Update the exchange rate or 3PL costs anytime

---

## 📄 App Features
- Add multiple products per calculation
- Enter quantity, shipping type, description, RRP (defaulted)
- Enter marketing, royalty, commission and other costs
- Full profitability P&L and partner income table
- Save calculations for later retrieval
- Download results as CSV

---

## 🛠 Requirements
- Python 3.9 or later (Streamlit Cloud installs automatically)
- `streamlit`
- `pandas`
- `openpyxl` (optional, for Excel support)

---

## 📬 Questions?
If you have any issues deploying, feel free to create a GitHub issue, or ask for help!

---
