import json
import os
import pandas as pd

CONFIG_FILE = "config.json"
CALCULATIONS_FOLDER = "calculations"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"products": [], "shipping_options": ["Sea", "Air"], "exchange_rate": 1.25, "shipping_cost_per_unit_3pl": 2.00}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

def save_calculation(calc_name, product_data_list, summary, p_and_l_summary, costs):
    if not os.path.exists(CALCULATIONS_FOLDER):
        os.makedirs(CALCULATIONS_FOLDER)
    save_data = {
        "name": calc_name,
        "products": product_data_list,
        "summary": summary,
        "p_and_l_summary": p_and_l_summary,
        "costs": costs
    }
    file_path = os.path.join(CALCULATIONS_FOLDER, f"{calc_name}.json")
    with open(file_path, "w") as f:
        json.dump(save_data, f, indent=4)

def load_saved_calculations():
    saved = []
    if not os.path.exists(CALCULATIONS_FOLDER):
        return saved
    for filename in os.listdir(CALCULATIONS_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(CALCULATIONS_FOLDER, filename), "r") as f:
                data = json.load(f)
                csv_data = pd.DataFrame(data["products"]).to_csv(index=False)
                saved.append({"name": data.get("name", "Unnamed"), "data": data, "csv": csv_data})
    return saved

def load_calculation_by_name(name):
    filepath = os.path.join(CALCULATIONS_FOLDER, f"{name}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)

def calculate_results(products, additional_costs, config):
    exchange_rate = config.get("exchange_rate", 1.25)
    shipping_cost_per_unit_3pl_gbp = config.get("shipping_cost_per_unit_3pl", 2.0)

    product_summaries = []
    total_revenue = 0
    total_cogs_usd = 0
    total_units = 0

    for product in products:
        quantity = product["quantity"]
        cogs_gbp = product["cogs_gbp"]
        rrp_usd = product["rrp_usd"]
        cogs_usd = cogs_gbp * exchange_rate
        gmv_usd = quantity * rrp_usd
        gm_percentage = (rrp_usd - cogs_usd) / rrp_usd if rrp_usd else 0
        gm_value = gmv_usd * gm_percentage

        product_summary = {
            "Product": product["product_name"],
            "Description": product["description"],
            "Shipping Type": product["shipping_type"],
            "Quantity": quantity,
            "COGS GBP": f"£{round(cogs_gbp, 2)}",
            "COGS USD": f"${round(cogs_usd, 2)}",
            "RRP USD": f"${round(rrp_usd, 2)}",
            "GMV USD": f"${round(gmv_usd, 2)}",
            "GM %": f"{round(gm_percentage * 100, 2)}%",
            "GM Value USD": f"${round(gm_value, 2)}"
        }

        product_summaries.append(product_summary)
        total_revenue += gmv_usd
        total_cogs_usd += cogs_usd * quantity
        total_units += quantity

    amazon_fee = total_revenue * (additional_costs.get("amazon_fee_percent", 0) / 100)
    royalty_fee = total_revenue * (additional_costs.get("royalty_fee_percent", 0) / 100)
    commission_fee = total_revenue * (additional_costs.get("commission_percent", 0) / 100)
    paid_ads_usd = additional_costs.get("paid_ads_gbp", 0) * exchange_rate
    shipping_cost_total = total_units * shipping_cost_per_unit_3pl_gbp * exchange_rate
    total_other_costs = sum([
        additional_costs.get("partner_fee_usd", 0),
        additional_costs.get("partner_content_usd", 0),
        additional_costs.get("influencer_budget_usd", 0),
        additional_costs.get("ugc_budget_usd", 0),
        additional_costs.get("trtl_content_usd", 0),
        additional_costs.get("product_gifting_usd", 0),
        additional_costs.get("other_usd", 0),
        paid_ads_usd
    ])
    total_costs = amazon_fee + royalty_fee + commission_fee + total_cogs_usd + shipping_cost_total + total_other_costs
    gross_profit = total_revenue - total_costs
    gross_profit_percent = (gross_profit / total_revenue) if total_revenue else 0

    p_and_l_summary = {
        "Revenue": f"${round(total_revenue, 2)}",
        "Amazon Fees": f"${round(amazon_fee, 2)}",
        "Royalty Fees": f"${round(royalty_fee, 2)}",
        "Commission Fee": f"${round(commission_fee, 2)}",
        "Total COGS": f"${round(total_cogs_usd, 2)}",
        "Shipping Costs": f"${round(shipping_cost_total, 2)}",
        "Other Costs": f"${round(total_other_costs, 2)}",
        "Total Costs": f"${round(total_costs, 2)}",
        "Gross Profit": f"${round(gross_profit, 2)}",
        "Gross Profit %": f"{round(gross_profit_percent * 100, 2)}%"
    }

    return product_summaries, p_and_l_summary
