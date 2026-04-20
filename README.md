# PitchPlanner Backend

PitchPlanner Backend is a Flask-based RESTful API designed to optimize cricket match schedules (specifically for the IPL). It utilizes a Greedy algorithm to process an initial schedule and minimize conflicts. Conflicts are defined as either two matches happening at the same venue concurrently, or a team being scheduled to play in overlapping matches.

## Features
- **Schedule Optimization:** Uses a Greedy algorithm to evaluate match schedules and resolve time, venue, and team conflicts.
- **RESTful API:** Provides an endpoint to upload a CSV file and get JSON responses with the optimized schedule.
- **Resilient Data Processing:** Built with `pandas` to handle and standardize inconsistent column names and datetime formats.

## Prerequisites
- Python 3.8+
- pip (Python package installer)

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd pitchPlannerBE
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   Ensure you have a `requirements.txt` file, or install the primary packages directly:
   ```bash
   pip install flask flask-cors pandas numpy
   ```

## Running the API

Start the Flask development server:
```bash
python app.py
```
The API will be available at `http://localhost:5000`.

## API Endpoints

### 1. Health Check
- **URL:** `/api/health`
- **Method:** `GET`
- **Description:** Verifies that the API is running correctly.
- **Response:**
  ```json
  {
    "message": "IPL Scheduling Optimizer API is running.",
    "status": "healthy"
  }
  ```

### 2. Optimize Schedule
- **URL:** `/api/optimize`
- **Method:** `GET` or `POST`
- **Description:** 
  - **POST:** Upload a CSV file using `multipart/form-data` with the key `file` to process a custom schedule.
  - **GET:** Processes the default dataset (`ipl_schedule.csv`) if present in the root directory.
- **Response Example:**
  ```json
  {
    "success": true,
    "data": {
      "original_count": 100,
      "selected_count": 85,
      "rejected_count": 15,
      "optimal_schedule": [
        {
          "Date": "01/04/23",
          "Team_A": "CSK",
          "Team_B": "MI",
          "Venue": "Wankhede Stadium",
          "START_TIME": "2023-04-01 19:30:00",
          "END_TIME": "2023-04-01 23:00:00"
        }
      ],
      "rejected_schedule": [ ... ]
    }
  }
  ```

## CSV Data Format Requirements
For best results, the input CSV should ideally have the following logical columns (the processor attempts to auto-map aliases like "HOME TEAM" to "Team_A"):
- **Team_A** (or Home Team, Team 1)
- **Team_B** (or Away Team, Team 2)
- **Venue** (or Stadium, Ground)
- **Date** (Date of the match)
- **Time** & **AmPm** (Optional if time is included in the Date string)

## Project Structure
- `app.py`: Main Flask application handling routing and API requests.
- `optimizer.py`: Contains the core logic for data preprocessing, standardization, and the greedy scheduling algorithm.
- `ipl_schedule.csv`: Default dataset used for fallback testing.
- `ipl_scheduling_optimization.ipynb`: Research notebook for algorithmic prototyping and visualizations.
