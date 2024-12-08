
# Segwise Game Analytics

This is a Flask-based web application designed for managing and querying game data. The system connects to a PostgreSQL database, supports uploading game data from a CSV file, and provides an API to retrieve the data with various filters and sorting capabilities.

---

## Features

- **Database Integration**: Connects to a PostgreSQL database to store and manage game data.
- **Game Data API**: Allows querying game data with advanced filtering, sorting, and pagination.
- **CSV Upload**: Supports uploading game data from a CSV file, parsing the contents, and inserting them into the database.
- **Dynamic SQL Query Building**: Supports dynamic query building for filtering, grouping, and ordering data based on user input.

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
   - [Running the Application](#running-the-application)
   - [Using the API](#using-the-api)
4. [Project Structure](#project-structure)
5. [License](#license)

---

## Installation

To get started with this project, you need to set up a few things:

### Prerequisites

- Python 3.x
- PostgreSQL Database (or any compatible database)
- `pip` (Python package installer)

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/amtsngh/segwise-game-analytics.git
cd segwise-game-analytics
```

### Step 2: Set up a Virtual Environment

Create a virtual environment to isolate dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies

Install the required dependencies by running:

```bash
pip install -r requirements.txt
```

### Step 4: Configure Database

Create a PostgreSQL database if you don't have one. You can use the following SQL to create the necessary schema:

```sql
CREATE DATABASE game_data;
```

Once your database is created, set up your `.env` file to configure database credentials and other settings:

Create a `.env` file in the root of the project and add the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=game_data

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

---

## Configuration

The application uses environment variables to store sensitive information like database credentials. These values are loaded from the `.env` file using the `python-dotenv` package.

### Configurations in `config.py`

- **DB_HOST**: Database host (e.g., `localhost` or the AWS RDS endpoint).
- **DB_USER**: The username to connect to the database.
- **DB_PASSWORD**: The password to connect to the database.
- **DB_NAME**: The name of the PostgreSQL database to use.
- **FLASK_ENV**: The environment the Flask app is running in (`development` or `production`).
- **FLASK_DEBUG**: Enables debugging in the development environment.

---

## Usage

### Running the Application

After setting up the environment and configurations, you can run the Flask app using:

```bash
flask run
```

By default, the app will run on `http://127.0.0.1:5000/`.

---

### Using the API

The API allows interaction with the game data stored in the PostgreSQL database. You can perform the following operations:

#### 1. **Get Game Data**

- **Endpoint**: `/data`
- **Method**: `POST`
- **Description**: Fetches game data based on various filtering, grouping, and sorting parameters.

##### Request Body (JSON format)

```json
{
  "startRow": 0,
  "endRow": 100,
  "filterModel": {
    "Name": {"filterType": "text", "type": "contains", "filter": "Game"},
    "Price": {"filterType": "number", "type": "greaterThan", "filter": 10}
  },
  "sortModel": [{"colId": "Price", "sort": "asc"}],
  "rowGroupCols": [{"field": "Genres"}],
  "groupKeys": []
}
```

- `startRow`, `endRow`: Pagination parameters.
- `filterModel`: Filters to apply on different columns.
- `sortModel`: Sorting options.
- `rowGroupCols`: Columns to group by.
- `groupKeys`: Keys for grouping the data.

##### Response (JSON format)

```json
{
  "data": [
    {
      "AppID": 1234,
      "Name": "Sample Game",
      "Release_date": "2022-01-01",
      "Price": 20.5,
      "Genres": ["Action", "Adventure"]
    }
  ],
  "rowCount": 100
}
```

#### 2. **Upload CSV Data**

- **Endpoint**: `/upload-csv`
- **Method**: `POST`
- **Description**: Uploads game data from a CSV file via a URL.

##### Request Body (JSON format)

```json
{
  "csv_link": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSCtraqtnsdYd4FgEfqKsHMR2kiwqX1H9uewvAbuqBmOMSZqTAkSEXwPxWK_8uYQap5omtMrUF1UJAY/pub?gid=1439814054&single=true&output=csv"
}
```

The server will download the CSV file, parse it, and insert the data into the database.

##### Response (JSON format)

```json
{
  "data": null,
  "message": "CSV data successfully uploaded."
}
```

---

## Project Structure

Here’s an overview of the project structure:

```
/segwise-game-analytics
│
├── app.py               # Main entry point for the Flask app
├── config.py            # Configuration file (for DB, secret keys, etc.)
├── models.py            # Database models and logic related to the database
├── services.py          # Game data service logic
├── routes.py            # Routes for the application
├── utils.py             # Utility functions (e.g., CSV parsing, date formatting)
└── requirements.txt     # Dependencies for the app
└── Dockerfile           # Docker config for the app
└── Static               
    └── swagger.json     # Swagger config
```

### Key Files and Directories:

- **`app.py`**: This is the entry point for the Flask application, where routes are registered and the server is started.
- **`config.py`**: Contains the configuration for connecting to the database and Flask-specific settings.
- **`models.py`**: Contains functions for interacting with the database (e.g., ensuring the table exists, managing connections).
- **`services.py`**: Contains business logic for querying the database, including dynamic SQL query building.
- **`routes.py`**: Defines the API endpoints for querying and uploading game data.
- **`utils.py`**: Contains helper functions like CSV parsing, date formatting, etc.
- **`requirements.txt`**: Lists all the required Python packages.

---

### Cost of Running in Production (Approximation):

If you choose to deploy this system in a production environment using an AWS t2.medium instance (2 vCPU, 4GB RAM) and 50GB of EBS storage, and run it continuously for 30 days, the approximate monthly cost would be:

t2.medium Instance (24x7 for 30 days): ~USD 33.4/month
50GB EBS Storage: ~USD 5/month
Total in USD: ~USD 38.4/month
In INR (assuming 1 USD ≈ 83 INR):

~38.4 * 83 = ~3,187.2 INR (≈3,200 INR per month)
This estimate assumes minimal data transfer costs and a negligible increase in price from the one file upload and 100 queries per day. Actual costs may vary based on region, reserved instances, and other factors.

---