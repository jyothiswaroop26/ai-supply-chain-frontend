import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _detect_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """Return the first column whose name contains any of the given keywords (case-insensitive)."""
    for col in df.columns:
        if any(kw in col.lower() for kw in keywords):
            return col
    return None


def render_inventory_view():
    """Render Inventory Levels section from uploaded dataset."""
    st.markdown(
        '<div class="section-header"><span class="section-header-accent"></span>Inventory</div>',
        unsafe_allow_html=True,
    )
    st.write("Analyse inventory levels, identify low-stock items, and track stock movements from your uploaded data.")

    # ── Data guard ──────────────────────────────────────────────────────────
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.markdown(
            """
<div class="empty-state">
  <div class="empty-state-icon">📦</div>
  <div class="empty-state-title">No data loaded yet</div>
  <div class="empty-state-body">Upload a CSV in <strong>Data Upload</strong> to view inventory insights.</div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    df: pd.DataFrame = st.session_state.uploaded_df.copy()
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found in your dataset. Inventory analysis requires at least one numeric column.")
        return

    # ── Auto-detect sensible defaults ───────────────────────────────────────
    default_inventory_col = (
        _detect_column(df, ["inventory", "stock", "quantity", "qty", "level", "on_hand", "onhand"])
        or numeric_cols[0]
    )
    default_product_col = _detect_column(df, ["product", "item", "sku", "name", "description"])
    default_date_col = _detect_column(df, ["date", "week", "month", "period", "time"])

    # ── Column selection ─────────────────────────────────────────────────────
    st.subheader("Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        inventory_col = st.selectbox(
            "Inventory / Stock column",
            options=numeric_cols,
            index=numeric_cols.index(default_inventory_col),
            help="Numeric column representing inventory quantity or level",
        )

    with col2:
        all_cols = df.columns.tolist()
        product_options = [None] + all_cols
        product_default_idx = (
            product_options.index(default_product_col) if default_product_col in product_options else 0
        )
        product_col = st.selectbox(
            "Product / Item column (optional)",
            options=product_options,
            index=product_default_idx,
            format_func=lambda x: "— None —" if x is None else x,
            help="Categorical column to group inventory by product or SKU",
        )

    with col3:
        date_options = [None] + all_cols
        date_default_idx = (
            date_options.index(default_date_col) if default_date_col in date_options else 0
        )
        date_col = st.selectbox(
            "Date / Period column (optional)",
            options=date_options,
            index=date_default_idx,
            format_func=lambda x: "— None —" if x is None else x,
            help="Column representing time so stock can be plotted over time",
        )

    st.markdown("---")

    # ── Summary KPI cards ────────────────────────────────────────────────────
    st.subheader("Inventory Summary")
    total_inv = df[inventory_col].sum()
    avg_inv = df[inventory_col].mean()
    min_inv = df[inventory_col].min()
    max_inv = df[inventory_col].max()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📦 Total Stock", f"{total_inv:,.0f}")
    k2.metric("📊 Average Level", f"{avg_inv:,.1f}")
    k3.metric("🔻 Minimum Level", f"{min_inv:,.0f}")
    k4.metric("🔺 Maximum Level", f"{max_inv:,.0f}")

    st.markdown("---")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_labels = ["Stock Levels", "Low Stock Alerts", "Raw Data"]
    if date_col:
        tab_labels.insert(1, "Trend Over Time")

    tabs = st.tabs(tab_labels)
    tab_index = 0

    # Tab: Stock Levels (by product or distribution)
    with tabs[tab_index]:
        tab_index += 1
        if product_col:
            st.subheader(f"Inventory by {product_col}")
            group = (
                df.groupby(product_col)[inventory_col]
                .sum()
                .reset_index()
                .sort_values(inventory_col, ascending=False)
            )
            top_n = st.slider("Show top N items", min_value=5, max_value=min(50, len(group)), value=min(20, len(group)))
            group_top = group.head(top_n)
            fig = px.bar(
                group_top,
                x=product_col,
                y=inventory_col,
                title=f"Total {inventory_col} by {product_col}",
                labels={inventory_col: "Stock Level", product_col: "Product"},
                template="plotly_white",
                color=inventory_col,
                color_continuous_scale="Blues",
            )
            fig.update_layout(xaxis_tickangle=-40, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader(f"Distribution of {inventory_col}")
            fig = px.histogram(
                df,
                x=inventory_col,
                nbins=30,
                title=f"Distribution of {inventory_col}",
                template="plotly_white",
                labels={inventory_col: "Stock Level"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # Tab: Trend Over Time (only when date_col selected)
    if date_col:
        with tabs[tab_index]:
            tab_index += 1
            st.subheader(f"{inventory_col} Over Time")
            try:
                df["_date_parsed"] = pd.to_datetime(df[date_col], infer_datetime_format=True, errors="coerce")
                valid = df.dropna(subset=["_date_parsed"])
                if valid.empty:
                    st.warning("Could not parse the selected date column as dates.")
                else:
                    if product_col:
                        agg = (
                            valid.groupby(["_date_parsed", product_col])[inventory_col]
                            .sum()
                            .reset_index()
                        )
                        fig = px.line(
                            agg,
                            x="_date_parsed",
                            y=inventory_col,
                            color=product_col,
                            title=f"{inventory_col} over time by {product_col}",
                            labels={"_date_parsed": date_col, inventory_col: "Stock Level"},
                            template="plotly_white",
                            markers=True,
                        )
                    else:
                        agg = valid.groupby("_date_parsed")[inventory_col].sum().reset_index()
                        fig = px.line(
                            agg,
                            x="_date_parsed",
                            y=inventory_col,
                            title=f"Total {inventory_col} over time",
                            labels={"_date_parsed": date_col, inventory_col: "Stock Level"},
                            template="plotly_white",
                            markers=True,
                        )
                    fig.update_xaxes(title_text=date_col)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not plot trend: {e}")

    # Tab: Low Stock Alerts
    with tabs[tab_index]:
        tab_index += 1
        st.subheader("Low Stock Alerts")
        threshold_default = float(df[inventory_col].quantile(0.20))
        threshold = st.number_input(
            "Low-stock threshold (items at or below this level are flagged)",
            min_value=0.0,
            value=round(threshold_default, 2),
            step=1.0,
            help="Default is the 20th percentile of your inventory column",
        )
        low_stock = df[df[inventory_col] <= threshold]
        if low_stock.empty:
            st.success(f"No items at or below {threshold:.0f} — inventory looks healthy!")
        else:
            st.warning(f"⚠️ {len(low_stock):,} record(s) with inventory ≤ {threshold:.0f}")
            display_cols = []
            if product_col:
                display_cols.append(product_col)
            if date_col:
                display_cols.append(date_col)
            display_cols.append(inventory_col)
            st.dataframe(
                low_stock[display_cols].sort_values(inventory_col).reset_index(drop=True),
                use_container_width=True,
            )

            if product_col:
                low_group = (
                    low_stock.groupby(product_col)[inventory_col]
                    .sum()
                    .reset_index()
                    .sort_values(inventory_col)
                    .head(20)
                )
                fig = px.bar(
                    low_group,
                    x=product_col,
                    y=inventory_col,
                    title="Lowest-stock items",
                    template="plotly_white",
                    color=inventory_col,
                    color_continuous_scale="Reds",
                )
                fig.update_layout(xaxis_tickangle=-40, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

    # Tab: Raw Data
    with tabs[tab_index]:
        st.subheader("Raw Inventory Data")
        display_df = df.drop(columns=["_date_parsed"], errors="ignore")
        st.dataframe(display_df, use_container_width=True)
        st.caption(f"{len(display_df):,} rows · {len(display_df.columns)} columns")
