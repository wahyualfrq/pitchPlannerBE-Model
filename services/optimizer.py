import pandas as pd
import numpy as np
from datetime import timedelta

def standardize_columns(df):
    """Standardize DataFrame columns with protection against duplicates."""
    col_mapping = {}
    seen_targets = set()
    
    # Priority order for mapping to avoid duplicates
    # We process in a specific order so that 'DATE' takes precedence over 'STARTTIME' if both exist
    categories = [
        (['HOMETEAM', 'TEAM1', 'TEAMA', 'HOME'], 'Team_A'),
        (['AWAYTEAM', 'TEAM2', 'TEAMB', 'AWAY'], 'Team_B'),
        (['VENUE', 'STADIUM', 'LOCATION', 'GROUND', 'MATCHVENUE'], 'Venue'),
        (['DATE', 'MATCHDATE', 'DATETIME', 'STARTDATE'], 'Date'),
        (['TIME', 'MATCHTIME', 'STARTTIME'], 'Time'),
        (['PM/AM', 'AMPM', 'MERIDIEM'], 'AmPm')
    ]
    
    for col in df.columns:
        # Hapus BOM character dari Excel (\ufeff), spasi, garis bawah, titik, dan tanda kutip
        clean_col = str(col).upper().strip('\uFEFF\ufeff \t\n\r"\'')
        clean_col = clean_col.replace(' ', '').replace('_', '').replace('.', '')
        
        for patterns, target in categories:
            if clean_col in patterns and target not in seen_targets:
                col_mapping[col] = target
                seen_targets.add(target)
                break

    df_renamed = df.rename(columns=col_mapping)
    return df_renamed

def preprocess_data(df):
    """Preprocess the raw dataset."""
    df_processed = standardize_columns(df.copy())
    
    required_cols = {'Team_A', 'Team_B', 'Venue', 'Date'}
    current_cols = set(df_processed.columns)
    missing = required_cols - current_cols
    
    if missing:
        raise KeyError(f"Dataset is missing required logical columns: {missing}. Please check the CSV format.")

    try:
        # Build datetime string from available columns
        if 'Date' in df_processed.columns:
            dates = df_processed['Date'].astype(str).str.strip()
            
            if 'Time' in df_processed.columns:
                times = df_processed['Time'].astype(str).str.strip()
                if 'AmPm' in df_processed.columns:
                    ampms = df_processed['AmPm'].astype(str).str.strip().str.upper()
                    # Filter out any non-AM/PM strings
                    ampms = ampms.apply(lambda x: x if x in ['AM', 'PM'] else '')
                    datetime_str = dates + ' ' + times + ' ' + ampms
                else:
                    datetime_str = dates + ' ' + times
            else:
                datetime_str = dates
        else:
            # Fallback if somehow Date is missing but we got this far
            raise KeyError("Kolom tanggal (Date) tidak ditemukan.")

        # Enhanced parsing with mixed format support and dayfirst priority
        df_processed['DATETIME'] = pd.to_datetime(
            datetime_str, 
            dayfirst=True,
            format='mixed', 
            errors='coerce'
        )
        
        # Secondary check for rows that failed to parse
        mask = df_processed['DATETIME'].isna()
        if mask.any():
            # Try parsing just the date part for failed rows
            df_processed.loc[mask, 'DATETIME'] = pd.to_datetime(
                dates[mask], 
                dayfirst=True,
                errors='coerce'
            )
        
    except Exception as e:
        raise ValueError(f"Gagal memproses kolom Tanggal/Waktu: {str(e)}")

    # Drop rows where datetime could not be determined
    df_processed = df_processed.dropna(subset=['DATETIME'])
    
    # Ensure other required columns exist after drop
    for col in ['Team_A', 'Team_B', 'Venue']:
        if col not in df_processed.columns:
             df_processed[col] = "Unknown"
        else:
             df_processed = df_processed.dropna(subset=[col])
    
    match_duration = timedelta(hours=3, minutes=30)
    df_processed['START_TIME'] = df_processed['DATETIME']
    df_processed['END_TIME'] = df_processed['START_TIME'] + match_duration
    
    df_processed = df_processed.sort_values(by='START_TIME').reset_index(drop=True)
    
    columns_to_keep = ['Team_A', 'Team_B', 'Venue', 'START_TIME', 'END_TIME', 'Date']
    df_processed = df_processed[[col for col in columns_to_keep if col in df_processed.columns]]
    
    return df_processed

def check_conflict(match, selected_matches):
    """Check if a match conflicts with already selected matches."""
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
    """Apply greedy algorithm to optimize match scheduling."""
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

def load_and_optimize(filepath='data/ipl_schedule.csv'):
    """Helper function to load data from file, preprocess, and optimize."""
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
