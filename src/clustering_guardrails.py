"""
Customer Clustering and Sales Rep Rogue Diagnostics
Performs RFM + Margin multi-dimensional clustering using K-Means.
Identifies unauthorized sales rep discounting and margin destruction patterns.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Tuple

class CustomerClusteringAndRepDiagnostics:
    """
    Segments B2B customer accounts based on volume, frequency, margin, and discount behavior.
    Diagnoses sales rep discounting behavior to detect rogue discounting.
    """
    
    def __init__(self, df: pd.DataFrame, n_clusters: int = 4, random_state: int = 42):
        self.df = df.copy()
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = None
        self.df_clients = None
        self.cluster_summary = None
        
    def fit_customer_clusters(self) -> pd.DataFrame:
        """
        Builds RFM + Profitability customer profiles and applies K-Means clustering.
        """
        # Aggregate customer behavioral features
        cust = self.df.groupby("client_id").agg(
            client_tier=("client_tier", "first"),
            industry=("industry", "first"),
            assigned_rep=("sales_rep_id", "first"),
            order_frequency=("invoice_id", "count"),
            total_invoice_revenue=("invoice_revenue", "sum"),
            total_pocket_margin=("net_pocket_margin", "sum"),
            avg_order_value=("invoice_revenue", "mean"),
            avg_discount_pct=("discount_pct", "mean"),
            avg_payment_delay=("payment_delay_days", "mean"),
            avg_quantity_per_order=("quantity", "mean")
        ).reset_index()
        
        cust["pocket_margin_ratio"] = np.where(
            cust["total_invoice_revenue"] > 0,
            cust["total_pocket_margin"] / cust["total_invoice_revenue"],
            -1.0
        )
        
        # Features for clustering
        feature_cols = [
            "total_invoice_revenue",
            "order_frequency",
            "avg_order_value",
            "avg_discount_pct",
            "avg_payment_delay",
            "pocket_margin_ratio"
        ]
        
        X = cust[feature_cols].copy()
        # Handle log transforms for heavily skewed financial values
        X["log_revenue"] = np.log1p(np.maximum(X["total_invoice_revenue"], 0))
        X["log_aov"] = np.log1p(np.maximum(X["avg_order_value"], 0))
        
        cluster_features = [
            "log_revenue",
            "order_frequency",
            "log_aov",
            "avg_discount_pct",
            "avg_payment_delay",
            "pocket_margin_ratio"
        ]
        
        X_scaled = self.scaler.fit_transform(X[cluster_features])
        
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        cust["cluster_id"] = self.kmeans.fit_predict(X_scaled)
        
        # Name clusters meaningfully based on their centroid characteristics
        cluster_profiles = cust.groupby("cluster_id").agg(
            mean_margin=("total_pocket_margin", "mean"),
            mean_rev=("total_invoice_revenue", "mean"),
            mean_discount=("avg_discount_pct", "mean"),
            mean_delay=("avg_payment_delay", "mean"),
            mean_qty=("avg_quantity_per_order", "mean")
        ).reset_index()
        
        name_map = {}
        for _, row in cluster_profiles.iterrows():
            cid = int(row["cluster_id"])
            if row["mean_margin"] < 0:
                name = "Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)"
            elif row["mean_rev"] > cluster_profiles["mean_rev"].quantile(0.70):
                name = "Tier-A: Strategic Enterprise (High Volume Anchor)"
            elif row["mean_margin"] > cluster_profiles["mean_margin"].median():
                name = "Tier-B: Core Growth (Solid Margin & Predictable Terms)"
            else:
                name = "Tier-C: SMB Long-Tail (Standard Pricing, Low Volume)"
            name_map[cid] = name
            
        cust["cluster_name"] = cust["cluster_id"].map(name_map)
        self.df_clients = cust
        
        # Create cluster summary table
        self.cluster_summary = cust.groupby(["cluster_id", "cluster_name"]).agg(
            account_count=("client_id", "count"),
            total_revenue=("total_invoice_revenue", "sum"),
            total_pocket_margin=("total_pocket_margin", "sum"),
            avg_aov=("avg_order_value", "mean"),
            avg_discount=("avg_discount_pct", "mean"),
            avg_delay_days=("avg_payment_delay", "mean")
        ).reset_index()
        
        self.cluster_summary["pocket_margin_pct"] = (
            self.cluster_summary["total_pocket_margin"] / self.cluster_summary["total_revenue"]
        ) * 100.0
        
        return self.df_clients
        
    def diagnose_sales_reps(self) -> pd.DataFrame:
        """
        Identifies rogue sales rep discounting behavior.
        Compares average discount conceded on small orders (< 5 units) vs. large orders (> 40 units).
        """
        rep_agg = self.df.groupby(["sales_rep_id", "rep_profile"]).agg(
            total_orders=("invoice_id", "count"),
            total_invoice_revenue=("invoice_revenue", "sum"),
            total_net_margin=("net_pocket_margin", "sum"),
            overall_avg_discount=("discount_pct", "mean"),
            small_orders_count=("quantity", lambda q: (q <= 5).sum()),
            small_orders_avg_discount=("discount_pct", lambda d: d[self.df.loc[d.index, "quantity"] <= 5].mean()),
            large_orders_avg_discount=("discount_pct", lambda d: d[self.df.loc[d.index, "quantity"] >= 40].mean())
        ).reset_index()
        
        rep_agg["pocket_margin_pct"] = (rep_agg["total_net_margin"] / rep_agg["total_invoice_revenue"]) * 100.0
        
        # Rogue Index: Disparity between small order discount and acceptable discipline
        # A disciplined seller discounts small orders ~5-10% and large orders ~18-25%.
        # A rogue rep discounts small orders >35%!
        rep_agg["rogue_leakage_spread"] = rep_agg["small_orders_avg_discount"] - rep_agg["large_orders_avg_discount"]
        
        # Identify Rogue Reps
        rep_agg["is_rogue_flagged"] = (rep_agg["small_orders_avg_discount"] > 0.30) & (rep_agg["pocket_margin_pct"] < 20.0)
        
        return rep_agg.sort_values(by="small_orders_avg_discount", ascending=False)

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    diag = CustomerClusteringAndRepDiagnostics(df_raw, n_clusters=4)
    df_clustered = diag.fit_customer_clusters()
    
    print("\n================ CUSTOMER CLUSTER PROFILES ================")
    print(diag.cluster_summary[["cluster_name", "account_count", "total_revenue", "total_pocket_margin", "pocket_margin_pct", "avg_discount"]].to_string(index=False))
    
    print("\n================ SALES REP ROGUE DISCOUNT AUDIT ================")
    df_reps = diag.diagnose_sales_reps()
    print(df_reps[["sales_rep_id", "rep_profile", "total_orders", "overall_avg_discount", "small_orders_avg_discount", "pocket_margin_pct", "is_rogue_flagged"]].head(10).to_string(index=False))
