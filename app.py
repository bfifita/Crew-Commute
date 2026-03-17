import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CrewCommute", layout="wide")

st.title("CrewCommute")
st.subheader("Airline Crew Commuting Intelligence Platform")
st.write(
    "A prototype tool designed to help airline crew evaluate commuting risk based on "
    "flight load pressure, backup options, delay risk, and report timing."
)

st.divider()

# Sidebar inputs
st.sidebar.header("Commute Scenario Inputs")

standby_load = st.sidebar.slider(
    "Standby Load Pressure (%)",
    min_value=0,
    max_value=100,
    value=65,
    help="Higher values mean a fuller flight and lower standby chances."
)

backup_flights = st.sidebar.slider(
    "Available Backup Flights",
    min_value=0,
    max_value=5,
    value=2,
    help="More backup flights reduce commuting risk."
)

delay_risk = st.sidebar.slider(
    "Delay Risk Level",
    min_value=0,
    max_value=10,
    value=4,
    help="Higher values indicate a greater chance of delay disruption."
)

hours_before_report = st.sidebar.slider(
    "Hours Arriving Before Report Time",
    min_value=0,
    max_value=24,
    value=6,
    help="More buffer before report time reduces risk."
)

connection_required = st.sidebar.selectbox(
    "Commute Type",
    options=["Nonstop", "1 Connection", "2+ Connections"]
)

# Risk scoring logic
risk_score = 0

risk_score += standby_load * 0.4
risk_score += delay_risk * 5

if backup_flights == 0:
    risk_score += 20
elif backup_flights == 1:
    risk_score += 12
elif backup_flights == 2:
    risk_score += 6
else:
    risk_score -= 5

if hours_before_report <= 2:
    risk_score += 20
elif hours_before_report <= 4:
    risk_score += 12
elif hours_before_report <= 6:
    risk_score += 6
else:
    risk_score -= 5

if connection_required == "Nonstop":
    risk_score += 0
elif connection_required == "1 Connection":
    risk_score += 10
else:
    risk_score += 20

risk_score = max(0, min(100, int(risk_score)))

# Risk classification
if risk_score < 35:
    risk_level = "LOW"
    recommendation = "This commute appears relatively safe. Keep monitoring loads and delays."
elif risk_score < 70:
    risk_level = "MODERATE"
    recommendation = "This commute has some risk. Consider taking an earlier flight or identifying stronger backup options."
else:
    risk_level = "HIGH"
    recommendation = "This commute is high risk. A safer strategy would be to commute earlier, reduce connections, or build a larger report-time buffer."

# Layout
col1, col2 = st.columns(2)

with col1:
    st.metric("Commute Risk Score", f"{risk_score}/100")
    st.metric("Risk Level", risk_level)

    st.markdown("### Recommendation")
    st.info(recommendation)

with col2:
    scenario_data = pd.DataFrame({
        "Factor": [
            "Standby Load",
            "Delay Risk",
            "Backup Flights",
            "Arrival Buffer",
            "Connection Complexity"
        ],
        "Impact": [
            standby_load * 0.4,
            delay_risk * 5,
            20 if backup_flights == 0 else 12 if backup_flights == 1 else 6 if backup_flights == 2 else -5,
            20 if hours_before_report <= 2 else 12 if hours_before_report <= 4 else 6 if hours_before_report <= 6 else -5,
            0 if connection_required == "Nonstop" else 10 if connection_required == "1 Connection" else 20
        ]
    })

    fig, ax = plt.subplots()
    ax.bar(scenario_data["Factor"], scenario_data["Impact"])
    ax.set_ylabel("Risk Impact")
    ax.set_title("Commute Risk Drivers")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)

st.divider()

# Scenario comparison
st.markdown("## Scenario Comparison")

comparison_df = pd.DataFrame({
    "Scenario": ["Current Plan", "Earlier Flight Option", "Extra Backup Option"],
    "Estimated Risk Score": [
        risk_score,
        max(0, risk_score - 15),
        max(0, risk_score - 10)
    ]
})

st.dataframe(comparison_df, use_container_width=True)

fig2, ax2 = plt.subplots()
ax2.plot(comparison_df["Scenario"], comparison_df["Estimated Risk Score"], marker="o")
ax2.set_ylabel("Estimated Risk Score")
ax2.set_title("Commuting Scenario Comparison")
st.pyplot(fig2)

st.divider()

# Simple commute planning summary
st.markdown("## Commute Planning Summary")

summary = {
    "Standby Load Pressure": f"{standby_load}%",
    "Backup Flights Available": backup_flights,
    "Delay Risk Level": delay_risk,
    "Arrival Buffer (Hours)": hours_before_report,
    "Commute Type": connection_required,
    "Overall Commute Risk": risk_level
}

summary_df = pd.DataFrame(list(summary.items()), columns=["Category", "Value"])
st.table(summary_df)

st.caption(
    "Disclaimer: CrewCommute is a prototype concept for demonstration purposes only. "
    "It does not use live airline inventory or operational data."
)
