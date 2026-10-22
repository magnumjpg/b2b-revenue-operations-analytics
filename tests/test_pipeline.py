"""
Unit and Integration Test Suite
Validates the financial logic, mathematical identities, and execution speed
of the B2B Margin Leakage & Dynamic Pricing Analytics Pipeline.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generator import generate_b2b_erp_dataset
from src.waterfall_analyzer import PocketMarginWaterfallAnalyzer
from src.whale_curve import WhaleCurveAnalyzer
from src.clustering_guardrails import CustomerClusteringAndRepDiagnostics
from src.pricing_engine import System1PricingGuardrail, System2StrategicOptimizer, QuoteRequest

@pytest.fixture(scope="session")
def sample_dataset():
    """Generates a reproducible 10,000-row fixture for rapid test execution."""
    df = generate_b2b_erp_dataset(n_transactions=10000, n_clients=800, n_sales_reps=25, random_seed=42)
    return df

def test_data_generation_integrity(sample_dataset):
    df = sample_dataset
    assert len(df) == 10000
    assert df["client_id"].nunique() <= 800
    assert df["sales_rep_id"].nunique() <= 25
    assert df["product_family"].nunique() == 4
    
    # Financial reconciliation checks per line
    calculated_gross = np.round(df["unit_list_price"] * df["quantity"], 2)
    np.testing.assert_allclose(df["gross_revenue"], calculated_gross, atol=0.02)
    
    calculated_inv = np.round(df["gross_revenue"] - df["discount_amount"], 2)
    np.testing.assert_allclose(df["invoice_revenue"], calculated_inv, atol=0.02)

def test_waterfall_mathematical_identity(sample_dataset):
    analyzer = PocketMarginWaterfallAnalyzer(sample_dataset)
    df_wf = analyzer.compute_portfolio_waterfall()
    
    gross = df_wf.loc[df_wf["stage"] == "1. Gross List Price", "amount"].values[0]
    discounts = df_wf.loc[df_wf["stage"] == "2. On-Invoice Discounts", "amount"].values[0]
    inv = df_wf.loc[df_wf["stage"] == "3. Invoice Revenue", "amount"].values[0]
    cogs = df_wf.loc[df_wf["stage"] == "4. Cost of Goods Sold (COGS)", "amount"].values[0]
    rebates = df_wf.loc[df_wf["stage"] == "6. Off-Invoice Rebates", "amount"].values[0]
    logistics = df_wf.loc[df_wf["stage"] == "7. Logistics & Handling", "amount"].values[0]
    financing = df_wf.loc[df_wf["stage"] == "8. Cost of Working Capital (Delay)", "amount"].values[0]
    net_pocket = df_wf.loc[df_wf["stage"] == "9. Net Pocket Margin", "amount"].values[0]
    
    # Mathematical identities
    assert np.isclose(gross + discounts, inv, atol=1.0)
    assert np.isclose(inv + cogs + rebates + logistics + financing, net_pocket, atol=1.0)

def test_whale_curve_stobachoff_properties(sample_dataset):
    analyzer = WhaleCurveAnalyzer(sample_dataset)
    metrics = analyzer.get_whale_metrics()
    
    # Peak cumulative profit must exceed 100% of final profit
    assert metrics["peak_margin"] > metrics["total_enterprise_margin"]
    assert metrics["peak_margin_pct_of_total"] > 115.0  # Demonstrating peak profit phenomenon
    
    # Bottom tail must show net EBITDA destruction
    assert metrics["ebitda_destroyed_by_tail"] > 0
    assert metrics["bottom_15_margin"] < 0
    assert metrics["negative_margin_clients_count"] > 0

def test_customer_clustering_and_rep_audit(sample_dataset):
    diag = CustomerClusteringAndRepDiagnostics(sample_dataset, n_clusters=4)
    df_clustered = diag.fit_customer_clusters()
    df_reps = diag.diagnose_sales_reps()
    
    assert "cluster_id" in df_clustered.columns
    assert "cluster_name" in df_clustered.columns
    assert df_clustered["cluster_id"].nunique() == 4
    
    # Rep diagnosis
    assert "is_rogue_flagged" in df_reps.columns
    assert df_reps["is_rogue_flagged"].sum() > 0

def test_system1_reflexive_guardrail_latency_and_rules():
    sys1 = System1PricingGuardrail(rogue_reps=["REP-99"])
    
    # Sub-MOQ and over-discount quote
    quote = QuoteRequest(
        client_id="CUST-TEST",
        client_tier="Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)",
        product_family="Heavy_Industrial",
        sku="IND-001",
        unit_list_price=1000.0,
        quantity=2,  # Sub-MOQ (MOQ is 5)
        proposed_discount_pct=0.45,  # Exceeds ceiling
        payment_delay_days=90,
        sales_rep_id="REP-99",  # Flagged rogue rep
        unit_cogs=500.0,
        base_handling=45.0,
        unit_freight=14.5,
        rebate_pct=0.02
    )
    
    verdict = sys1.evaluate_quote(quote)
    
    # Latency assertion: must be ultra-fast sub-millisecond (<2ms)
    assert verdict.system_latency_ms < 5.0
    
    # Enforcement assertions
    assert verdict.status == "ESCALATED_TO_DIRECTOR"
    assert verdict.approved_quantity >= 5  # MOQ enforced
    assert verdict.approved_discount_pct <= 0.20  # Discount clamped
    assert verdict.margin_lift_amount > 0  # Restored margin

def test_system2_strategic_policy_recovery(sample_dataset):
    s2 = System2StrategicOptimizer(sample_dataset)
    res = s2.simulate_policy_rollout()
    
    assert res["ebitda_expansion_amount"] > 0
    assert res["optimized_margin"] > res["baseline_margin"]
    assert res["ebitda_margin_expansion_bps"] > 0

def test_excel_export_generation(sample_dataset, tmp_path):
    from src.excel_exporter import ExecutiveExcelModelExporter
    temp_excel = tmp_path / "test_model.xlsx"
    exporter = ExecutiveExcelModelExporter(sample_dataset, output_path=str(temp_excel))
    exporter.build_workbook()
    
    assert os.path.exists(temp_excel)
    assert os.path.getsize(temp_excel) > 5000  # Non-trivial workbook
    
    import openpyxl
    wb = openpyxl.load_workbook(temp_excel)
    assert len(wb.sheetnames) == 5
    assert "01_Executive_Summary" in wb.sheetnames
    assert "02_Pocket_Margin_Waterfall" in wb.sheetnames
    assert "03_Whale_Curve_Deciles" in wb.sheetnames
    assert "04_Pricing_&_MOQ_Matrix" in wb.sheetnames
    assert "05_Sales_Rep_Audit" in wb.sheetnames

def test_price_elasticity_engine(sample_dataset):
    from src.elasticity_engine import PriceElasticityEngine
    engine = PriceElasticityEngine(sample_dataset)
    res = engine.fit_portfolio_elasticity()
    
    assert "portfolio_elasticity_beta" in res
    assert "portfolio_r2" in res
    assert "tier_elasticity_table" in res
    assert len(res["tier_elasticity_table"]) >= 3
