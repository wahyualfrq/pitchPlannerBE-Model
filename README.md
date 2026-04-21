# PitchPlanner Backend

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-orange.svg)
![Algorithm](https://img.shields.io/badge/Algorithm-Greedy-purple.svg)

**PitchPlanner Backend** is a robust and resilient Flask-based RESTful API designed to solve sports scheduling problems, specifically tailored for optimizing cricket match schedules like the Indian Premier League (IPL). 

The core of this system utilizes a **Greedy Algorithm** to automatically process an initial schedule and minimize scheduling conflicts. It efficiently handles cases such as overlapping match times at the same venue or a single team being scheduled to play in two different matches concurrently.

---

## 🚀 Features

- **Algorithmic Schedule Optimization:** Evaluates massive datasets to intelligently resolve time, venue, and team conflicts using a greedy scheduling strategy.
- **RESTful API Interface:** Provides a simple, unified endpoint for uploading a custom CSV file or testing against a default dataset to receive optimized JSON schedules.
- **Resilient Data Processing:** Built with the `pandas` library to perform dictionary-based fuzzy matching. It can automatically standardize inconsistent column names (e.g., mapping `HOMETEAM`, `TEAM1`, or `HOME` to `Team_A`) and parse mixed datetime formats effortlessly.
- **CORS Enabled:** Fully configured to accept requests from cross-origin frontend applications (e.g., React, Vue, or Angular).

---

## 🛠️ Technologies Used

- **Framework:** [Flask](https://flask.palletsprojects.com/) (Python)
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Cross-Origin Configuration:** `flask-cors`
- **Algorithm:** Greedy Approach

---

## 📋 Prerequisites

Before setting up the project locally, ensure you have the following installed:
- **Python 3.8** or higher
- **pip** (Python package installer)

---

## ⚙️ Installation & Setup

Follow these steps to get your development environment running:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wahyualfrq/pitchPlannerBE-Model.git
   cd pitchPlannerBE
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   # On macOS and Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install flask flask-cors pandas numpy
   ```
   *(Alternatively, if a `requirements.txt` is present, run: `pip install -r requirements.txt`)*

---

## 🏃‍♂️ Running the Application

To start the local development server, run:
```bash
python app.py
```
By default, the API will be accessible at `http://localhost:5000`.

---

## 📖 API Documentation

### 1. Health Check
Endpoint to verify the operational status of the server.

- **URL:** `/api/health`
- **Method:** `GET`
- **Success Response:**
  - **Code:** 200 OK
  - **Content:**
    ```json
    {
      "message": "IPL Scheduling Optimizer API is running.",
      "status": "healthy"
    }
    ```

### 2. Optimize Schedule
Endpoint to process and optimize the match schedule dataset.

- **URL:** `/api/optimize`
- **Method:** `POST` | `GET`
- **Parameters (POST):** 
  - Send as `multipart/form-data`. Include a CSV file with the key `file`.
- **Behavior (GET):**
  - Automatically processes the default dataset (`ipl_schedule.csv`) located in the root directory.
- **Success Response:**
  - **Code:** 200 OK
  - **Content Example:**
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
        "rejected_schedule": [
          {
            "Date": "01/04/23",
            "Team_A": "RCB",
            "Team_B": "DC",
            "Venue": "Wankhede Stadium",
            "START_TIME": "2023-04-01 20:00:00",
            "END_TIME": "2023-04-01 23:30:00"
          }
        ]
      }
    }
    ```
- **Error Responses:**
  - **Code:** 400 Bad Request (Invalid file format, empty file, or missing expected columns).
  - **Code:** 404 Not Found (Default CSV not found for GET requests).
  - **Code:** 500 Internal Server Error (Server-side processing errors).

---

## 📊 CSV Data Format Requirements

To guarantee seamless optimization, ensure the uploaded CSV contains the following logical columns. Note that the backend's resilient preprocessor will automatically attempt to map known aliases to the standard schema.

- **Team_A:** Also maps from `Home Team`, `Team 1`, `TeamA`, `Home`.
- **Team_B:** Also maps from `Away Team`, `Team 2`, `TeamB`, `Away`.
- **Venue:** Also maps from `Stadium`, `Ground`, `Location`, `Match Venue`.
- **Date:** The match date (`Date`, `Match Date`, `Start Date`).
- **Time & AmPm:** Optional columns if the time parameter is merged into the Date string.

---

## 📂 Project Structure

```text
pitchPlannerBE/
│
├── app.py                             # Main Flask application and API route definitions
├── optimizer.py                       # Core logic: data preprocessing, schema mapping, & Greedy Algorithm
├── ipl_schedule.csv                   # Default testing dataset
├── ipl_scheduling_optimization.ipynb  # Jupyter Notebook for algorithm prototyping/research
├── requirements.txt                   # Project dependencies (if generated)
└── README.md                          # Comprehensive documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
When contributing, please ensure your code follows standard PEP 8 guidelines and all API endpoints respond appropriately.

## 📄 License

This project is intended for educational and academic scheduling research purposes. Feel free to fork and utilize it as per your requirements.
