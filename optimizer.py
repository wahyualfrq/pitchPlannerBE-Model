import pandas as pd
import numpy as np
from datetime import timedelta

def standardize_columns(df):
    """
    Standardize DataFrame columns using dictionary-based fuzzy matching.
    Maps inconsistent column names to standard schema:
    ["Team_A", "Team_B", "Venue", "Date", "Time", "AmPm"]
    """
    col_mapping = {}
    
    for col in df.columns:
        clean_col = str(col).upper().replace(' ', '').replace('_', '').replace('.', '')
        
        if clean_col in ['HOMETEAM', 'TEAM1', 'TEAMA', 'HOME']:
            col_mapping[col] = 'Team_A'
        elif clean_col in ['AWAYTEAM', 'TEAM2', 'TEAMB', 'AWAY']:
            col_mapping[col] = 'Team_B'
        elif clean_col in ['VENUE', 'STADIUM', 'LOCATION', 'GROUND', 'MATCHVENUE']:
            col_mapping[col] = 'Venue'
        elif clean_col in ['DATE', 'MATCHDATE', 'DATETIME', 'STARTDATE']:
            col_mapping[col] = 'Date'
        elif clean_col in ['TIME', 'MATCHTIME', 'STARTTIME']:
            col_mapping[col] = 'Time'
        elif clean_col in ['PM/AM', 'AMPM', 'MERIDIEM']:
            col_mapping[col] = 'AmPm'

    df_renamed = df.rename(columns=col_mapping)
    return df_renamed

def preprocess_data(df):
    """
    Preprocess the raw dataset resiliently.
    Handles column mapping, missing values, and date parsing.
    """
    df_processed = standardize_columns(df.copy())
    
    required_cols = {'Team_A', 'Team_B', 'Venue', 'Date'}
    current_cols = set(df_processed.columns)
    missing = required_cols - current_cols
    
    if missing:
        raise KeyError(f"Dataset is missing required logical columns: {missing}. Please check the CSV format.")

    try:
        if 'Time' in df_processed.columns:
            if 'AmPm' in df_processed.columns:
                datetime_str = df_processed['Date'].astype(str) + ' ' + df_processed['Time'].astype(str) + ' ' + df_processed['AmPm'].astype(str)
            else:
                datetime_str = df_processed['Date'].astype(str) + ' ' + df_processed['Time'].astype(str)
        else:
            datetime_str = df_processed['Date'].astype(str)
            
        df_processed['DATETIME'] = pd.to_datetime(datetime_str, dayfirst=True, format='mixed', errors='coerce')
        
    except Exception as e:
        raise ValueError(f"Failed to parse Date/Time columns: {str(e)}")

    df_processed = df_processed.dropna(subset=['DATETIME', 'Team_A', 'Team_B', 'Venue'])
    
    match_duration = timedelta(hours=3, minutes=30)
    df_processed['START_TIME'] = df_processed['DATETIME']
    df_processed['END_TIME'] = df_processed['START_TIME'] + match_duration
    
    df_processed = df_processed.sort_values(by='START_TIME').reset_index(drop=True)
    
    columns_to_keep = ['Team_A', 'Team_B', 'Venue', 'START_TIME', 'END_TIME', 'Date']
    df_processed = df_processed[[col for col in columns_to_keep if col in df_processed.columns]]
    
    return df_processed

def check_conflict(match, selected_matches):
    """
    Check if a match conflicts with already selected matches.
    """
    for selected in selected_matches:
        time_overlap = (match['START_TIME'] < selected['END_TIME']) and (selected['START_TIME'] < match['END_TIME'])
        
        if time_overlap:
            if match['Venue'] == selected['Venue']:
                return True
            
            teams_in_match = {match['Team_A'], match['Team_B']}
            teams_in_selected = {selected['Team_A'], selected['Team_B']}
            
            if teams_in_match.intersection(teams_in_selected):
                return True
            
    return False

def optimize_schedule(df):
    """
    Apply greedy algorithm to optimize match scheduling.
    """
    sorted_df = df.sort_values(by='START_TIME').reset_index(drop=True)
    
    selected_matches = []
    rejected_matches = []
    
    for _, row in sorted_df.iterrows():
        if not check_conflict(row, selected_matches):
            selected_matches.append(row)
        else:
            rejected_matches.append(row)
            
    df_selected = pd.DataFrame(selected_matches)
    df_rejected = pd.DataFrame(rejected_matches)
    
    return df_selected, df_rejected

def load_and_optimize(filepath='ipl_schedule.csv'):
    """
    Helper function to load data from file, preprocess, and optimize.
    """
    df = pd.read_csv(filepath, on_bad_lines='skip')
    df_processed = preprocess_data(df)
    df_selected, df_rejected = optimize_schedule(df_processed)
    
    for df_result in [df_selected, df_rejected]:
        if not df_result.empty:
            df_result['START_TIME'] = df_result['START_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_result['END_TIME'] = df_result['END_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
            df_result.fillna("", inplace=True)
            
    return {
        "original_count": len(df_processed),
        "selected_count": len(df_selected),
        "rejected_count": len(df_rejected),
        "optimal_schedule": df_selected.to_dict(orient='records'),
        "rejected_schedule": df_rejected.to_dict(orient='records')
    }
