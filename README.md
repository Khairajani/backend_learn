# Elementary dbt Data Monitoring

**Learn dbt with Elementary - Automated dbt data monitoring and observability**

This project demonstrates how to use Elementary, an open-source data observability tool for dbt, to monitor your data pipeline health, detect anomalies, and generate beautiful reports.

## What is Elementary?

Elementary is a dbt package that adds data monitoring capabilities to your dbt project. It automatically detects data quality issues, schema changes, and performance problems in your data pipeline.

## 🚀 Quick Start

### Prerequisites
- Python >= 3.8
- dbt >= 1.0.0
- Virtual environment activated

### 1. Install Dependencies

First, activate your Python virtual environment and install the required packages:

```bash
# Activate your virtual environment (if not already activated)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install all required dependencies
pip install -r requirements.txt
```

### 2. Configure dbt Profile

Create a dbt profile configuration file to connect Elementary CLI to your dbt project:

```bash
# Generate the Elementary CLI profile configuration
cd jaffle_shop
dbt run-operation elementary.generate_elementary_cli_profile
```

Copy the output and create the profile file:

```bash
# Create the dbt profiles directory if it doesn't exist
mkdir -p ~/.dbt

# Create or edit the profiles.yml file
nano ~/.dbt/profiles.yml
```

Paste the generated profile configuration into `~/.dbt/profiles.yml`. It should look something like this:

```yaml
elementary:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ./elementary.duckdb
      threads: 4
```

### 3. Run dbt with Elementary

Navigate to the jaffle_shop directory and execute the following commands in sequence:

```bash
cd jaffle_shop

# Clean previous dbt artifacts
dbt clean

# Install dbt dependencies (including Elementary package)
dbt deps

# Load seed data
dbt seed

# Run Elementary models first to set up monitoring infrastructure
dbt run --select elementary

# Run all your dbt models
dbt run

# Run dbt tests (including Elementary's automated tests)
dbt test

# Generate dbt documentation
dbt docs generate

# Generate Elementary monitoring report
edr report --project-dir .
```

### 4. View Your Results

After running the commands above:

- **dbt docs**: Available at `http://localhost:8080` (run `dbt docs serve`)
- **Elementary Report**: Generated HTML report will be created in your project directory
- **Data Quality Tests**: Results visible in the Elementary dashboard

## 📊 What Elementary Provides

### Automated Data Monitoring
- **Schema Changes**: Detects when table schemas change unexpectedly
- **Data Freshness**: Monitors if your data is being updated as expected
- **Volume Anomalies**: Identifies unusual spikes or drops in data volume
- **Null Rate Changes**: Tracks changes in null percentages

### Data Quality Tests
Elementary automatically adds tests for:
- Column-level anomaly detection
- Table-level volume monitoring
- Schema change detection
- Data freshness monitoring

### Beautiful Reports
- Interactive HTML dashboards
- Test results visualization
- Performance metrics
- Lineage graphs with monitoring overlay

## 📁 Project Structure

```
learn_dbt/
├── jaffle_shop/              # Main dbt project
│   ├── models/              # dbt models
│   ├── tests/               # Custom dbt tests
│   ├── seeds/               # Seed data files
│   ├── dbt_project.yml      # dbt project configuration
│   └── packages.yml         # dbt package dependencies
├── requirements.txt         # Python dependencies
├── venv/                   # Python virtual environment
└── README.md              # This file
```

## 🔧 Elementary Configuration

Elementary is configured through your `dbt_project.yml` file in the jaffle_shop directory. Key configurations include:

```yaml
# Elementary configuration
vars:
  # Elementary specific variables
  days_back: 7                    # How far back to look for anomalies
  anomaly_sensitivity: 3          # Sensitivity for anomaly detection (1-5)
  anomaly_direction: both         # 'spike', 'drop', or 'both'
```

## 📈 Monitoring Commands

### Generate Reports
```bash
# Generate Elementary report for current project
edr report --project-dir .

# Generate report for specific time range
edr report --project-dir . --days-back 30

# Generate report and open in browser
edr report --project-dir . --open-browser
```

### Send Alerts (Optional)
```bash
# Send Slack alerts (requires configuration)
edr send-report --slack-webhook YOUR_WEBHOOK_URL

# Monitor and send alerts automatically
edr monitor --slack-webhook YOUR_WEBHOOK_URL
```

## 🚨 Troubleshooting

### Common Issues

**1. "Elementary package not found"**
```bash
# Make sure you've installed dependencies
dbt deps
```

**2. "Profile not found"**
```bash
# Verify your profiles.yml is in the correct location
ls ~/.dbt/profiles.yml
```

**3. "Permission denied on elementary.duckdb"**
```bash
# Make sure the database file has proper permissions
chmod 644 elementary.duckdb
```

## 📚 Learn More

- [Elementary Documentation](https://docs.elementary-data.com/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Elementary GitHub Repository](https://github.com/elementary-data/elementary)

## 🤝 Contributing

This is a learning project! Feel free to:
1. Fork the repository
2. Add your own models and tests
3. Experiment with Elementary features
4. Share your learnings

## 📄 License

This project is for educational purposes. Elementary is licensed under Apache 2.0.

---

**Happy monitoring! 📊✨** 