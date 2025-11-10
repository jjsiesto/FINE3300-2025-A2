#==========================================================================================
# FINE 3300 (Fall 2025): Assignment 2 - Part B - Consumer Price Index
#
# This script performs a comprehensive analysis of Consumer Price Index (CPI)
# data from 11 jurisdictions and analyzes it against minimum wage data.
#
# It prompts the user for file paths instead of hardcoding them to enhance flexibility.
# The analysis includes loading and transforming data, calculating month-to-month changes,
# determining equivalent salaries, and analyzing minimum wages in real terms.
# The code also includes print statements to inform the user of progress and any potential issues.
#==========================================================================================

# Import necessary libraries
import pandas as pd
import glob
import os

# Method to load and combine all CPI data files
def load_all_cpi_data(path_pattern):
    """
    Loads and combines all 11 CPI data files into a single DataFrame.
    
    This function demonstrates file I/O using pandas (L6) and concatenation (L6).
    It also performs a critical data manipulation (pd.melt) to transform
    the data from its "wide" format to the "long" format required for analysis.
    
    Args:
        path_pattern (str): A glob pattern to find the 11 CPI files 
                            (e.g., "./cpi_data/*.csv")

    Returns:
        pandas.DataFrame: A single, consolidated DataFrame.
    """
    # Find all matching files
    all_files = glob.glob(path_pattern)
    # Handle case where no files are found with an error message
    if not all_files:
        print(f"FATAL ERROR: No files found at '{path_pattern}'.")
        print("Please ensure your 11 CPI files are in a subdirectory (e.g., 'cpi_data').")
        return pd.DataFrame() # Return empty DataFrame

    # Sort the list to ensure 'Canada' is processed first.
    # We sort by a tuple:
    # 1. A boolean: 'Canada' in the filename is 'False' (which sorts before 'True').
    # 2. The filename itself, to keep the rest alphabetical.
    all_files_sorted = sorted(all_files, key=lambda f: ('Canada' not in os.path.basename(f), os.path.basename(f)))

    # List to hold individual DataFrames
    dataframe_list = []
    print(f"Found {len(all_files)} files. Processing...")
    
    # Process each file and transform
    for filepath in all_files_sorted:
        df_wide = pd.read_csv(filepath)
        
        # Extract Jurisdiction from filename (e.g., "AB.CPI.1810000401.csv" -> "AB")
        filename = os.path.basename(filepath)
        jurisdiction_name = filename.split('.')[0]
        
        # Transform from wide to long using pd.melt
        df_long = pd.melt(df_wide, 
                          id_vars=['Item'], 
                          var_name='Month', 
                          value_name='CPI')
        
        # Add the new 'Jurisdiction' column
        df_long['Jurisdiction'] = jurisdiction_name
        dataframe_list.append(df_long)

    # Combine all DataFrames into one (L6 - pd.concat)
    master_df = pd.concat(dataframe_list, ignore_index=True)
    
    # Reorder columns to assignment spec and return
    return master_df[['Item', 'Month', 'Jurisdiction', 'CPI']]

# Method to calculate month-to-month changes
def calculate_mtm_changes(df):
    """
    Calculates the average month-to-month change for specified items
    and returns a clean DataFrame.
    
    Arguments:
        df (pandas.DataFrame): The master CPI DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame with [Jurisdiction, Item, Avg_MtM_Change_Percent].
    """
    # 1. Filter items
    items_needed = ['Food', 'Shelter', 'All-items excluding food and energy']
    filtered_df = df[df['Item'].isin(items_needed)].copy() 
    
    # 2. Map months to sortable numbers
    month_map = {
        '24-Jan': 1, '24-Feb': 2, '24-Mar': 3, '24-Apr': 4,
        '24-May': 5, '24-Jun': 6, '24-Jul': 7, '24-Aug': 8,
        '24-Sep': 9, '24-Oct': 10, '24-Nov': 11, '24-Dec': 12
    }
    filtered_df['Month_Num'] = filtered_df['Month'].map(month_map)

    # Handle any potential nulls
    if filtered_df['Month_Num'].isnull().any():
        print("WARNING: Some month names in CSV headers did not match the map. Check data.")
        filtered_df = filtered_df.dropna(subset=['Month_Num'])

    # 3. Sort by Jurisdiction, Item, and then Month
    filtered_df.sort_values(by=['Jurisdiction', 'Item', 'Month_Num'], inplace=True)
    
    # 4. Calculate pct_change() within each group
    filtered_df['MtM_Change'] = filtered_df.groupby(['Jurisdiction', 'Item'])['CPI'].pct_change()
    
    # 5. Aggregate to get average month-to-month change
    avg_changes_series = filtered_df.groupby(['Jurisdiction', 'Item'])['MtM_Change'].mean()
    
    # 6. Format to percent, rounded to 1 decimal
    formatted_series = (avg_changes_series * 100).round(1)
    
    # 7. Convert the Series to a clean DataFrame
    avg_changes_df = formatted_series.reset_index()
    
    # 8. Rename the calculated column for clarity
    avg_changes_df.rename(columns={'MtM_Change': 'Avg_MtM_Change_Percent'}, inplace=True)

    return avg_changes_df

# Method to calculate equivalent salaries
def calculate_equivalent_salaries(df, base_jurisdiction='ON', base_salary=100000):
    """
    Calculates equivalent salary based on Dec-24 'All-items' CPI. (Q5)
    
    Demonstrates filtering and creating new columns from arithmetic (L6).
    
    Args:
        df (pandas.DataFrame): The master CPI DataFrame.
        base_jurisdiction (str): The jurisdiction to use as the baseline. ('ON' for Ontario)
        base_salary (int): The baseline salary.

    Returns:
        pandas.DataFrame: A DataFrame with salaries, indexed by Jurisdiction.
    """
    # 1. Filter for Dec-24, All-items CPI
    cpi_dec_all_items = df[
        (df['Item'] == 'All-items') & (df['Month'] == '24-Dec')
    ].copy()
    
    # 2. Get base CPI
    try:
        base_cpi = cpi_dec_all_items.loc[
            cpi_dec_all_items['Jurisdiction'] == base_jurisdiction, 'CPI'
        ].values[0]
    except IndexError:
        print(f"ERROR: Base jurisdiction '{base_jurisdiction}' not found in Dec-24 data.")
        return pd.DataFrame()

    # 3. Calculate equivalent salary (L6 - New Column)
    cpi_dec_all_items['Equivalent_Salary'] = (cpi_dec_all_items['CPI'] / base_cpi) * base_salary
    
    # Set Jurisdiction as index for cleaner output
    cpi_dec_all_items = cpi_dec_all_items.set_index('Jurisdiction')
    
    return cpi_dec_all_items[['CPI', 'Equivalent_Salary']].round(2)

# Method to analyze minimum wages
def analyze_minimum_wages(cpi_data_df, wages_filepath):
    """
    Analyzes nominal vs. real minimum wages. (Q6)
    
    Demonstrates reading a CSV, finding min/max, merging, and 
    creating new columns (L6).
    
    Args:
        cpi_data_df (pandas.DataFrame): The master CPI DataFrame.
        wages_filepath (str): Path to 'MinimumWages.csv'.

    Returns:
        tuple: (nominal_max, nominal_min, real_max, real_wage_df)
    """
    # 1. Read wages file (L6)
    try:
        wages_df = pd.read_csv(wages_filepath)
    except FileNotFoundError:
        print(f"ERROR: Could not find '{wages_filepath}'. Skipping Q6.")
        return None, None, None, pd.DataFrame()
    except Exception as e:
        print(f"An error occurred reading '{wages_filepath}': {e}. Skipping Q6.")
        return None, None, None, pd.DataFrame()

    # 2. Nominal analysis (finding max/min row)
    nominal_max = wages_df.loc[wages_df['Minimum Wage'].idxmax()]
    nominal_min = wages_df.loc[wages_df['Minimum Wage'].idxmin()]
    
    # 3. Get Dec-24 'All-items' CPI data for merging
    cpi_dec_all_items = cpi_data_df[
        (cpi_data_df['Item'] == 'All-items') & (cpi_data_df['Month'] == '24-Dec')
    ]
    
    # 4. Merge (L6 - pd.merge)
    # We rename 'Province' to 'Jurisdiction' to match the CPI data
    wages_df = wages_df.rename(columns={'Province': 'Jurisdiction'}) # L6 - rename
    
    merged_df = pd.merge(wages_df, cpi_dec_all_items, on='Jurisdiction')
    
    # 5. Calculate Real Wage (as an index) (L6 - New Column)
    merged_df['Real_Wage_Index'] = (merged_df['Minimum Wage'] / merged_df['CPI']) * 100
    
    # 6. Find max real wage
    real_max = merged_df.loc[merged_df['Real_Wage_Index'].idxmax()]
    
    return nominal_max, nominal_min, real_max, merged_df.set_index('Jurisdiction')

# Method to calculate annual inflation for 'Services'
def calculate_annual_service_inflation(df):
    """
    Computes the annual change in CPI for 'Services'. (Q7)
    
    Demonstrates filtering and using pivot_table for clean calculation.
    
    Args:
        df (pandas.DataFrame): The master CPI DataFrame.

    Returns:
        pandas.DataFrame: A DataFrame with Jan/Dec CPI and % change.
    """
    # 1. Filter
    services_df = df[
        (df['Item'] == 'Services') & 
        (df['Month'].isin(['24-Jan', '24-Dec']))
    ]
    
    # 2. Pivot the table (adjacent concept to L6 groupby)
    # This creates columns '24-Jan' and '24-Dec'
    pivot_df = services_df.pivot_table(index='Jurisdiction', columns='Month', values='CPI')
    
    # 3. Calculate annual change
    pivot_df['Annual_Change_Pct'] = (
        (pivot_df['24-Dec'] - pivot_df['24-Jan']) / pivot_df['24-Jan']
    ) * 100
    
    return pivot_df[['24-Jan', '24-Dec', 'Annual_Change_Pct']].round(1)

#==========================================================================================
# Main Execution Block
#==========================================================================================

def main(cpi_path_pattern, wages_filepath):
    """
    Main function to execute the complete Part B analysis pipeline. 
    Includes Print statements to tell the user what is being executed. 
    
    Args:
        cpi_path_pattern (str): The glob pattern for CPI files.
        wages_filepath (str): The full path to the MinimumWages.csv file.
    """
    # Load CPI Data
    print("--- Loading and Combining CPI Data ---")
    master_cpi_df = load_all_cpi_data(cpi_path_pattern)

    # Check if data loaded successfully
    if master_cpi_df.empty:
        print("Halting execution. Please fix the file path in CPI_FILE_PATTERN.")
        return
    
    # Confirm load
    print(f"Successfully loaded and combined {len(master_cpi_df)} rows from {len(master_cpi_df['Jurisdiction'].unique())} files.\n")

    # Display outputs for each question
    print("="*80)
    print("--- Master DataFrame ---")
    print("="*80)
    # Display first 12 rows
    print(master_cpi_df.head(12))
    print("\n")

    # Calculate Month-to-Month Changes
    print("="*80)
    print("--- Average Month-to-Month % Change ---")
    print("="*80)
    mtm_changes = calculate_mtm_changes(master_cpi_df)
    print(mtm_changes)
    print("\n")
    
    '''
    print("="*80)
    print("--- Highest MtM Change ---")
    print("="*80)
    # .head(1) will show the single highest value
    top_changes = mtm_changes.sort_values(by='Avg_MtM_Change_Percent', ascending=False)
    print(top_changes.head(1))
    '''
    print("="*80)
    print("--- Highest MtM Change Per Item ---")
    print("="*80)
    try:
        # 1. Group by 'Item', then find the index (row label) of the
        #    row with the maximum 'Avg_MtM_Change_Percent' in each group.
        idx_highest_per_item = mtm_changes.groupby('Item')['Avg_MtM_Change_Percent'].idxmax()
        
        # 2. Use .loc[] to select the complete rows from the original
        #    DataFrame using the indices we just found.
        highest_per_item = mtm_changes.loc[idx_highest_per_item]
        
        # 3. Sort by item name for a clean, readable report (optional)
        print(highest_per_item.sort_values(by='Item'))
        
    except Exception as e:
        print(f"Could not determine max values per item: {e}")
    print("\n")

    # --- Equivalent Salary to $100k in Ontario ---
    print("="*80)
    # ... (Rest of your main function continues below this) ...

    # Calculate Equivalent Salaries
    print("="*80)
    print("--- Equivalent Salary to $100k in Ontario ---")
    print("="*80)
    salaries_df = calculate_equivalent_salaries(master_cpi_df)
    print(salaries_df)
    print("\n")

    # Analyze Minimum Wages
    print("="*80)
    print("--- Minimum Wage Analysis  ---")
    print("="*80)
    
    # Analyze Minimum Wages and Real Wages
    # Handle case where wages file might be missing
    nom_max, nom_min, real_max, real_wage_df = analyze_minimum_wages(master_cpi_df, wages_filepath)
    if not real_wage_df.empty:
        print("--- Highest Nominal Wage ---")
        print(nom_max)
        print("\n--- Lowest Nominal Wage ---")
        print(nom_min)
        print("\n--- Highest Real Wage (Indexed to Dec-24 CPI) ---")
        print(real_max)
        print("\n--- Full Real Wage Data (for reference) ---")
        print(real_wage_df[['Minimum Wage', 'CPI', 'Real_Wage_Index']].round(2))
    print("\n")

    # Calculate Annual Inflation for 'Services'
    print("="*80)
    print("--- Annual Inflation for 'Services' ---")
    print("="*80)
    service_inflation_df = calculate_annual_service_inflation(master_cpi_df)
    print(service_inflation_df)
    print("\n")

    # Identify Highest Service Inflation
    print("="*80)
    print("--- Highest Service Inflation ---")
    print("="*80)
    # Safely attempt to print max jurisdiction and value in case of unexpected data
    try:
        print(f"Jurisdiction: {service_inflation_df['Annual_Change_Pct'].idxmax()}")
        print(f"Value: {service_inflation_df['Annual_Change_Pct'].max():.1f}%")
    except Exception as e:
        print(f"Could not determine max inflation: {e}")
    print("\n")
    
    # Completion Message
    print("="*80)
    print("--- Analysis Complete ---")
    print("="*80)

if __name__ == "__main__":
    '''This block now gathers user input *before* calling the main logic.
    This separates data input from program logic. '''
    
    # Get CPI folder path
    cpi_folder = input("Enter the path to the folder containing your 11 CPI .csv files: ")
    
    # Construct the glob pattern
    cpi_pattern = os.path.join(cpi_folder, '*.csv')
    
    # Get MinimumWages.csv path
    wages_path = input("Enter the full path to your MinimumWages.csv file: ")
    
    print("\n--- Starting Analysis ---")

    # Call the main function with the user-provided paths
    main(cpi_path_pattern=cpi_pattern, wages_filepath=wages_path)