# app.py

import streamlit as st
import pandas as pd
import os
import json
from utils import load_config, save_config, calculate_results, save_calculation, load_saved_calculations

# Ensure calculations folder exists
os.makedirs("calculations", exist_ok=True)

# Load configuration
config = load_config()

# Set page configuration
st.set_page_config(
    page_title="Trtl Profitability Calculator",
    page_icon="https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png",
    layout="centered",
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stButton>button {
        background-color: #FFD500;
        color: black;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        font-size: 16px;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div>input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("New Calculation", "Saved Calculations", "Configuration"))

# New Calculation Page
if page == "New Calculation":
    st.title("\U0001F4C8 New Profitability Calculation")
    st.write("🚧 **Product Entry form coming here next based on our latest conversation.**")

# Saved Calculations Page
elif page == "Saved Calculations":
    st.title("\U0001F4C1 Saved Calculations")
    saved_files = load_saved_calculations()

    for file in saved_files:
        with st.expander(file["name"]):
            st.write(file["data"])
            st.download_button("Download as CSV", data=file["csv"], file_name=f"{file['name']}.csv", mime="text/csv")

# Configuration Page
elif page == "Configuration":
    st.title("\u2699\ufe0f Reference Data Configuration")

    with st.form("config_form"):
        st.subheader("Exchange Rate (GBP ➔ USD)")
        exchange_rate = st.number_input("Exchange Rate", value=config.get("exchange_rate", 1.25))

        st.subheader("3PL Shipping Cost per Unit (GBP)")
        shipping_cost_per_unit_3pl = st.number_input("3PL Cost (GBP)", value=config.get("shipping_cost_per_unit_3pl", 2.00))

        st.subheader("Manage Products")
        products = config.get("products", [])

        updated_products = []
        for i, product in enumerate(products):
            with st.expander(f"Edit Product {i+1}: {product['name']}"):
                name = st.text_input(f"Product Name {i+1}", value=product["name"], key=f"name_{i}")
                cogs_sea = st.number_input(f"COGS GBP (Sea) {i+1}", value=product["cogs_gbp_sea"], key=f"sea_{i}")
                cogs_air = st.number_input(f"COGS GBP (Air) {i+1}", value=product["cogs_gbp_air"], key=f"air_{i}")
                rrp_usd = st.number_input(f"Default RRP USD {i+1}", value=product.get("default_rrp_usd", 0.0), key=f"rrp_{i}")
                updated_products.append({"name": name, "cogs_gbp_sea": cogs_sea, "cogs_gbp_air": cogs_air, "default_rrp_usd": rrp_usd})

        st.markdown("---")
        st.subheader("Add New Product")
        new_product_name = st.text_input("New Product Name", key="new_product_name")
        new_cogs_sea = st.number_input("New COGS GBP (Sea)", value=0.0, key="new_cogs_sea")
        new_cogs_air = st.number_input("New COGS GBP (Air)", value=0.0, key="new_cogs_air")
        new_rrp_usd = st.number_input("New Default RRP USD", value=0.0, key="new_rrp_usd")

        if new_product_name:
            updated_products.append({"name": new_product_name, "cogs_gbp_sea": new_cogs_sea, "cogs_gbp_air": new_cogs_air, "default_rrp_usd": new_rrp_usd})

        save_config_button = st.form_submit_button("Save Configuration")

    if save_config_button:
        new_config = {
            "products": updated_products,
            "shipping_options": ["Sea", "Air"],
            "exchange_rate": exchange_rate,
            "shipping_cost_per_unit_3pl": shipping_cost_per_unit_3pl
        }
        save_config(new_config)
        st.success("Configuration saved!")
