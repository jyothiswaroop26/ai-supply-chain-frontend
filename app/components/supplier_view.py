import streamlit as st
import pandas as pd
import plotly.express as px


def _detect_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """Return the first column whose name contains any of the given keywords (case-insensitive)."""
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return None


def render_supplier_view():
    """Render Supplier Insights section from the uploaded dataset."""
    st.markdown(
        '<div class="section-header"><span class="section-header-accent"></span>Supplier Insights</div>',
        unsafe_allow_html=True,
    )
    st.write("Analyse supplier performance, lead times, and risk scoring from your uploaded data.")

    # ── Data guard ───────────────────────────────────────────────────────────
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">🏭</div>
  <div class="empty-state-title">No data loaded yet</div>
  <div class="empty-state-body">Upload a CSV in <strong>Data Upload</strong> to view supplier insights.</div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    df: pd.DataFrame = st.session_state.uploaded_df.copy()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found. Supplier analysis requires at least one numeric column.")
        return

    # ── Auto-detect columns ──────────────────────────────────────────────────
    default_supplier_col = _detect_column(df, ["supplier", "vendor", "manufacturer", "provider", "partner"])
    default_lead_col = _detect_column(df, ["lead", "lead_time", "leadtime", "delivery", "days"])
    default_cost_col = _detect_column(df, ["cost", "price", "amount", "spend", "value", "revenue"])
    default_qty_col = _detect_column(df, ["quantity", "qty", "volume", "units", "order"])
    default_date_col = _detect_column(df, ["date", "week", "month", "period", "time"])

    # ── Column configuration ─────────────────────────────────────────────────
    st.subheader("Configuration")
    col1, col2, col3 = st.columns(3)

    all_cols = df.columns.tolist()

    with col1:
        supplier_options = [None] + all_cols
        supplier_default_idx = (
            supplier_options.index(default_supplier_col) if default_supplier_col in supplier_options else 0
        )
        supplier_col = st.selectbox(
            "Supplier / Vendor column",
            options=supplier_options,
            index=supplier_default_idx,
            format_func=lambda x: "— None —" if x is None else x,
            help="Categorical column identifying each supplier",
        )

    with col2:
        metric_options = [None] + numeric_cols
        lead_default_idx = metric_options.index(default_lead_col) if default_lead_col in metric_options else 0
        lead_col = st.selectbox(
            "Lead Time / Performance metric",
            options=metric_options,
            index=lead_default_idx,
            format_func=lambda x: "— None —" if x is None else x,
            help="Numeric column representing lead time or a performance KPI",
        )

    with col3:
        cost_default_idx = metric_options.index(default_cost_col) if default_cost_col in metric_options else 0
        cost_col = st.selectbox(
            "Cost / Spend metric (optional)",
            options=metric_options,
            index=cost_default_idx,
            format_func=lambda x: "— None —" if x is None else x,
            help="Numeric column representing cost or spend per supplier",
        )

    st.markdown("---")

    # Resolve primary metric for analysis
    primary_metric = lead_col or cost_col or numeric_cols[0]

    # ── Summary KPIs ─────────────────────────────────────────────────────────
    st.subheader("Supplier Summary")

    k1, k2, k3, k4 = st.columns(4)
    if supplier_col:
        k1.metric("🏭 Unique Suppliers", f"{df[supplier_col].nunique():,}")
    else:
        k1.metric("📋 Total Records", f"{len(df):,}")

    k2.metric(f"📊 Avg {primary_metric}", f"{df[primary_metric].mean():.2f}")
    k3.metric(f"🔻 Min {primary_metric}", f"{df[primary_metric].min():.2f}")
    k4.metric(f"🔺 Max {primary_metric}", f"{df[primary_metric].max():.2f}")

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_labels = ["Performance Overview", "Lead Time Analysis", "Risk Scoring", "Raw Data"]
    if cost_col and lead_col:
        tab_labels.insert(2, "Cost vs Lead Time")
    tabs = st.tabs(tab_labels)
    tab_index = 0

    # ── Tab: Performance Overview ────────────────────────────────────────────
    with tabs[tab_index]:
        tab_index += 1
        st.subheader("Supplier Performance Overview")
        if supplier_col:
            agg = (
                df.groupby(supplier_col)[primary_metric]
                .mean()
                .reset_index()
                .sort_values(primary_metric, ascending=False)
            )
            top_n = st.slider("Show top N suppliers", 5, min(50, len(agg)), min(20, len(agg)), key="perf_n")
            fig = px.bar(
                agg.head(top_n),
                x=supplier_col,
                y=primary_metric,
                title=f"Average {primary_metric} by Supplier",
                template="plotly_white",
                color=primary_metric,
                color_continuous_scale="Blues",
                labels={primary_metric: primary_metric, supplier_col: "Supplier"},
            )
            fig.update_layout(xaxis_tickangle=-40, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.histogram(
                df,
                x=primary_metric,
                nbins=30,
                title=f"Distribution of {primary_metric}",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab: Lead Time Analysis ───────────────────────────────────────────────
    with tabs[tab_index]:
        tab_index += 1
        st.subheader("Lead Time Analysis")
        lc = lead_col or primary_metric
        if supplier_col:
            box_data = df[[supplier_col, lc]].dropna()
            top_suppliers = (
                box_data.groupby(supplier_col)[lc].count().nlargest(20).index.tolist()
            )
            box_data = box_data[box_data[supplier_col].isin(top_suppliers)]
            fig = px.box(
                box_data,
                x=supplier_col,
                y=lc,
                title=f"{lc} distribution by Supplier (top 20)",
                template="plotly_white",
                color=supplier_col,
            )
            fig.update_layout(xaxis_tickangle=-40, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.box(
                df,
                y=lc,
                title=f"Overall {lc} distribution",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Avg lead time table
        if supplier_col:
            st.subheader("Average Lead Time per Supplier")
            tbl = (
                df.groupby(supplier_col)[lc]
                .agg(["mean", "min", "max", "count"])
                .rename(columns={"mean": "Avg", "min": "Min", "max": "Max", "count": "Orders"})
                .round(2)
                .sort_values("Avg")
                .reset_index()
            )
            st.dataframe(tbl, use_container_width=True)

    # ── Tab: Cost vs Lead Time (optional) ────────────────────────────────────
    if cost_col and lead_col:
        with tabs[tab_index]:
            tab_index += 1
            st.subheader("Cost vs Lead Time")
            scatter_df = df[[lead_col, cost_col] + ([supplier_col] if supplier_col else [])].dropna()
            fig = px.scatter(
                scatter_df,
                x=lead_col,
                y=cost_col,
                color=supplier_col if supplier_col else None,
                title=f"{cost_col} vs {lead_col}",
                template="plotly_white",
                labels={lead_col: lead_col, cost_col: cost_col},
                opacity=0.7,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab: Risk Scoring ────────────────────────────────────────────────────
    with tabs[tab_index]:
        tab_index += 1
        st.subheader("Supplier Risk Scoring")
        st.caption("Risk is scored by normalising the primary metric — higher values indicate higher risk.")

        if supplier_col:
            risk_df = (
                df.groupby(supplier_col)[primary_metric]
                .mean()
                .reset_index()
                .rename(columns={primary_metric: "avg_metric"})
            )
            min_v, max_v = risk_df["avg_metric"].min(), risk_df["avg_metric"].max()
            denom = max_v - min_v if max_v != min_v else 1
            risk_df["Risk Score"] = ((risk_df["avg_metric"] - min_v) / denom * 100).round(1)
            risk_df["Risk Level"] = pd.cut(
                risk_df["Risk Score"],
                bins=[-1, 33, 66, 101],
                labels=["🟢 Low", "🟡 Medium", "🔴 High"],
            )
            risk_df = risk_df.sort_values("Risk Score", ascending=False).reset_index(drop=True)
            risk_df.columns = [supplier_col, f"Avg {primary_metric}", "Risk Score", "Risk Level"]

            fig = px.bar(
                risk_df.head(20),
                x=supplier_col,
                y="Risk Score",
                color="Risk Level",
                title="Supplier Risk Scores (top 20)",
                template="plotly_white",
                color_discrete_map={"🟢 Low": "#22c55e", "🟡 Medium": "#f59e0b", "🔴 High": "#ef4444"},
            )
            fig.update_layout(xaxis_tickangle=-40)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(risk_df, use_container_width=True)
        else:
            st.info("Select a **Supplier / Vendor column** above to enable risk scoring.")

    # ── Tab: Raw Data ─────────────────────────────────────────────────────────
    with tabs[tab_index]:
        st.subheader("Raw Supplier Data")
        st.dataframe(df, use_container_width=True)
        st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
