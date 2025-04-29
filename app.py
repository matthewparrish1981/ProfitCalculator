# app.py (updated - New Calculation Page)

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
    layout="wide",
)

# Sidebar Navigation
st.sidebar.image("https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("New Calculation", "Saved Calculations", "Configuration"))

# Session state for dynamic products
if "products" not in st.session_state:
    st.session_state.products = []

def add_product():
    st.session_state.products.append({
        "product_name": "",
        "description": "",
        "shipping_type": "Sea",
        "quantity": 0,
        "cogs_gbp": 0.0,
        "rrp_usd": 0.0
    })

def remove_product(index):
    st.session_state.products.pop(index)

# New Calculation Page
if page == "New Calculation":
    st.title("\U0001F4C8 New Profitability Calculation")

    st.subheader("Enter Product Details")

    if st.button("+ Add Product"):
        add_product()

    for index, product in enumerate(st.session_state.products):
        with st.expander(f"Product {index+1}", expanded=True):
            cols = st.columns(2)

            product_names = [prod["name"] for prod in config.get("products", [])]
            selected_product_name = cols[0].selectbox("Product Name", product_names, index=product_names.index(product["product_name"]) if product["product_name"] in product_names else 0, key=f"product_name_{index}")

            description = cols[1].text_input("Description", value=product["description"], key=f"description_{index}")

            shipping_type = cols[0].selectbox("Shipping Type", ["Sea", "Air"], index=["Sea", "Air"].index(product["shipping_type"]) if product["shipping_type"] in ["Sea", "Air"] else 0, key=f"shipping_type_{index}")

            quantity = cols[1].number_input("Quantity", min_value=0, value=product["quantity"], step=1, key=f"quantity_{index}")

            selected_product = next((prod for prod in config.get("products", []) if prod["name"] == selected_product_name), None)

            if selected_product:
                if shipping_type == "Sea":
                    cogs_gbp = selected_product.get("cogs_gbp_sea", 0.0)
                else:
                    cogs_gbp = selected_product.get("cogs_gbp_air", 0.0)
                default_rrp_usd = selected_product.get("default_rrp_usd", 0.0)
            else:
                cogs_gbp = 0.0
                default_rrp_usd = 0.0

            rrp_usd = cols[0].number_input("RRP USD", value=product.get("rrp_usd", default_rrp_usd), key=f"rrp_usd_{index}")

            # Update session state with selections
            st.session_state.products[index]["product_name"] = selected_product_name
            st.session_state.products[index]["description"] = description
            st.session_state.products[index]["shipping_type"] = shipping_type
            st.session_state.products[index]["quantity"] = quantity
            st.session_state.products[index]["cogs_gbp"] = cogs_gbp
            st.session_state.products[index]["rrp_usd"] = rrp_usd

            st.write(f"COGS GBP: **£{round(cogs_gbp, 2)}**")

            if st.button(f"❌ Remove Product {index+1}", key=f"remove_{index}"):
                remove_product(index)
                st.experimental_rerun()

    if st.session_state.products:
        st.markdown("---")
        st.subheader("📋 Preview of Products Added")
        preview_data = []
        for p in st.session_state.products:
            exchange_rate = config.get("exchange_rate", 1.25)
            cogs_usd = p["cogs_gbp"] * exchange_rate
            gmv_usd = p["quantity"] * p["rrp_usd"]
            gm_percentage = ((p["rrp_usd"] - cogs_usd) / p["rrp_usd"]) if p["rrp_usd"] else 0
            gm_value = gmv_usd * gm_percentage

            preview_data.append({
                "Product": p["product_name"],
                "Description": p["description"],
                "Shipping": p["shipping_type"],
                "Quantity": p["quantity"],
                "COGS GBP": round(p["cogs_gbp"], 2),
                "COGS USD": round(cogs_usd, 2),
                "RRP USD": round(p["rrp_usd"], 2),
                "GMV USD": round(gmv_usd, 2),
                "GM %": f"{round(gm_percentage * 100, 2)}%",
                "GM Value USD": round(gm_value, 2)
            })

        preview_df = pd.DataFrame(preview_data)
        st.dataframe(preview_df)

    if st.session_state.products:
        st.markdown("---")
        if st.button("➡️ Proceed to Cost Inputs"):
            st.success("Next section coming soon: Fixed Fees, Influencer Content, Paid Ads input, Full P&L Calculation!")  # Placeholder for next development

# (Saved Calculations and Configuration pages remain same as posted before)
