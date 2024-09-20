import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="RAGA",
    page_icon="☣",
    layout="centered",
)

st.title("Cyber Risk Insight")
st.subheader("Upload your data, select specific risks, and uncover critical insights")

st.sidebar.title("Instructions")
st.sidebar.info("1. Upload a CSV file with risk data.\n"
                "2. Select risks to analyze.\n"
                "3. View risk assessment breakdown.")

uploaded_file = st.file_uploader("Upload CSV with Risk Data", type=["csv"])

selected_risks = []
df = None

def extract_risk_ratings(text):
    ratings = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}

    matches = re.findall(r'(Critical|High|Medium|Low)', text)

    for match in matches:
        if match in ratings:
            ratings[match] += 1

    return ratings

if uploaded_file:
    try:

        df = pd.read_csv(uploaded_file)

        if 'risks' in df.columns:
            risks = df['risks'].unique().tolist()

            st.sidebar.subheader("Select Risks to Analyze")
            select_all = st.sidebar.checkbox("Select All Risks")

            if select_all:
                selected_risks = st.sidebar.multiselect("Choose Risks", risks, default=risks)
            else:
                selected_risks = st.sidebar.multiselect("Choose Risks", risks)

            if selected_risks:

                st.write(f"*Selected Risks:* {', '.join(selected_risks)}")

                risks_description = "\n".join([f"- {risk}" for risk in selected_risks])
                prompt = f"Analyze the following risks and provide a detailed cybersecurity risk assessment. "\
                         f"For each risk, categorize it explicitly as 'Critical', 'High', 'Medium', or 'Low' using the format: 'Risk: Level'. "\
                         f"Here are the risks:\n{risks_description}"

                with st.spinner("Generating risk analysis..."):
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a cybersecurity risk analyst and perform risk assessment."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.5,
                    )

                analysis = response.choices[0].message['content'].strip()
                st.markdown("### Risk Analysis Summary")
                st.write(analysis)

                ratings = extract_risk_ratings(analysis)

                if sum(ratings.values()) > 0:

                    labels = list(ratings.keys())
                    sizes = list(ratings.values())
                    colors = ['#FF4C4C', '#FFA500', '#FFD700', '#98FB98']

                    fig, ax = plt.subplots()
                    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                    ax.axis('equal')

                    st.markdown("### Risk Rating Distribution")
                    st.pyplot(fig)
                else:
                    st.warning("No risk ratings found in the analysis. Make sure the API response contains the expected 'Critical', 'High', 'Medium', or 'Low' labels.")

            else:
                st.info("Please select at least one risk to analyze.")

        else:
            st.error("The uploaded file does not contain a 'risks' column.")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload a CSV file to proceed.")
