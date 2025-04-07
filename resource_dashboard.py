import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="🏥 Hospital Resource Dashboard", layout="wide")

st.title("🏥 Hospital Resource Optimization Dashboard")
st.markdown("Analyze and monitor resource availability, usage, and critical alerts across departments.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/hospital_resources.csv')
    return df

df = load_data()

# ==================================
# 🎛️ Sidebar Filters (Clean Layout)
# ==================================
with st.sidebar.expander("🎛️ Filter Resources", expanded=True):
    selected_depts = st.multiselect(
        "Select Departments",
        options=df["Department"].unique(),
        default=df["Department"].unique()
    )

    status_options = st.multiselect(
        "Select Status Levels",
        options=df["Status"].unique(),
        default=df["Status"].unique()
    )

# Filter dataset
df_filtered = df[
    (df["Department"].isin(selected_depts)) &
    (df["Status"].isin(status_options))
]

# ===============================
# 📋 Resource Table with Styling
# ===============================
st.subheader("📋 Current Resource Status")

def highlight_status(val):
    color = "red" if val == "Critical" else "orange" if val == "Warning" else "green"
    return f"background-color: {color}; color: white;"

st.dataframe(df_filtered.style.applymap(highlight_status, subset=["Status"]))

# ===========================
# 📤 Export Filtered Table
# ===========================
st.download_button(
    label="📁 Download Filtered Data as CSV",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_resources.csv",
    mime="text/csv"
)

# ========================================
# 📊 Bar Chart: Resources In Use by Dept
# ========================================
st.subheader("📊 Total Resources In Use by Department")
chart_df = df_filtered.groupby("Department")["In Use"].sum().reset_index()

fig = px.bar(
    chart_df,
    x="Department",
    y="In Use",
    color="Department",
    title="Resource Usage by Department",
    labels={"In Use": "Resources in Use"},
)
st.plotly_chart(fig, use_container_width=True)

# ========================================
# 📈 Pie Chart: Status Breakdown
# ========================================
st.subheader("📈 Resource Status Distribution")

status_counts = df_filtered["Status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]

fig2 = px.pie(
    status_counts,
    names="Status",
    values="Count",
    title="Current Resource Status Breakdown",
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(fig2, use_container_width=True)

# ===========================
# 🚨 Critical Resource Alerts
# ===========================
st.subheader("🚨 Critical Resource Alerts")

critical_df = df_filtered[df_filtered["Status"] == "Critical"]

if not critical_df.empty:
    st.error(f"⚠️ {len(critical_df)} critical resources found!")
    st.dataframe(critical_df)
else:
    st.success("✅ No critical resources detected.")
