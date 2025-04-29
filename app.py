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
    layout="wide",
)

# Sidebar Navigation
st.sidebar.image("https://cdn.shopify.com/s/files/1/0045/7356/5421/files/trtl-logo-black_250x.png", width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("New Calculation", "Saved Calculations", "Configuration"))

# Session state for dynamic products
if "products" not in st.session_state:
    st.session_state.products = []
if "costs" not in st.session_state:
    st.session_state.costs = {}

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

            # Update session state
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

        st.markdown("---")
        st.subheader("Enter Cost Inputs")

        with st.form("cost_inputs_form"):
            amazon_fee_percent = st.number_input("Amazon Referral Fee %", value=15.0)
            royalty_fee_percent = st.number_input("Royalty Fee %", value=10.0)
            commission_percent = st.number_input("Partner Commission %", value=20.0)

            fixed_fee_usd = st.number_input("Fixed Fee Amount (USD)", value=0.0)
            launch_content_usd = st.number_input("Launch Content (USD)", value=0.0)
            influencer_content_usd = st.number_input("Supporting Influencer Content (USD)", value=0.0)
            ugc_content_usd = st.number_input("UGC Content (USD)", value=0.0)
            product_gifting_usd = st.number_input("Product Gifting (USD)", value=0.0)
            other_usd = st.number_input("Other Costs (USD)", value=0.0)
            paid_ads_gbp = st.number_input("Paid Ads Budget (GBP)", value=0.0)

            submitted = st.form_submit_button("Calculate Full P&L")

        if submitted:
            additional_costs = {
                "amazon_fee_percent": amazon_fee_percent,
                "royalty_fee_percent": royalty_fee_percent,
                "commission_percent": commission_percent,
                "fixed_fee_usd": fixed_fee_usd,
                "launch_content_usd": launch_content_usd,
                "influencer_content_usd": influencer_content_usd,
                "ugc_content_usd": ugc_content_usd,
                "product_gifting_usd": product_gifting_usd,
                "other_usd": other_usd,
                "paid_ads_gbp": paid_ads_gbp,
            }

            product_summary, p_and_l_summary = calculate_results(st.session_state.products, additional_costs, config)

            st.markdown("---")
            st.subheader("📈 Product Summary Table")
            st.dataframe(pd.DataFrame(product_summary))

            st.markdown("---")
            st.subheader("📊 Summary P&L Table")
            st.dataframe(pd.DataFrame([p_and_l_summary]))

            st.markdown("---")
            calc_name = st.text_input("Save Calculation As:", value="New Calculation")
            if st.button("Save Calculation"):
                save_calculation(calc_name, st.session_state.products, product_summary, p_and_l_summary)
                st.success(f"Calculation '{calc_name}' saved!")

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

