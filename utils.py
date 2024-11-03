import pandas as pd
from scipy.stats import zscore

def join_data(qualtrics_data, devpost_data):

    qualtrics_data = qualtrics_data.iloc[:, -5:].iloc[2:]

    qualtrics_data["Team"] = qualtrics_data.apply(lambda x: x["Q8"].split(" | ")[-1].strip(), axis=1)
    qualtrics_data["ID"] = qualtrics_data.apply(lambda x: x["Q8"].split(" | ")[0].strip(), axis=1).astype(int)

    qualtrics_data.drop('Q8', axis=1, inplace=True)

    qualtrics_data.rename(columns=
                        {'Name': 'Judge', 
                        'Score_1': 'Technical',
                        'Score_2': 'Novelty',
                        'Score_3': 'Viability'}, inplace=True)

    qualtrics_data = qualtrics_data.loc[:,["ID", "Team", "Judge", "Technical", "Novelty", "Viability"]].sort_values(by="ID").reset_index(drop=True)

    judging_data = pd.merge(qualtrics_data, devpost_data, on="ID", how="inner")

    judging_data.rename(columns=
                        {'Team_x': 'Team', "Track Name": "Track"}, inplace=True)

    judging_data.drop('Team_y', axis=1, inplace=True)

    judging_data = judging_data.loc[:,["ID", "Team", "Track", "Judge", "Technical", "Novelty", "Viability"]].sort_values(by="ID").reset_index(drop=True)

    judging_data["Technical"] = judging_data["Technical"].astype(float)
    judging_data["Novelty"] = judging_data["Novelty"].astype(float)
    judging_data["Viability"] = judging_data["Viability"].astype(float)

    return judging_data
    

# Step 1: Load the CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Step 2: Normalize Judge Scores within each judge
def normalize_scores(df):
    # Z-score normalization per judge per track
    print("Inside normalize_scores")

    norm_df = df.copy()

    print("Copied df")

    for judge in df['Judge'].unique():
        judge_df = df[df['Judge'] == judge]
        print(judge_df)
        norm_df.loc[df['Judge'] == judge, ['Technical', 'Novelty', 'Viability']] = judge_df[['Technical', 'Novelty', 'Viability']].apply(zscore)
    return norm_df

# Step 3: Average normalized scores by team and calculate the average Z-score
def average_team_scores(norm_df):
    # Group by team and calculate the mean across normalized scores
    team_scores = norm_df.groupby(['Track', 'Team'])[['Technical', 'Novelty', 'Viability']].mean()
    # Add an average Z-score column
    team_scores['Average_Z_score'] = team_scores.mean(axis=1)
    return team_scores.reset_index()

# Step 4: Rank teams within each track
def rank_teams_by_track(averaged_scores):
    averaged_scores['Rank'] = averaged_scores.groupby('Track')['Average_Z_score'].rank(ascending=False)
    return averaged_scores

# Step 5: Identify top n teams per track and flag judges
def identify_top_n_teams(df, norm_df, n=3):
    # Select the top n teams per track
    top_teams = df[df['Rank'] <= n]
    top_team_judges = []

    print(top_teams)
    
    for _, row in top_teams.iterrows():
        # Find the judges who evaluated each top team
        team_name = row['Team']
        track_name = row['Track']
        judges = norm_df[(norm_df['Team'] == team_name) & (norm_df['Track'] == track_name)]['Judge'].unique()
        top_team_judges.append({
            'Track': track_name,
            'Team': team_name,
            'Average_Z_score': row['Average_Z_score'],
            'Rank': row['Rank'],
            'Judges': ', '.join(judges)
        })
        
    top_teams_df = pd.DataFrame(top_team_judges)
    top_teams_df = top_teams_df.sort_values(by=['Track', 'Rank']).reset_index(drop=True)
    
    return top_teams_df

# Main function to run the full process
def process_hackathon_results(file_path, top_n=3):

    print("Inside process_hackathon_results")

    print("Processing file:", file_path)
    # Load the data
    df = file_path

    print("Dataframe shape:", df.shape)
    
    # Normalize scores per judge
    norm_df = normalize_scores(df)

    print("Normalized DataFrame shape:", norm_df.shape)

    print(norm_df)
    
    # Average normalized scores by team
    avg_scores = average_team_scores(norm_df)

    print("Averaged scores DataFrame shape:", avg_scores.shape)
    
    # Rank teams within their track
    ranked_teams = rank_teams_by_track(avg_scores)

    print("Ranked teams DataFrame shape:", ranked_teams.shape)

    
    # Identify top n teams and their judges
    top_teams_df = identify_top_n_teams(ranked_teams, norm_df, n=top_n)

    print("Top teams DataFrame shape:", top_teams_df.shape)
    
    # Output the ranked teams and top teams information
    return ranked_teams, top_teams_df
