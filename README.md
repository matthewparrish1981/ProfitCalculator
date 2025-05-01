# Trtl Profitability Calculator

A custom-built Streamlit app to calculate product profitability across different scenarios, including COGS, RRP, shipping, commissions, and marketing spend.

---

## 🛠 Features

- Dynamic product entry with default COGS and RRP pulled from config
- Configurable exchange rate and 3PL shipping cost
- Live margin and GMV calculations
- Full P&L breakdown (Amazon fees, commission, influencer, gifting, etc.)
- Save and reopen previous calculations
- Download result tables as CSV
- Fully responsive layout with Trtl branding

---

## 🚀 Deploying on Streamlit Cloud

1. Clone or upload this repo to your GitHub account
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app**
4. Select your repository and set `app.py` as the main file
5. Click **Deploy**

---

## 📁 Folder Structure

```
.
├── app.py
├── utils.py
├── config.json
├── requirements.txt
└── .streamlit/
    └── config.toml
```

The `/calculations/` folder will be created automatically when users save calculations.

---

## 📦 Requirements

- Python 3.9+
- Streamlit
- Pandas
- OpenPyXL (for potential Excel export support)

Install with:

```bash
pip install -r requirements.txt
```

---

## 🧰 Config Fields

`config.json` contains:

- Product list with COGS for Sea and Air
- Default RRP (USD)
- Exchange rate (GBP to USD)
- 3PL shipping cost

---

## 📝 Customisation

You can add/edit products directly in the app under the Configuration page, or by editing `config.json`.

---

Built by Trtl.
