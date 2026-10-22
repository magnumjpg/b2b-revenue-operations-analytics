"""
Generates the executive walkthrough notebook 01_executive_margin_audit.ipynb
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.cells = [
    nbf.v4.new_markdown_cell(
"""# B2B Margin Leakage Diagnostics, Whale Curve & Dynamic Pricing Optimization
**Executive Analytics Portfolio Walkthrough**
*Chief Revenue Operations & Pricing Analytics Director*

---

### Business Case & Operational Overview
In B2B wholesale distribution and industrial supply, enterprise revenue growth frequently masks catastrophic pocket margin erosion. Sales representatives seeking volume quota bonuses grant steep uncoordinated discounts on small orders, less-than-truckload (LTL) rush deliveries incur exorbitant handling costs, and extended payment terms create heavy working capital drag.

This notebook executes an end-to-end diagnostic and remediation framework on 55,000+ ERP transaction lines across 800 B2B accounts.
"""
    ),
    nbf.v4.new_code_cell(
"""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Ensure root is on path
sys.path.insert(0, os.path.abspath('..'))

from src.data_generator import generate_b2b_erp_dataset
from src.waterfall_analyzer import PocketMarginWaterfallAnalyzer
from src.whale_curve import WhaleCurveAnalyzer
from src.clustering_guardrails import CustomerClusteringAndRepDiagnostics
from src.pricing_engine import System1PricingGuardrail, System2StrategicOptimizer, QuoteRequest
from src.visualizations import FinancialVisualizationEngine

print('Libraries loaded successfully.')
"""
    ),
    nbf.v4.new_markdown_cell(
"""## 1. Load ERP Transactional Data
We ingest 55,000 transaction lines spanning 800 accounts, 25 sales reps, and 4 product families (Heavy Industrial, Specialty Chemicals, Electronic Sensors, and MRO Consumables).
"""
    ),
    nbf.v4.new_code_cell(
"""df = pd.read_parquet('../data/b2b_erp_transactions.parquet')
print(f"Total Invoiced Revenue: ${df['invoice_revenue'].sum():,.2f}")
print(f"Total Realized Pocket Margin: ${df['net_pocket_margin'].sum():,.2f} ({df['net_pocket_margin'].sum()/df['invoice_revenue'].sum()*100:.2f}% Margin)")
df.head(5)
"""
    ),
    nbf.v4.new_markdown_cell(
"""## 2. Pocket Margin Waterfall Analysis
Deconstructing the value bridge from Gross List Price to Net Pocket Margin.
"""
    ),
    nbf.v4.new_code_cell(
"""wf = PocketMarginWaterfallAnalyzer(df)
df_wf = wf.compute_portfolio_waterfall()
display(df_wf)
"""
    ),
    nbf.v4.new_markdown_cell(
"""## 3. The Whale Curve (Stobachoff Cumulative Profitability)
Demonstrating how the top 20% of clients generate ~133-141% of profits, while the bottom 15% actively destroy EBITDA.
"""
    ),
    nbf.v4.new_code_cell(
"""wc = WhaleCurveAnalyzer(df)
metrics = wc.get_whale_metrics()
for k, v in metrics.items():
    if isinstance(v, float):
        print(f"{k:35s}: {v:,.2f}")
    else:
        print(f"{k:35s}: {v}")
"""
    ),
    nbf.v4.new_markdown_cell(
"""## 4. Customer RFM Clustering & Rogue Sales Rep Diagnostics
Using K-Means on RFM + Profitability dimensions to isolate toxic accounts and uncover unauthorized rep discounting.
"""
    ),
    nbf.v4.new_code_cell(
"""diag = CustomerClusteringAndRepDiagnostics(df, n_clusters=4)
df_clustered = diag.fit_customer_clusters()
display(diag.cluster_summary)

df_reps = diag.diagnose_sales_reps()
print('Top Rogue Discounters:')
display(df_reps.head(5))
"""
    ),
    nbf.v4.new_markdown_cell(
"""## 5. Dual-Tier Decision Architecture: System 1 (Instant CPQ) & System 2 (Policy Simulator)
- **System 1**: Microsecond heuristic rule gate for quoting.
- **System 2**: Portfolio-wide policy simulation.
"""
    ),
    nbf.v4.new_code_cell(
"""# Test System 1
sys1 = System1PricingGuardrail(rogue_reps=df_reps[df_reps['is_rogue_flagged']]['sales_rep_id'].tolist())
sample_quote = QuoteRequest(
    client_id='CUST-0042',
    client_tier='Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)',
    product_family='Heavy_Industrial',
    sku='IND-001',
    unit_list_price=1850.0,
    quantity=2,
    proposed_discount_pct=0.45,
    payment_delay_days=115,
    sales_rep_id='REP-02',
    unit_cogs=1050.0,
    base_handling=45.0,
    unit_freight=14.5,
    rebate_pct=0.03
)
verdict = sys1.evaluate_quote(sample_quote)
print(f"System 1 Latency: {verdict.system_latency_ms:.3f} ms")
print(f"Decision Status : {verdict.status}")
print(f"Original Margin : ${verdict.original_pocket_margin:,.2f}")
print(f"Approved Margin : ${verdict.approved_pocket_margin:,.2f} (Lift: +${verdict.margin_lift_amount:,.2f})")
print(f"Enforced Reasons: {verdict.reasons}")

# Test System 2
sys2 = System2StrategicOptimizer(df)
sim_res = sys2.simulate_policy_rollout()
print(f"\\nTotal EBITDA Recovery: +${sim_res['ebitda_expansion_amount']:,.2f} (+{sim_res['ebitda_margin_expansion_bps']:.0f} bps)")
display(sim_res['tier_recovery'])
"""
    )
]

with open("notebooks/01_executive_margin_audit.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook notebooks/01_executive_margin_audit.ipynb written successfully.")
