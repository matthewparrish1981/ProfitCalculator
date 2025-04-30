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

        st.dataframe(pd.DataFrame(preview_data))

        st.markdown("---")
        st.subheader("💸 Cost Inputs")

        with st.form("cost_inputs_form"):
            costs = st.session_state.costs

            col1, col2 = st.columns(2)
            costs["partner_fee_usd"] = col1.number_input("Partner Fee (USD)", value=costs.get("partner_fee_usd", 0.0))
            costs["partner_content_usd"] = col2.number_input("Partner Content (USD)", value=costs.get("partner_content_usd", 0.0))

            col3, col4 = st.columns(2)
            costs["influencer_budget_usd"] = col3.number_input("Influencer Budget (USD)", value=costs.get("influencer_budget_usd", 0.0))
            costs["ugc_budget_usd"] = col4.number_input("UGC Budget (USD)", value=costs.get("ugc_budget_usd", 0.0))

            col5, col6 = st.columns(2)
            costs["paid_ads_gbp"] = col5.number_input("Paid Ad Budget (Standalone, GBP)", value=costs.get("paid_ads_gbp", 0.0))
            costs["commission_percent"] = col6.number_input("Commission % (All Sales)", value=costs.get("commission_percent", 0.0))

            col7, col8 = st.columns(2)
            costs["amazon_fee_percent"] = col7.number_input("Commission % (Affiliate Link)", value=costs.get("amazon_fee_percent", 0.0))
            costs["trtl_content_usd"] = col8.number_input("Trtl Content (USD)", value=costs.get("trtl_content_usd", 0.0))

            col9, col10 = st.columns(2)
            costs["product_gifting_usd"] = col9.number_input("Product Gifting (USD)", value=costs.get("product_gifting_usd", 0.0))
            costs["other_usd"] = col10.number_input("Other Costs (USD)", value=costs.get("other_usd", 0.0))

            submitted = st.form_submit_button("📊 Calculate Full P&L")

        if submitted:
            product_summary, p_and_l_summary = calculate_results(st.session_state.products, costs, config)

            st.subheader("📈 Product Summary Table")
            st.dataframe(pd.DataFrame(product_summary))

            st.subheader("📊 Summary P&L Table")
            st.dataframe(pd.DataFrame([p_and_l_summary]))

            st.session_state.costs = costs
            calc_name = st.text_input("Save Calculation As:", value=st.session_state.loaded_calc_name or "New Calculation")

            if st.button("💾 Save Calculation"):
                save_calculation(
                    calc_name,
                    st.session_state.products,
                    product_summary,
                    p_and_l_summary,
                    costs
                )
                st.success(f"Calculation '{calc_name}' saved!")

elif page == "Saved Calculations":
    st.title("📂 Saved Calculations")
    saved = load_saved_calculations()

    for item in saved:
        with st.expander(item["name"]):
            st.download_button("📥 Download CSV", item["csv"], file_name=f"{item['name']}.csv")
            if st.button(f"✏️ Load & Edit '{item['name']}'", key=f"edit_{item['name']}"):
                data = item["data"]
                st.session_state.products = data.get("products", [])
                st.session_state.costs = data.get("costs", {})
                st.session_state.edit_mode = True
                st.session_state.loaded_calc_name = item["name"]
                st.success("Calculation loaded. Go to 'New Calculation' to edit.")
                st.experimental_rerun()

elif page == "Configuration":
    st.title("⚙️ Configuration")

    with st.form("config_form"):
        exchange_rate = st.number_input("Exchange Rate (GBP ➝ USD)", value=config.get("exchange_rate", 1.25))
        shipping_cost_per_unit_3pl = st.number_input("3PL Shipping Cost per Unit (GBP)", value=config.get("shipping_cost_per_unit_3pl", 2.00))

        st.subheader("Product List")
        updated_products = []
        for i, prod in enumerate(config.get("products", [])):
            with st.expander(f"Product {i + 1}: {prod['name']}"):
                name = st.text_input(f"Product Name {i}", value=prod["name"], key=f"name_{i}")
                sea = st.number_input(f"COGS GBP (Sea) {i}", value=prod["cogs_gbp_sea"], key=f"sea_{i}")
                air = st.number_input(f"COGS GBP (Air) {i}", value=prod["cogs_gbp_air"], key=f"air_{i}")
                rrp = st.number_input(f"Default RRP USD {i}", value=prod.get("default_rrp_usd", 0.0), key=f"rrp_{i}")
                updated_products.append({
                    "name": name,
                    "cogs_gbp_sea": sea,
                    "cogs_gbp_air": air,
                    "default_rrp_usd": rrp
                })

        st.subheader("➕ Add New Product")
        new_name = st.text_input("New Product Name")
        new_sea = st.number_input("New COGS GBP (Sea)", value=0.0)
        new_air = st.number_input("New COGS GBP (Air)", value=0.0)
        new_rrp = st.number_input("New Default RRP USD", value=0.0)

        if new_name:
            updated_products.append({
                "name": new_name,
                "cogs_gbp_sea": new_sea,
                "cogs_gbp_air": new_air,
                "default_rrp_usd": new_rrp
            })

        if st.form_submit_button("💾 Save Configuration"):
            config = {
                "products": updated_products,
                "shipping_options": ["Sea", "Air"],
                "exchange_rate": exchange_rate,
                "shipping_cost_per_unit_3pl": shipping_cost_per_unit_3pl
            }
            save_config(config)
            st.success("Configuration saved!")
