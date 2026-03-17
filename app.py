import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CrewCommute", layout="wide")

st.title("CrewCommute")
st.subheader("Airline Crew Commuter Risk & Reliability Dashboard")
st.write(
    "A prototype tool to help airline crew members evaluate commute reliability, "
    "overnight backup planning, and report-time risk before duty."
)

st.divider()

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Commute Planning Inputs")

origin = st.sidebar.text_input("Origin City / Airport", "ATL")
destination = st.sidebar.text_input("Base City / Airport", "CLT")

commute_mode = st.sidebar.selectbox(
    "Primary Commute Mode",
    ["Flight", "Drive", "Train", "Mixed"]
)

report_time = st.sidebar.selectbox(
    "Report Time Window",
    ["Early Morning", "Midday", "Afternoon", "Evening", "Late Night"]
)

backup_option = st.sidebar.selectbox(
    "Backup Plan Available?",
    ["Yes", "No"]
)

overnight_option = st.sidebar.selectbox(
    "Arrive the Night Before?",
    ["Yes", "No"]
)

flight_load_factor = st.sidebar.slider("Expected Flight Fullness / Seat Competition", 0, 100, 70)
weather_risk = st.sidebar.slider("Weather / Disruption Risk", 0, 100, 30)
traffic_risk = st.sidebar.slider("Traffic / Ground Delay Risk", 0, 100, 20)
sleep_hours = st.sidebar.slider("Sleep Before Commute", 0, 12, 7)
buffer_hours = st.sidebar.slider("Time Buffer Before Report", 0, 24, 5)
nonrev_priority = st.sidebar.slider("Non-Rev Priority Strength", 0, 100, 50)

# -----------------------------
# Risk Calculation
# -----------------------------
def calculate_commute_score(
    commute_mode,
    report_time,
    backup_option,
    overnight_option,
    flight_load_factor,
    weather_risk,
    traffic_risk,
    sleep_hours,
    buffer_hours,
    nonrev_priority
):
    score = 50

    # Commute mode effects
    if commute_mode == "Flight":
        score -= 10
    elif commute_mode == "Drive":
        score += 5
    elif commute_mode == "Train":
        score += 2
    elif commute_mode == "Mixed":
        score -= 5

    # Report time effects
    if report_time == "Early Morning":
        score -= 12
    elif report_time == "Midday":
        score += 6
    elif report_time == "Afternoon":
        score += 4
    elif report_time == "Evening":
        score += 2
    elif report_time == "Late Night":
        score -= 4

    # Backup / overnight planning
    if backup_option == "Yes":
        score += 12
    else:
        score -= 12

    if overnight_option == "Yes":
        score += 15
    else:
        score -= 8

    # Operational factors
    score -= flight_load_factor * 0.18
    score -= weather_risk * 0.20
    score -= traffic_risk * 0.12

    # Personal readiness
    score += sleep_hours * 2
    score += buffer_hours * 2.5
    score += nonrev_priority * 0.10

    score = max(0, min(100, round(score, 1)))
    return score

score = calculate_commute_score(
    commute_mode,
    report_time,
    backup_option,
    overnight_option,
    flight_load_factor,
    weather_risk,
    traffic_risk,
    sleep_hours,
    buffer_hours,
    nonrev_priority
)

# -----------------------------
# Risk Level + Recommendation
# -----------------------------
def classify_commute(score):
    if score >= 75:
        return "LOW RISK", "Strong commute plan. Reliability looks solid for report time."
    elif score >= 50:
        return "MODERATE RISK", "Plan is workable, but backup planning is recommended."
    elif score >= 30:
        return "HIGH RISK", "Commute plan is vulnerable. Consider earlier travel or overnight stay."
    else:
        return "CRITICAL RISK", "Serious risk of misconnect, delay, or missed report. Rebuild this plan."

risk_level, summary = classify_commute(score)

def recommendation_engine(score, backup_option, overnight_option, weather_risk, flight_load_factor):
    actions = []

    if score < 50:
        actions.append("Increase your report-time buffer.")
    if backup_option == "No":
        actions.append("Add a same-day or alternate backup option.")
    if overnight_option == "No":
        actions.append("Consider arriving the night before duty.")
    if weather_risk > 60:
        actions.append("Monitor weather closely and move to an earlier commute window.")
    if flight_load_factor > 75:
        actions.append("Choose flights with more open-seat probability or multiple backup departures.")
    if not actions:
        actions.append("Your commute setup looks balanced. Maintain the same planning strategy.")

    return actions

recommendations = recommendation_engine(
    score,
    backup_option,
    overnight_option,
    weather_risk,
    flight_load_factor
)

# -----------------------------
# Main Dashboard
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Commute Reliability Score", f"{score}/100")

with col2:
    st.metric("Risk Category", risk_level)

with col3:
    if score >= 75:
        probability = "High probability of successful commute"
    elif score >= 50:
        probability = "Reasonable probability with some vulnerability"
    elif score >= 30:
        probability = "Low probability without stronger backup planning"
    else:
        probability = "Very low probability of safe commute success"
    st.metric("Assessment", probability)

st.divider()

st.subheader("Route Summary")
st.write(f"**Origin:** {origin}")
st.write(f"**Destination/Base:** {destination}")
st.write(f"**Primary Mode:** {commute_mode}")
st.write(f"**Report Window:** {report_time}")
st.write(summary)

st.divider()

st.subheader("Recommended Actions")
for item in recommendations:
    st.write(f"- {item}")

st.divider()

# -----------------------------
# Scenario Comparison
# -----------------------------
st.subheader("Scenario Comparison")

safer_score = min(
    100,
    calculate_commute_score(
        commute_mode,
        report_time,
        "Yes",
        "Yes",
        max(0, flight_load_factor - 15),
        max(0, weather_risk - 10),
        traffic_risk,
        min(12, sleep_hours + 1),
        min(24, buffer_hours + 4),
        min(100, nonrev_priority + 10)
    )
)

current_vs_improved = pd.DataFrame({
    "Scenario": ["Current Plan", "Improved Plan"],
    "Score": [score, safer_score]
})

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(current_vs_improved["Scenario"], current_vs_improved["Score"])
ax.set_ylabel("Reliability Score")
ax.set_title("Commute Plan Comparison")
ax.set_ylim(0, 100)
st.pyplot(fig)

st.divider()

# -----------------------------
# Weekly Commute Outlook
# -----------------------------
st.subheader("5-Day Commute Outlook")

days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
daily_weather = [weather_risk, min(100, weather_risk + 10), max(0, weather_risk - 5), min(100, weather_risk + 15), max(0, weather_risk - 10)]
daily_loads = [flight_load_factor, min(100, flight_load_factor + 8), max(0, flight_load_factor - 6), min(100, flight_load_factor + 12), max(0, flight_load_factor - 5)]

projection_scores = []
for i in range(5):
    projected = calculate_commute_score(
        commute_mode,
        report_time,
        backup_option,
        overnight_option,
        daily_loads[i],
        daily_weather[i],
        traffic_risk,
        sleep_hours,
        buffer_hours,
        nonrev_priority
    )
    projection_scores.append(projected)

outlook_df = pd.DataFrame({
    "Day": days,
    "Projected Score": projection_scores,
    "Weather Risk": daily_weather,
    "Seat Competition": daily_loads
})

st.dataframe(outlook_df, use_container_width=True)

fig2, ax2 = plt.subplots(figsize=(9, 4))
ax2.plot(outlook_df["Day"], outlook_df["Projected Score"], marker="o")
ax2.set_ylabel("Projected Reliability Score")
ax2.set_title("5-Day Crew Commute Outlook")
ax2.set_ylim(0, 100)
st.pyplot(fig2)

st.divider()

# -----------------------------
# Planning Notes
# -----------------------------
st.subheader("Planner Notes")
notes = st.text_area(
    "Add commute notes, backup flights, hotel plans, or personal reminders:",
    "Example: If loads look bad on the morning flight, list on the late-evening arrival the night before."
)

if notes:
    st.success("Notes saved in session for planning review.")

st.divider()

st.caption(
    "Disclaimer: CrewCommute is a planning prototype for personal decision support only. "
    "It does not replace airline policy, crew scheduling procedures, dispatch guidance, or operational control decisions."
)
