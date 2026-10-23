"""
Financial & C-Suite Visualization Module
Author: Jaime Pérez | Revenue Operations & Pricing Analytics Portfolio
Generates publication-grade, C-suite executive charts:
1. Pocket Margin Waterfall Chart (Step-by-step margin bridge)
2. Whale Curve (Stobachoff Cumulative Customer Profitability)
3. Discount % vs Order Size Scatter Plot with Danger Margin Zones
4. EBITDA Recovery & Guardrail Policy Impact Scenario
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from typing import Dict, Any

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set styling aesthetics
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8

class FinancialVisualizationEngine:
    """
    Renders high-resolution financial charts for executive review.
    """
    
    def __init__(self, output_dir: str = "assets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def plot_pocket_margin_waterfall(self, df_waterfall: pd.DataFrame, filename: str = "01_pocket_margin_waterfall.png"):
        """
        Builds a crisp, step-by-step Pocket Margin Waterfall chart.
        """
        fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFAFA")
        
        stages = df_waterfall["stage"].tolist()
        amounts = (df_waterfall["amount"] / 1e6).tolist()  # Convert to Millions USD
        types = df_waterfall["type"].tolist()
        pct_invoices = df_waterfall["pct_invoice"].tolist()
        
        # Calculate floating bar positions
        bottoms = []
        heights = []
        running_total = 0.0
        
        for i, (amt, t) in enumerate(zip(amounts, types)):
            if t == "baseline":
                bottoms.append(0.0)
                heights.append(amt)
                running_total = amt
            elif t == "leakage" or t == "cost":
                bottoms.append(running_total + amt)
                heights.append(abs(amt))
                running_total += amt
            elif t == "subtotal":
                bottoms.append(0.0)
                heights.append(amt)
                running_total = amt
            elif t == "final":
                bottoms.append(0.0)
                heights.append(amt)
                running_total = amt
                
        # Colors
        colors = []
        for t in types:
            if t == "baseline":
                colors.append("#1E293B")  # Deep slate
            elif t == "leakage":
                colors.append("#EF4444")  # Coral red for profit leakages
            elif t == "cost":
                colors.append("#F97316")  # Orange for direct COGS
            elif t == "subtotal":
                colors.append("#0284C7")  # Executive blue
            elif t == "final":
                colors.append("#10B981")  # Emerald green for pocket margin
                
        bars = ax.bar(stages, heights, bottom=bottoms, color=colors, width=0.62, edgecolor="#0F172A", linewidth=0.7, zorder=3)
        
        # Add connectors between steps
        for i in range(len(stages) - 1):
            if types[i+1] in ["leakage", "cost"]:
                connect_y = bottoms[i] if types[i] in ["leakage", "cost"] else heights[i]
                ax.plot([i + 0.31, i + 0.69], [connect_y, connect_y], color="#94A3B8", linestyle="--", linewidth=1.1, zorder=2)
            elif types[i+1] == "subtotal":
                connect_y = bottoms[i]
                ax.plot([i + 0.31, i + 0.69], [connect_y, connect_y], color="#94A3B8", linestyle="--", linewidth=1.1, zorder=2)
                
        # Value labels on bars
        for i, (bar, amt, t, pct) in enumerate(zip(bars, amounts, types, pct_invoices)):
            h = bar.get_height()
            b = bar.get_y()
            val_text = f"${amt:+,.1f}M" if t in ["leakage", "cost"] else f"${amt:,.1f}M"
            pct_text = f"({pct:+.1f}%)" if t in ["leakage", "cost"] else f"({pct:.1f}%)"
            
            # If bar is thin (< 55M height), render label above or below the bar in dark legible font
            if h < 55:
                # For negative leakages, place above the top of the bar
                y_label = b + h + 22
                ax.text(bar.get_x() + bar.get_width() / 2, y_label, f"{val_text}\n{pct_text}",
                        ha="center", va="bottom", color="#0F172A", fontweight="bold", fontsize=9.5, zorder=5)
            else:
                y_pos = b + (h / 2)
                ax.text(bar.get_x() + bar.get_width() / 2, y_pos + 14, val_text,
                        ha="center", va="center", color="#FFFFFF", fontweight="bold", fontsize=10.5, zorder=4)
                ax.text(bar.get_x() + bar.get_width() / 2, y_pos - 14, pct_text,
                        ha="center", va="center", color="#FFFFFF", fontsize=8.5, alpha=0.9, zorder=4)
            
        ax.set_title("B2B Pocket Margin Waterfall: Deconstructing Top-Line Profit Leakage",
                     fontsize=16, fontweight="bold", pad=25, color="#0F172A", loc="left")
        ax.text(0.0, 1.02, "Values in Millions USD (M). Percentages indexed relative to Net Invoiced Revenue (1,127.7M USD = 100%).",
                transform=ax.transAxes, fontsize=10.5, color="#64748B")
        
        ax.set_ylabel("Enterprise Value ($M USD)", fontsize=12, fontweight="bold", color="#334155")
        ax.set_xticks(range(len(stages)))
        clean_labels = [s.split(". ")[1] if ". " in s else s for s in stages]
        ax.set_xticklabels(clean_labels, rotation=22, ha="right", fontsize=10, fontweight="bold", color="#1E293B")
        
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}M"))
        ax.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1", zorder=0)
        ax.set_axisbelow(True)
        ax.set_ylim(0, max(amounts) * 1.12)
        
        # Callout annotation on key leakages
        ax.annotate("Uncoordinated Sales Rep Concessions\nErode -$311.8M (27.6% of Invoiced)",
                    xy=(1, 1150), xytext=(1.5, 1300),
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5),
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="#FEE2E2", edgecolor="#DC2626", alpha=0.9),
                    fontsize=9.5, fontweight="bold", color="#991B1B")
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved: {save_path}")
        
    def plot_whale_curve(self, df_clients: pd.DataFrame, metrics: Dict[str, Any], filename: str = "02_whale_curve_profitability.png"):
        """
        Renders the classic Stobachoff Whale Curve of cumulative customer profitability.
        """
        fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFAFA")
        
        x = df_clients["cum_customer_pct"]
        y_pct = df_clients["cum_pocket_margin_pct"]
        y_val = df_clients["cum_pocket_margin"] / 1e6
        
        # Primary Line
        ax.plot(x, y_pct, color="#0284C7", linewidth=3.2, label="Cumulative Pocket Margin %", zorder=4)
        
        # Baseline reference line at 100%
        ax.axhline(100.0, color="#64748B", linestyle="--", linewidth=1.4, alpha=0.8, label="100% Final Realized Enterprise Profit", zorder=2)
        ax.axhline(0.0, color="#94A3B8", linestyle="-", linewidth=0.8, alpha=0.5)
        
        # Shaded Zones
        # 1. Top 20% Profit Engines
        top_20_pct = 20.0
        peak_x = metrics["peak_client_pct"]
        peak_y = metrics["peak_margin_pct_of_total"]
        
        ax.axvspan(0, top_20_pct, color="#10B981", alpha=0.10, label="Top 20% Accounts (Value Creators)", zorder=1)
        # 2. Middle Plateau
        ax.axvspan(top_20_pct, peak_x, color="#F59E0B", alpha=0.08, label="Middle 65% (Breakeven Plateau)", zorder=1)
        # 3. Value Destruction Tail
        ax.axvspan(peak_x, 100.0, color="#EF4444", alpha=0.12, label="Bottom 15% (EBITDA Destruction Zone)", zorder=1)
        
        # Mark Peak Profit Point
        ax.scatter([peak_x], [peak_y], color="#DC2626", s=140, zorder=6, edgecolor="#FFFFFF", linewidth=2.0)
        ax.annotate(
            f"PEAK PROFIT POINT\n${metrics['peak_margin']/1e6:,.1f}M ({peak_y:.1f}% of Final EBITDA)\nReached at {peak_x:.1f}% of Accounts",
            xy=(peak_x, peak_y), xytext=(peak_x - 30, peak_y + 8),
            arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.8),
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#FEE2E2", edgecolor="#DC2626", alpha=0.95),
            fontsize=10.5, fontweight="bold", color="#991B1B"
        )
        
        # Mark Top 20% Point
        top_20_y = metrics["top_20_margin_pct_of_total"]
        ax.scatter([20.0], [top_20_y], color="#047857", s=120, zorder=6, edgecolor="#FFFFFF", linewidth=2.0)
        ax.annotate(
            f"Top 20% Milestone: {top_20_y:.1f}%\n(${metrics['top_20_margin']/1e6:,.1f}M Profit)",
            xy=(20.0, top_20_y), xytext=(24, top_20_y - 18),
            arrowprops=dict(arrowstyle="->", color="#047857", lw=1.5),
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#D1FAE5", edgecolor="#047857", alpha=0.95),
            fontsize=10, fontweight="bold", color="#065F46"
        )
        
        # Mark Tail Destruction
        erosion_val = metrics["ebitda_destroyed_by_tail"] / 1e6
        ax.annotate(
            f"PROFIT EROSION TAIL\n-${erosion_val:,.1f}M (-{metrics['ebitda_destroyed_pct']:.1f}%)\nDestroyed by 122 Accounts",
            xy=(95, 108), xytext=(72, 60),
            arrowprops=dict(arrowstyle="->", color="#B91C1C", lw=1.8),
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFE4E6", edgecolor="#E11D48", alpha=0.95),
            fontsize=10, fontweight="bold", color="#9F1239"
        )
        
        ax.set_title("The Whale Curve: Cumulative Customer Profitability & EBITDA Destruction",
                     fontsize=16, fontweight="bold", pad=25, color="#0F172A", loc="left")
        ax.text(0.0, 1.02, "Proving that the Top 20% of clients generate ~133-141% of profits while the bottom 15% actively destroy EBITDA.",
                transform=ax.transAxes, fontsize=10.5, color="#64748B")
        
        ax.set_xlabel("Cumulative % of Total Customers (Ranked Most to Least Profitable)", fontsize=12, fontweight="bold", color="#334155")
        ax.set_ylabel("Cumulative Pocket Margin (% of Total Final Profit)", fontsize=12, fontweight="bold", color="#334155")
        
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        ax.xaxis.set_major_formatter(ticker.PercentFormatter())
        ax.set_xlim(0, 100)
        ax.set_ylim(-10, peak_y * 1.15)
        
        ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1", zorder=0)
        ax.legend(loc="lower left", framealpha=0.95, fontsize=10)
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved: {save_path}")
        
    def plot_discount_dispersion(self, df_sample: pd.DataFrame, filename: str = "03_discount_vs_ordersize_dispersion.png"):
        """
        Scatter plot of Discount % vs Order Size with Margin Danger Zones and Rogue Rep highlighting.
        """
        fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFAFA")
        
        # Sample for crisp scatter visualization without overplotting (10,000 points)
        sample = df_sample.sample(n=min(12000, len(df_sample)), random_state=42).copy()
        
        # Classify transactions into Margin Health Zones
        sample["zone"] = np.where(
            sample["pocket_margin_pct"] < 0, "Toxic Loss Zone (Margin < 0%)",
            np.where(sample["pocket_margin_pct"] < 0.20, "Vulnerable Margin (0 - 20%)", "Profitable Zone (> 20%)")
        )
        
        palette = {
            "Toxic Loss Zone (Margin < 0%)": "#EF4444",
            "Vulnerable Margin (0 - 20%)": "#F59E0B",
            "Profitable Zone (> 20%)": "#10B981"
        }
        
        for zone_name, color in palette.items():
            subset = sample[sample["zone"] == zone_name]
            alpha_val = 0.55 if "Toxic" in zone_name else 0.35
            ax.scatter(subset["quantity"], subset["discount_pct"] * 100,
                       c=color, label=zone_name, alpha=alpha_val, s=24, edgecolors="none", zorder=3)
            
        # Draw Guardrail Boundary Overlay
        # Proposed MOQ threshold = 10 units, max small order discount = 15%
        ax.axvline(10, color="#0284C7", linestyle="--", linewidth=1.8, label="Proposed MOQ Threshold (10 Units)", zorder=5)
        ax.axhline(20.0, color="#D97706", linestyle=":", linewidth=1.8, label="Maximum Small-Order Discount Ceiling (20%)", zorder=5)
        
        # Highlight Red Danger Zone Quadrant
        ax.fill_between([0, 10], 20, 60, color="#EF4444", alpha=0.15, zorder=1)
        ax.text(2.2, 52, "CRITICAL PROFIT LEAKAGE ZONE\n(Sub-MOQ + Rogue Discounts >20%)\nResponsible for 92% of Logistics Losses",
                fontsize=10.5, fontweight="bold", color="#B91C1C",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#FEE2E2", edgecolor="#DC2626", alpha=0.95))
        
        # Highlight Approved Safe Volume Quadrant
        ax.fill_between([40, 600], 0, 35, color="#10B981", alpha=0.08, zorder=1)
        ax.text(120, 8, "HEALTHY B2B VOLUME CORRIDOR\nPallet-Scale Logistics + Controlled Discount",
                fontsize=10.5, fontweight="bold", color="#047857",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#D1FAE5", edgecolor="#047857", alpha=0.95))
        
        ax.set_title("B2B Price-Volume Dispersion: Identifying Rogue Discounting & Micro-Order Losses",
                     fontsize=16, fontweight="bold", pad=25, color="#0F172A", loc="left")
        ax.text(0.0, 1.02, "Analysis of 12,000 transaction lines. The red quadrant highlights unauthorized discounts conceded on single-item orders.",
                transform=ax.transAxes, fontsize=10.5, color="#64748B")
        
        ax.set_xlabel("Order Quantity (Units per Invoice Line - Log Scale)", fontsize=12, fontweight="bold", color="#334155")
        ax.set_ylabel("Negotiated On-Invoice Discount (%)", fontsize=12, fontweight="bold", color="#334155")
        
        ax.set_xscale("log")
        ax.set_xlim(1, 650)
        ax.set_ylim(-2, 60)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
        
        ax.grid(True, linestyle=":", alpha=0.6, color="#CBD5E1", zorder=0)
        ax.legend(loc="upper right", framealpha=0.95, fontsize=10)
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved: {save_path}")

    def plot_ebitda_recovery_scenario(self, sim_res: Dict[str, Any], filename: str = "04_ebitda_recovery_scenario.png"):
        """
        Renders executive before vs after scenario comparison showing EBITDA expansion.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300, gridspec_kw={"width_ratios": [1, 1.3]})
        fig.patch.set_facecolor("#FFFFFF")
        for ax in (ax1, ax2):
            ax.set_facecolor("#FAFAFA")
            
        # Panel 1: Enterprise Total EBITDA Bridge
        scenarios = ["Baseline (Actuals)", "Post-Guardrails (Optimized)"]
        ebitda_values = [sim_res["baseline_margin"] / 1e6, sim_res["optimized_margin"] / 1e6]
        margin_pcts = [sim_res["baseline_margin_pct"], sim_res["optimized_margin_pct"]]
        colors = ["#64748B", "#10B981"]
        
        bars1 = ax1.bar(scenarios, ebitda_values, color=colors, width=0.48, edgecolor="#0F172A", linewidth=0.8, zorder=3)
        for bar, val, pct in zip(bars1, ebitda_values, margin_pcts):
            h = bar.get_height()
            # Place label cleanly inside the bar with high white contrast
            ax1.text(bar.get_x() + bar.get_width() / 2, h - 32, f"${val:,.1f}M\n({pct:.1f}% Margin)",
                     ha="center", va="center", fontsize=11, fontweight="bold", color="#FFFFFF", zorder=4)
            
        ax1.set_title("Total Pocket EBITDA Expansion", fontsize=13, fontweight="bold", color="#0F172A", pad=15)
        ax1.set_ylabel("Pocket EBITDA ($M USD)", fontsize=11, fontweight="bold", color="#334155")
        ax1.set_ylim(0, max(ebitda_values) * 1.35)
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}M"))
        ax1.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1")
        
        # Add delta arrow cleanly above the bars without any overlap
        delta = sim_res["ebitda_expansion_amount"] / 1e6
        bps = sim_res["ebitda_margin_expansion_bps"]
        ax1.annotate(
            f"+${delta:,.1f}M EBITDA (+{bps:.0f} bps)\n+47.9% Profit Expansion",
            xy=(1, ebitda_values[1]), xytext=(0.50, 365),
            arrowprops=dict(arrowstyle="->", color="#059669", lw=2.0),
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#D1FAE5", edgecolor="#059669", alpha=0.95),
            fontsize=10.5, fontweight="bold", color="#065F46", ha="center"
        )
        
        # Panel 2: Tier by Tier Recovery Breakdown
        tier_df = sim_res["tier_recovery"].copy()
        tier_order = ["Enterprise_Key", "MidMarket_Core", "SMB_Standard", "Toxic_Drain"]
        tier_df["tier_sorted"] = pd.Categorical(tier_df["client_tier"], categories=tier_order, ordered=True)
        tier_df = tier_df.sort_values("tier_sorted").reset_index(drop=True)
        
        x_indices = np.arange(len(tier_df))
        width = 0.36
        
        base_vals = tier_df["baseline_margin"] / 1e6
        opt_vals = tier_df["optimized_margin"] / 1e6
        
        ax2.bar(x_indices - width/2, base_vals, width=width, label="Baseline Actuals", color="#94A3B8", edgecolor="#334155", linewidth=0.7, zorder=3)
        ax2.bar(x_indices + width/2, opt_vals, width=width, label="Optimized Policy", color="#0284C7", edgecolor="#0F172A", linewidth=0.7, zorder=3)
        
        ax2.axhline(0, color="#475569", linestyle="-", linewidth=1.0, zorder=2)
        ax2.set_xticks(x_indices)
        clean_tier_names = ["Strategic\nEnterprise", "Mid-Market\nCore", "SMB\nStandard", "Toxic Accounts\n(Restructured)"]
        ax2.set_xticklabels(clean_tier_names, fontsize=10, fontweight="bold", color="#1E293B")
        
        ax2.set_title("Pocket EBITDA by Customer Tier ($M USD)", fontsize=13, fontweight="bold", color="#0F172A", pad=15)
        ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}M"))
        ax2.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1")
        ax2.legend(loc="upper right", framealpha=0.95, fontsize=10)
        
        # Toxic turn-around callout
        toxic_rec = tier_df.loc[tier_df["client_tier"] == "Toxic_Drain", "ebitda_recovery"].values[0] / 1e6
        ax2.annotate(
            f"Turnaround: +${toxic_rec:,.1f}M\nFrom -$85.6M to +$8.7M",
            xy=(3 + width/2, 10), xytext=(2.1, -45),
            arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.8),
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#EFF6FF", edgecolor="#2563EB", alpha=0.95),
            fontsize=9.5, fontweight="bold", color="#1E40AF"
        )
        
        fig.suptitle("Strategic Policy Simulation: MOQ Enforcement + Discount Floor Impact",
                     fontsize=16, fontweight="bold", y=1.02, color="#0F172A")
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, filename)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved: {save_path}")

if __name__ == "__main__":
    from src.waterfall_analyzer import PocketMarginWaterfallAnalyzer
    from src.whale_curve import WhaleCurveAnalyzer
    from src.pricing_engine import System2StrategicOptimizer
    
    print("Loading ERP transaction data for visualization generation...")
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    
    vis = FinancialVisualizationEngine(output_dir="assets")
    
    # 1. Waterfall
    print("Generating Pocket Margin Waterfall...")
    wf_analyzer = PocketMarginWaterfallAnalyzer(df_raw)
    df_wf = wf_analyzer.compute_portfolio_waterfall()
    vis.plot_pocket_margin_waterfall(df_wf)
    
    # 2. Whale Curve
    print("Generating Whale Curve...")
    wc_analyzer = WhaleCurveAnalyzer(df_raw)
    df_curve = wc_analyzer.get_curve_dataframe()
    wc_metrics = wc_analyzer.get_whale_metrics()
    vis.plot_whale_curve(df_curve, wc_metrics)
    
    # 3. Discount Dispersion
    print("Generating Price-Volume Dispersion...")
    vis.plot_discount_dispersion(df_raw)
    
    # 4. Scenario Recovery
    print("Generating EBITDA Recovery Scenario...")
    s2_opt = System2StrategicOptimizer(df_raw)
    sim_res = s2_opt.simulate_policy_rollout()
    vis.plot_ebitda_recovery_scenario(sim_res)
    
    print("\nAll 4 executive visualizations successfully generated at 300 DPI in /assets!")
