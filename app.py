import streamlit as st
import pandas as pd
import os
import json
from utils import (
    load_config,
    save_config,
    calculate_results,
    save_calculation,
    load_saved_calculations,
    load_calculation_by_name
)

os.makedirs("calculations", exist_ok=True)
config = load_config()

st.set_page_config(
    page_title="Trtl Profitability Calculator",
    page_icon="https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png?v=1695992032",
    layout="wide",
)

st.sidebar.image("https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png?v=1695992032", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("New Calculation", "Saved Calculations", "Configuration"))

# Initialise state
if "products" not in st.session_state:
    st.session_state.products = []
if "costs" not in st.session_state:
    st.session_state.costs = {}
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "loaded_calc_name" not in st.session_state:
    st.session_state.loaded_calc_name = ""

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

def reset_calculation_state():
    st.session_state.products = []
    st.session_state.costs = {}
    st.session_state.edit_mode = False
    st.session_state.loaded_calc_name = ""

# New Calculation Page
if page == "New Calculation":
    st.title("🧮 New Profitability Calculation")

    if st.button("➕ Add Product"):
        add_product()

    for index, product in enumerate(st.session_state.products):
        with st.expander(f"Product {index + 1}", expanded=True):
            cols = st.columns(2)
            product_names = [prod["name"] for prod in config.get("products", [])]

            selected_product_name = cols[0].selectbox(
                "Product Name", product_names,
                index=product_names.index(product["product_name"]) if product["product_name"] in product_names else 0,
                key=f"product_name_{index}"
            )

            description = cols[1].text_input("Description", value=product["description"], key=f"description_{index}")
            shipping_type = cols[0].selectbox("Shipping Type", ["Sea", "Air"], key=f"shipping_type_{index}")
            quantity = cols[1].number_input("Quantity", min_value=0, value=product["quantity"], step=1, key=f"quantity_{index}")

            selected_product = next((prod for prod in config["products"] if prod["name"] == selected_product_name), None)
            if selected_product:
                cogs_gbp = selected_product["cogs_gbp_sea"] if shipping_type == "Sea" else selected_product["cogs_gbp_air"]
                default_rrp_usd = selected_product.get("default_rrp_usd", 0.0)
            else:
                cogs_gbp = 0.0
                default_rrp_usd = 0.0

            rrp_usd = cols[0].number_input("RRP USD", value=product.get("rrp_usd", default_rrp_usd), key=f"rrp_usd_{index}")

            st.session_state.products[index] = {
                "product_name": selected_product_name,
                "description": description,
                "shipping_type": shipping_type,
                "quantity": quantity,
                "cogs_gbp": cogs_gbp,
                "rrp_usd": rrp_usd
            }

            st.write(f"COGS GBP: £{round(cogs_gbp, 2)}")

            if st.button(f"❌ Remove Product {index + 1}", key=f"remove_{index}"):
                remove_product(index)
                st.experimental_rerun()

    if st.session_state.products:
        st.markdown("---")
        st.subheader("📋 Preview of Products")
        preview_data = []

        for i, p in enumerate(st.session_state.products, start=1):
            exchange_rate = config.get("exchange_rate", 1.25)
            cogs_usd = p["cogs_gbp"] * exchange_rate
            gmv = p["quantity"] * p["rrp_usd"]
            gm_pct = ((p["rrp_usd"] - cogs_usd) / p["rrp_usd"]) if p["rrp_usd"] else 0
            gm_val = gmv * gm_pct

           preview_data.append({
    "#": i,
    "Product": p["product_name"],
    "Description": p["description"],
    "Shipping": p["shipping_type"],
    "Quantity": p["quantity"],
    "COGS GBP": f"£{round(p['cogs_gbp'], 2)}",
    "COGS USD": f"${round(cogs_usd, 2)}",
    "RRP USD": f"${round(p['rrp_usd'], 2)}",
    "GMV USD": f"${round(gmv, 2)}",
    "GM %": f"{round(gm_pct * 100, 2)}%",
    "GM Value USD": f"${round(gm_val, 2)}"
})
