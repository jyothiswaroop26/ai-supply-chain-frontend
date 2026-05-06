import streamlit as st
import pandas as pd


def render_data_upload():
    st.header("Data Upload")
    st.write("Upload a CSV file to preview and work with your supply chain data.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Store in session state for use in other components
            st.session_state.uploaded_df = df

            st.success(f"File uploaded successfully: **{uploaded_file.name}**")
            st.markdown(f"**Rows:** {df.shape[0]}  |  **Columns:** {df.shape[1]}")

            st.subheader("Data Preview")

            col1, col2, col3 = st.columns(3)
            with col1:
                search_query = st.text_input("Search", placeholder="Filter any column...")
            with col2:
                rows_to_show = st.selectbox("Rows to display", [10, 25, 50, 100, "All"], index=0)
            with col3:
                selected_columns = st.multiselect(
                    "Select columns",
                    options=df.columns.tolist(),
                    default=df.columns.tolist(),
                )

            filtered_df = df[selected_columns] if selected_columns else df

            if search_query:
                mask = filtered_df.apply(
                    lambda col: col.astype(str).str.contains(search_query, case=False, na=False)
                ).any(axis=1)
                filtered_df = filtered_df[mask]

            if rows_to_show != "All":
                display_df = filtered_df.head(int(rows_to_show))
            else:
                display_df = filtered_df

            st.dataframe(display_df, use_container_width=True)

            if search_query or rows_to_show != "All":
                st.caption(f"Showing {len(display_df)} of {len(filtered_df)} filtered rows (total: {len(df)} rows)")
            else:
                st.caption(f"Showing {len(display_df)} of {len(df)} rows")

            with st.expander("Column Summary"):
                st.dataframe(df.describe(include="all"), use_container_width=True)

            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download processed CSV",
                data=csv_bytes,
                file_name=f"processed_{uploaded_file.name}",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"Failed to read file: {e}")
    else:
        st.info("Upload a CSV file above to display its contents here.")
