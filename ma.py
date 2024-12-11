import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import requests
import os

# Constants
TARGET_CPA = 50
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Better to store your API key securely

# Define GEMINI API URL (ensure this is the correct endpoint for Gemini API)
GEMINI_API_URL = "https://api.gemini.com/insights"  # Update with the actual URL

# Load dataset
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Preprocess dataset
def preprocess_data(df):
    df.fillna(0, inplace=True)
    df['CTR'] = (df['Clicks'] / df['Impressions']) * 100
    df['CPA'] = df['Spend'] / df['Conversions']
    df['ROAS'] = df['Revenue'] / df['Spend']
    return df

# Analyze campaigns
def analyze_campaigns(df):
    actions = []
    for _, row in df.iterrows():
        action = {'Campaign_ID': row['Campaign_ID'], 'Action': None, 'Reason': None}

        # Pause campaigns
        if row['CTR'] < 1:
            action['Action'] = 'Pause'
            action['Reason'] = 'Low CTR'
        elif row['CPA'] > 3 * TARGET_CPA:
            action['Action'] = 'Pause'
            action['Reason'] = 'High CPA'

        # Increase budget
        elif row['ROAS'] > 4:
            action['Action'] = 'Increase Budget'
            action['Reason'] = 'High ROAS'

        # Decrease budget
        elif row['ROAS'] < 1.5:
            action['Action'] = 'Decrease Budget'
            action['Reason'] = 'Low ROAS'

        # Default
        if action['Action'] is None:
            action['Action'] = 'No Action'
            action['Reason'] = 'Metrics within acceptable range'

        actions.append(action)
    return pd.DataFrame(actions)

# Generate Gemini insights
def generate_insights(campaign_text):
    payload = {
        "text": campaign_text,
        "api_key": GEMINI_API_KEY
    }
    try:
        response = requests.post(GEMINI_API_URL, json=payload)
        response.raise_for_status()  # This will raise an exception for bad HTTP status
        return response.json().get('insights', 'No insights available')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Visualize metrics
def visualize_metrics(df):
    plt.figure(figsize=(10, 6))
    plt.bar(df['Campaign_ID'], df['ROAS'], color='skyblue')
    plt.axhline(y=1.5, color='r', linestyle='--', label='ROAS Threshold')
    plt.xlabel('Campaign ID')
    plt.ylabel('ROAS')
    plt.title('ROAS by Campaign')
    plt.legend()
    return plt  # Return the plot to streamlit

# Streamlit UI
def main():
    st.title("AI Marketing Automation Agent")

    # File upload
    uploaded_file = st.file_uploader("Upload Campaign Data (CSV)", type="csv")

    if uploaded_file:
        # Load and preprocess data
        df = load_data(uploaded_file)
        df = preprocess_data(df)

        # Display data
        st.subheader("Campaign Data")
        st.dataframe(df)

        # Analyze campaigns
        actions = analyze_campaigns(df)
        st.subheader("Campaign Actions")
        st.dataframe(actions)

        # Generate insights
        st.subheader("Generate Insights")
        sample_campaign_text = st.text_input("Enter Campaign Text for Analysis")
        if sample_campaign_text:
            insights = generate_insights(sample_campaign_text)
            st.write("Gemini Insights:", insights)

        # Visualize metrics
        st.subheader("Campaign Metrics Visualization")
        st.pyplot(visualize_metrics(df))  # Directly pass to Streamlit

if __name__ == "__main__":
    main()
