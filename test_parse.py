import sys
import pandas as pd
sys.path.append('d:/PROJECT/pitchPlannerBE')
from services.optimizer import preprocess_data, load_and_optimize

try:
    filepath = 'd:/PROJECT/pitchPlannerBE/data/ipl_schedule34.csv'
    result = load_and_optimize(filepath)
    print("SUCCESS!")
    print(result['optimal_schedule'][:1])
except Exception as e:
    print("FAILED!")
    print(str(e))
