"""
B2B Price-Volume Elasticity & Willingness-to-Pay (WTP) Econometric Engine
Implements a log-log demand model using Scikit-Learn to estimate customer price sensitivity,
uncover empirical elasticity variations across customer tiers, and derive optimal discount ceilings.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from typing import Dict, Any, Tuple

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class PriceElasticityEngine:
    """
    Econometric demand estimation for B2B wholesale pricing optimization.
    Fits log-log demand curves: ln(Quantity) = alpha + beta * ln(Realized_Price) + Controls
    where beta represents the constant price elasticity of demand.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.model = None
        self.tier_models: Dict[str, Any] = {}
        self.results_summary: Dict[str, Any] = {}
        
    def _prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts log-transformed price, quantity, and control variables.
        """
        # Effective unit realized price = invoice_revenue / quantity
        effective_price = np.maximum(data["invoice_revenue"] / data["quantity"], 1.0)
        log_price = np.log(effective_price)
        log_qty = np.log(np.maximum(data["quantity"], 1.0))
        
        # Additional controls: catalog list price, payment delay
        log_list_price = np.log(np.maximum(data["unit_list_price"], 1.0))
        log_delay = np.log1p(np.maximum(data["payment_delay_days"], 0))
        
        # Product family dummies
        family_dummies = pd.get_dummies(data["product_family"], drop_first=True, dtype=float)
        
        X = np.column_stack([log_price, log_list_price, log_delay, family_dummies.values])
        y = log_qty.values
        return X, y

    def fit_portfolio_elasticity(self) -> Dict[str, Any]:
        """
        Estimates portfolio-wide and tier-specific price elasticities of demand.
        """
        # 1. Enterprise-Wide Model
        X_all, y_all = self._prepare_features(self.df)
        portfolio_model = Ridge(alpha=1.0)
        portfolio_model.fit(X_all, y_all)
        y_pred = portfolio_model.predict(X_all)
        
        portfolio_elasticity = portfolio_model.coef_[0]
        portfolio_r2 = r2_score(y_all, y_pred)
        portfolio_mae = mean_absolute_error(y_all, y_pred)
        
        self.model = portfolio_model
        
        # 2. Segment-Specific Elasticity Estimation
        tier_results = []
        for tier in ["Enterprise_Key", "MidMarket_Core", "SMB_Standard", "Toxic_Drain"]:
            sub = self.df[self.df["client_tier"] == tier].copy()
            if len(sub) < 50:
                continue
                
            X_t, y_t = self._prepare_features(sub)
            t_model = Ridge(alpha=1.0)
            t_model.fit(X_t, y_t)
            y_t_pred = t_model.predict(X_t)
            
            beta_elasticity = float(t_model.coef_[0])
            r2 = float(r2_score(y_t, y_t_pred))
            
            # Categorize economic demand regime
            if abs(beta_elasticity) < 0.60:
                regime = "Inelastic (Reliability & SLA Driven)"
                rec_max_discount = 0.22
            elif abs(beta_elasticity) < 1.10:
                regime = "Unitary / Balanced Sensitivity"
                rec_max_discount = 0.18
            else:
                regime = "Highly Elastic (Opportunistic Arbitrage)"
                rec_max_discount = 0.12  # Tight discount guardrail required
                
            self.tier_models[tier] = t_model
            tier_results.append({
                "client_tier": tier,
                "sample_size": len(sub),
                "price_elasticity_beta": beta_elasticity,
                "r_squared": r2,
                "demand_regime": regime,
                "recommended_discount_ceiling": rec_max_discount
            })
            
        df_tier_elasticity = pd.DataFrame(tier_results)
        
        self.results_summary = {
            "portfolio_elasticity_beta": portfolio_elasticity,
            "portfolio_r2": portfolio_r2,
            "portfolio_mae": portfolio_mae,
            "tier_elasticity_table": df_tier_elasticity
        }
        return self.results_summary

if __name__ == "__main__":
    df_raw = pd.read_parquet("data/b2b_erp_transactions.parquet")
    engine = PriceElasticityEngine(df_raw)
    res = engine.fit_portfolio_elasticity()
    
    print("\n================ B2B PRICE-VOLUME ELASTICITY MODEL ================")
    print(f"Enterprise Elasticity Beta : {res['portfolio_elasticity_beta']:.4f}")
    print(f"Overall Model R-Squared    : {res['portfolio_r2']:.4f}")
    print(f"Mean Absolute Error (MAE)  : {res['portfolio_mae']:.4f}\n")
    print("Segment-Specific Price Elasticity & Guardrail Recommendations:")
    print(res["tier_elasticity_table"].to_string(index=False))
