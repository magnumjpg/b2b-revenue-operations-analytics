"""
Pocket Margin Waterfall Analyzer
Deconstructs transaction value erosion from List Price to Net Pocket Margin.
Identifies hidden leakage drivers: uncoordinated discounting, logistics freight,
off-invoice rebates, and payment term capital costs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class PocketMarginWaterfallAnalyzer:
    """
    Deconstructs top-line revenue into realized cash pocket margin.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def compute_portfolio_waterfall(self) -> pd.DataFrame:
        """
        Calculates the enterprise-level waterfall stages.
        """
        gross_rev = self.df["gross_revenue"].sum()
        discounts = self.df["discount_amount"].sum()
        invoice_rev = self.df["invoice_revenue"].sum()
        cogs = self.df["total_cogs"].sum()
        gross_profit = self.df["standard_gross_profit"].sum()
        rebates = self.df["off_invoice_rebate_amount"].sum()
        logistics = self.df["logistics_cost"].sum()
        capital_cost = self.df["cost_of_capital"].sum()
        net_pocket = self.df["net_pocket_margin"].sum()
        
        stages = [
            {"stage": "1. Gross List Price", "amount": gross_rev, "pct_gross": 100.0, "pct_invoice": (gross_rev / invoice_rev) * 100, "type": "baseline"},
            {"stage": "2. On-Invoice Discounts", "amount": -discounts, "pct_gross": (-discounts / gross_rev) * 100, "pct_invoice": (-discounts / invoice_rev) * 100, "type": "leakage"},
            {"stage": "3. Invoice Revenue", "amount": invoice_rev, "pct_gross": (invoice_rev / gross_rev) * 100, "pct_invoice": 100.0, "type": "subtotal"},
            {"stage": "4. Cost of Goods Sold (COGS)", "amount": -cogs, "pct_gross": (-cogs / gross_rev) * 100, "pct_invoice": (-cogs / invoice_rev) * 100, "type": "cost"},
            {"stage": "5. Standard Gross Profit", "amount": gross_profit, "pct_gross": (gross_profit / gross_rev) * 100, "pct_invoice": (gross_profit / invoice_rev) * 100, "type": "subtotal"},
            {"stage": "6. Off-Invoice Rebates", "amount": -rebates, "pct_gross": (-rebates / gross_rev) * 100, "pct_invoice": (-rebates / invoice_rev) * 100, "type": "leakage"},
            {"stage": "7. Logistics & Handling", "amount": -logistics, "pct_gross": (-logistics / gross_rev) * 100, "pct_invoice": (-logistics / invoice_rev) * 100, "type": "leakage"},
            {"stage": "8. Cost of Working Capital (Delay)", "amount": -capital_cost, "pct_gross": (-capital_cost / gross_rev) * 100, "pct_invoice": (-capital_cost / invoice_rev) * 100, "type": "leakage"},
            {"stage": "9. Net Pocket Margin", "amount": net_pocket, "pct_gross": (net_pocket / gross_rev) * 100, "pct_invoice": (net_pocket / invoice_rev) * 100, "type": "final"}
        ]
        
        return pd.DataFrame(stages)
        
    def analyze_by_tier(self) -> pd.DataFrame:
        """
        Decomposes pocket margin performance across customer tiers.
        """
        agg = self.df.groupby("client_tier").agg(
            transactions=("invoice_id", "count"),
            clients=("client_id", "nunique"),
            gross_revenue=("gross_revenue", "sum"),
            discounts=("discount_amount", "sum"),
            invoice_revenue=("invoice_revenue", "sum"),
            cogs=("total_cogs", "sum"),
            rebates=("off_invoice_rebate_amount", "sum"),
            logistics=("logistics_cost", "sum"),
            cost_of_capital=("cost_of_capital", "sum"),
            net_pocket_margin=("net_pocket_margin", "sum")
        ).reset_index()
        
        agg["discount_rate_pct"] = (agg["discounts"] / agg["gross_revenue"]) * 100
        agg["gross_margin_pct"] = ((agg["invoice_revenue"] - agg["cogs"]) / agg["invoice_revenue"]) * 100
        agg["logistics_ratio_pct"] = (agg["logistics"] / agg["invoice_revenue"]) * 100
        agg["net_pocket_margin_pct"] = (agg["net_pocket_margin"] / agg["invoice_revenue"]) * 100
        
        return agg.sort_values(by="net_pocket_margin", ascending=False)

    def analyze_by_product_family(self) -> pd.DataFrame:
        """
        Decomposes pocket margin performance by product category.
        """
        agg = self.df.groupby("product_family").agg(
            transactions=("invoice_id", "count"),
            invoice_revenue=("invoice_revenue", "sum"),
            cogs=("total_cogs", "sum"),
            rebates=("off_invoice_rebate_amount", "sum"),
            logistics=("logistics_cost", "sum"),
            cost_of_capital=("cost_of_capital", "sum"),
            net_pocket_margin=("net_pocket_margin", "sum")
        ).reset_index()
        
        agg["pocket_margin_pct"] = (agg["net_pocket_margin"] / agg["invoice_revenue"]) * 100
        agg["logistics_pct"] = (agg["logistics"] / agg["invoice_revenue"]) * 100
        agg["cogs_pct"] = (agg["cogs"] / agg["invoice_revenue"]) * 100
        return agg.sort_values(by="net_pocket_margin", ascending=False)

    def analyze_order_size_brackets(self) -> pd.DataFrame:
        """
        Demonstrates how micro-orders suffer massive logistics erosion.
        """
        bins = [0, 250, 1000, 5000, 25000, np.inf]
        labels = ["< $250 (Micro)", "$250 - $1K", "$1K - $5K", "$5K - $25K", "> $25K (Bulk)"]
        
        df_binned = self.df.copy()
        df_binned["order_bracket"] = pd.cut(df_binned["invoice_revenue"], bins=bins, labels=labels)
        
        agg = df_binned.groupby("order_bracket", observed=False).agg(
            orders=("invoice_id", "count"),
            invoice_revenue=("invoice_revenue", "sum"),
            logistics_cost=("logistics_cost", "sum"),
            net_pocket_margin=("net_pocket_margin", "sum")
        ).reset_index()
        
        agg["logistics_drag_pct"] = (agg["logistics_cost"] / agg["invoice_revenue"]) * 100
        agg["pocket_margin_pct"] = (agg["net_pocket_margin"] / agg["invoice_revenue"]) * 100
        
        return agg

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    analyzer = PocketMarginWaterfallAnalyzer(df_raw)
    
    print("\n--- ENTERPRISE WATERFALL STAGES ---")
    df_waterfall = analyzer.compute_portfolio_waterfall()
    print(df_waterfall.to_string(index=False))
    
    print("\n--- PERFORMANCE BY CUSTOMER TIER ---")
    df_tier = analyzer.analyze_by_tier()
    print(df_tier[["client_tier", "clients", "invoice_revenue", "net_pocket_margin", "net_pocket_margin_pct", "discount_rate_pct"]].to_string(index=False))
    
    print("\n--- ORDER SIZE BRACKETS & LOGISTICS EROSION ---")
    df_brackets = analyzer.analyze_order_size_brackets()
    print(df_brackets.to_string(index=False))
