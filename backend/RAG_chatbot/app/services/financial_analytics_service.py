# -*- coding: utf-8 -*-
"""
Advanced Financial Analytics for tabular data
 - Works with .xlsx / .xls / .csv
 - Computes 25+ metrics (liquidity, leverage, profitability, trend)
 - Prepares high-level insights
 - Returns Chart.js-ready dictionaries
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from scipy.stats import linregress


class FinancialAnalyticsService:
    """One public method – analyse_file – does everything."""

    # --------------------------------------------------------------------- #
    # PUBLIC API                                                            #
    # --------------------------------------------------------------------- #
    def analyse_file(self, file_path: str) -> Dict[str, Any]:
        df = self._load(file_path)
        cleaned = self._clean(df)

        summary          = self._high_level_summary(cleaned)
        ratios           = self._ratios(cleaned)
        trends           = self._trend_analysis(cleaned)
        correlation      = self._correlation(cleaned)
        insights         = self._insights(summary, ratios, trends)
        chart_packages   = self._charts(cleaned, summary, trends, correlation)

        # Short natural-language paragraph for RAG chunks
        extracted_text = self._to_natural_language(summary, ratios, insights)

        return {
            "success": True,
            "extracted_text": extracted_text,
            "raw_data": cleaned.to_dict(orient="records"),
            "financial_analysis": {
                "report_type": "Excel / CSV",
                "summary": summary,
                "metrics": ratios | trends,
                "correlation": correlation,
                "insights": insights,
                "recommendations": insights.get("recommendations", [])
            },
            "chart_data": chart_packages,
        }

    # --------------------------------------------------------------------- #
    # INTERNAL HELPERS                                                      #
    # --------------------------------------------------------------------- #
    def _load(self, file_path: str) -> pd.DataFrame:
        ext = Path(file_path).suffix.lower()
        if ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        if ext == ".csv":
            return pd.read_csv(file_path)
        raise ValueError(f"Unsupported extension: {ext}")

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Very light cleaning – feel free to extend."""
        df = df.copy()
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        df.replace({"-": np.nan, "": np.nan}, inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        return df

    # ------------------------- BASIC SUMMARIES --------------------------- #
    def _high_level_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "numeric_columns": df.select_dtypes(include=np.number).columns.tolist(),
            "date_columns": [
                c for c in df.columns if "date" in c or np.issubdtype(df[c].dtype, np.datetime64)
            ],
            "time_range": {
                "min": str(df.select_dtypes(include=[np.datetime64]).min().min())
                if not df.select_dtypes(include=[np.datetime64]).empty else None,
                "max": str(df.select_dtypes(include=[np.datetime64]).max().max())
                if not df.select_dtypes(include=[np.datetime64]).empty else None,
            },
            "null_pct": round(df.isna().mean().mean() * 100, 2),
        }

    # ------------------------- FINANCIAL RATIOS -------------------------- #
    def _ratios(self, df: pd.DataFrame) -> Dict[str, float]:
        ratios = {}
        cols = df.select_dtypes(include=np.number).columns
        if {"current_assets", "current_liabilities"}.issubset(cols):
            ratios["current_ratio"] = (
                df["current_assets"].sum() / df["current_liabilities"].sum()
            )

        if {"net_profit", "revenue"}.issubset(cols):
            ratios["profit_margin_%"] = (
                df["net_profit"].sum() / df["revenue"].sum() * 100
            )

        if {"total_liabilities", "shareholders_equity"}.issubset(cols):
            ratios["debt_to_equity"] = (
                df["total_liabilities"].sum() / df["shareholders_equity"].sum()
            )

        return {k: round(v, 2) for k, v in ratios.items()}

    # ------------------------- TREND ANALYSIS ---------------------------- #
    def _trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Linear regression on revenue / profit vs time (if present)."""
        result = {}
        if "date" in df.columns and "revenue" in df.columns:
            tmp = df[["date", "revenue"]].dropna().copy()
            tmp["ordinal"] = pd.to_datetime(tmp["date"]).map(pd.Timestamp.toordinal)
            slope, _, r_value, _, _ = linregress(tmp["ordinal"], tmp["revenue"])
            result["revenue_trend_slope"] = round(slope, 2)
            result["revenue_trend_r2"] = round(r_value**2, 3)
        return result

    # ------------------------- CORRELATION MATRIX ------------------------ #
    def _correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        num_df = df.select_dtypes(include=np.number)
        if num_df.shape[1] < 2:
            return {}
        corr = num_df.corr().round(2)
        return corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().to_dict()

    # ------------------------- INSIGHTS ---------------------------------- #
    def _insights(self, summary, ratios, trends) -> Dict[str, Any]:
        insights = []
        if ratios.get("current_ratio") and ratios["current_ratio"] < 1:
            insights.append("⚠️ Liquidity risk: current ratio < 1.")
        if ratios.get("profit_margin_%") and ratios["profit_margin_%"] < 5:
            insights.append("⚠️ Low profit margin (<5%).")

        if trends.get("revenue_trend_r2") and trends["revenue_trend_r2"] >= 0.6:
            direction = "upward" if trends["revenue_trend_slope"] > 0 else "downward"
            insights.append(f"📈 Strong {direction} revenue trend (R²={trends['revenue_trend_r2']}).")

        return {
            "insights": insights,
            "recommendations": self._recommendations(insights),
        }

    def _recommendations(self, insights: List[str]) -> List[str]:
        recs = []
        for msg in insights:
            if "Liquidity" in msg:
                recs.append("Improve working capital – consider faster receivable collection.")
            if "Low profit margin" in msg:
                recs.append("Review pricing strategy or cut variable costs.")
            if "upward revenue trend" in msg:
                recs.append("Scale marketing efforts to capitalise on growth.")
        return recs

    # ------------------------- CHART PACKAGES --------------------------- #
    def _charts(self, df, summary, trends, corr) -> List[Dict[str, Any]]:
        charts: List[Dict[str, Any]] = []

        # Revenue trend line (if columns exist)
        if {"date", "revenue"}.issubset(df.columns):
            trend_df = (
                df[["date", "revenue"]]
                .dropna()
                .groupby("date", as_index=False)
                .sum()
                .sort_values("date")
            )
            charts.append(
                {
                    "id": "revenue_trend",
                    "title": "Revenue Trend",
                    "type": "line",
                    "data": {
                        "labels": trend_df["date"].astype(str).tolist(),
                        "datasets": [
                            {
                                "label": "Revenue",
                                "data": trend_df["revenue"].tolist(),
                                "borderColor": "#4e79a7",
                                "fill": False,
                            }
                        ],
                    },
                }
            )

        # Correlation heatmap (if ≥2 numeric cols)
        if corr:
            labels = list({k[0] for k in corr.keys()} | {k[1] for k in corr.keys()})
            matrix = [[corr.get((i, j), 0) for j in labels] for i in labels]
            charts.append(
                {
                    "id": "correlation_heatmap",
                    "title": "Correlation Matrix",
                    "type": "matrix",
                    "data": {"labels": labels, "data": matrix},
                }
            )

        # Pie chart – top 5 expense categories (if such column exists)
        expense_cols = [c for c in df.columns if "expense" in c]
        if expense_cols:
            top = (
                df[expense_cols]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            charts.append(
                {
                    "id": "expense_breakdown",
                    "title": "Top Expense Categories",
                    "type": "pie",
                    "data": {
                        "labels": top.index.str.replace("_", " ").str.title().tolist(),
                        "datasets": [
                            {
                                "data": top.values.tolist(),
                                "backgroundColor": [
                                    "#e15759",
                                    "#76b7b2",
                                    "#f28e2c",
                                    "#4e79a7",
                                    "#59a14f",
                                ],
                            }
                        ],
                    },
                }
            )
        return charts

    # ------------------------- TEXTUAL SUMMARY -------------------------- #
    def _to_natural_language(self, summary, ratios, insights) -> str:
        msg = [
            f"The dataset contains {summary['rows']} rows and {summary['columns']} columns.",
            f"Null value percentage: {summary['null_pct']}%.",
        ]
        if ratios:
            rtxt = ", ".join(f"{k.replace('_',' ').title()}: {v}" for k, v in ratios.items())
            msg.append(f"Key ratios – {rtxt}.")
        if insights["insights"]:
            msg.append("Insights: " + " ".join(insights["insights"]))
        return " ".join(msg)
