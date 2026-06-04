import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def render_filters():
    """Render filter controls for supply chain data filtering and analysis."""
    st.markdown('<div class="section-header"><span class="section-header-accent"></span>Filters &amp; Search</div>', unsafe_allow_html=True)
    st.write("Use the controls below to filter and refine your supply chain data.")

    # Check if data is available in session state
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.info("📊 No data available. Please upload a CSV file in the **Data Upload** section first.")
        return None

    df = st.session_state.uploaded_df

    # Initialize filter state
    if "active_filters" not in st.session_state:
        st.session_state.active_filters = {}

    # Create tabs for different filter types
    filter_tab1, filter_tab2, filter_tab3 = st.tabs(["Column Filters", "Advanced Filters", "Filter Summary"])

    # ==================== TAB 1: Column Filters ====================
    with filter_tab1:
        st.subheader("Select Columns to Display")
        
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Choose columns to display",
            options=all_columns,
            default=all_columns,
            key="column_filter"
        )

        st.session_state.active_filters["columns"] = selected_columns

        # Display selected data
        if selected_columns:
            st.subheader("Filtered Data Preview")
            st.dataframe(df[selected_columns].head(10), use_container_width=True)

            # Download filtered data
            csv = df[selected_columns].to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv"
            )

    # ==================== TAB 2: Advanced Filters ====================
    with filter_tab2:
        st.subheader("Advanced Filtering Options")

        # Get column types for smart filtering
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
        datetime_cols = []
        
        # Detect potential date columns
        for col in df.columns:
            try:
                pd.to_datetime(df[col], errors='coerce')
                if df[col].dtype == "object":
                    datetime_cols.append(col)
            except:
                pass

        # Filter section in columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Categorical Filters")
            if categorical_cols:
                selected_categorical = st.selectbox(
                    "Select a categorical column",
                    options=categorical_cols,
                    key="categorical_select"
                )
                
                if selected_categorical:
                    unique_values = df[selected_categorical].unique().tolist()
                    
                    filter_type = st.radio(
                        f"Filter type for {selected_categorical}",
                        ["Include", "Exclude"],
                        horizontal=True,
                        key=f"filter_type_{selected_categorical}"
                    )
                    
                    selected_values = st.multiselect(
                        f"Select values to {filter_type.lower()}",
                        options=unique_values,
                        key=f"cat_filter_{selected_categorical}"
                    )

                    if selected_values:
                        if filter_type == "Include":
                            df = df[df[selected_categorical].isin(selected_values)]
                        else:
                            df = df[~df[selected_categorical].isin(selected_values)]
                        
                        st.session_state.active_filters[selected_categorical] = {
                            "type": filter_type,
                            "values": selected_values
                        }
                        st.success(f"✅ Filtered by {selected_categorical}")
            else:
                st.info("No categorical columns available for filtering.")

        with col2:
            st.subheader("Numeric Filters")
            if numeric_cols:
                selected_numeric = st.selectbox(
                    "Select a numeric column",
                    options=numeric_cols,
                    key="numeric_select"
                )
                
                if selected_numeric:
                    col_min, col_max = df[selected_numeric].min(), df[selected_numeric].max()
                    
                    filter_min, filter_max = st.slider(
                        f"Range for {selected_numeric}",
                        min_value=float(col_min),
                        max_value=float(col_max),
                        value=(float(col_min), float(col_max)),
                        key=f"numeric_filter_{selected_numeric}"
                    )
                    
                    df = df[(df[selected_numeric] >= filter_min) & (df[selected_numeric] <= filter_max)]
                    
                    st.session_state.active_filters[selected_numeric] = {
                        "min": filter_min,
                        "max": filter_max
                    }
                    st.success(f"✅ Filtered by {selected_numeric}")
            else:
                st.info("No numeric columns available for filtering.")

        # Date filter section
        if datetime_cols:
            st.subheader("Date Range Filter")
            selected_date_col = st.selectbox(
                "Select a date column",
                options=datetime_cols,
                key="date_select"
            )
            
            if selected_date_col:
                try:
                    df[selected_date_col] = pd.to_datetime(df[selected_date_col], errors='coerce')
                    
                    col_min_date = df[selected_date_col].min()
                    col_max_date = df[selected_date_col].max()
                    
                    date_range = st.date_input(
                        f"Select date range for {selected_date_col}",
                        value=(col_min_date.date(), col_max_date.date()),
                        min_value=col_min_date.date(),
                        max_value=col_max_date.date(),
                        key=f"date_filter_{selected_date_col}"
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df = df[(df[selected_date_col] >= pd.Timestamp(start_date)) & 
                               (df[selected_date_col] <= pd.Timestamp(end_date))]
                        
                        st.session_state.active_filters[selected_date_col] = {
                            "start": start_date,
                            "end": end_date
                        }
                        st.success(f"✅ Filtered by date range")
                except Exception as e:
                    st.error(f"Error processing date column: {str(e)}")

        # Text search filter
        st.subheader("Text Search")
        search_column = st.selectbox(
            "Search in column",
            options=df.columns.tolist(),
            key="search_select"
        )
        
        search_term = st.text_input(
            f"Search term in {search_column}",
            key="search_term"
        )
        
        if search_term:
            df = df[df[search_column].astype(str).str.contains(search_term, case=False, na=False)]
            st.session_state.active_filters["search"] = {
                "column": search_column,
                "term": search_term
            }
            st.success(f"✅ Found {len(df)} matching records")

    # ==================== TAB 3: Filter Summary ====================
    with filter_tab3:
        st.subheader("Active Filters Summary")
        
        if st.session_state.active_filters:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Active Filters", len(st.session_state.active_filters))
            
            with col2:
                st.metric("Records Remaining", len(df))
            
            with col3:
                st.metric("Records Removed", len(st.session_state.uploaded_df) - len(df))
            
            st.markdown("---")
            st.write("**Active Filter Conditions:**")
            for filter_name, filter_config in st.session_state.active_filters.items():
                if isinstance(filter_config, dict):
                    if "type" in filter_config:  # Categorical filter
                        st.write(f"• **{filter_name}** ({filter_config['type']}): {', '.join(map(str, filter_config['values']))}")
                    elif "min" in filter_config:  # Numeric filter
                        st.write(f"• **{filter_name}**: {filter_config['min']:.2f} - {filter_config['max']:.2f}")
                    elif "start" in filter_config:  # Date filter
                        st.write(f"• **{filter_name}**: {filter_config['start']} to {filter_config['end']}")
                    elif "term" in filter_config:  # Text search
                        st.write(f"• **Search**: '{filter_config['term']}' in {filter_config['column']}")
                else:
                    st.write(f"• **{filter_name}**: {filter_config}")
            
            # Clear filters button
            if st.button("🔄 Reset All Filters", use_container_width=True):
                st.session_state.active_filters = {}
                st.rerun()
        else:
            st.info("No active filters. Use the tabs above to apply filters.")

    return df


def get_filtered_dataframe():
    """Get the currently filtered dataframe from session state."""
    if "uploaded_df" in st.session_state and st.session_state.uploaded_df is not None:
        return st.session_state.uploaded_df
    return None


def apply_filters_to_dataframe(df, filter_config):
    """
    Apply a filter configuration to a dataframe.
    
    Args:
        df (pd.DataFrame): Input dataframe
        filter_config (dict): Filter configuration dictionary
    
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    filtered_df = df.copy()
    
    for filter_name, filter_value in filter_config.items():
        if isinstance(filter_value, dict):
            if "type" in filter_value:  # Categorical filter
                if filter_value["type"] == "Include":
                    filtered_df = filtered_df[filtered_df[filter_name].isin(filter_value["values"])]
                else:
                    filtered_df = filtered_df[~filtered_df[filter_name].isin(filter_value["values"])]
            
            elif "min" in filter_value:  # Numeric filter
                filtered_df = filtered_df[
                    (filtered_df[filter_name] >= filter_value["min"]) & 
                    (filtered_df[filter_name] <= filter_value["max"])
                ]
            
            elif "start" in filter_value:  # Date filter
                filtered_df[filter_name] = pd.to_datetime(filtered_df[filter_name], errors='coerce')
                filtered_df = filtered_df[
                    (filtered_df[filter_name] >= pd.Timestamp(filter_value["start"])) & 
                    (filtered_df[filter_name] <= pd.Timestamp(filter_value["end"]))
                ]
            
            elif "term" in filter_value:  # Text search
                filtered_df = filtered_df[
                    filtered_df[filter_value["column"]].astype(str).str.contains(
                        filter_value["term"], case=False, na=False
                    )
                ]
        
        elif isinstance(filter_value, list):  # Column selection
            if set(filter_value).issubset(set(filtered_df.columns)):
                filtered_df = filtered_df[filter_value]
    
    return filtered_df


def create_dropdown_filter(label, options, key=None, multi=False):
    """
    Create a dropdown filter component.
    
    Args:
        label (str): Label for the dropdown
        options (list): List of options to display
        key (str): Unique key for the dropdown
        multi (bool): Allow multiple selections
    
    Returns:
        Selected value(s)
    """
    if multi:
        return st.multiselect(label, options=options, key=key)
    else:
        return st.selectbox(label, options=options, key=key)


def create_range_filter(label, df_column, key=None):
    """
    Create a numeric range filter slider.
    
    Args:
        label (str): Label for the slider
        df_column (pd.Series): Column data for min/max bounds
        key (str): Unique key for the slider
    
    Returns:
        Tuple of (min_value, max_value)
    """
    col_min, col_max = df_column.min(), df_column.max()
    
    return st.slider(
        label,
        min_value=float(col_min),
        max_value=float(col_max),
        value=(float(col_min), float(col_max)),
        key=key
    )
