"""
B2B ERP Transactional Data Generator
Simulates realistic B2B distribution orders with margin leakages:
uncoordinated discounting, small order logistics leakage, off-invoice rebates,
and working capital drag from delayed payment terms.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

def generate_b2b_erp_dataset(
    n_transactions: int = 55000,
    n_clients: int = 800,
    n_sales_reps: int = 25,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Generates a realistic B2B ERP transaction dataset.
    
    Parameters:
        n_transactions: Number of invoice lines (>50,000)
        n_clients: Number of distinct B2B accounts (800)
        n_sales_reps: Number of sales representatives (25)
        random_seed: Seed for reproducible generation
        
    Returns:
        pd.DataFrame containing detailed transaction and profitability fields.
    """
    np.random.seed(random_seed)
    
    # -------------------------------------------------------------
    # 1. Product Catalog Configuration
    # -------------------------------------------------------------
    product_families = {
        "Heavy_Industrial": {
            "skus": [f"IND-{i:03d}" for i in range(1, 16)],
            "price_range": (850.0, 3200.0),
            "base_cogs_pct": 0.58,
            "base_handling": 45.0,
            "unit_freight": 14.5,  # Heavy weight
            "base_rebate_pct": 0.020
        },
        "Specialty_Chemicals": {
            "skus": [f"CHM-{i:03d}" for i in range(1, 16)],
            "price_range": (280.0, 920.0),
            "base_cogs_pct": 0.52,
            "base_handling": 38.0,
            "unit_freight": 8.0,  # Hazmat / Drum freight
            "base_rebate_pct": 0.025
        },
        "Electronic_Sensors": {
            "skus": [f"ELE-{i:03d}" for i in range(1, 16)],
            "price_range": (55.0, 340.0),
            "base_cogs_pct": 0.45,
            "base_handling": 20.0,
            "unit_freight": 1.2,  # Lightweight
            "base_rebate_pct": 0.035
        },
        "MRO_Consumables": {
            "skus": [f"MRO-{i:03d}" for i in range(1, 21)],
            "price_range": (14.0, 115.0),
            "base_cogs_pct": 0.40,
            "base_handling": 22.0,
            "unit_freight": 0.9,  # Small package handling
            "base_rebate_pct": 0.015
        }
    }
    
    sku_master = []
    for family, config in product_families.items():
        for sku in config["skus"]:
            list_p = np.round(np.random.uniform(*config["price_range"]), 2)
            unit_cogs = np.round(list_p * config["base_cogs_pct"] * np.random.uniform(0.95, 1.05), 2)
            sku_master.append({
                "sku": sku,
                "product_family": family,
                "unit_list_price": list_p,
                "unit_cogs": unit_cogs,
                "base_handling": config["base_handling"],
                "unit_freight": config["unit_freight"],
                "base_rebate_pct": config["base_rebate_pct"]
            })
    df_skus = pd.DataFrame(sku_master)
    
    # -------------------------------------------------------------
    # 2. Sales Rep Profiles (Disciplined vs. Rogue Volume Hunters)
    # -------------------------------------------------------------
    sales_rep_ids = [f"REP-{i:02d}" for i in range(1, n_sales_reps + 1)]
    rep_profiles = {}
    for idx, rep in enumerate(sales_rep_ids):
        # 5 Rogue reps who concede heavy discounts to chase volume quotas
        # 5 Value sellers who defend price
        # 15 Standard reps
        if idx < 5:
            profile = "Rogue_Volume_Hunter"
            discount_bias = 0.12  # adds ~12% extra discount
            min_order_discipline = 0.4  # lax on small orders
        elif idx < 10:
            profile = "Value_Defending_Seller"
            discount_bias = -0.05  # discounts 5% less
            min_order_discipline = 0.95  # strongly pushes bundle/large orders
        else:
            profile = "Standard_Commercial"
            discount_bias = 0.00
            min_order_discipline = 0.70
            
        rep_profiles[rep] = {
            "sales_rep_id": rep,
            "rep_profile": profile,
            "discount_bias": discount_bias,
            "min_order_discipline": min_order_discipline
        }
    df_reps = pd.DataFrame(list(rep_profiles.values()))
    
    # -------------------------------------------------------------
    # 3. Client Segmentation (Archetypes)
    # -------------------------------------------------------------
    client_ids = [f"CUST-{i:04d}" for i in range(1, n_clients + 1)]
    # Tiers:
    # Enterprise_Key (~5% = 40): High volume, master agreements, moderate margin
    # MidMarket_Core (~25% = 200): Steady volume, disciplined margins
    # SMB_Standard (~45% = 360): Moderate volume, standard pricing
    # Toxic_Drain (~25% = 200): Micro-orders, delayed payment (90d+), high discount concessions
    tier_distribution = (
        ["Enterprise_Key"] * 40 +
        ["MidMarket_Core"] * 120 +
        ["SMB_Standard"] * 520 +
        ["Toxic_Drain"] * 120
    )
    np.random.shuffle(tier_distribution)
    
    industries = ["Manufacturing", "Automotive_OEM", "Construction", "Chemical_Processing", "Aerospace_Defense", "Facility_Services"]
    
    client_master = []
    for c_id, tier in zip(client_ids, tier_distribution):
        assigned_rep = np.random.choice(sales_rep_ids)
        industry = np.random.choice(industries)
        
        if tier == "Enterprise_Key":
            base_delay_days = np.random.normal(28, 3)
            order_volume_weight = 8.5
            mean_qty = 135
            base_discount_mean = 0.16
            rebate_multiplier = 1.0
        elif tier == "MidMarket_Core":
            base_delay_days = np.random.normal(32, 4)
            order_volume_weight = 2.6
            mean_qty = 42
            base_discount_mean = 0.12
            rebate_multiplier = 0.9
        elif tier == "SMB_Standard":
            base_delay_days = np.random.normal(42, 6)
            order_volume_weight = 0.8
            mean_qty = 8
            base_discount_mean = 0.18
            rebate_multiplier = 1.1
        else:  # Toxic_Drain (120 accounts = exactly 15% of portfolio): micro-orders, rogue 44% discounts, 110d delay
            base_delay_days = np.random.normal(110, 16)
            order_volume_weight = 1.9
            mean_qty = 2.1
            base_discount_mean = 0.44
            rebate_multiplier = 1.7
            
        client_master.append({
            "client_id": c_id,
            "client_tier": tier,
            "industry": industry,
            "assigned_rep": assigned_rep,
            "base_delay_days": max(15, base_delay_days),
            "order_volume_weight": order_volume_weight,
            "mean_qty": mean_qty,
            "base_discount_mean": base_discount_mean,
            "rebate_multiplier": rebate_multiplier
        })
    df_clients = pd.DataFrame(client_master)
    
    # -------------------------------------------------------------
    # 4. Generate 55,000+ ERP Invoice Transactions
    # -------------------------------------------------------------
    # Sample clients according to order_volume_weight
    client_weights = df_clients["order_volume_weight"].values / df_clients["order_volume_weight"].sum()
    chosen_client_indices = np.random.choice(len(df_clients), size=n_transactions, p=client_weights)
    
    sampled_clients = df_clients.iloc[chosen_client_indices].reset_index(drop=True)
    
    # Sample SKUs with category weighting
    sku_weights = [0.20 if s["product_family"] == "Heavy_Industrial" else
                   0.25 if s["product_family"] == "Specialty_Chemicals" else
                   0.30 if s["product_family"] == "Electronic_Sensors" else 0.25
                   for s in sku_master]
    sku_weights = np.array(sku_weights) / sum(sku_weights)
    chosen_sku_indices = np.random.choice(len(df_skus), size=n_transactions, p=sku_weights)
    sampled_skus = df_skus.iloc[chosen_sku_indices].reset_index(drop=True)
    
    # Merge Rep details
    sampled_reps = pd.merge(sampled_clients[["assigned_rep"]], df_reps, left_on="assigned_rep", right_on="sales_rep_id", how="left")
    
    # Dates across a full fiscal year
    start_date = pd.to_datetime("2024-01-01")
    days_offset = np.random.randint(0, 365, size=n_transactions)
    order_dates = start_date + pd.to_timedelta(days_offset, unit="D")
    
    # Quantities: lognormal / Poisson around client mean_qty
    raw_qty = np.random.exponential(scale=sampled_clients["mean_qty"].values) + 1
    quantities = np.clip(np.round(raw_qty), 1, 600).astype(int)
    
    # Calculate Discounts with Rep Bias and Size Sensitivity
    base_discounts = sampled_clients["base_discount_mean"].values + sampled_reps["discount_bias"].values
    
    discount_noise = np.random.normal(0.0, 0.04, size=n_transactions)
    final_discounts = base_discounts + discount_noise
    
    legit_volume_boost = np.where(quantities > 50, 0.04, np.where(quantities > 20, 0.02, 0.0))
    is_rogue = sampled_reps["rep_profile"].values == "Rogue_Volume_Hunter"
    final_discounts = np.where(is_rogue, final_discounts + 0.08, final_discounts + legit_volume_boost)
    
    discounts_pct = np.clip(np.round(final_discounts, 4), 0.0, 0.58)
    
    # Payment delays (Days)
    delay_noise = np.random.normal(0, 8, size=n_transactions)
    payment_delays = np.clip(np.round(sampled_clients["base_delay_days"].values + delay_noise), 10, 180).astype(int)
    
    # -------------------------------------------------------------
    # 5. Financial Ledger Computations
    # -------------------------------------------------------------
    unit_list_price = sampled_skus["unit_list_price"].values
    unit_cogs = sampled_skus["unit_cogs"].values
    
    gross_revenue = np.round(unit_list_price * quantities, 2)
    on_invoice_discount_val = np.round(gross_revenue * discounts_pct, 2)
    invoice_revenue = np.round(gross_revenue - on_invoice_discount_val, 2)
    total_cogs = np.round(unit_cogs * quantities, 2)
    
    # Standard Gross Profit
    standard_gross_profit = np.round(invoice_revenue - total_cogs, 2)
    
    # Off-invoice Rebates (accrued contractual kickbacks)
    rebate_pct = np.round(sampled_skus["base_rebate_pct"].values * sampled_clients["rebate_multiplier"].values, 4)
    off_invoice_rebate_val = np.round(invoice_revenue * rebate_pct, 2)
    
    # Order Logistics & Freight fulfillment:
    fixed_handling = sampled_skus["base_handling"].values
    variable_freight = sampled_skus["unit_freight"].values * quantities
    freight_scale_discount = np.where(quantities > 40, 0.85, 1.0)
    
    # Subscale / LTL accessorial freight penalty:
    # When orders are below MOQ (quantities <= 4) on industrial/chemical goods or for toxic accounts,
    # non-standard courier/split-pallet dispatches create massive freight leakage
    subscale_ltl_accessorial = np.where(
        (sampled_clients["client_tier"].values == "Toxic_Drain") & (quantities <= 4),
        np.random.uniform(8200.0, 13200.0, size=n_transactions),
        np.where((quantities <= 2), 45.0, 0.0)
    )
    total_logistics_cost = np.round(fixed_handling + subscale_ltl_accessorial + (variable_freight * freight_scale_discount), 2)
    
    # Working capital cost (Cost of carrying accounts receivable / WACC @ 8.5% p.a.)
    wacc_annual = 0.085
    daily_wacc = wacc_annual / 365.0
    cost_of_capital = np.round(invoice_revenue * daily_wacc * payment_delays, 2)
    
    # Net Pocket Margin (Net cash contribution before corporate overhead/EBITDA)
    net_pocket_margin = np.round(
        invoice_revenue - total_cogs - off_invoice_rebate_val - total_logistics_cost - cost_of_capital, 2
    )
    
    # Ratios
    pocket_margin_pct = np.round(np.where(invoice_revenue > 0, net_pocket_margin / invoice_revenue, 0.0), 4)
    nominal_gross_margin_pct = np.round(np.where(invoice_revenue > 0, standard_gross_profit / invoice_revenue, 0.0), 4)
    
    # Assemble DataFrame
    invoice_ids = [f"INV-2024-{i:06d}" for i in range(1, n_transactions + 1)]
    
    df_transactions = pd.DataFrame({
        "invoice_id": invoice_ids,
        "order_date": order_dates,
        "client_id": sampled_clients["client_id"].values,
        "client_tier": sampled_clients["client_tier"].values,
        "industry": sampled_clients["industry"].values,
        "sales_rep_id": sampled_reps["sales_rep_id"].values,
        "rep_profile": sampled_reps["rep_profile"].values,
        "sku": sampled_skus["sku"].values,
        "product_family": sampled_skus["product_family"].values,
        "quantity": quantities,
        "unit_list_price": unit_list_price,
        "gross_revenue": gross_revenue,
        "discount_pct": discounts_pct,
        "discount_amount": on_invoice_discount_val,
        "invoice_revenue": invoice_revenue,
        "unit_cogs": unit_cogs,
        "total_cogs": total_cogs,
        "standard_gross_profit": standard_gross_profit,
        "nominal_gross_margin_pct": nominal_gross_margin_pct,
        "rebate_pct": rebate_pct,
        "off_invoice_rebate_amount": off_invoice_rebate_val,
        "logistics_cost": total_logistics_cost,
        "payment_delay_days": payment_delays,
        "cost_of_capital": cost_of_capital,
        "net_pocket_margin": net_pocket_margin,
        "pocket_margin_pct": pocket_margin_pct
    })
    
    return df_transactions

if __name__ == "__main__":
    print("Generating B2B ERP Transactional Dataset...")
    df = generate_b2b_erp_dataset(n_transactions=55000, n_clients=800, n_sales_reps=25)
    output_path = "data/b2b_erp_transactions.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Dataset generated successfully: {len(df):,} records saved to {output_path}")
    print(f"Total Gross Revenue: ${df['gross_revenue'].sum():,.2f}")
    print(f"Total Invoice Revenue: ${df['invoice_revenue'].sum():,.2f}")
    print(f"Total Net Pocket Margin: ${df['net_pocket_margin'].sum():,.2f}")
    print(f"Overall Pocket Margin %: {df['net_pocket_margin'].sum() / df['invoice_revenue'].sum() * 100:.2f}%")
