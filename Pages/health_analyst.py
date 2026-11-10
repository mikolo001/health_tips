
# pages/health_analyst.py
import streamlit as st
import pandas as pd
import plotly.express as px

from config import client, MODEL_NAME

st.title("📊 Health Data Analyst")

st.write(
    "Upload a health dataset to explore data quality, "
    "statistics, visualisations, and an AI-assisted report."
)

st.info(
    "Use authorised, de-identified data. Avoid uploading names, "
    "phone numbers, patient IDs, or other identifying information. "
    "Aggregated analysis is not a medical diagnosis."
)

# ==========================================
# 1. UPLOAD DATA
# ==========================================

uploaded_file = st.file_uploader(
    "Upload a health dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.markdown("### What you can analyse")
    st.markdown(
        """
        - Patient age and demographic distributions
        - Health measurements and laboratory values
        - Missing values and duplicate records
        - Numerical relationships and trends
        - Summary reports for research and education
        """
    )
    st.stop()

# ==========================================
# 2. READ THE FILE
# ==========================================

try:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as error:
    st.error("Unable to read this file.")
    st.caption(str(error))
    st.stop()

if df.empty:
    st.error("The uploaded dataset contains no records.")
    st.stop()

# ==========================================
# 3. DATASET OVERVIEW
# ==========================================

st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{len(df.columns):,}")
col3.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
col4.metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")

st.subheader("Data Preview")
st.dataframe(df.head(10), use_container_width=True)

# ==========================================
# 4. DATA QUALITY
# ==========================================

st.subheader("Data Quality Report")

quality = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [str(dtype) for dtype in df.dtypes],
    "Missing Values": df.isna().sum().values,
    "Missing (%)": (
        df.isna().mean().values * 100
    ).round(2),
    "Unique Values": df.nunique(dropna=True).values
})

st.dataframe(quality, use_container_width=True)

# ==========================================
# 5. NUMERICAL STATISTICS
# ==========================================

numeric_df = df.select_dtypes(include="number")

st.subheader("Numerical Summary")

if not numeric_df.empty:
    st.dataframe(
        numeric_df.describe().T.round(3),
        use_container_width=True
    )
else:
    st.info("No numerical columns were detected.")

# ==========================================
# 6. COLUMN EXPLORER
# ==========================================

st.subheader("Explore a Column")

column = st.selectbox(
    "Choose a column",
    df.columns.tolist()
)

selected_series = df[column]

if pd.api.types.is_numeric_dtype(selected_series):
    fig = px.histogram(
        df,
        x=column,
        title=f"Distribution of {column}",
        marginal="box"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    value_counts = (
        selected_series
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(20)
        .rename_axis(column)
        .reset_index(name="Count")
    )

    fig = px.bar(
        value_counts,
        x=column,
        y="Count",
        title=f"Most common values in {column}"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 7. CORRELATION ANALYSIS
# ==========================================

st.subheader("Numerical Correlations")

if numeric_df.shape[1] >= 2:
    correlation = numeric_df.corr()

    fig = px.imshow(
        correlation,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Matrix",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Correlation does not establish causation. "
        "Associations may be influenced by missing data, "
        "confounding variables, or the dataset's sampling method."
    )
else:
    st.info("At least two numerical columns are needed.")

# ==========================================
# 8. PREPARE A PRIVACY-MINIMISED SUMMARY
# ==========================================

def build_dataset_summary(data):
    """Create aggregate statistics without sending individual rows."""

    summary = {
        "number_of_rows": len(data),
        "number_of_columns": len(data.columns),
        "duplicate_rows": int(data.duplicated().sum()),
        "columns": {}
    }

    for col in data.columns:
        series = data[col]

        column_info = {
            "data_type": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_percentage": round(
                float(series.isna().mean() * 100), 2
            ),
            "unique_values": int(series.nunique(dropna=True))
        }

        if pd.api.types.is_numeric_dtype(series):
            values = series.dropna()

            if not values.empty:
                column_info["statistics"] = {
                    "mean": round(float(values.mean()), 3),
                    "median": round(float(values.median()), 3),
                    "standard_deviation": round(
                        float(values.std()), 3
                    ) if len(values) > 1 else None,
                    "minimum": round(float(values.min()), 3),
                    "maximum": round(float(values.max()), 3)
                }

        summary["columns"][str(col)] = column_info

    return summary


# ==========================================
# 9. AI REPORT GENERATION
# ==========================================

st.divider()
st.subheader("Generate an AI Analysis Report")

report_model = st.selectbox(
    "Report model",
    [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b"
    ],
    key="analyst_model"
)

report_context = st.text_area(
    "Research question or analysis objective",
    placeholder=(
        "Example: Examine missing data, age distribution, "
        "and relationships between the available measurements."
    )
)

if st.button("Generate Analysis Report", type="primary"):

    if not report_context.strip():
        st.warning("Please describe the purpose of your analysis.")

    else:
        summary = build_dataset_summary(df)

        instructions = """
        You are a careful health data analyst.

        Produce a structured analytical report using only the
        supplied aggregate dataset summary and the user's objective.

        Include:
        1. Executive summary
        2. Dataset overview
        3. Data quality and missingness
        4. Key descriptive statistics
        5. Relevant observations and limitations
        6. Recommendations for further analysis

        RULES:
        - Use only statistics explicitly supplied in the summary.
        - Do not invent numbers, trends, relationships, or test results.
        - The supplied summary does not include raw individual records.
        - Do not claim to have performed statistical significance tests.
        - Do not diagnose individuals or recommend treatment.
        - Distinguish observations from hypotheses.
        - Explain that correlation does not prove causation.
        - If the evidence is insufficient, state that clearly.
        - Avoid presenting descriptive statistics as clinical conclusions.
        """

        with st.spinner("Analysing the dataset summary..."):
            try:
                response = client.responses.create(
                    model=report_model,
                    instructions=instructions,
                    input=(
                        "Analysis objective:\n"
                        + report_context
                        + "\n\nAggregate dataset summary:\n"
                        + pd.Series(
                            [summary]
                        ).to_json(
                            orient="values",
                            force_ascii=False
                        )
                    )
                )

                report = response.output_text

                if report:
                    st.session_state["latest_health_report"] = report
                    st.session_state["latest_report_filename"] = (
                        uploaded_file.name.rsplit(".", 1)[0]
                    )
                else:
                    st.error("The model returned an empty report.")

            except Exception as error:
                st.error("Report generation failed.")
                st.caption(str(error))

# ==========================================
# 10. DISPLAY AND DOWNLOAD REPORT
# ==========================================

if st.session_state.get("latest_health_report"):

    st.subheader("Analysis Report")

    st.markdown(
        st.session_state["latest_health_report"]
    )

    st.download_button(
        "Download Report (Markdown)",
        data=st.session_state["latest_health_report"],
        file_name=(
            st.session_state.get(
                "latest_report_filename",
                "health_analysis"
            ) + "_report.md"
        ),
        mime="text/markdown"
    )