# B2B Margin Leakage Diagnostics, Whale Curve Profitability & Dynamic Pricing Optimization

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Pytest Passed](https://img.shields.io/badge/tests-8%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Deliverable: Excel Model](https://img.shields.io/badge/Excel%20Model-5%20Tabs%20.XLSX-success.svg)](data/B2B_Margin_Leakage_Executive_Model.xlsx)

[English](README.md) | [Español](README_ES.md)

**Author:** Jaime Pérez  
**Focus:** Business Operations, Revenue Operations & Quantitative Pricing Analytics  
**Corporate Scope:** 55,000 ERP Invoice Lines | 800 B2B Accounts | 25 Sales Representatives | 4 Product Families  
**Primary Deliverables:** Fully Modular Python Analytics Pipeline (`/src`), High-Resolution Visualizations (`/assets`), and an Institutional-Grade Multi-Tab Excel Financial Model (`data/B2B_Margin_Leakage_Executive_Model.xlsx`).

---

## 1. Executive Summary & Business Case

In wholesale distribution, industrial manufacturing, and B2B supply chains, enterprise revenue growth frequently masks catastrophic pocket margin erosion. Commercial teams celebrate record top-line billings while operating cash flows stagnate or decline. This structural divergence is driven by what revenue operations professionals term **silent margin leakage**: uncoordinated sales discounting to satisfy quarterly volume quotas, sub-scale order fulfillment that triggers punitive freight accessorial charges, off-invoice annual rebates, and extended payment terms that turn accounts receivable into an expensive interest-free loan funded by the distributor.

This project develops an end-to-end quantitative diagnostic and decision engine applied to a realistic enterprise transactional dataset of 55,000 invoice lines across 800 accounts. By deconstructing the full transaction lifecycle from list price to realized pocket cash contribution, the framework isolates the exact operational friction points that destroy operating income. 

The baseline audit establishes that out of $1,127.70M in recognized net invoiced revenue, the enterprise captures only $210.72M in net pocket margin (an 18.69% pocket EBITDA margin). The root cause lies in extreme customer profitability asymmetry: customer portfolio stratification via the Stobachoff Whale Curve proves that the top 20% of accounts generate 132.87% of total enterprise profit, while the bottom 15% actively destroy -$85.58M in EBITDA. 

To rectify this imbalance without inducing customer attrition, we deploy a **Dual-Tier Pricing Decision Architecture** combining a sub-millisecond reflexive guardrail engine (System 1) for quoting approval with a portfolio policy simulator (System 2). The empirical rollout achieves an annual **+$100.95M EBITDA expansion (+47.9% net profit growth)**, lifting operating margin by **+791 basis points (to 26.60%)**, while transforming the toxic tail from a -$85.58M drain into a profitable +$8.71M contribution.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   EXECUTIVE VALUE SCORECARD                                      │
├───────────────────────────────┬───────────────────────────────┬──────────────────────────────────┤
│ Metric                        │ Baseline Actuals              │ Post-Guardrails Policy           │
├───────────────────────────────┼───────────────────────────────┼──────────────────────────────────┤
│ Net Invoiced Revenue          │ $1,127.70M                    │ $1,171.91M (+$44.21M / +3.9%)    │
│ Realized Pocket EBITDA        │ $210.72M                      │ $311.67M (+$100.95M / +47.9%)    │
│ Pocket EBITDA Margin %        │ 18.69%                        │ 26.60% (+791 bps margin lift)    │
│ Toxic Tail EBITDA Impact      │ -$85.58M (-40.6% erosion)     │ +$8.71M (+26.9% pocket margin)   │
│ System 1 Decision Latency     │ Manual / Discretionary        │ 0.009 ms (<10 microseconds)      │
│ Executive Financial Deliverable│ Static PDF Reports            │ 5-Tab Structured Excel Model     │
└───────────────────────────────┴───────────────────────────────┴──────────────────────────────────┘
```

---

## 2. Dataset & ERP Data Architecture

Because real-world enterprise transactional records from B2B wholesale distributors are protected under strict non-disclosure agreements (NDAs), this project uses a synthetically generated but structurally realistic ERP transactional dataset (`data/b2b_erp_transactions.parquet`). 

The generator (`src/data_generator.py`) simulates a full fiscal year of activity across **55,000 invoice lines, 800 SMB and mid-market accounts, 25 sales representatives, and 4 product families** (Heavy Industrial Machinery, Specialty Chemicals, Electronic Sensors, and MRO Supplies). The schema mirrors actual relational tables found in ERP systems such as Sage 50 and SAP S/4HANA:
- **Commercial Variables:** Unit List Price, Negotiated Discount %, Invoiced Revenue, Sales Rep ID, Customer Account Tier, and Contracted Off-Invoice Rebates (1.5% to 3.5%).
- **Fulfillment & Operational Variables:** Cost of Goods Sold (COGS), base warehouse pick/pack handling fees ($20 to $45), unit freight rates, and less-than-truckload (LTL) rush accessorial fees for emergency drop-shipments.
- **Financial Terms:** Payment terms and empirical payment delay days (ranging from 25 days for disciplined accounts to over 110 days for delinquent accounts), evaluated against an 8.5% annual Weighted Average Cost of Capital (WACC).

All random distributions and customer behavioral profiles are seeded (`random_state=42`) to guarantee 100% reproducible results.

---

## 3. Pocket Margin Waterfall Analysis

Conventional financial statements mislead commercial leadership by evaluating profitability at the gross margin tier ($\text{Gross Profit} = \text{Revenue} - \text{COGS}$). In multi-echelon B2B distribution, gross profit ignores fulfillment friction, volume kickbacks, and working capital carrying charges. The **Pocket Margin Waterfall** bridges Gross List Value down to true net cash contribution, exposing where value leaks between catalog pricing and cash collection.

![Pocket Margin Waterfall](assets/01_pocket_margin_waterfall.png)

The enterprise catalog begins at $1,439.50M in Gross List Price value across the 55,000 transactions. The primary point of margin destruction occurs immediately at the commercial negotiation stage: sales representatives concede -$311.79M in on-invoice discounts (representing 27.65% of net invoiced revenue), bringing top-line invoiced billings down to $1,127.70M. Direct Cost of Goods Sold (COGS) absorbs -$785.46M (69.65%), yielding an apparent standard gross profit of $342.25M (30.35% gross margin). 

Beneath this line, however, significant below-the-line deductions erode profitability. Contractual off-invoice rebates accrued to enterprise customers subtract -$25.10M (2.23%). Order fulfillment logistics—encompassing warehouse picking, packing, and carrier freight—absorbs -$98.40M (8.73%). Because sales reps permitted emergency drop-shipping on single-unit orders, carriers billed severe accessorial surcharges. Finally, accounts receivable carrying costs evaluated at an 8.5% weighted average cost of capital (WACC) consume -$8.03M (0.71%) due to customer payment delays extending past 100 days. The resulting realized Net Pocket Margin is $210.72M, proving that standard gross margin overstates true cash contribution by more than $131.5M.

---

## 3. The Whale Curve: Cumulative Customer Profitability

The distribution of enterprise profit across customer accounts follows an extreme Pareto skew. The **Whale Curve (Stobachoff Analysis)** plots cumulative pocket profit against cumulative customer percentage, ranking all 800 accounts from most to least profitable to determine where profit is generated, where it plateaus, and where it is destroyed.

![Whale Curve Profitability](assets/02_whale_curve_profitability.png)

The curve reveals three distinct operational regimes across the customer base:

1. **The Profit Engines (Top 20% / 160 Accounts):** This segment generates $279.98M, representing 132.87% of total enterprise profit. These accounts order in pallet and truckload batches, respect agreed pricing tiers, and maintain disciplined payment cycles.
2. **The Breakeven Plateau (Middle 65% / 518 Accounts):** These accounts generate $16.32M in net pocket margin. While individual order margins are modest, their aggregate volume absorbs warehouse overhead and procurement scale without burdening executive operations. Cumulative profit reaches its theoretical peak of **$296.30M (140.61% of final enterprise profit) at Account #678 (84.75% of the portfolio)**.
3. **The Value Destruction Tail (Bottom 15% / 122 Accounts):** Beyond the peak point, cumulative profit collapses. The bottom 122 accounts systematically destroy **-$85.58M in cash contribution**, pulling final enterprise EBITDA down from $296.30M to $210.72M. In other words, over 40% of the enterprise profits generated by core accounts are consumed subsidizing the operational inefficiencies of the bottom 15%.

---

## 4. Root Cause Diagnostics: Rogue Discounting & Price-Volume Dispersion

Cross-referencing invoice-level discount rates against order quantities exposes the operational driver of the toxic tail. Standard commercial logic dictates an upward-sloping quantity discount schedule: small orders receive minimal discounts to offset fixed order-processing costs, while bulk orders earn higher volume incentives. In this enterprise, however, decentralized commercial governance created severe price dispersion.

![Price-Volume Dispersion](assets/03_discount_vs_ordersize_dispersion.png)

The scatter audit demonstrates that thousands of micro-orders (1 to 4 units) received discounts ranging between 35% and 52%, placing them squarely within the **Critical Profit Leakage Zone** (highlighted in red). The underlying cause is sales incentive misalignment: representatives were measured on gross invoiced volume rather than pocket contribution.

By clustering sales representative performance across 25 commercial territories, the diagnostic flagged 12 "Rogue Volume Hunters" who systematically used deep discounts to secure small, transactional orders:
- **REP-02:** Recorded an average discount of **49.08% on micro-orders** (<5 units), generating an aggregate pocket margin of **-59.35%** across all managed orders.
- **REP-04:** Conceded **47.77% on micro-orders**, yielding an aggregate pocket margin of **-2.16%**.
- **REP-05:** Conceded **47.34% on micro-orders**, yielding an aggregate pocket margin of **+4.78%**.

Because warehouse picking and shipping minimums range between $45 and $120 per dispatch, an order for 2 units of an MRO or industrial chemical item discounted by 45% generates an immediate operational cash loss before accounting for financing or sales commissions.

---

## 5. Dual-Tier Decision Architecture: System 1 & System 2 Engine

To address both real-time operational execution and long-term portfolio strategy, the pricing architecture is split into two interconnected layers inspired by cognitive decision theory:

```
                                  [ ERP / CPQ Quote Submission ]
                                                │
                                                ▼
                   ┌─────────────────────────────────────────────────────────┐
                   │    SYSTEM 1: Reflexive Real-Time Pricing Guardrail      │
                   │    - Sub-millisecond Execution Latency (<10 μs)         │
                   │    - Deterministic Rules: Volume MOQ & Floor Ceilings   │
                   │    - Automated Rogue Rep Detection & Director Escalation│
                   └────────────────────────────┬────────────────────────────┘
                                                │
                          ┌─────────────────────┴─────────────────────┐
                          ▼                                           ▼
                 [ In-Bounds Quote ]                         [ Policy Violation ]
                          │                                           │
                    AUTO-APPROVED                              AUTO-ADJUSTED
                                                               - Enforce MOQ
                                                               - Clamp Discount
                                                               - Flag Sales Rep
                                                │
                                                ▼
                   ┌─────────────────────────────────────────────────────────┐
                   │    SYSTEM 2: Strategic Analytical Optimizer             │
                   │    - Log-Log Econometric Demand & Elasticity Modeling   │
                   │    - Portfolio-Wide K-Means RFM + Margin Clustering     │
                   │    - Financial Policy Simulation & EBITDA Projections   │
                   └─────────────────────────────────────────────────────────┘
```

### System 1: Real-Time CPQ Reflexive Guardrail
System 1 operates within Configure, Price, Quote (CPQ) and ERP order entry workflows with an average execution latency of **0.009 milliseconds (<10 microseconds)**. When a sales representative submits an order line, System 1 evaluates three deterministic checkpoints:
1. **Minimum Order Quantity (MOQ):** Ensures the order quantity covers base logistics handling fees by product family (5 units for Heavy Industrial, 8 for Chemicals, 20 for Sensors, 25 for MRO). If sub-MOQ, quantity is rounded up or an automated $120 handling surcharge is attached.
2. **Discount Floor Grid:** Caps allowable discounts by volume bracket (micro-orders capped at 8-12%; bulk pallet orders eligible for up to 35%).
3. **Rogue Representative Audit:** Flagged representatives attempting unauthorized concessions are blocked and escalated to the Commercial Finance Director.

*Live Execution Example:* When `REP-02` requested an order for 2 units of Heavy Industrial equipment at a 42.0% discount for toxic account `CUST-0099`, the baseline calculation projected an operating loss of **-$8,663.93**. System 1 intercepted the request, adjusted quantity to the 5-unit MOQ, clamped the discount to 12.0%, and escalated the quote. The revised transaction generated a positive pocket margin of **+$2,943.20**, delivering an **immediate +$11,607.13 margin lift on a single order**.

### System 2: Econometric Elasticity & Policy Optimization
System 2 evaluates the structural macroeconomic response of customer accounts using an empirical log-log demand model estimated via Scikit-Learn:
$$\ln(\text{Quantity}_i) = \alpha + \beta \ln(\text{Realized Price}_i) + \gamma \ln(\text{Catalog Price}_i) + \sum \delta_j \text{Category}_j + \epsilon_i$$

The empirical price elasticity coefficient ($\beta$) confirms that strategic enterprise accounts exhibit near-unitary sensitivity ($\beta = -1.000$), meaning volume reductions are proportional to price increases and margin expansion compensates for unit shrinkage. Mid-Market accounts are moderately elastic ($\beta = -1.185$), while SMB accounts prioritize supplier availability and fulfillment reliability over marginal price differences ($\beta = -0.161$).

Simulating the corporate-wide implementation of MOQ enforcement, discount guardrails, and terms contraction (capping late payers at Net 35) across all 55,000 transactions yields significant EBITDA expansion:

![EBITDA Recovery Scenario](assets/04_ebitda_recovery_scenario.png)

Total enterprise EBITDA expands from **$210.72M to $311.67M (+47.9% net growth)**. Crucially, the turnaround is achieved almost entirely by restructuring toxic accounts: Tier-D EBITDA improves from -$85.58M to +$8.71M (**+$94.29M recovery**), while Tier-A and Tier-B accounts maintain stable volumes and protected relationships.

---

## 7. Corporate Deliverable: Executive Excel Financial Model

Since commercial leadership and operations teams work daily in spreadsheets, the pipeline automatically compiles the complete analysis into a clean, structured Excel financial model: [`data/B2B_Margin_Leakage_Executive_Model.xlsx`](data/B2B_Margin_Leakage_Executive_Model.xlsx).

Designed with a clean, monochrome layout (pure white background, soft grey headers, charcoal dividers, and native red accounting formatting for negative values), the model organizes the findings across five dedicated tabs:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               EXCEL FINANCIAL MODEL ARCHITECTURE                                 │
├───────────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ Sheet Tab                     │ Core Contents & Financial Functionality                          │
├───────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ 01_Executive_Summary          │ Full scorecard comparing Baseline vs. Optimized across all       │
│                               │ financial lines, plus customer tier EBITDA reconciliation tables.│
│ 02_Pocket_Margin_Waterfall    │ 9-stage waterfall bridge tracking list-to-pocket value erosion    │
│                               │ with step percentages and operational variance explanations.    │
│ 03_Whale_Curve_Deciles        │ Decile-by-decile customer stratification proving the 140.6% peak │
│                               │ profit point and documenting bottom-decile EBITDA destruction.   │
│ 04_Pricing_&_MOQ_Matrix       │ Actionable commercial matrix defining SKU MOQ thresholds, freight│
│                               │ accessorial surcharges, and tiered discount ceiling corridors.   │
│ 05_Sales_Rep_Audit            │ Performance and compliance rankings across 25 sales reps,        │
│                               │ flagging unauthorized small-order discount leakage in crimson.   │
└───────────────────────────────┴──────────────────────────────────────────────────────────────────┘
```

Column widths are dynamically sized with generous safety margins (18 to 39 characters) to ensure complete readability without cell clipping or `###` overflow errors.

---

## 8. Repository Structure

```
proyecto-analisis-datos-b2b/
├── assets/                               # Publication-Grade Visualizations (300 DPI)
│   ├── 01_pocket_margin_waterfall.png    # Step-by-step pocket margin bridge
│   ├── 02_whale_curve_profitability.png  # Stobachoff cumulative profit curve
│   ├── 03_discount_vs_ordersize_dispersion.png # Scatter plot with leakage danger zones
│   └── 04_ebitda_recovery_scenario.png   # Enterprise EBITDA recovery scenario
├── data/                                 # Datasets & Corporate Deliverables
│   ├── B2B_Margin_Leakage_Executive_Model.xlsx # 5-Tab Institutional Financial Model
│   └── b2b_erp_transactions.parquet      # 55,000 ERP line items (Parquet format)
├── notebooks/                            # Interactive Walkthroughs
│   └── 01_executive_margin_audit.ipynb   # Step-by-step Jupyter analysis notebook
├── src/                                  # Modular Quantitative Python Package
│   ├── __init__.py                       # Package initializer
│   ├── data_generator.py                 # ERP transaction generator with realistic noise
│   ├── waterfall_analyzer.py             # Pocket margin waterfall calculation engine
│   ├── whale_curve.py                    # Stobachoff customer curve analyzer
│   ├── clustering_guardrails.py          # K-Means RFM clustering & rogue rep audit
│   ├── elasticity_engine.py              # Log-log econometric price elasticity model
│   ├── pricing_engine.py                 # System 1 real-time gate & System 2 simulator
│   ├── visualizations.py                 # High-resolution chart rendering module
│   └── excel_exporter.py                 # Automated executive Excel model generator
├── tests/                                # Test Suite & SWE Verification
│   └── test_pipeline.py                  # Pytest unit tests (8 passing tests)
├── main.py                               # Master orchestration pipeline script
├── SYSTEM_NOTES.md                       # Empirical audit ledger with exact numbers
└── README.md                             # Executive portfolio case study
```

---

## 9. Execution & Verification Guide

The codebase is engineered with strict production standards: fully modular functions, explicit type annotations, reproducible random seeds, and an automated test suite.

### 1. Environment Setup
Clone the repository and install required dependencies:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn pytest pyarrow openpyxl nbformat
```

### 2. End-to-End Pipeline Execution
Run the master orchestration script to execute data ingestion, waterfall decomposition, whale curve analysis, elasticity modeling, System 1/2 quote evaluation, visualization generation, and Excel model compilation:
```bash
python main.py
```
*The full pipeline completes in approximately 4.1 seconds.*

### 3. Automated Test Verification
Run the comprehensive test suite to validate mathematical identities, financial balances, latency thresholds, and workbook generation:
```bash
python -m pytest tests/test_pipeline.py -v
```
*Expected output: 8 passed in ~3.5 seconds.*

---

## 10. Operational Governance & Implementation Roadmap

To operationalize these analytical findings within an active wholesale or distribution business, revenue operations leadership should execute a phased commercial governance rollout:

1. **CPQ System 1 Integration (Weeks 1–4):** Deploy the lightweight guardrail logic into the CRM/CPQ quoting tool (e.g., Salesforce CPQ, HubSpot, or ERP order entry). Enforce hard MOQ stops on bulky or hazardous SKUs and implement automated manager approval routing for quotes exceeding tier discount ceilings.
2. **Sales Incentive Realignment (Weeks 5–8):** Transition sales compensation plans from gross booked revenue to **net pocket margin contribution**. By linking commission payouts directly to realized margin after discounts and freight, representative behavior naturally shifts away from unprofitable volume chasing toward disciplined value selling.
3. **Account Surcharge Migration (Weeks 9–12):** Contact accounts currently situated within the toxic tail with a structured choice: consolidate micro-orders into bi-weekly scheduled deliveries that meet MOQ thresholds, or accept an automated $120 small-order handling fee to cover individual courier costs.
4. **Working Capital Enforcement (Weeks 13–16):** Institute automated credit holds on accounts exceeding 45 days past terms, combined with a 2% 10 Net 30 prompt payment discount to accelerate accounts receivable cash collection.

---

## License & Citation
Developed under the MIT License. Designed as an open-source executive case study for corporate finance, revenue operations, and commercial pricing analytics.
