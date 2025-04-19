import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(layout="wide")

# --------- HEADER UI STYLING ---------
st.markdown("""
<style>
.center { display: flex; justify-content: center; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='center' style='color:rgb(70, 130, 255);'>An EsteStyle Streamlit Page<br>Where Python Wiz Meets Data Viz!</h2>", unsafe_allow_html=True)
st.markdown("<img src='https://1drv.ms/i/s!ArWyPNkF5S-foZspwsary83MhqEWiA?embed=1&width=307&height=307' width='300' style='display: block; margin: 0 auto;'>", unsafe_allow_html=True)
st.markdown("<h3 class='center' style='color: rgb(135, 206, 250);'>🏨 Originally created for Best Western at Firestone 🛎️</h3>", unsafe_allow_html=True)
st.markdown("<h3 class='center' style='color: rgb(135, 206, 250);'>🤖 By Esteban C Loetz 📟</h3>", unsafe_allow_html=True)

def colored_metric(label, value, color):
    st.markdown(
        f"""
        <div style='
            background-color: {color};
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            color: white;
            font-weight: bold;
        '>
            <div style='font-size: 0.9rem;'>{label}</div>
            <div style='font-size: 1.3rem;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------- SESSION STATE SETUP ---------
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

if "excel_bytes" not in st.session_state:
    st.session_state.excel_bytes = None

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown("---")  # Just a divider line for UX
    # --------- FILE UPLOADER ---------
    st.subheader("📥 Download file for analysis:")
    st.write('')
    uploaded_file = st.file_uploader("📄 Select Visual Matrix output CSV to analyze", type="csv")
    st.write('')
    st.caption("Or try it out with a demo dataset!")
    use_demo = st.button("📂 Use Demo File")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file).reset_index(drop=True)
        st.session_state.uploaded_df = df
        st.success("✅ CSV file uploaded and stored!")

    elif use_demo:
        # Example demo DataFrame
        demo_data_path = "Company Revenue Report Demo.csv"
        df = pd.read_csv(demo_data_path)
        st.session_state.uploaded_df = df
        st.success("Demo file loaded!")

    # --------- UI OPTIONS ---------
    if st.session_state.uploaded_df is not None:
        st.markdown("---")  # Just a divider line for UX
        st.subheader("🔍 Choose what to graph:")
        st.write('')
        # Checkbox to show original data preview
        st.caption("If viewing the original data will assist in column selection, check box:")
        show_original = st.checkbox("🗃️ Show Original Data", value=False)
        if show_original:
            if "uploaded_df" in st.session_state:
                st.subheader("Original Uploaded Data")
                st.dataframe(st.session_state.uploaded_df, hide_index=True)
            else:
                st.warning("No uploaded data available.")

        column_to_graph = st.selectbox(
            "Which data column do you want to analyze?",
            options=[col for col in st.session_state.uploaded_df.columns if col not in ["CompanyName", "CompanyCode"]],
        )

        sort_order = st.selectbox("Sort order?", options=["Descending", "Ascending"])
        ascending = sort_order == "Ascending"

        if st.button("📊 Generate Graph"):
            # Reset the Excel bytes in session state
            st.session_state.excel_bytes = None  # Clear the previous Excel file

            df = st.session_state.uploaded_df.copy()
            df = df[["CompanyName", column_to_graph]].sort_values(by=column_to_graph, ascending=ascending)

            # Store filtered for Excel export
            st.session_state.filtered_df = df

            if ascending:
                bottom3 = df.head(3)
                top3 = df.tail(3)
            else:
                top3 = df.head(3)
                bottom3 = df.tail(3)

            st.subheader("Top 3 Values")
            top_cols = st.columns(3)
            for i, row in enumerate((top3.itertuples(index=False))):
                with top_cols[i]:
                    colored_metric(label=row.CompanyName, value=getattr(row, column_to_graph), color="#155724")  # Green


            st.subheader("Bottom 3 Values")
            bottom_cols = st.columns(3)
            for i, row in enumerate(bottom3.itertuples(index=False)):
                with bottom_cols[i]:
                    colored_metric(label=row.CompanyName, value=getattr(row, column_to_graph), color="#721c24")  # Red

            st.markdown("---")  # Just a divider line for UX

            fig = px.bar(
                df,
                x="CompanyName",
                y=column_to_graph,
                title=f"{column_to_graph} by CompanyName",
                labels={"CompanyName": "Company", column_to_graph: column_to_graph},
                color=column_to_graph,
                color_continuous_scale="Blues"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")  # Just a divider line for UX

        if st.session_state.filtered_df is not None:

            st.subheader("🚀 View and export filtered data options:")

            col1, col2 = st.columns(2)
                
            with col1:
                st.write('')
                # Checkbox to show processed subset preview
                show_processed = st.checkbox("🔬 Show Data Subset", value=False)
                if show_processed:
                    if "filtered_df" in st.session_state:
                        st.subheader("Data Subset (Filtered)")
                        # Reset the index to exclude it from the display
                        st.dataframe(st.session_state.filtered_df, hide_index=True)
                    else:
                        st.warning("No data available.")

            with col2:
                # --------- EXCEL EXPORT ---------
                st.write('')
                if st.button("💾 Convert to Excel"):
                    to_export = st.session_state.filtered_df

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        to_export.to_excel(writer, index=False, sheet_name="Export")
                    output.seek(0)
                    st.session_state.excel_bytes = output
                    st.success("✅ CSV file converted to Excel file!")

                # If excel_bytes exists, show download button
                if st.session_state.excel_bytes:
                    if st.download_button(
                        label="⬇️ Download Excel File",
                        data=st.session_state.excel_bytes,
                        file_name="estestyle_exported_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ):
                        st.success("✅ Excel file downloaded!")

