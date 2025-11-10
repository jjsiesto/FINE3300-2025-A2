# FINE 3300 (Fall 2025): Assignment 2

This repository contains the Python scripts and data files for Assignment 2. 

## Repository Contents

This assignment has two main parts:

### Part A: Loan and Amortization Schedules

* **Script:** `LoanPmt.py`
* **Description:** A Python script containing the `MortgagePayment` class. This class models and calculates various payment schemes for a Canadian fixed-rate mortgage. It also generates detailed amortization schedules and a plot visualizing the loan balance decline over time.

### Part B: Consumer Price Index (CPI) Analysis

* **Script:** `CPI_analysis.py`
* **Description:** A Python script that performs a comprehensive analysis of Consumer Price Index (CPI) data. It loads and combines data from 11 jurisdictions, analyzes it against provincial minimum wage data, and calculates various metrics such as month-to-month changes and equivalent salaries.
* **Data Files:**
    * `cpi_data/` (directory): Contains 11 `.csv` files, one for each jurisdiction's CPI data.
    * `MinimumWages.csv`: Contains minimum wage data for each province.

## Requirements

The scripts are written in Python 3 and require the following libraries:

* `pandas`
* `matplotlib`
* `numpy`

You can install these dependencies using pip:
```bash
pip install pandas matplotlib numpy
