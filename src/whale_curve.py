"""
Whale Curve (Stobachoff Cumulative Profitability) Analyzer
Calculates customer-level Pareto distribution and cumulative profitability.
Proves how the top accounts generate ~140% of enterprise profits,
a middle plateau hovers near breakeven, and the bottom 15% actively destroy EBITDA.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class WhaleCurveAnalyzer:
    """
    Computes cumulative customer profitability curves and identifies
    peak profit points, plateau zones, and EBITDA destruction tails.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df_clients = self._aggregate_clients()
        
    def _aggregate_clients(self) -> pd.DataFrame:
        """
        Aggregates metrics to the unique customer level and computes cumulative curve.
        """
        cust = self.df.groupby("client_id").agg(
            client_tier=("client_tier", "first"),
            industry=("industry", "first"),
            assigned_rep=("sales_rep_id", "first"),
            orders_count=("invoice_id", "count"),
            gross_revenue=("gross_revenue", "sum"),
            discounts=("discount_amount", "sum"),
            invoice_revenue=("invoice_revenue", "sum"),
            total_cogs=("total_cogs", "sum"),
            logistics_cost=("logistics_cost", "sum"),
            cost_of_capital=("cost_of_capital", "sum"),
            avg_payment_delay=("payment_delay_days", "mean"),
            net_pocket_margin=("net_pocket_margin", "sum")
        ).reset_index()
        
        # Sort descending by Net Pocket Margin
        cust = cust.sort_values(by="net_pocket_margin", ascending=False).reset_index(drop=True)
        
        # Rankings and cumulative metrics
        total_enterprise_margin = cust["net_pocket_margin"].sum()
        total_enterprise_revenue = cust["invoice_revenue"].sum()
        total_clients = len(cust)
        
        cust["customer_rank"] = cust.index + 1
        cust["cum_customer_pct"] = (cust["customer_rank"] / total_clients) * 100.0
        
        cust["cum_pocket_margin"] = cust["net_pocket_margin"].cumsum()
        cust["cum_pocket_margin_pct"] = (cust["cum_pocket_margin"] / total_enterprise_margin) * 100.0
        
        cust["cum_revenue"] = cust["invoice_revenue"].cumsum()
        cust["cum_revenue_pct"] = (cust["cum_revenue"] / total_enterprise_revenue) * 100.0
        
        cust["client_pocket_margin_pct"] = np.where(
            cust["invoice_revenue"] > 0,
            (cust["net_pocket_margin"] / cust["invoice_revenue"]) * 100.0,
            0.0
        )
        cust["avg_order_value"] = cust["invoice_revenue"] / cust["orders_count"]
        cust["avg_discount_rate_pct"] = (cust["discounts"] / cust["gross_revenue"]) * 100.0
        
        return cust
        
    def get_curve_dataframe(self) -> pd.DataFrame:
        """
        Returns the ranked client DataFrame with all cumulative metrics.
        """
        return self.df_clients
        
    def get_whale_metrics(self) -> Dict[str, Any]:
        """
        Extracts key quantitative milestones of the Whale Curve.
        """
        cust = self.df_clients
        total_margin = cust["net_pocket_margin"].sum()
        total_clients = len(cust)
        
        # Peak profit point
        peak_idx = cust["cum_pocket_margin"].idxmax()
        peak_row = cust.loc[peak_idx]
        peak_margin = peak_row["cum_pocket_margin"]
        peak_pct = peak_row["cum_pocket_margin_pct"]
        peak_client_pct = peak_row["cum_customer_pct"]
        peak_client_rank = int(peak_row["customer_rank"])
        
        # Top 20% milestone
        top_20_count = int(np.round(total_clients * 0.20))
        top_20_margin = cust.iloc[:top_20_count]["net_pocket_margin"].sum()
        top_20_pct = (top_20_margin / total_margin) * 100.0
        
        # Bottom 15% erosion milestone
        bottom_15_count = int(np.round(total_clients * 0.15))
        bottom_15_margin = cust.tail(bottom_15_count)["net_pocket_margin"].sum()
        bottom_15_pct = (bottom_15_margin / total_margin) * 100.0
        
        # Destroyed EBITDA (Peak margin - Final margin)
        ebitda_destroyed = peak_margin - total_margin
        ebitda_destroyed_pct = (ebitda_destroyed / total_margin) * 100.0
        
        # Negative margin clients count
        neg_clients = cust[cust["net_pocket_margin"] < 0]
        neg_count = len(neg_clients)
        neg_margin_sum = neg_clients["net_pocket_margin"].sum()
        
        return {
            "total_clients": total_clients,
            "total_enterprise_margin": total_margin,
            "peak_margin": peak_margin,
            "peak_margin_pct_of_total": peak_pct,
            "peak_client_rank": peak_client_rank,
            "peak_client_pct": peak_client_pct,
            "top_20_clients_count": top_20_count,
            "top_20_margin": top_20_margin,
            "top_20_margin_pct_of_total": top_20_pct,
            "bottom_15_clients_count": bottom_15_count,
            "bottom_15_margin": bottom_15_margin,
            "bottom_15_margin_pct_of_total": bottom_15_pct,
            "ebitda_destroyed_by_tail": ebitda_destroyed,
            "ebitda_destroyed_pct": ebitda_destroyed_pct,
            "negative_margin_clients_count": neg_count,
            "negative_margin_clients_pct": (neg_count / total_clients) * 100.0,
            "negative_margin_total_loss": neg_margin_sum
        }
        
    def profile_tail_accounts(self) -> pd.DataFrame:
        """
        Profiles the characteristics of value-destroying accounts versus top performers.
        """
        cust = self.df_clients
        cust["profitability_segment"] = np.where(
            cust["cum_customer_pct"] <= 20.0, "Top 20% (Profit Drivers)",
            np.where(cust["net_pocket_margin"] >= 0, "Middle 65% (Breakeven / Plateau)", "Bottom 15% (EBITDA Destroyers)")
        )
        
        segment_summary = cust.groupby("profitability_segment", observed=False).agg(
            clients=("client_id", "count"),
            invoice_revenue=("invoice_revenue", "sum"),
            net_pocket_margin=("net_pocket_margin", "sum"),
            avg_aov=("avg_order_value", "mean"),
            avg_discount_rate=("avg_discount_rate_pct", "mean"),
            orders_per_client=("orders_count", "mean")
        ).reset_index()
        
        segment_summary["margin_pct"] = (
            segment_summary["net_pocket_margin"] / segment_summary["invoice_revenue"]
        ) * 100.0
        
        return segment_summary

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    analyzer = WhaleCurveAnalyzer(df_raw)
    metrics = analyzer.get_whale_metrics()
    
    print("\n================ WHALE CURVE METRICS ================")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k:35s}: {v:,.2f}")
        else:
            print(f"{k:35s}: {v}")
            
    print("\n================ PROFITABILITY SEGMENTS ================")
    print(analyzer.profile_tail_accounts().to_string(index=False))
