import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re

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
st.header("")

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
if "uploaded_df_tab1" not in st.session_state:
    st.session_state.uploaded_df_tab1 = None

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = {}

if "comparison_df_time" not in st.session_state:
    st.session_state.comparison_df_time = None

if "excel_bytes" not in st.session_state:
    st.session_state.excel_bytes = None

if "use_demo" not in st.session_state:
    st.session_state.use_demo = False

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

st.markdown("""
    <style>
        div[data-testid="stTabs"] button {
            display: flex;
            justify-content: center;
            flex-grow: 1;
        }
    </style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Single CSV Analysis by Company", "Multi CSV Analysis by Date"])

with tab1:

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.header("Single CSV Analysis by Company")
        st.markdown("---")  # Just a divider line for UX
        # --------- FILE UPLOADER ---------
        st.subheader("📥 Download file for analysis:")
        st.write('')

        # Handle file upload
        uploaded_file = st.file_uploader("📄 Select Visual Matrix output CSV to analyze", type="csv")

        # Handle demo file button
        use_demo = st.button("📂 Use Demo File")

        # Logic to handle file selection
        if use_demo:
            # Reset uploaded file state
            st.session_state.uploaded_file = None
            st.session_state.use_demo = True
            st.session_state.generated_graph = None  # Reset the graph

            # Load demo file
            # Example demo DataFrame
            demo_data_path = 'Company Revenue Report Demo.csv'
            df = pd.read_csv(demo_data_path).reset_index(drop=True)
            st.session_state.uploaded_df = df
            st.success("✅ Demo file loaded!")

        elif uploaded_file is not None:
            # Reset demo file state
            st.session_state.use_demo = False
            st.session_state.uploaded_file = uploaded_file
            st.session_state.generated_graph = None  # Reset the graph
            
            # Load uploaded file
            df = pd.read_csv(uploaded_file).reset_index(drop=True)
            st.session_state.uploaded_df_tab1 = df
            st.success("✅ CSV file uploaded and stored!")

        # Ensure only one file source is active
        if st.session_state.use_demo:
            st.info("Using the demo file. Uploading a new file will reset this option.")
        elif st.session_state.uploaded_file:
            st.info("Using the uploaded file. Selecting the demo file will reset this option.")

        # --------- UI OPTIONS ---------
        st.dataframe(st.session_state.uploaded_df)
        if st.session_state.uploaded_df_tab1 is not None:
            st.markdown("---")  # Just a divider line for UX
            st.subheader("🔍 Choose what to graph:")
            st.write('')
            # Checkbox to show original data preview
            st.caption("If viewing the original data will assist in column selection, check box:")
            show_original = st.checkbox("🗃️ Show Original Data", value=False)
            if show_original:
                if "uploaded_df_tab1" in st.session_state:
                    st.subheader("Original Uploaded Data")
                    st.dataframe(st.session_state.uploaded_df_tab1, hide_index=True)
                else:
                    st.warning("No uploaded data available.")

            column_to_graph = st.selectbox(
                "Which data column do you want to analyze?",
                options=[col for col in st.session_state.uploaded_df_tab1.columns if col not in ["CompanyName", "CompanyCode"]],
            )

            sort_order = st.selectbox("Sort order?", options=["Descending", "Ascending"])
            ascending = sort_order == "Ascending"

            if st.button("📊 Generate Graph"):
                # Reset the Excel bytes in session state
                st.session_state.excel_bytes = None  # Clear the previous Excel file

                df = st.session_state.uploaded_df_tab1.copy()
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
                st.session_state.generated_graph = fig  # Store the graph in session state

            # Display the graph if it exists in session state
            if "generated_graph" in st.session_state and st.session_state.generated_graph is not None:
                st.plotly_chart(st.session_state.generated_graph, use_container_width=True)

            if st.session_state.filtered_df is not None:
                st.markdown("---")  # Just a divider line for UX
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

with tab2:

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.header("Multi CSV Analysis by Date")
        st.markdown("---")  # Just a divider line for UX
        # --------- FILE UPLOADER ---------
        st.subheader("📥 Download multiple files for analysis:")
        st.write('Minimum of 2 files must be loaded & file names must contain either "YYYY-MM" or "YYYY-MM-DD"')

        # Add a unique key for the file uploader
        file_uploader_key = "file_uploader_default"

        use_demo = st.button("📂 Use Demo Files")

        if use_demo:
            # Reset uploaded files state
            st.session_state.uploaded_data = {}  # Clear any previously uploaded files
            st.session_state.use_demo = True  # Mark demo mode as active
            file_uploader_key = "file_uploader_reset"  # Change the key to reset the file uploader
            successful_uploads = []  # List to store successfully uploaded filenames

            # Load demo files
            demo_files = {
                "2024-01 Company Revenue Report.csv": "2024-01 Company Revenue Report.csv",
                "2024-02 Company Revenue Report.csv": "2024-02 Company Revenue Report.csv",
                "2024-03 Company Revenue Report.csv": "2024-03 Company Revenue Report.csv",
                "2025-01 Company Revenue Report.csv": "2025-01 Company Revenue Report.csv",
                "2025-02 Company Revenue Report.csv": "2025-02 Company Revenue Report.csv",
                "2025-03 Company Revenue Report.csv": "2025-03 Company Revenue Report.csv",
            }
            for filename, path in demo_files.items():
                date_match_ymd = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                date_match_ym = re.search(r"(\d{4}-\d{2})", filename)
                if date_match_ymd:
                    extracted_date = date_match_ymd.group(1)
                elif date_match_ym:
                    extracted_date = date_match_ym.group(1)
                else:
                    extracted_date = None
                    st.warning(f"⚠️ Could not extract date from filename: {filename} (demo file).")
                    continue
                try:
                    df = pd.read_csv(path)
                    st.session_state.uploaded_data[filename] = {"df": df, "date": extracted_date}
                    successful_uploads.append(filename)  # Add to the list of successful uploads
                except Exception as e:
                    st.error(f"🚨 Error reading demo file '{filename}': {e}")

            # Display a single success message with the total count of uploaded files
            if successful_uploads:
                success_message = f"✅ **{len(successful_uploads)} Demo files successfully uploaded:**\n\n" + "\n".join(f"- {file}" for file in successful_uploads)
                st.markdown(success_message)

        # File uploader with dynamic key
        uploaded_files = st.file_uploader(
            "📄 Select Multiple Visual Matrix output CSVs to analyze",
            type="csv",
            accept_multiple_files=True,
            key=file_uploader_key,  # Use the dynamic key
        )

        if uploaded_files:
            # Reset demo file state
            st.session_state.use_demo = False  # Mark demo mode as inactive
            st.session_state.uploaded_data = {}  # Clear any previously loaded demo files

            successful_uploads = []  # List to store successfully uploaded filenames

            for uploaded_file in uploaded_files:
                filename = uploaded_file.name
                date_match_ymd = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                date_match_ym = re.search(r"(\d{4}-\d{2})", filename)

                if date_match_ymd:
                    extracted_date = date_match_ymd.group(1)
                elif date_match_ym:
                    extracted_date = date_match_ym.group(1)
                else:
                    extracted_date = None
                    st.warning(f"⚠️ Could not extract date from filename: {filename}. This file will not be used for the time-based graph.")
                    continue

                try:
                    df = pd.read_csv(uploaded_file).reset_index(drop=True)
                    st.session_state.uploaded_data[filename] = {"df": df, "date": extracted_date}
                    successful_uploads.append(filename)  # Add to the list of successful uploads
                except Exception as e:
                    st.error(f"🚨 Error reading CSV file '{filename}': {e}")

            # Display a single success message with the total count of uploaded files
            if successful_uploads:
                success_message = f"✅ **{len(successful_uploads)} files successfully uploaded:**\n\n" + "\n".join(f"- {file}" for file in successful_uploads)
                st.markdown(success_message)

        # --------- UI OPTIONS ---------
        if len(st.session_state.uploaded_data) >= 2:
            st.markdown("---")  # Divider line for UX
            st.subheader("🔍 Data references for graph:")
            st.write("")

            all_columns = set()
            for file_data in st.session_state.uploaded_data.values():
                if 'df' in file_data:
                    all_columns.update(file_data['df'].columns)

            if all_columns:
                # Filter out potential non-data columns (you might need to adjust this list)
                valid_columns = [col for col in all_columns if col not in ["CompanyName", "CompanyCode"]]
                if valid_columns:
                    column_to_graph = st.selectbox(
                        "Which data column do you want to analyze?",
                        options=valid_columns,
                    )

                    if st.button("📊 Create Graph"):
    
                        # Reset the Excel bytes in session state
                        st.session_state.excel_bytes = None  # Clear the previous Excel file

                        graph_data = []
                        for filename, data in st.session_state.uploaded_data.items():
                            if 'df' in data and 'date' in data and data['date'] and column_to_graph in data['df'].columns:
                                summed_value = data['df'][column_to_graph].sum()
                                graph_data.append({"Date": data['date'], "Summed Value": summed_value, "Filename": filename})

                        if graph_data:
                            comparison_df_time = pd.DataFrame(graph_data)
                            comparison_df_time = comparison_df_time.sort_values(by="Date")
                            # Store filtered for Excel export
                            st.session_state.comparison_df_time = comparison_df_time

                            # Bar Chart
                            fig_bar = px.bar(
                                comparison_df_time,
                                x="Date",  # Use Date as the x-axis
                                y="Summed Value",
                                title=f"Comparison of {column_to_graph} Sum Over Time",
                                labels={"Summed Value": f"Sum of {column_to_graph}"},
                                color="Filename",  # Differentiate bars by file
                            )

                            # Update layout to ensure no gaps for missing dates
                            fig_bar.update_layout(
                                xaxis=dict(
                                    type="category",  # Treat the x-axis as categorical
                                    categoryorder="array",  # Ensure the order matches the data
                                    categoryarray=comparison_df_time['Date'].tolist(),  # Dynamically set the order of dates
                                ),
                                yaxis_title=f"Sum of {column_to_graph}",
                                xaxis_tickangle=-45,
                                showlegend=False,  # Hide the legend completely
                            )

                            st.plotly_chart(fig_bar, use_container_width=True)

                            
                            # Ensure the Date column is treated as a string (categorical)
                            comparison_df_time['Date'] = comparison_df_time['Date'].astype(str)

                            # Sort by Date to ensure the points are ordered
                            comparison_df_time = comparison_df_time.sort_values(by="Date")

                            # Create the scatter plot with the correct color (Plotly automatically handles this)
                            fig_line = px.scatter(
                                comparison_df_time,
                                x="Date",
                                y="Summed Value",
                                title=f"Trend of {column_to_graph} Sum Over Time",
                                labels={"Summed Value": f"Sum of {column_to_graph}"},
                                color="Filename",  # Separate lines for each file, Plotly handles colors
                            )

                            # Add the connecting line manually, ensuring the same color for the line and markers
                            for trace in fig_line.data:
                                trace.marker.color = trace.line.color  # Ensure marker color matches the line color

                            # Add the connecting line manually
                            fig_line.add_trace(go.Scatter(
                                x=comparison_df_time['Date'],
                                y=comparison_df_time['Summed Value'],
                                mode='lines+markers',  # Connect the dots with lines and show markers
                                line=dict(shape='linear', color="skyblue"),  # Use color from first trace
                                marker=dict(color=fig_line.data[0].marker.color),  # Use color from first trace
                                showlegend=False,  # Hide legend for the lines (or customize as needed)
                            ))

                            # Update layout to treat x-axis as categorical
                            fig_line.update_layout(
                                xaxis=dict(
                                    type="category",  # Make the x-axis categorical (no date gaps)
                                    categoryorder="array",  # Ensure the order matches the data
                                    categoryarray=comparison_df_time['Date'].tolist(),  # Explicitly set the order of categories
                                    tickmode='array',
                                    tickvals=comparison_df_time['Date'].tolist(),  # Only show ticks for actual dates
                                    ticktext=comparison_df_time['Date'].tolist(),  # Display actual dates as tick labels
                                ),
                                yaxis_title=f"Sum of {column_to_graph}",
                                xaxis_tickangle=-45,
                                showlegend=False,  # Hide the legend completely
                            )

                            st.plotly_chart(fig_line, use_container_width=True)

                            # Extract the month name and year from the Date column
                            comparison_df_time['Month'] = pd.to_datetime(comparison_df_time['Date']).dt.strftime('%B')  # Extract month name
                            comparison_df_time['Year'] = pd.to_datetime(comparison_df_time['Date']).dt.year  # Extract year for coloring

                            # Dynamically sort by Month based on the data present
                            unique_months = comparison_df_time['Month'].unique()
                            comparison_df_time['Month'] = pd.Categorical(comparison_df_time['Month'], categories=unique_months, ordered=True)
                            comparison_df_time = comparison_df_time.sort_values(by="Month")

                            # Create the scatter plot with Month as the x-axis
                            fig_line = px.scatter(
                                comparison_df_time,
                                x="Month",  # Use Month as the x-axis
                                y="Summed Value",
                                title=f"Comparison of {column_to_graph} by Month",
                                labels={"Summed Value": f"Sum of {column_to_graph}"},
                                color="Year",  # Differentiate points by year
                            )

                            # Add connecting lines for each year
                            for year in comparison_df_time['Year'].unique():
                                year_data = comparison_df_time[comparison_df_time['Year'] == year]
                                fig_line.add_trace(go.Scatter(
                                    x=year_data['Month'],
                                    y=year_data['Summed Value'],
                                    mode='lines+markers',
                                    name=f"{year}",  # Legend entry for the year
                                    line=dict(shape='linear'),
                                    marker=dict(size=8),
                                ))

                            # Update layout to ensure proper spacing and ordering
                            fig_line.update_layout(
                                xaxis=dict(
                                    categoryorder="array",  # Ensure months are ordered correctly
                                    categoryarray=unique_months,  # Dynamically set the order of months
                                ),
                                yaxis_title=f"Sum of {column_to_graph}",
                                xaxis_tickangle=-45,
                                showlegend=True,  # Show legend to differentiate years
                                coloraxis_showscale=False  # Disable the color bar
                            )

                            st.plotly_chart(fig_line, use_container_width=True)


                    if st.session_state.comparison_df_time is not None:
                        st.markdown("---")  # Just a divider line for UX
                        
                        st.subheader("🚀 View and export filtered data options:")

                        col1, col2 = st.columns(2)
                            
                        with col1:
                            st.write('')
                        
                            # Checkbox to show processed subset preview
                            show_calc_val = st.checkbox("🔬 Show Calculated Data", value=False)
                            if show_calc_val:
                                st.subheader("Calculated Sums")
                                # Display the DataFrame with Date, Summed Value, and Filename
                                st.dataframe(st.session_state.comparison_df_time, hide_index=True)
                                
                        with col2:
                            st.write('')
                            if st.button("💾 Export Calculated Data to Excel"):
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    st.session_state.comparison_df_time.to_excel(writer, index=False, sheet_name="Calculated Data")
                                output.seek(0)
                                st.session_state.excel_bytes = output
                                st.success("✅ Calculated data converted to Excel file!")

                            if st.session_state.excel_bytes:
                                if st.download_button(
                                    label="⬇️ Download Calculated Data as Excel",
                                    data=st.session_state.excel_bytes,
                                    file_name="estestyle_calculated_data.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                ):
                                    st.success("✅ Excel file downloaded!")
            else:
                st.warning("⚠️ No valid columns found in the uploaded files to analyze (excluding 'CompanyName' and 'CompanyCode').")
