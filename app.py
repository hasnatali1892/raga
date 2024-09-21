import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import re

# Set the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit page configuration
st.set_page_config(
    page_title="RAGA",
    page_icon="☣",
    layout="centered",
)

# Main title and subheader
def display_header():
    """
    Display the main title and sidebar instructions.
    """
    st.title("IT Risk Assessment with Generative AI (IT-RAGA)")
    st.subheader("Upload your data, select specific risks, and uncover critical insights")
    st.title("Instructions")
    st.info("1. Upload a CSV file with risk data.\n"
            "2. Select risks to analyze.\n"
            "3. View risk assessment breakdown.")

# Upload and read CSV
def upload_file():
    """
    Upload and process a CSV file containing risk data.
    Ensure the file contains a 'risks' column.
    """
    st.subheader("Step 1: Upload CSV with Risk Data")
    uploaded_file = st.file_uploader("Upload CSV with Risk Data", type=["csv"])
    if uploaded_file:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            # Check if the 'risks' column exists
            if 'risks' not in df.columns:
                st.error("The uploaded file does not contain a 'risks' column.")
                return None
            return df
        except Exception as e:
            # Display an error if something goes wrong while processing the file
            st.error(f"An error occurred while processing the file: {e}")
            return None
    else:
        st.info("Please upload a CSV file to proceed.")
        return None

# Sidebar to select risks using checkboxes
def select_risks(df):
    """
    Display a sidebar allowing the user to select risks to analyze using checkboxes.
    Each risk will have its own checkbox.
    """
    risks = df['risks'].unique().tolist()
    st.subheader("Step 2: Select Risks to Analyze")
    selected_risks = []
    select_all = st.checkbox("Select All Risks")

    # Create a checkbox for each risk
    for risk in risks:
        if select_all:
            # Automatically select all risks if 'Select All' is checked
            checked = True
        else:
            checked = False

        if st.checkbox(risk, value=checked):
            selected_risks.append(risk)

    if not selected_risks:
        st.info("Please select at least one risk to analyze.")

    return selected_risks

# Extract risk ratings (Critical, High, Medium, Low) from the analysis
def extract_risk_ratings(text):
    """
    Extract risk ratings such as Critical, High, Medium, and Low
    from the text generated by the AI model.
    """
    ratings = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    # Use regular expressions to find the occurrence of these risk levels in the text
    matches = re.findall(r'\b(Critical|High|Medium|Low)\b', text)
    for match in matches:
        if match in ratings:
            ratings[match] += 1
    return ratings

# Call OpenAI API to generate the risk analysis
def generate_risk_analysis(selected_risks):
    """
    Send the selected risks to the OpenAI API and generate a risk analysis.
    The analysis categorizes risks into Critical, High, Medium, and Low.
    """
    risks_description = "\n".join([f"- {risk}" for risk in selected_risks])
    prompt = (f"Analyze the following risks and write a detailed cybersecurity risk statement. "
              f"For each risk, categorize it explicitly as 'Critical', 'High', 'Medium', or 'Low' "
              f"using the format: 'Risk: Level', and provide a cybersecurity risk treatment. "
              f"Here are the risks:\n{risks_description}")

    with st.spinner("Generating risk analysis..."):
        # Call the OpenAI API to get the risk analysis
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity risk analyst and perform risk assessment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.5,
        )

    # Get the response from the API
    analysis = response.choices[0].message['content'].strip()
    return analysis

# Display pie chart of risk ratings
def display_pie_chart(ratings):
    """
    Display a pie chart showing the distribution of the extracted risk ratings.
    """
    if sum(ratings.values()) > 0:
        labels = list(ratings.keys())
        sizes = list(ratings.values())
        colors = ['#FF4C4C', '#FFA500', '#FFD700', '#98FB98']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.markdown("### Risk Rating Distribution")
        st.pyplot(fig)
    else:
        st.warning("No risk ratings found in the analysis. Make sure the API response contains the expected 'Critical', 'High', 'Medium', or 'Low' labels.")

# Main function to run the app
def main():
    """
    Main function to execute the Streamlit app.
    It covers file upload, risk selection, risk analysis generation,
    and visual representation of risk ratings.
    """
    display_header()

    # Step 1: File Upload
    df = upload_file()
    if df is not None:
        # Step 2: Risk Selection
        selected_risks = select_risks(df)

        if selected_risks:
            # Step 3: Analyze button
            if st.button("Analyze Selected Risks"):
                # Step 4: Generate Risk Analysis
                analysis = generate_risk_analysis(selected_risks)
                st.markdown("### Step 3: Risk Analysis Summary")
                st.write(analysis)

                # Step 5: Extract and Display Risk Ratings
                ratings = extract_risk_ratings(analysis)
                display_pie_chart(ratings)

# Run the app
if __name__ == "__main__":
    main()
