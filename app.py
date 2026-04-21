from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from services.optimizer import load_and_optimize, preprocess_data, optimize_schedule

app = Flask(__name__)
CORS(app)

DEFAULT_CSV_PATH = 'data/ipl_schedule.csv'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to ensure API is running."""
    return jsonify({"status": "healthy", "message": "IPL Scheduling Optimizer API is running."})

@app.route('/api/optimize', methods=['GET', 'POST'])
def optimize():
    """Endpoint to trigger the scheduling optimization."""
    try:
        if request.method == 'POST' and 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"success": False, "error": "No selected file."}), 400
                
            if file and file.filename.endswith('.csv'):
                df = pd.read_csv(file)
                df_processed = preprocess_data(df)
                df_selected, df_rejected = optimize_schedule(df_processed)
                
                for df_result in [df_selected, df_rejected]:
                    if not df_result.empty:
                        df_result['START_TIME'] = df_result['START_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
                        df_result['END_TIME'] = df_result['END_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
                        df_result.fillna("", inplace=True)
                
                return jsonify({
                    "success": True,
                    "data": {
                        "original_count": len(df_processed),
                        "selected_count": len(df_selected),
                        "rejected_count": len(df_rejected),
                        "optimal_schedule": df_selected.to_dict(orient='records'),
                        "rejected_schedule": df_rejected.to_dict(orient='records')
                    }
                })
            else:
                return jsonify({"success": False, "error": "Invalid file format. Please upload a CSV file."}), 400
                
        elif os.path.exists(DEFAULT_CSV_PATH):
            result = load_and_optimize(DEFAULT_CSV_PATH)
            return jsonify({
                "success": True,
                "data": result
            })
            
        else:
            return jsonify({"success": False, "error": "Default dataset not found and no file was uploaded."}), 404

    except pd.errors.EmptyDataError:
        return jsonify({"success": False, "error": "Uploaded CSV file is empty."}), 400
    except KeyError as e:
        return jsonify({"success": False, "error": f"Missing expected column in dataset: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
