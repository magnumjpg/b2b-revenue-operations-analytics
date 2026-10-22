"""
Main Orchestration Pipeline
B2B Margin Leakage Diagnostics, Whale Curve Profitability & Dynamic Pricing Optimization
Coordinates all analytical workstreams:
1. Data Architecture: Generates or loads ERP transactional dataset (55,000+ lines).
2. Quantitative Analysis: Runs Waterfall, Whale Curve, and Customer Clustering.
3. Pricing Engine: Executes System 1 (Instant CPQ Guardrail) and System 2 (Policy Simulator).
4. Financial Visualizations: Renders 300 DPI executive charts in /assets.
5. System Ledger: Logs exact recoveries to SYSTEM_NOTES.md.
"""

import os
import sys
import time
import pandas as pd
import numpy as np

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_generator import generate_b2b_erp_dataset
from src.waterfall_analyzer import PocketMarginWaterfallAnalyzer
from src.whale_curve import WhaleCurveAnalyzer
from src.clustering_guardrails import CustomerClusteringAndRepDiagnostics
from src.pricing_engine import System1PricingGuardrail, System2StrategicOptimizer, QuoteRequest
from src.visualizations import FinancialVisualizationEngine

def run_full_pipeline():
    start_total_time = time.time()
    print("================================================================================")
    print("  CHIEF REVENUE OPERATIONS & PRICING ANALYTICS - EXECUTIVE PIPELINE")
    print("  Project: B2B Margin Leakage Diagnostics & Dynamic Pricing Optimization")
    print("================================================================================\n")
    
    # -------------------------------------------------------------
    # 1. B2B ERP Transaction Data Generation / Ingestion
    # -------------------------------------------------------------
    data_path = "data/b2b_erp_transactions.parquet"
    if not os.path.exists(data_path):
        print("[Workstream 1] Generating fresh 55,000-line B2B ERP transaction dataset...")
        df = generate_b2b_erp_dataset(n_transactions=55000, n_clients=800, n_sales_reps=25)
        df.to_parquet(data_path, index=False)
    else:
        print(f"[Workstream 1] Loading existing B2B ERP dataset from {data_path}...")
        df = pd.read_parquet(data_path)
        
    print(f" -> Processed {len(df):,} invoice lines across {df['client_id'].nunique()} accounts and {df['sales_rep_id'].nunique()} sales reps.")
    print(f" -> Total Gross List Value: ${df['gross_revenue'].sum():,.2f}")
    print(f" -> Total Invoiced Revenue: ${df['invoice_revenue'].sum():,.2f}")
    print(f" -> Realized Pocket Margin: ${df['net_pocket_margin'].sum():,.2f} ({df['net_pocket_margin'].sum()/df['invoice_revenue'].sum()*100:.2f}% Margin)\n")
    
    # -------------------------------------------------------------
    # 2. Pocket Margin Waterfall Analysis
    # -------------------------------------------------------------
    print("[Workstream 2A] Executing Pocket Margin Waterfall Decomposition...")
    wf_analyzer = PocketMarginWaterfallAnalyzer(df)
    df_waterfall = wf_analyzer.compute_portfolio_waterfall()
    print("  Stage-by-Stage Value Bridge:")
    for _, row in df_waterfall.iterrows():
        print(f"   * {row['stage']:35s}: ${row['amount']/1e6:+9.2f}M  ({row['pct_invoice']:+6.1f}% of Invoiced)")
    print()
    
    # -------------------------------------------------------------
    # 3. Whale Curve Cumulative Profitability
    # -------------------------------------------------------------
    print("[Workstream 2B] Computing Whale Curve (Stobachoff Cumulative Profitability)...")
    wc_analyzer = WhaleCurveAnalyzer(df)
    wc_metrics = wc_analyzer.get_whale_metrics()
    df_curve = wc_analyzer.get_curve_dataframe()
    
    print(f"   * Peak Cumulative Margin   : ${wc_metrics['peak_margin']/1e6:,.2f}M ({wc_metrics['peak_margin_pct_of_total']:.1f}% of Final Profit)")
    print(f"   * Reached at Customer Rank : Account #{wc_metrics['peak_client_rank']} ({wc_metrics['peak_client_pct']:.1f}% of Accounts)")
    print(f"   * Top 20% Accounts Profit  : ${wc_metrics['top_20_margin']/1e6:,.2f}M ({wc_metrics['top_20_margin_pct_of_total']:.1f}% of Final Profit)")
    print(f"   * Bottom 15% Accounts Loss : ${wc_metrics['bottom_15_margin']/1e6:,.2f}M ({wc_metrics['bottom_15_margin_pct_of_total']:.1f}% of Final Profit)")
    print(f"   * Total EBITDA Destroyed   : ${wc_metrics['ebitda_destroyed_by_tail']/1e6:,.2f}M ({wc_metrics['ebitda_destroyed_pct']:.1f}% Margin Destruction)\n")
    
    # -------------------------------------------------------------
    # 4. Customer Clustering & Rogue Sales Rep Diagnostics
    # -------------------------------------------------------------
    print("[Workstream 2C] Executing RFM + Margin Clustering & Sales Rep Audit...")
    diag = CustomerClusteringAndRepDiagnostics(df, n_clusters=4)
    df_clustered = diag.fit_customer_clusters()
    df_reps = diag.diagnose_sales_reps()
    
    rogue_rep_ids = df_reps[df_reps["is_rogue_flagged"]]["sales_rep_id"].tolist()
    print(f"   * Flagged {len(rogue_rep_ids)} Rogue Sales Reps conceding unauthorized discounts: {rogue_rep_ids[:5]}")
    for _, r in df_reps.head(3).iterrows():
        print(f"     - {r['sales_rep_id']} ({r['rep_profile']}): Small Orders Avg Discount = {r['small_orders_avg_discount']*100:.1f}%, Net Margin = {r['pocket_margin_pct']:.1f}%")
    print()
    
    # -------------------------------------------------------------
    # 5. Price-Volume Elasticity Econometric Modeling
    # -------------------------------------------------------------
    print("[Workstream 2D] Fitting Log-Log Price-Volume Elasticity Model (Scikit-Learn)...")
    from src.elasticity_engine import PriceElasticityEngine
    el_engine = PriceElasticityEngine(df)
    el_res = el_engine.fit_portfolio_elasticity()
    print(f"   * Portfolio Price Elasticity Beta : {el_res['portfolio_elasticity_beta']:.4f} (R² = {el_res['portfolio_r2']:.4f})")
    for _, er in el_res["tier_elasticity_table"].iterrows():
        print(f"     - {er['client_tier']:15s}: Beta={er['price_elasticity_beta']:+.3f} | Regime={er['demand_regime']} | Max Rec Discount={er['recommended_discount_ceiling']*100:.0f}%")
    print()

    # -------------------------------------------------------------
    # 6. Dynamic Pricing Engine: System 1 (Instant CPQ) & System 2 (Policy Simulator)
    # -------------------------------------------------------------
    print("[Workstream 2E] Evaluating Pricing Decision Engine (System 1 & System 2)...")
    
    # System 1 Demo
    sys1 = System1PricingGuardrail(rogue_reps=rogue_rep_ids)
    test_quote = QuoteRequest(
        client_id="CUST-0099",
        client_tier="Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)",
        product_family="Heavy_Industrial",
        sku="IND-004",
        unit_list_price=2200.0,
        quantity=2,  # Sub-MOQ
        proposed_discount_pct=0.42,  # Rogue concession
        payment_delay_days=110,
        sales_rep_id=rogue_rep_ids[0] if rogue_rep_ids else "REP-02",
        unit_cogs=1250.0,
        base_handling=45.0,
        unit_freight=14.5,
        rebate_pct=0.03
    )
    verdict = sys1.evaluate_quote(test_quote)
    print(f"   * System 1 Real-Time Gate [Latency: {verdict.system_latency_ms:.3f} ms]:")
    print(f"     - Decision Status: {verdict.status}")
    print(f"     - Original Quote : Qty={test_quote.quantity}, Discount={test_quote.proposed_discount_pct*100:.1f}%, Pocket Margin=${verdict.original_pocket_margin:,.2f}")
    print(f"     - Approved Quote : Qty={verdict.approved_quantity}, Discount={verdict.approved_discount_pct*100:.1f}%, Pocket Margin=${verdict.approved_pocket_margin:,.2f}")
    print(f"     - Immediate Order Margin Lift: +${verdict.margin_lift_amount:,.2f}")
    
    # System 2 Portfolio Simulation
    sys2 = System2StrategicOptimizer(df)
    sim_res = sys2.simulate_policy_rollout()
    print("\n   * System 2 Strategic Portfolio Policy Simulation:")
    print(f"     - Baseline Enterprise Pocket EBITDA : ${sim_res['baseline_margin']/1e6:,.2f}M ({sim_res['baseline_margin_pct']:.2f}%)")
    print(f"     - Optimized Enterprise Pocket EBITDA: ${sim_res['optimized_margin']/1e6:,.2f}M ({sim_res['optimized_margin_pct']:.2f}%)")
    print(f"     - TOTAL NET EBITDA RECOVERY         : +${sim_res['ebitda_expansion_amount']/1e6:,.2f}M (+{sim_res['ebitda_margin_expansion_bps']:.0f} bps / +{sim_res['ebitda_margin_expansion_bps']/100:.2f}%)")
    print()
    
    # -------------------------------------------------------------
    # 6. Financial Visualizations
    # -------------------------------------------------------------
    print("[Workstream 3] Rendering 300 DPI Publication-Grade Executive Visualizations...")
    vis = FinancialVisualizationEngine(output_dir="assets")
    vis.plot_pocket_margin_waterfall(df_waterfall)
    vis.plot_whale_curve(df_curve, wc_metrics)
    vis.plot_discount_dispersion(df)
    vis.plot_ebitda_recovery_scenario(sim_res)
    print()
    
    # -------------------------------------------------------------
    # 7. Executive Financial Model Excel Export
    # -------------------------------------------------------------
    print("[Corporate Deliverable] Building Institutional-Grade Multi-Tab Excel Financial Model...")
    from src.excel_exporter import ExecutiveExcelModelExporter
    excel_path = "data/B2B_Margin_Leakage_Executive_Model.xlsx"
    exporter = ExecutiveExcelModelExporter(df, output_path=excel_path)
    exporter.build_workbook()
    print()
    
    # -------------------------------------------------------------
    # 8. Write Ledger to SYSTEM_NOTES.md
    # -------------------------------------------------------------
    print("[System Notes] Generating continuous ledger SYSTEM_NOTES.md...")
    log_content = f"""# System Notes: B2B Margin Leakage Diagnostics & Dynamic Pricing Optimization

## Executive Metadata
- **Analysis Date**: 2026-10-22
- **Lead Role**: Chief Revenue Operations & Pricing Analytics Director
- **Dataset Scope**: {len(df):,} ERP Invoice Lines | {df['client_id'].nunique()} B2B Accounts | {df['sales_rep_id'].nunique()} Sales Reps | 4 Product Families
- **Fiscal Base**: 2024 Full Fiscal Year

---

## 1. Enterprise Financial Baseline (Actuals)
| Metric | Amount ($ USD) | % of Net Invoiced Revenue |
| :--- | :--- | :--- |
| **Gross List Revenue** | ${df['gross_revenue'].sum():,.2f} | {(df['gross_revenue'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **On-Invoice Discounts Conceded** | -${df['discount_amount'].sum():,.2f} | -{(df['discount_amount'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Net Invoiced Revenue** | **${df['invoice_revenue'].sum():,.2f}** | **100.00%** |
| **Cost of Goods Sold (COGS)** | -${df['total_cogs'].sum():,.2f} | -{(df['total_cogs'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Standard Gross Profit** | ${df['standard_gross_profit'].sum():,.2f} | {(df['standard_gross_profit'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Off-Invoice Rebates & Allowances** | -${df['off_invoice_rebate_amount'].sum():,.2f} | -{(df['off_invoice_rebate_amount'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Order Logistics & Freight Fulfillment** | -${df['logistics_cost'].sum():,.2f} | -{(df['logistics_cost'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Cost of Working Capital (WACC @ 8.5%)** | -${df['cost_of_capital'].sum():,.2f} | -{(df['cost_of_capital'].sum()/df['invoice_revenue'].sum())*100:.2f}% |
| **Realized Net Pocket Margin (EBITDA)** | **${df['net_pocket_margin'].sum():,.2f}** | **{df['net_pocket_margin'].sum()/df['invoice_revenue'].sum()*100:.2f}%** |

---

## 2. The Whale Curve (Stobachoff Analysis) Milestones
- **Total Portfolio Accounts**: {wc_metrics['total_clients']}
- **Peak Cumulative Profit Point**: **${wc_metrics['peak_margin']/1e6:,.2f}M** ({wc_metrics['peak_margin_pct_of_total']:.1f}% of Final Realized Profit) reached at **Client #{wc_metrics['peak_client_rank']}** ({wc_metrics['peak_client_pct']:.1f}% of total accounts).
- **Top 20% Accounts (Value Creators)**: {wc_metrics['top_20_clients_count']} accounts generate **${wc_metrics['top_20_margin']/1e6:,.2f}M** ({wc_metrics['top_20_margin_pct_of_total']:.1f}% of Final Enterprise Profit).
- **Middle 65% Accounts (Breakeven Plateau)**: Generate modest net profit (+${df_curve.iloc[wc_metrics['top_20_clients_count']:wc_metrics['peak_client_rank']]['net_pocket_margin'].sum()/1e6:,.2f}M) absorbing fixed overhead.
- **Bottom 15% Accounts (Value Destruction Tail)**: {wc_metrics['bottom_15_clients_count']} accounts produce **-${abs(wc_metrics['bottom_15_margin'])/1e6:,.2f}M** ({wc_metrics['bottom_15_margin_pct_of_total']:.1f}% of Final Enterprise Profit).
- **Total EBITDA Destroyed by Toxic Tail**: **${wc_metrics['ebitda_destroyed_by_tail']/1e6:,.2f}M** ({wc_metrics['ebitda_destroyed_pct']:.1f}% of baseline EBITDA).
- **Negative Margin Accounts**: {wc_metrics['negative_margin_clients_count']} accounts ({wc_metrics['negative_margin_clients_pct']:.1f}% of customer base) operate at a net loss.

---

## 3. Root Cause Attribution of Margin Leakage
1. **Sub-Scale Micro-Order Fulfillment**: 
   - Orders under 5 units incurred severe LTL accessorial courier penalties ($8,000 - $13,000 per shipment on hazardous chemicals and industrial items) because sales reps allowed emergency drop-shipping without minimum order consolidation.
2. **Rogue Sales Rep Discounting**:
   - Identified {len(rogue_rep_ids)} rogue sales representatives ({', '.join(rogue_rep_ids[:5])}) who systematically conceded 40% - 50% discounts on micro-orders (1-3 units) to hit quarterly sales volume bonuses, destroying gross profit before logistics was even billed.
3. **Chronic Working Capital Delay**:
   - Toxic accounts averaged 110 days payment delay versus contract terms of Net 30, inflicting substantial working capital financing costs at 8.5% WACC.

---

## 4. Algorithmic Guardrail Simulation (System 1 + System 2 Decision Engine)
### Policy Adjustments Enforced:
1. **MOQ Policy**: Enforced Minimum Order Quantities by SKU category (5 for Heavy Industrial, 8 for Chemicals, 20 for Sensors, 25 for MRO) or automated sub-scale surcharge, eliminating emergency LTL accessorial leakage.
2. **Discount Floor Corridor**: Capped small-order discounts to a maximum ceiling of 15% (preventing rogue 45% concessions on tiny orders).
3. **Payment Term Discipline**: Enforced strict Net 35 terms on chronic late payers.

### Quantitative Recovery Results:
- **Baseline Net Invoiced Revenue**: ${sim_res['baseline_revenue']:,.2f}
- **Optimized Net Invoiced Revenue**: ${sim_res['optimized_revenue']:,.2f} (+${sim_res['optimized_revenue'] - sim_res['baseline_revenue']:,.2f} lift from volume consolidation & discount discipline)
- **Baseline Pocket EBITDA**: ${sim_res['baseline_margin']:,.2f} ({sim_res['baseline_margin_pct']:.2f}%)
- **Optimized Pocket EBITDA**: ${sim_res['optimized_margin']:,.2f} ({sim_res['optimized_margin_pct']:.2f}%)
- **NET EBITDA EXPANSION**: **+${sim_res['ebitda_expansion_amount']:,.2f}**
- **EBITDA MARGIN EXPANSION**: **+{sim_res['ebitda_margin_expansion_bps']:.0f} basis points (+{sim_res['ebitda_margin_expansion_bps']/100:.2f}% margin lift)**

### Segment-Level EBITDA Recovery:
| Customer Segment | Baseline EBITDA ($M) | Optimized EBITDA ($M) | EBITDA Recovery ($M) | Baseline Margin % | Optimized Margin % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier-A: Enterprise Key** | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Enterprise_Key', 'baseline_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Enterprise_Key', 'optimized_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Enterprise_Key', 'ebitda_recovery'].values[0]/1e6:+,.2f}M | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Enterprise_Key', 'baseline_pct'].values[0]:.2f}% | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Enterprise_Key', 'optimized_pct'].values[0]:.2f}% |
| **Tier-B: MidMarket Core** | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='MidMarket_Core', 'baseline_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='MidMarket_Core', 'optimized_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='MidMarket_Core', 'ebitda_recovery'].values[0]/1e6:+,.2f}M | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='MidMarket_Core', 'baseline_pct'].values[0]:.2f}% | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='MidMarket_Core', 'optimized_pct'].values[0]:.2f}% |
| **Tier-C: SMB Standard** | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='SMB_Standard', 'baseline_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='SMB_Standard', 'optimized_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='SMB_Standard', 'ebitda_recovery'].values[0]/1e6:+,.2f}M | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='SMB_Standard', 'baseline_pct'].values[0]:.2f}% | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='SMB_Standard', 'optimized_pct'].values[0]:.2f}% |
| **Tier-D: Toxic Accounts** | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Toxic_Drain', 'baseline_margin'].values[0]/1e6:,.2f}M | ${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Toxic_Drain', 'optimized_margin'].values[0]/1e6:,.2f}M | **${sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Toxic_Drain', 'ebitda_recovery'].values[0]/1e6:+,.2f}M** | {sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Toxic_Drain', 'baseline_pct'].values[0]:.2f}% | **{sim_res['tier_recovery'].loc[sim_res['tier_recovery']['client_tier']=='Toxic_Drain', 'optimized_pct'].values[0]:.2f}%** |

---

## 5. Architectural Innovations: System 1 vs. System 2 Decision Engine
- **System 1 (Reflexive Real-Time CPQ Gate)**: Evaluates incoming sales rep quote requests in **{verdict.system_latency_ms:.3f} milliseconds**. Automatically applies MOQ rounding, enforces maximum discount ceilings by volume tier, flags rogue reps, and escalates out-of-bounds quotes to Revenue Operations leadership.
- **System 2 (Strategic Analytical Simulator)**: Aggregates portfolio-wide data, runs K-Means RFM clustering, models price elasticity, and projects corporate EBITDA expansion across alternative policy thresholds.
"""
    
    with open("SYSTEM_NOTES.md", "w", encoding="utf-8") as f:
        f.write(log_content)
    print(" -> Successfully wrote SYSTEM_NOTES.md")
    
    total_elapsed = time.time() - start_total_time
    print(f"\n================================================================================")
    print(f"  PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {total_elapsed:.2f} SECONDS")
    print(f"================================================================================\n")

if __name__ == "__main__":
    run_full_pipeline()
