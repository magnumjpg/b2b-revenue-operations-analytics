"""
Executive Excel Financial Model Exporter
Generates a multi-tab, institutional-grade corporate financial model in Excel (.xlsx).
Designed with a clean, minimalist aesthetic matching executive resume typography:
monochrome palette, pure white background, subtle charcoal borders, generous column
spacing, and native financial formatting with red for negative values.
"""

import os
import sys
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.waterfall_analyzer import PocketMarginWaterfallAnalyzer
from src.whale_curve import WhaleCurveAnalyzer
from src.clustering_guardrails import CustomerClusteringAndRepDiagnostics
from src.pricing_engine import System2StrategicOptimizer

class ExecutiveExcelModelExporter:
    """
    Builds the executive corporate financial workbook in Excel.
    """
    
    def __init__(self, df: pd.DataFrame, output_path: str = "data/B2B_Margin_Leakage_Executive_Model.xlsx"):
        self.df = df.copy()
        self.output_path = output_path
        
        # Analytics components
        self.wf_analyzer = PocketMarginWaterfallAnalyzer(self.df)
        self.wc_analyzer = WhaleCurveAnalyzer(self.df)
        self.diag = CustomerClusteringAndRepDiagnostics(self.df, n_clusters=4)
        self.s2_opt = System2StrategicOptimizer(self.df)
        
        # Design Tokens (Minimalist Monochrome / Resume-Matched)
        self.FONT_FAMILY = "Segoe UI"
        self.COLOR_TEXT_MAIN = "111827"       # Charcoal / Black
        self.COLOR_TEXT_MUTED = "4B5563"      # Medium Grey
        self.COLOR_BG_HEADER = "F3F4F6"       # Soft Light Grey (clean, NO gaudy blues)
        self.COLOR_BG_SUBTLE = "F9FAFB"       # Very Light Accent
        self.COLOR_BORDER = "E5E7EB"          # Crisp Hairline Grey
        self.COLOR_BORDER_DARK = "111827"     # Dark Divider
        self.COLOR_RED_TEXT = "DC2626"        # Professional Crimson Red for negatives
        self.COLOR_RED_BG = "FEE2E2"          # Soft Red Tint for danger callouts
        self.COLOR_GREEN_BG = "ECFDF5"        # Soft Green Tint for recovery callouts
        
        # Borders
        self.border_thin = Border(
            left=Side(style="thin", color=self.COLOR_BORDER),
            right=Side(style="thin", color=self.COLOR_BORDER),
            top=Side(style="thin", color=self.COLOR_BORDER),
            bottom=Side(style="thin", color=self.COLOR_BORDER)
        )
        self.border_header = Border(
            left=Side(style="thin", color=self.COLOR_BORDER),
            right=Side(style="thin", color=self.COLOR_BORDER),
            top=Side(style="thin", color=self.COLOR_BORDER_DARK),
            bottom=Side(style="medium", color=self.COLOR_BORDER_DARK)
        )
        self.border_total = Border(
            top=Side(style="thin", color=self.COLOR_BORDER_DARK),
            bottom=Side(style="double", color=self.COLOR_BORDER_DARK)
        )
        
        # Standard Number Formats
        self.FMT_CURRENCY = "$#,##0.00;[Red]($#,##0.00);\"-\""
        self.FMT_CURRENCY_M = "$#,##0.0\"M\";[Red]($#,##0.0\"M\");\"-\""
        self.FMT_PERCENT = "0.00%;[Red](0.00%);\"0.00%\""
        self.FMT_PERCENT_1 = "0.0%;[Red](0.0%);\"0.0%\""
        self.FMT_INTEGER = "#,##0;[Red](#,##0);\"-\""

    def _apply_sheet_view_settings(self, ws):
        """Ensures gridlines are explicitly visible and zoom is crisp."""
        ws.views.sheetView[0].showGridLines = True
        ws.views.sheetView[0].zoomScale = 100

    def _auto_fit_columns(self, ws, min_width=16, extra_padding=6):
        """Generously spaces columns to completely prevent truncated text or ### values, ignoring banner titles."""
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            if col_letter == "A":
                ws.column_dimensions["A"].width = 4
                continue
                
            max_len = 0
            for cell in col:
                # Ignore top banner title rows (rows 1-4)
                if cell.row <= 4:
                    continue
                val = cell.value
                if val is not None:
                    val_str = str(val)
                    # If it's a section description subtitle spanning across, don't bloat column width
                    if col_letter == "B" and len(val_str) > 42:
                        continue
                    if "\n" in val_str:
                        lines = val_str.split("\n")
                        line_len = max(len(l) for l in lines)
                        max_len = max(max_len, line_len)
                    else:
                        max_len = max(max_len, len(val_str))
            
            calculated_width = max(max_len + extra_padding, min_width)
            if col_letter == "B":
                calculated_width = min(calculated_width, 38)
            ws.column_dimensions[col_letter].width = calculated_width

    def _write_section_header(self, ws, row: int, title: str, subtitle: str = ""):
        """Writes an uppercase minimalist section header matching the user's CV layout."""
        ws.cell(row=row, column=2, value=title.upper()).font = Font(
            name=self.FONT_FAMILY, size=11, bold=True, color=self.COLOR_TEXT_MAIN
        )
        if subtitle:
            ws.cell(row=row+1, column=2, value=subtitle).font = Font(
                name=self.FONT_FAMILY, size=9.5, italic=True, color=self.COLOR_TEXT_MUTED
            )
            return row + 3
        return row + 2

    def build_workbook(self):
        """Generates all 5 executive sheets and saves the workbook."""
        wb = openpyxl.Workbook()
        # Remove default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)
        
        # 1. Executive Summary
        self._build_executive_summary_tab(wb)
        # 2. Pocket Margin Waterfall
        self._build_waterfall_tab(wb)
        # 3. Whale Curve Deciles
        self._build_whale_curve_tab(wb)
        # 4. Pricing & MOQ Matrix
        self._build_pricing_matrix_tab(wb)
        # 5. Sales Rep Audit
        self._build_sales_rep_tab(wb)
        
        wb.save(self.output_path)
        print(f"Executive Excel Model successfully exported to: {self.output_path}")

    def _build_executive_summary_tab(self, wb):
        ws = wb.create_sheet(title="01_Executive_Summary")
        self._apply_sheet_view_settings(ws)
        
        # Main Title Banner
        ws.cell(row=2, column=2, value="B2B REVENUE OPERATIONS & PRICING ANALYTICS").font = Font(
            name=self.FONT_FAMILY, size=16, bold=True, color=self.COLOR_TEXT_MAIN
        )
        ws.cell(row=3, column=2, value="Executive Scorecard: Baseline Actuals vs. Post-Guardrails Policy Optimization").font = Font(
            name=self.FONT_FAMILY, size=10.5, italic=True, color=self.COLOR_TEXT_MUTED
        )
        ws.cell(row=4, column=2, value="Dataset Scope: 55,000 Invoice Lines | 800 Accounts | 25 Sales Reps | FY2024").font = Font(
            name=self.FONT_FAMILY, size=9, color=self.COLOR_TEXT_MUTED
        )
        
        # Run Simulation
        sim_res = self.s2_opt.simulate_policy_rollout()
        
        # KPI Highlights Table
        start_row = 6
        headers = ["CORE FINANCIAL METRIC", "BASELINE (ACTUALS)", "OPTIMIZED (POLICY)", "NET EXPANSION (DELTA)", "GROWTH / LIFT"]
        for c_idx, h in enumerate(headers, start=2):
            cell = ws.cell(row=start_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left", vertical="center")
            
        kpis = [
            ("Gross List Revenue", self.df["gross_revenue"].sum(), sim_res["simulation_df"]["optimized_gross_revenue"].sum(), "USD"),
            ("On-Invoice Discounts Conceded", -self.df["discount_amount"].sum(), -(sim_res["simulation_df"]["optimized_gross_revenue"].sum() - sim_res["optimized_revenue"]), "USD"),
            ("Net Invoiced Revenue", sim_res["baseline_revenue"], sim_res["optimized_revenue"], "USD"),
            ("Cost of Goods Sold (COGS)", -self.df["total_cogs"].sum(), -sim_res["simulation_df"]["optimized_cogs"].sum(), "USD"),
            ("Logistics & Freight Fulfillment", -self.df["logistics_cost"].sum(), -sim_res["simulation_df"]["optimized_logistics_cost"].sum(), "USD"),
            ("Cost of Working Capital (Delay)", -self.df["cost_of_capital"].sum(), -sim_res["simulation_df"]["optimized_cost_of_capital"].sum(), "USD"),
            ("Off-Invoice Rebates Accrued", -self.df["off_invoice_rebate_amount"].sum(), -sim_res["simulation_df"]["optimized_rebates"].sum(), "USD"),
            ("Realized Pocket EBITDA", sim_res["baseline_margin"], sim_res["optimized_margin"], "EBITDA"),
            ("Pocket EBITDA Margin %", sim_res["baseline_margin_pct"] / 100.0, sim_res["optimized_margin_pct"] / 100.0, "PCT")
        ]
        
        cur_row = start_row + 1
        for name, base, opt, ktype in kpis:
            delta = opt - base
            pct_lift = (delta / abs(base)) if base != 0 else 0.0
            
            c_name = ws.cell(row=cur_row, column=2, value=name)
            c_base = ws.cell(row=cur_row, column=3, value=base)
            c_opt = ws.cell(row=cur_row, column=4, value=opt)
            c_delta = ws.cell(row=cur_row, column=5, value=delta)
            c_lift = ws.cell(row=cur_row, column=6, value=pct_lift)
            
            is_ebitda = ktype in ["EBITDA", "PCT"]
            is_highlight = name == "Realized Pocket EBITDA"
            
            for cell in [c_name, c_base, c_opt, c_delta, c_lift]:
                cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=is_ebitda, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_total if is_highlight else self.border_thin
                if is_highlight:
                    cell.fill = PatternFill(start_color=self.COLOR_GREEN_BG, end_color=self.COLOR_GREEN_BG, fill_type="solid")
                    
            if ktype == "PCT":
                c_base.number_format = self.FMT_PERCENT
                c_opt.number_format = self.FMT_PERCENT
                c_delta.number_format = self.FMT_PERCENT
                c_lift.value = f"+{delta*10000:.0f} bps"
                c_lift.alignment = Alignment(horizontal="right")
            else:
                c_base.number_format = self.FMT_CURRENCY
                c_opt.number_format = self.FMT_CURRENCY
                c_delta.number_format = self.FMT_CURRENCY
                c_lift.number_format = self.FMT_PERCENT_1
                
            cur_row += 1
            
        # Segment Recovery Breakdown
        cur_row += 3
        cur_row = self._write_section_header(
            ws, cur_row,
            "CUSTOMER SEGMENT EBITDA RECONCILIATION",
            "Dissection of profit recovery across Strategic Enterprise, Mid-Market, SMB, and Toxic Tail Accounts"
        )
        
        seg_headers = ["CUSTOMER TIER", "BASELINE EBITDA", "OPTIMIZED EBITDA", "EBITDA RECOVERY", "BASELINE MARGIN %", "OPTIMIZED MARGIN %", "STRATEGIC LEVER"]
        for c_idx, h in enumerate(seg_headers, start=2):
            cell = ws.cell(row=cur_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left", vertical="center")
            
        cur_row += 1
        tier_data = sim_res["tier_recovery"]
        tier_descriptions = {
            "Enterprise_Key": "Master volume agreements; protected truckload logistics efficiency.",
            "MidMarket_Core": "Stable profitable core; enforced standard freight terms.",
            "SMB_Standard": "Disciplined price realization; standard order consolidation.",
            "Toxic_Drain": "Restructured with MOQ policy ($120 subscale fee) + discount floor capped at 18%."
        }
        
        for _, r in tier_data.iterrows():
            tier_name = r["client_tier"]
            base_m = r["baseline_margin"]
            opt_m = r["optimized_margin"]
            rec_m = r["ebitda_recovery"]
            base_pct = r["baseline_pct"] / 100.0
            opt_pct = r["optimized_pct"] / 100.0
            lever = tier_descriptions.get(tier_name, "Operational guardrail alignment.")
            
            c_tier = ws.cell(row=cur_row, column=2, value=tier_name.replace("_", " "))
            c_base = ws.cell(row=cur_row, column=3, value=base_m)
            c_opt = ws.cell(row=cur_row, column=4, value=opt_m)
            c_rec = ws.cell(row=cur_row, column=5, value=rec_m)
            c_bpct = ws.cell(row=cur_row, column=6, value=base_pct)
            c_opct = ws.cell(row=cur_row, column=7, value=opt_pct)
            c_lever = ws.cell(row=cur_row, column=8, value=lever)
            
            is_toxic = tier_name == "Toxic_Drain"
            for cell in [c_tier, c_base, c_opt, c_rec, c_bpct, c_opct, c_lever]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, bold=is_toxic, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_thin
                if is_toxic:
                    cell.fill = PatternFill(start_color=self.COLOR_GREEN_BG, end_color=self.COLOR_GREEN_BG, fill_type="solid")
                    
            c_base.number_format = self.FMT_CURRENCY
            c_opt.number_format = self.FMT_CURRENCY
            c_rec.number_format = self.FMT_CURRENCY
            c_bpct.number_format = self.FMT_PERCENT_1
            c_opct.number_format = self.FMT_PERCENT_1
            
            cur_row += 1
            
        self._auto_fit_columns(ws, min_width=18, extra_padding=8)

    def _build_waterfall_tab(self, wb):
        ws = wb.create_sheet(title="02_Pocket_Margin_Waterfall")
        self._apply_sheet_view_settings(ws)
        
        ws.cell(row=2, column=2, value="POCKET MARGIN WATERFALL BRIDGE").font = Font(
            name=self.FONT_FAMILY, size=15, bold=True, color=self.COLOR_TEXT_MAIN
        )
        ws.cell(row=3, column=2, value="Step-by-step value erosion tracking from Gross List Price to Net Pocket Margin (EBITDA)").font = Font(
            name=self.FONT_FAMILY, size=10, italic=True, color=self.COLOR_TEXT_MUTED
        )
        
        df_wf = self.wf_analyzer.compute_portfolio_waterfall()
        
        headers = ["STAGE #", "FINANCIAL BRIDGE STEP", "CATEGORY TYPE", "AMOUNT ($ USD)", "% OF GROSS LIST", "% OF NET INVOICED", "OPERATIONAL IMPACT & DRIVERS"]
        start_row = 5
        for c_idx, h in enumerate(headers, start=2):
            cell = ws.cell(row=start_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx in [2, 4] else "left", vertical="center")
            
        descriptions = {
            "1. Gross List Price": "Full catalog catalog value across 55,000 order lines before commercial concessions.",
            "2. On-Invoice Discounts": "Immediate price concessions granted by sales representatives during negotiations.",
            "3. Invoice Revenue": "Recognized top-line revenue recorded on customer invoices and official ERP ledger.",
            "4. Cost of Goods Sold (COGS)": "Direct manufacturing, procurement, and bill-of-materials cost of products.",
            "5. Standard Gross Profit": "Conventional gross profit before below-the-line fulfillment and financing costs.",
            "6. Off-Invoice Rebates": "Contractual annual volume kickbacks and co-op marketing allowances paid post-sale.",
            "7. Logistics & Handling": "Fixed warehouse pick/pack labor, pallet wrapping, and line-item freight delivery.",
            "8. Cost of Working Capital (Delay)": "Financing carrying cost of accounts receivable (WACC 8.5% annual rate).",
            "9. Net Pocket Margin": "Realized operating cash contribution (Pocket EBITDA) after all friction points."
        }
        
        cur_row = start_row + 1
        for _, r in df_wf.iterrows():
            stage_full = r["stage"]
            stage_num = stage_full.split(". ")[0] if ". " in stage_full else ""
            stage_name = stage_full.split(". ")[1] if ". " in stage_full else stage_full
            cat_type = r["type"].upper()
            amt = r["amount"]
            pct_gross = r["pct_gross"] / 100.0
            pct_inv = r["pct_invoice"] / 100.0
            note = descriptions.get(stage_full, "")
            
            c_num = ws.cell(row=cur_row, column=2, value=stage_num)
            c_name = ws.cell(row=cur_row, column=3, value=stage_name)
            c_type = ws.cell(row=cur_row, column=4, value=cat_type)
            c_amt = ws.cell(row=cur_row, column=5, value=amt)
            c_pg = ws.cell(row=cur_row, column=6, value=pct_gross)
            c_pi = ws.cell(row=cur_row, column=7, value=pct_inv)
            c_note = ws.cell(row=cur_row, column=8, value=note)
            
            is_subtotal = cat_type in ["BASELINE", "SUBTOTAL", "FINAL"]
            
            for cell in [c_num, c_name, c_type, c_amt, c_pg, c_pi, c_note]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, bold=is_subtotal, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_total if cat_type == "FINAL" else self.border_thin
                if cat_type == "FINAL":
                    cell.fill = PatternFill(start_color=self.COLOR_GREEN_BG, end_color=self.COLOR_GREEN_BG, fill_type="solid")
                    
            c_num.alignment = Alignment(horizontal="center")
            c_amt.number_format = self.FMT_CURRENCY
            c_pg.number_format = self.FMT_PERCENT_1
            c_pi.number_format = self.FMT_PERCENT_1
            
            cur_row += 1
            
        self._auto_fit_columns(ws, min_width=18, extra_padding=8)

    def _build_whale_curve_tab(self, wb):
        ws = wb.create_sheet(title="03_Whale_Curve_Deciles")
        self._apply_sheet_view_settings(ws)
        
        ws.cell(row=2, column=2, value="THE STOBACHOFF WHALE CURVE (CUSTOMER PROFITABILITY DECILES)").font = Font(
            name=self.FONT_FAMILY, size=15, bold=True, color=self.COLOR_TEXT_MAIN
        )
        ws.cell(row=3, column=2, value="Portfolio stratification proving how the top 20% generate 133-141% of profits while the bottom 15% destroy EBITDA").font = Font(
            name=self.FONT_FAMILY, size=10, italic=True, color=self.COLOR_TEXT_MUTED
        )
        
        df_clients = self.wc_analyzer.get_curve_dataframe().copy()
        total_enterprise_margin = df_clients["net_pocket_margin"].sum()
        
        # Segment into 10 Deciles
        df_clients["decile"] = pd.qcut(df_clients.index, q=10, labels=[f"Decile {i+1} (Top {(i+1)*10}%)" for i in range(10)])
        
        decile_agg = df_clients.groupby("decile", observed=False).agg(
            accounts_count=("client_id", "count"),
            invoice_revenue=("invoice_revenue", "sum"),
            net_pocket_margin=("net_pocket_margin", "sum"),
            avg_aov=("avg_order_value", "mean"),
            avg_discount_rate=("avg_discount_rate_pct", "mean"),
            avg_delay_days=("avg_payment_delay", "mean")
        ).reset_index()
        
        decile_agg["margin_pct"] = (decile_agg["net_pocket_margin"] / decile_agg["invoice_revenue"]) * 100.0
        decile_agg["cum_margin"] = decile_agg["net_pocket_margin"].cumsum()
        decile_agg["cum_margin_pct"] = (decile_agg["cum_margin"] / total_enterprise_margin) * 100.0
        
        headers = ["DECILE BRACKET", "ACCOUNTS", "INVOICE REVENUE ($)", "POCKET EBITDA ($)", "CUMULATIVE EBITDA ($)", "CUMULATIVE PROFIT %", "MARGIN %", "AVG DISCOUNT %", "AVG PAYMENT DELAY", "STRATIFICATION TIER"]
        start_row = 5
        for c_idx, h in enumerate(headers, start=2):
            cell = ws.cell(row=start_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left", vertical="center")
            
        cur_row = start_row + 1
        for idx, r in decile_agg.iterrows():
            decile_name = r["decile"]
            accts = r["accounts_count"]
            rev = r["invoice_revenue"]
            margin = r["net_pocket_margin"]
            cum_m = r["cum_margin"]
            cum_pct = r["cum_margin_pct"] / 100.0
            m_pct = r["margin_pct"] / 100.0
            disc = r["avg_discount_rate"] / 100.0
            delay = r["avg_delay_days"]
            
            if idx < 2:
                tier_label = "TOP 20% PROFIT ENGINE (133% PROFIT)"
            elif idx < 8:
                tier_label = "MIDDLE 60% BREAKEVEN PLATEAU"
            else:
                tier_label = "BOTTOM 20% EBITDA DESTRUCTION ZONE"
                
            c_dec = ws.cell(row=cur_row, column=2, value=decile_name)
            c_acc = ws.cell(row=cur_row, column=3, value=accts)
            c_rev = ws.cell(row=cur_row, column=4, value=rev)
            c_mar = ws.cell(row=cur_row, column=5, value=margin)
            c_cum = ws.cell(row=cur_row, column=6, value=cum_m)
            c_cumpct = ws.cell(row=cur_row, column=7, value=cum_pct)
            c_mpct = ws.cell(row=cur_row, column=8, value=m_pct)
            c_disc = ws.cell(row=cur_row, column=9, value=disc)
            c_del = ws.cell(row=cur_row, column=10, value=delay)
            c_tier = ws.cell(row=cur_row, column=11, value=tier_label)
            
            is_toxic = margin < 0
            is_top = idx < 2
            
            for cell in [c_dec, c_acc, c_rev, c_mar, c_cum, c_cumpct, c_mpct, c_disc, c_del, c_tier]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, bold=(is_toxic or is_top), color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_thin
                if is_toxic:
                    cell.fill = PatternFill(start_color=self.COLOR_RED_BG, end_color=self.COLOR_RED_BG, fill_type="solid")
                elif is_top:
                    cell.fill = PatternFill(start_color=self.COLOR_GREEN_BG, end_color=self.COLOR_GREEN_BG, fill_type="solid")
                    
            c_acc.alignment = Alignment(horizontal="center")
            c_rev.number_format = self.FMT_CURRENCY
            c_mar.number_format = self.FMT_CURRENCY
            c_cum.number_format = self.FMT_CURRENCY
            c_cumpct.number_format = self.FMT_PERCENT_1
            c_mpct.number_format = self.FMT_PERCENT_1
            c_disc.number_format = self.FMT_PERCENT_1
            c_del.number_format = "0.0\" days\""
            
            cur_row += 1
            
        self._auto_fit_columns(ws, min_width=18, extra_padding=8)

    def _build_pricing_matrix_tab(self, wb):
        ws = wb.create_sheet(title="04_Pricing_&_MOQ_Matrix")
        self._apply_sheet_view_settings(ws)
        
        ws.cell(row=2, column=2, value="COMMERCIAL PRICING GUARDRAILS & OPERATIONAL MOQ MATRIX").font = Font(
            name=self.FONT_FAMILY, size=15, bold=True, color=self.COLOR_TEXT_MAIN
        )
        ws.cell(row=3, column=2, value="Governing rules enforced by System 1 Real-Time Quoting Engine to prevent freight and discount margin leakage").font = Font(
            name=self.FONT_FAMILY, size=10, italic=True, color=self.COLOR_TEXT_MUTED
        )
        
        # Table 1: MOQ & Logistics Guardrails by Product Family
        cur_row = 5
        cur_row = self._write_section_header(
            ws, cur_row,
            "1. PRODUCT FAMILY FULFILLMENT & MINIMUM ORDER QUANTITIES (MOQ)",
            "Enforced thresholds to prevent single-unit expedited freight leakage"
        )
        
        moq_headers = ["PRODUCT FAMILY", "CATALOG PRICE RANGE", "BASE COGS %", "MINIMUM ORDER QUANTITY (MOQ)", "FIXED HANDLING FEE", "SUBSCALE SURCHARGE (<MOQ)", "FREIGHT CHARACTERISTIC"]
        for c_idx, h in enumerate(moq_headers, start=2):
            cell = ws.cell(row=cur_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx in [5, 6, 7] else "left", vertical="center")
            
        cur_row += 1
        moq_data = [
            ("Heavy Industrial Machinery", "$850.00 - $3,200.00", 0.58, 5, 45.0, 120.0, "Heavyweight LTL; requires pallet consolidation"),
            ("Specialty Chemicals / Fluids", "$280.00 - $920.00", 0.52, 8, 38.0, 120.0, "Hazardous material handling & drum transport"),
            ("Electronic Hardware & Sensors", "$55.00 - $340.00", 0.45, 20, 20.0, 45.0, "Compact parcel; sensitive to rebate allowances"),
            ("MRO Consumables & Supplies", "$14.00 - $115.00", 0.40, 25, 22.0, 35.0, "High velocity; micro-orders cause fixed handling erosion")
        ]
        
        for name, prange, cogs, moq, handling, surcharge, char in moq_data:
            c1 = ws.cell(row=cur_row, column=2, value=name)
            c2 = ws.cell(row=cur_row, column=3, value=prange)
            c3 = ws.cell(row=cur_row, column=4, value=cogs)
            c4 = ws.cell(row=cur_row, column=5, value=moq)
            c5 = ws.cell(row=cur_row, column=6, value=handling)
            c6 = ws.cell(row=cur_row, column=7, value=surcharge)
            c7 = ws.cell(row=cur_row, column=8, value=char)
            
            for cell in [c1, c2, c3, c4, c5, c6, c7]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_thin
                
            c3.number_format = self.FMT_PERCENT_1
            c4.number_format = self.FMT_INTEGER
            c5.number_format = self.FMT_CURRENCY
            c6.number_format = self.FMT_CURRENCY
            cur_row += 1
            
        # Table 2: Discount Floor & Ceiling Grid by Account Tier
        cur_row += 3
        cur_row = self._write_section_header(
            ws, cur_row,
            "2. MAXIMUM ALLOWABLE DISCOUNT CEILING GRID (SYSTEM 1 GUARDRAIL)",
            "Discounts exceeding these thresholds are blocked or require VP Commercial approval"
        )
        
        disc_headers = ["CUSTOMER ACCOUNT TIER", "MICRO ORDERS (<5 UNITS)", "SMALL ORDERS (5-19 UNITS)", "MID VOLUME (20-49 UNITS)", "BULK PALLET (50+ UNITS)", "PAYMENT TERMS POLICY"]
        for c_idx, h in enumerate(disc_headers, start=2):
            cell = ws.cell(row=cur_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left", vertical="center")
            
        cur_row += 1
        disc_grid = [
            ("Tier-D: Toxic Drain Accounts", 0.08, 0.12, 0.15, 0.20, "Strict Net 30; credit hold if >45 days delinquent"),
            ("Tier-C: SMB Standard Long-Tail", 0.10, 0.15, 0.20, 0.25, "Net 30; 2% 10 Net 30 prompt payment incentive"),
            ("Tier-B: Core Mid-Market Accounts", 0.12, 0.18, 0.22, 0.28, "Net 35 standard commercial terms"),
            ("Tier-A: Strategic Enterprise Partners", 0.15, 0.20, 0.26, 0.35, "Contracted Master Service Agreement terms (Net 30/45)")
        ]
        
        for tier, m1, m2, m3, m4, terms in disc_grid:
            c1 = ws.cell(row=cur_row, column=2, value=tier)
            c2 = ws.cell(row=cur_row, column=3, value=m1)
            c3 = ws.cell(row=cur_row, column=4, value=m2)
            c4 = ws.cell(row=cur_row, column=5, value=m3)
            c5 = ws.cell(row=cur_row, column=6, value=m4)
            c6 = ws.cell(row=cur_row, column=7, value=terms)
            
            for cell in [c1, c2, c3, c4, c5, c6]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_thin
                
            for cell in [c2, c3, c4, c5]:
                cell.number_format = self.FMT_PERCENT_1
                cell.alignment = Alignment(horizontal="center")
                
            cur_row += 1
            
        self._auto_fit_columns(ws, min_width=20, extra_padding=8)

    def _build_sales_rep_tab(self, wb):
        ws = wb.create_sheet(title="05_Sales_Rep_Audit")
        self._apply_sheet_view_settings(ws)
        
        ws.cell(row=2, column=2, value="SALES REPRESENTATIVE COMMERCIAL INTEGRITY AUDIT").font = Font(
            name=self.FONT_FAMILY, size=15, bold=True, color=self.COLOR_TEXT_MAIN
        )
        ws.cell(row=3, column=2, value="Ranking sales rep discipline: exposing rogue discounting on small orders (<5 units) vs large orders (>40 units)").font = Font(
            name=self.FONT_FAMILY, size=10, italic=True, color=self.COLOR_TEXT_MUTED
        )
        
        df_reps = self.diag.diagnose_sales_reps()
        
        headers = ["REP ID", "SALES PROFILE", "TOTAL ORDERS", "INVOICED REVENUE ($)", "NET POCKET EBITDA ($)", "POCKET MARGIN %", "OVERALL AVG DISCOUNT", "SMALL ORDERS (<5) DISCOUNT", "LARGE ORDERS (>40) DISCOUNT", "ROGUE SPREAD", "AUDIT STATUS"]
        start_row = 5
        for c_idx, h in enumerate(headers, start=2):
            cell = ws.cell(row=start_row, column=c_idx, value=h)
            cell.font = Font(name=self.FONT_FAMILY, size=9.5, bold=True, color=self.COLOR_TEXT_MAIN)
            cell.fill = PatternFill(start_color=self.COLOR_BG_HEADER, end_color=self.COLOR_BG_HEADER, fill_type="solid")
            cell.border = self.border_header
            cell.alignment = Alignment(horizontal="center" if c_idx in [2, 3, 12] else "left", vertical="center")
            
        cur_row = start_row + 1
        for _, r in df_reps.iterrows():
            rep_id = r["sales_rep_id"]
            profile = r["rep_profile"].replace("_", " ")
            orders = r["total_orders"]
            rev = r["total_invoice_revenue"]
            margin = r["total_net_margin"]
            margin_pct = r["pocket_margin_pct"] / 100.0
            overall_disc = r["overall_avg_discount"]
            small_disc = r["small_orders_avg_discount"]
            large_disc = r["large_orders_avg_discount"]
            spread = r["rogue_leakage_spread"]
            is_rogue = r["is_rogue_flagged"]
            status_text = "FLAGGED: ROGUE DISCOUNTER" if is_rogue else "COMPLIANT / VALUE DEFENDER"
            
            c1 = ws.cell(row=cur_row, column=2, value=rep_id)
            c2 = ws.cell(row=cur_row, column=3, value=profile)
            c3 = ws.cell(row=cur_row, column=4, value=orders)
            c4 = ws.cell(row=cur_row, column=5, value=rev)
            c5 = ws.cell(row=cur_row, column=6, value=margin)
            c6 = ws.cell(row=cur_row, column=7, value=margin_pct)
            c7 = ws.cell(row=cur_row, column=8, value=overall_disc)
            c8 = ws.cell(row=cur_row, column=9, value=small_disc)
            c9 = ws.cell(row=cur_row, column=10, value=large_disc)
            c10 = ws.cell(row=cur_row, column=11, value=spread)
            c11 = ws.cell(row=cur_row, column=12, value=status_text)
            
            for cell in [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]:
                cell.font = Font(name=self.FONT_FAMILY, size=9, bold=is_rogue, color=self.COLOR_TEXT_MAIN)
                cell.border = self.border_thin
                if is_rogue:
                    cell.fill = PatternFill(start_color=self.COLOR_RED_BG, end_color=self.COLOR_RED_BG, fill_type="solid")
                    
            c1.alignment = Alignment(horizontal="center")
            c3.alignment = Alignment(horizontal="center")
            c3.number_format = self.FMT_INTEGER
            c4.number_format = self.FMT_CURRENCY
            c5.number_format = self.FMT_CURRENCY
            c6.number_format = self.FMT_PERCENT_1
            c7.number_format = self.FMT_PERCENT_1
            c8.number_format = self.FMT_PERCENT_1
            c9.number_format = self.FMT_PERCENT_1
            c10.number_format = self.FMT_PERCENT_1
            
            cur_row += 1
            
        self._auto_fit_columns(ws, min_width=18, extra_padding=8)

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    exporter = ExecutiveExcelModelExporter(df_raw, output_path="data/B2B_Margin_Leakage_Executive_Model.xlsx")
    exporter.build_workbook()
