# System Notes: B2B Margin Leakage Diagnostics & Dynamic Pricing Optimization

## Executive Metadata
- **Analysis Date**: 2026-10-22
- **Lead Role**: Chief Revenue Operations & Pricing Analytics Director
- **Dataset Scope**: 55,000 ERP Invoice Lines | 800 B2B Accounts | 25 Sales Reps | 4 Product Families
- **Fiscal Base**: 2024 Full Fiscal Year

---

## 1. Enterprise Financial Baseline (Actuals)
| Metric | Amount ($ USD) | % of Net Invoiced Revenue |
| :--- | :--- | :--- |
| **Gross List Revenue** | $1,439,498,131.93 | 127.65% |
| **On-Invoice Discounts Conceded** | -$311,793,683.59 | -27.65% |
| **Net Invoiced Revenue** | **$1,127,704,448.34** | **100.00%** |
| **Cost of Goods Sold (COGS)** | -$785,457,722.51 | -69.65% |
| **Standard Gross Profit** | $342,246,725.83 | 30.35% |
| **Off-Invoice Rebates & Allowances** | -$25,097,609.58 | -2.23% |
| **Order Logistics & Freight Fulfillment** | -$98,397,151.22 | -8.73% |
| **Cost of Working Capital (WACC @ 8.5%)** | -$8,031,950.02 | -0.71% |
| **Realized Net Pocket Margin (EBITDA)** | **$210,720,015.01** | **18.69%** |

---

## 2. The Whale Curve (Stobachoff Analysis) Milestones
- **Total Portfolio Accounts**: 800
- **Peak Cumulative Profit Point**: **$296.30M** (140.6% of Final Realized Profit) reached at **Client #678** (84.8% of total accounts).
- **Top 20% Accounts (Value Creators)**: 160 accounts generate **$279.98M** (132.9% of Final Enterprise Profit).
- **Middle 65% Accounts (Breakeven Plateau)**: Generate modest net profit (+$16.32M) absorbing fixed overhead.
- **Bottom 15% Accounts (Value Destruction Tail)**: 120 accounts produce **-$85.58M** (-40.6% of Final Enterprise Profit).
- **Total EBITDA Destroyed by Toxic Tail**: **$85.58M** (40.6% of baseline EBITDA).
- **Negative Margin Accounts**: 122 accounts (15.2% of customer base) operate at a net loss.

---

## 3. Root Cause Attribution of Margin Leakage
1. **Sub-Scale Micro-Order Fulfillment**: 
   - Orders under 5 units incurred severe LTL accessorial courier penalties ($8,000 - $13,000 per shipment on hazardous chemicals and industrial items) because sales reps allowed emergency drop-shipping without minimum order consolidation.
2. **Rogue Sales Rep Discounting**:
   - Identified 12 rogue sales representatives (REP-02, REP-04, REP-05, REP-03, REP-01) who systematically conceded 40% - 50% discounts on micro-orders (1-3 units) to hit quarterly sales volume bonuses, destroying gross profit before logistics was even billed.
3. **Chronic Working Capital Delay**:
   - Toxic accounts averaged 110 days payment delay versus contract terms of Net 30, inflicting substantial working capital financing costs at 8.5% WACC.

---

## 4. Algorithmic Guardrail Simulation (System 1 + System 2 Decision Engine)
### Policy Adjustments Enforced:
1. **MOQ Policy**: Enforced Minimum Order Quantities by SKU category (5 for Heavy Industrial, 8 for Chemicals, 20 for Sensors, 25 for MRO) or automated sub-scale surcharge, eliminating emergency LTL accessorial leakage.
2. **Discount Floor Corridor**: Capped small-order discounts to a maximum ceiling of 15% (preventing rogue 45% concessions on tiny orders).
3. **Payment Term Discipline**: Enforced strict Net 35 terms on chronic late payers.

### Quantitative Recovery Results:
- **Baseline Net Invoiced Revenue**: $1,127,704,448.34
- **Optimized Net Invoiced Revenue**: $1,171,913,192.02 (+$44,208,743.68 lift from volume consolidation & discount discipline)
- **Baseline Pocket EBITDA**: $210,720,015.01 (18.69%)
- **Optimized Pocket EBITDA**: $311,674,300.41 (26.60%)
- **NET EBITDA EXPANSION**: **+$100,954,285.40**
- **EBITDA MARGIN EXPANSION**: **+791 basis points (+7.91% margin lift)**

### Segment-Level EBITDA Recovery:
| Customer Segment | Baseline EBITDA ($M) | Optimized EBITDA ($M) | EBITDA Recovery ($M) | Baseline Margin % | Optimized Margin % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier-A: Enterprise Key** | $205.15M | $204.31M | $-0.84M | 25.48% | 25.34% |
| **Tier-B: MidMarket Core** | $74.83M | $75.74M | $+0.91M | 30.18% | 30.20% |
| **Tier-C: SMB Standard** | $16.32M | $22.91M | $+6.59M | 24.76% | 27.80% |
| **Tier-D: Toxic Accounts** | $-85.58M | $8.71M | **$+94.29M** | -1002.15% | **26.91%** |

---

## 5. Architectural Innovations: System 1 vs. System 2 Decision Engine
- **System 1 (Reflexive Real-Time CPQ Gate)**: Evaluates incoming sales rep quote requests in **0.009 milliseconds**. Automatically applies MOQ rounding, enforces maximum discount ceilings by volume tier, flags rogue reps, and escalates out-of-bounds quotes to Revenue Operations leadership.
- **System 2 (Strategic Analytical Simulator)**: Aggregates portfolio-wide data, runs K-Means RFM clustering, models price elasticity, and projects corporate EBITDA expansion across alternative policy thresholds.
