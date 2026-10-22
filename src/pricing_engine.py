"""
B2B Dynamic Pricing Engine & Decision Architecture
Combines:
1. System 1 (Reflexive Real-Time Guardrail Engine): Fast microsecond quote evaluation for CPQ/ERP.
2. System 2 (Strategic Analytical Optimizer): Portfolio-wide simulation of MOQ and discount floor policies.
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class QuoteRequest:
    client_id: str
    client_tier: str
    product_family: str
    sku: str
    unit_list_price: float
    quantity: int
    proposed_discount_pct: float
    payment_delay_days: int
    sales_rep_id: str
    unit_cogs: float
    base_handling: float
    unit_freight: float
    rebate_pct: float

@dataclass
class PricingVerdict:
    status: str  # 'AUTO_APPROVED', 'ADJUSTED_AND_APPROVED', 'ESCALATED_TO_DIRECTOR'
    original_invoice_price: float
    approved_invoice_price: float
    original_discount_pct: float
    approved_discount_pct: float
    original_quantity: int
    approved_quantity: int
    original_pocket_margin: float
    approved_pocket_margin: float
    margin_lift_amount: float
    reasons: List[str]
    system_latency_ms: float

class System1PricingGuardrail:
    """
    System 1: Ultra-fast reflexive pricing guardrail and quoting decision gate.
    Executes in <1ms to provide instant CPQ feedback to sales reps and ERP order entry.
    """
    
    MOQ_THRESHOLDS = {
        "Heavy_Industrial": 5,
        "Specialty_Chemicals": 8,
        "Electronic_Sensors": 20,
        "MRO_Consumables": 25
    }
    
    # Maximum allowable discount floors by volume and tier
    DISCOUNT_CEILINGS = {
        "Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)": {
            "micro": 0.08, "small": 0.12, "mid": 0.15, "large": 0.20
        },
        "Tier-C: SMB Long-Tail (Standard Pricing, Low Volume)": {
            "micro": 0.10, "small": 0.15, "mid": 0.20, "large": 0.25
        },
        "Tier-B: Core Growth (Solid Margin & Predictable Terms)": {
            "micro": 0.12, "small": 0.18, "mid": 0.22, "large": 0.28
        },
        "Tier-A: Strategic Enterprise (High Volume Anchor)": {
            "micro": 0.15, "small": 0.20, "mid": 0.26, "large": 0.35
        }
    }
    
    def __init__(self, rogue_reps: Optional[List[str]] = None):
        self.rogue_reps = set(rogue_reps or [])
        
    def _get_volume_bracket(self, quantity: int) -> str:
        if quantity < 5:
            return "micro"
        elif quantity < 20:
            return "small"
        elif quantity < 50:
            return "mid"
        else:
            return "large"
            
    def evaluate_quote(self, quote: QuoteRequest) -> PricingVerdict:
        """
        Instant System 1 heuristic evaluation.
        """
        t0 = time.perf_counter()
        reasons = []
        status = "AUTO_APPROVED"
        
        approved_qty = quote.quantity
        approved_discount = quote.proposed_discount_pct
        
        # 1. MOQ Check
        moq = self.MOQ_THRESHOLDS.get(quote.product_family, 10)
        if quote.quantity < moq:
            approved_qty = moq
            reasons.append(f"MOQ Policy: Quantity adjusted from {quote.quantity} to minimum {moq} units.")
            status = "ADJUSTED_AND_APPROVED"
            
        # 2. Discount Floor Guardrail Check
        bracket = self._get_volume_bracket(approved_qty)
        tier_ceilings = self.DISCOUNT_CEILINGS.get(quote.client_tier, self.DISCOUNT_CEILINGS["Tier-C: SMB Long-Tail (Standard Pricing, Low Volume)"])
        max_allowed_discount = tier_ceilings.get(bracket, 0.20)
        
        if quote.proposed_discount_pct > max_allowed_discount:
            approved_discount = max_allowed_discount
            reasons.append(f"Discount Guardrail: Proposed {quote.proposed_discount_pct*100:.1f}% exceeds max {max_allowed_discount*100:.1f}% for {bracket} volume.")
            status = "ADJUSTED_AND_APPROVED"
            
        # 3. Rogue Rep Escalation Check
        if quote.sales_rep_id in self.rogue_reps and quote.proposed_discount_pct > (max_allowed_discount + 0.10):
            status = "ESCALATED_TO_DIRECTOR"
            reasons.append(f"Sales Rep Audit: {quote.sales_rep_id} flagged for unauthorized rogue discounting.")
            
        # 4. Financial Pocket Margin Calculation
        # Original
        orig_gross = quote.unit_list_price * quote.quantity
        orig_inv = orig_gross * (1.0 - quote.proposed_discount_pct)
        orig_cogs = quote.unit_cogs * quote.quantity
        orig_freight = quote.base_handling + (quote.unit_freight * quote.quantity)
        # Surcharge penalty on sub-MOQ
        if quote.quantity < moq:
            orig_freight += 8500.0 if "Toxic" in quote.client_tier else 45.0
        orig_capital = orig_inv * (0.085 / 365) * quote.payment_delay_days
        orig_rebate = orig_inv * quote.rebate_pct
        orig_margin = orig_inv - orig_cogs - orig_freight - orig_capital - orig_rebate
        
        # Approved
        app_gross = quote.unit_list_price * approved_qty
        app_inv = app_gross * (1.0 - approved_discount)
        app_cogs = quote.unit_cogs * approved_qty
        app_freight = quote.base_handling + (quote.unit_freight * approved_qty)
        # Since MOQ is met, no subscale penalty!
        app_capital = app_inv * (0.085 / 365) * min(quote.payment_delay_days, 35)
        app_rebate = app_inv * quote.rebate_pct
        app_margin = app_inv - app_cogs - app_freight - app_capital - app_rebate
        
        margin_lift = app_margin - orig_margin
        latency_ms = (time.perf_counter() - t0) * 1000.0
        
        if not reasons:
            reasons.append("Within standard pricing corridor. Auto-approved.")
            
        return PricingVerdict(
            status=status,
            original_invoice_price=orig_inv,
            approved_invoice_price=app_inv,
            original_discount_pct=quote.proposed_discount_pct,
            approved_discount_pct=approved_discount,
            original_quantity=quote.quantity,
            approved_quantity=approved_qty,
            original_pocket_margin=orig_margin,
            approved_pocket_margin=app_margin,
            margin_lift_amount=margin_lift,
            reasons=reasons,
            system_latency_ms=latency_ms
        )

class System2StrategicOptimizer:
    """
    System 2: Strategic Analytical Optimizer and Policy Simulator.
    Simulates portfolio-wide rollout of dynamic pricing guardrails across all transactions.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def simulate_policy_rollout(self) -> Dict[str, Any]:
        """
        Simulates corporate policy shift:
        1. MOQ Policy: Orders below MOQ (quantity <= 4) are either bundled to MOQ or charged freight surcharge.
           Eliminates subscale LTL accessorial freight leakage.
        2. Discount Guardrail: Caps rogue discounts on small orders to a maximum floor of 15% (or 20% on mid).
        3. Payment Delay Contraction: Enforces Net 30/35 payment terms on delinquent accounts.
        """
        sim = self.df.copy()
        
        # Policy 1: Logistics subscale leakage remediation
        # Baseline logistics cost includes the massive LTL subscale accessorials
        # Under policy, either MOQ is enforced or customer pays handling surcharge, neutralizing the loss
        sim["optimized_quantity"] = np.where(sim["quantity"] <= 4, 8, sim["quantity"])
        
        # Optimized Gross Revenue
        sim["optimized_gross_revenue"] = sim["unit_list_price"] * sim["optimized_quantity"]
        
        # Policy 2: Discount Guardrails
        # If order was small (<10 units) and discount was >20%, cap at 15%
        # If account was toxic with discount >25%, cap at 18%
        is_subscale = sim["quantity"] < 10
        is_toxic = sim["client_tier"] == "Toxic_Drain"
        
        sim["optimized_discount_pct"] = sim["discount_pct"]
        sim.loc[is_subscale & (sim["discount_pct"] > 0.20), "optimized_discount_pct"] = 0.15
        sim.loc[is_toxic & (sim["discount_pct"] > 0.22), "optimized_discount_pct"] = 0.18
        
        # Optimized Invoiced Revenue
        sim["optimized_invoice_revenue"] = sim["optimized_gross_revenue"] * (1.0 - sim["optimized_discount_pct"])
        
        # Optimized COGS
        sim["optimized_cogs"] = sim["unit_cogs"] * sim["optimized_quantity"]
        
        # Optimized Logistics: Freight scaled cleanly with bulk, eliminating emergency accessorials
        base_handling = sim["logistics_cost"] # reference
        freight_rate = np.where(sim["product_family"] == "Heavy_Industrial", 14.5,
                                np.where(sim["product_family"] == "Specialty_Chemicals", 8.0,
                                         np.where(sim["product_family"] == "Electronic_Sensors", 1.2, 0.9)))
        fixed_handling = np.where(sim["product_family"] == "Heavy_Industrial", 45.0,
                                  np.where(sim["product_family"] == "Specialty_Chemicals", 38.0,
                                           np.where(sim["product_family"] == "Electronic_Sensors", 20.0, 22.0)))
        
        sim["optimized_logistics_cost"] = np.round(fixed_handling + (freight_rate * sim["optimized_quantity"]), 2)
        
        # Policy 3: Payment Delay tightening (max 35 days)
        sim["optimized_payment_delay"] = np.minimum(sim["payment_delay_days"], 35)
        sim["optimized_cost_of_capital"] = np.round(
            sim["optimized_invoice_revenue"] * (0.085 / 365.0) * sim["optimized_payment_delay"], 2
        )
        
        # Optimized Rebates
        sim["optimized_rebates"] = np.round(sim["optimized_invoice_revenue"] * sim["rebate_pct"], 2)
        
        # Optimized Net Pocket Margin
        sim["optimized_pocket_margin"] = np.round(
            sim["optimized_invoice_revenue"] - sim["optimized_cogs"] - sim["optimized_rebates"] -
            sim["optimized_logistics_cost"] - sim["optimized_cost_of_capital"], 2
        )
        
        # Aggregated Comparisons
        baseline_revenue = self.df["invoice_revenue"].sum()
        baseline_margin = self.df["net_pocket_margin"].sum()
        baseline_margin_pct = (baseline_margin / baseline_revenue) * 100.0
        
        optimized_revenue = sim["optimized_invoice_revenue"].sum()
        optimized_margin = sim["optimized_pocket_margin"].sum()
        optimized_margin_pct = (optimized_margin / optimized_revenue) * 100.0
        
        ebitda_expansion_amount = optimized_margin - baseline_margin
        ebitda_margin_expansion_bps = (optimized_margin_pct - baseline_margin_pct) * 100.0
        
        # Breakdown by tier
        tier_recovery = sim.groupby("client_tier").agg(
            baseline_margin=("net_pocket_margin", "sum"),
            optimized_margin=("optimized_pocket_margin", "sum"),
            baseline_revenue=("invoice_revenue", "sum"),
            optimized_revenue=("optimized_invoice_revenue", "sum")
        ).reset_index()
        tier_recovery["ebitda_recovery"] = tier_recovery["optimized_margin"] - tier_recovery["baseline_margin"]
        tier_recovery["baseline_pct"] = (tier_recovery["baseline_margin"] / tier_recovery["baseline_revenue"]) * 100.0
        tier_recovery["optimized_pct"] = (tier_recovery["optimized_margin"] / tier_recovery["optimized_revenue"]) * 100.0
        
        return {
            "baseline_revenue": baseline_revenue,
            "baseline_margin": baseline_margin,
            "baseline_margin_pct": baseline_margin_pct,
            "optimized_revenue": optimized_revenue,
            "optimized_margin": optimized_margin,
            "optimized_margin_pct": optimized_margin_pct,
            "ebitda_expansion_amount": ebitda_expansion_amount,
            "ebitda_margin_expansion_bps": ebitda_margin_expansion_bps,
            "tier_recovery": tier_recovery,
            "simulation_df": sim
        }

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    
    print("\n--- TESTING SYSTEM 1 (MICROSECOND REFLEXIVE DECISION GATE) ---")
    sys1 = System1PricingGuardrail(rogue_reps=["REP-02", "REP-04"])
    
    sample_quote = QuoteRequest(
        client_id="CUST-0042",
        client_tier="Tier-D: Toxic Drain (High Micro-Orders & Over-Discounted)",
        product_family="Heavy_Industrial",
        sku="IND-001",
        unit_list_price=1850.0,
        quantity=2,
        proposed_discount_pct=0.45,
        payment_delay_days=115,
        sales_rep_id="REP-02",
        unit_cogs=1050.0,
        base_handling=45.0,
        unit_freight=14.5,
        rebate_pct=0.03
    )
    
    verdict = sys1.evaluate_quote(sample_quote)
    print(f"Verdict Status: {verdict.status}")
    print(f"System Latency: {verdict.system_latency_ms:.3f} ms")
    print(f"Original Invoiced: ${verdict.original_invoice_price:,.2f} | Original Margin: ${verdict.original_pocket_margin:,.2f}")
    print(f"Approved Invoiced: ${verdict.approved_invoice_price:,.2f} | Approved Margin: ${verdict.approved_pocket_margin:,.2f}")
    print(f"Margin Lift: +${verdict.margin_lift_amount:,.2f}")
    print(f"Enforced Reasons: {verdict.reasons}")
    
    print("\n--- TESTING SYSTEM 2 (STRATEGIC PORTFOLIO POLICY SIMULATOR) ---")
    sys2 = System2StrategicOptimizer(df_raw)
    res = sys2.simulate_policy_rollout()
    
    print(f"Baseline Enterprise Revenue : ${res['baseline_revenue']:,.2f}")
    print(f"Baseline Pocket EBITDA      : ${res['baseline_margin']:,.2f} ({res['baseline_margin_pct']:.2f}%)")
    print(f"Optimized Enterprise Revenue: ${res['optimized_revenue']:,.2f}")
    print(f"Optimized Pocket EBITDA     : ${res['optimized_margin']:,.2f} ({res['optimized_margin_pct']:.2f}%)")
    print(f"TOTAL EBITDA RECOVERY       : +${res['ebitda_expansion_amount']:,.2f} (+{res['ebitda_margin_expansion_bps']:.1f} bps / +{res['ebitda_margin_expansion_bps']/100:.2f}%)")
    
    print("\nEBITDA Recovery by Customer Tier:")
    print(res["tier_recovery"][["client_tier", "baseline_margin", "optimized_margin", "ebitda_recovery", "baseline_pct", "optimized_pct"]].to_string(index=False))
