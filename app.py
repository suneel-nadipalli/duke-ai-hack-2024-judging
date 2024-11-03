import streamlit as st
from utils import *
from pathlib import Path

st.title("Hackathon Results")

# File uploader
files = st.file_uploader("Upload your hackathon scores CSV file", type="csv", accept_multiple_files=True)

# Number of top teams to display
top_n = st.number_input("Number of top teams per track to display:", min_value=1, value=3, step=1)

print("Top N:", top_n)

# Process the file if uploaded
if len(files) > 0:
    dfs = { Path(file.name).stem: pd.read_csv(file) for file in files }

    judging_df = join_data(dfs['qualtrics'], dfs['devpost'])

    try:
        _, res_df = process_hackathon_results(judging_df, top_n=top_n)

        print("Top teams DataFrame shape:", res_df.shape)
        
        # Display the top teams DataFrame
        st.subheader("Top Teams per Track")
        st.dataframe(res_df)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")