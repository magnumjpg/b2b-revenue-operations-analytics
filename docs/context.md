# Project Context: B2B Margin Leakage Diagnostics, Whale Curve & Dynamic Pricing

## Executive Summary
This enterprise data analytics project models and solves silent profit erosion in B2B distribution and wholesale supply chains. By dissecting transaction-level ERP data across 50,000+ orders, 800 accounts, and 4 product families, the project exposes how uncoordinated sales rep discounting, sub-scale order fulfillment, extended payment terms, and off-invoice concessions erode nominal margins down to negative net pocket margin.

## Key Pillars of the Analytical Engine
1. **Pocket Margin Waterfall Analysis**:
   - Deconstructs nominal list price into invoice price, deducts logistics freight & order fulfillment handling costs, off-invoice rebates, and capital cost of payment delays.
   - Quantifies the true "Pocket Margin" (Net Contribution / Pocket EBITDA) per SKU, transaction, and client.
2. **Whale Curve Cumulative Profitability (Stobachoff Analysis)**:
   - Evaluates customer portfolio profitability: isolates the peak profit point where the top ~20% of clients generate 140%+ of enterprise profits, the plateau where 65% break even, and the profit-destroying tail (bottom 15%) that erodes millions in EBITDA.
3. **Dual-Tier Decision Architecture (System 1 & System 2 Pricing Engine)**:
   - **System 1 (Reflexive Real-Time Guardrail Engine)**: Fast microsecond rule-and-heuristic evaluation for quote requests (checks account RFM tier, minimum order quantity [MOQ], and maximum discount floor; triggers immediate reject/adjust/flag for rogue sales rep behavior).
   - **System 2 (Analytical Strategic Optimizer)**: Algorithmic clustering (RFM + Margin Profiling), price elasticity estimation, and policy simulation calculating recovery EBITDA from MOQ enforcement and dynamic discount guardrails.
4. **C-Suite Financial Visualization**:
   - Publication-grade visualizations saved to `/assets/` for executive presentation (Waterfall, Whale Curve, Scatter Dispersion with Danger Zones, Policy Impact).

## Directory Structure
- `/data/`: Raw and processed ERP transactional datasets (CSV / Parquet).
- `/src/`:
  - `data_generator.py`: Synthetic B2B ERP transaction generator with realistic noise, rep skew, and cost structures.
  - `waterfall_analyzer.py`: Pocket margin bridge and waterfall decomposition.
  - `whale_curve.py`: Customer profitability stratification, Pareto ranking, and whale curve computation.
  - `clustering_guardrails.py`: Account segmentation (RFM + Margin) and rogue rep discount detection.
  - `pricing_engine.py`: System 1 (fast guardrail check) & System 2 (simulation and policy optimization).
  - `visualizations.py`: Production-grade charts rendered with Matplotlib/Seaborn.
- `/notebooks/`: Interactive walkthrough notebook (`01_executive_margin_audit.ipynb`).
- `/assets/`: High-resolution figures (PNG, 300 DPI) for executive review.
- `SYSTEM_NOTES.md`: Operational ledger of computed recoveries and financial impacts.
- `README.md`: High-impact C-suite executive portfolio presentation.
