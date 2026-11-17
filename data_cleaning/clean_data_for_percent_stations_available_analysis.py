# Cleaning AFDC charging station daily data

# Import necessary packages
import pandas as pd
import datetime as dt
import os

# Define directories and file names for input and output data
DATA_DIR = "../data/example_data/"
SAVE_DIR = "../results/cleaned_data"
DATA_FILE = "example_data_2023_01.feather"
SAVE_FILE_NAME = DATA_FILE.replace(".feather", "_cleaned")

# Column names for Level 2 and DC fast chargers
L2_NUM_CHARGERS = 'EV Level2 EVSE Num'
DC_NUM_CHARGERS = 'EV DC Fast Count'

# Create save directory if it doesn't exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# AFDC charging networks can be found here: https://afdc.energy.gov/stations/charging-networks
# THis analysis only included networks that have an "API" import type
API_NETWORKS = ['ABM','BP_PULSE','CHAEVI', 'CHARGELAB', 'ChargePoint Network',\
                'CHARGESMART_EV', 'CHARGEUP', 'ELECTRIC_ERA', 'Electrify America', 'EV Connect', 'EVRANGE', 'EVIUM',\
                'EVCS', 'EVGATEWAY', 'eVgo Network', 'FLASH', 'FLIPTURN', 'FLITWAY', 'FLO', 'FORD_CHARGE', \
                'GRAVITI_ENERGY', 'IONNA', 'MERCEDES_BENZ', 'NOODOE', 'OpConnect', 'RED_E',\
                'RIVIAN_ADVENTURE', 'RIVIAN_WAYPOINTS', 'SHELL_RECHARGE', 'VIALYNK', 'ZEFNET']

# Define regions for regional analysis
STATE_TO_REGION = {
    'ME': 'Northeast', 'NH': 'Northeast', 'VT': 'Northeast',
    'MA': 'Northeast', 'RI': 'Northeast', 'CT': 'Northeast',
    'NY': 'Northeast', 'NJ': 'Northeast', 'PA': 'Northeast',
    'OH': 'Midwest', 'IN': 'Midwest', 'IL': 'Midwest', 'MI': 'Midwest',
    'WI': 'Midwest', 'MN': 'Midwest', 'IA': 'Midwest', 'MO': 'Midwest',
    'ND': 'Midwest', 'SD': 'Midwest', 'NE': 'Midwest', 'KS': 'Midwest',
    'DE': 'South', 'MD': 'South', 'VA': 'South', 'WV': 'South',
    'KY': 'South', 'NC': 'South', 'SC': 'South', 'GA': 'South',
    'FL': 'South', 'AL': 'South', 'MS': 'South', 'TN': 'South',
    'AR': 'South', 'LA': 'South', 'TX': 'South', 'OK': 'South', 'DC': 'South',
    'MT': 'West', 'ID': 'West', 'WY': 'West', 'NV': 'West',
    'UT': 'West', 'CO': 'West', 'AZ': 'West', 'NM': 'West',
    'WA': 'West', 'OR': 'West', 'CA': 'West', 'AK': 'West', 'HI': 'West'
}

assert(len(STATE_TO_REGION) == 51)  # 50 states + DC

def region_categories(state):
    """Return the US Census region for a two-letter state code."""
    assert(state in STATE_TO_REGION.keys())
    return(STATE_TO_REGION[state])

def categorize_station_age(open_date):
    """Bin a station's open date (YYYY-MM-DD) into two-year ranges, starting with "Before 2015"."""
    if not pd.isna(open_date):
        year = int(open_date[:4])
        if year < 2015:
            return "Before 2015"
        elif 2015 <= year < 2017:
            return "2015 - 2016"
        elif 2017 <= year < 2019:
            return "2017 - 2018"
        elif 2019 <= year < 2021:
            return "2019 - 2020"
        elif 2021 <= year < 2023:
            return "2021 - 2022"
        elif 2023 <= year < 2025:
            return "2023 - 2024"
    else:
        return pd.NA

def categorize_by_single_year(open_date):
    """Bin a station's open date (YYYY-MM-DD) by single year from 2015 on, with "Before 2015" for older stations."""
    if not pd.isna(open_date):
        year = int(open_date[:4])
        if year < 2015:
            return "Before 2015"
        elif 2015 <= year < 2016:
            return "2015"
        elif 2016 <= year < 2017:
            return "2016"
        elif 2017 <= year < 2018:
            return "2017"
        elif 2018 <= year < 2019:
            return "2018"
        elif 2019 <= year < 2020:
            return "2019"
        elif 2020 <= year < 2021:
            return "2020"
        elif 2021 <= year < 2022:
            return "2021"
        elif 2022 <= year < 2023:
            return "2022"
        elif 2023 <= year < 2024:
            return "2023"
        elif 2024 <= year < 2025:
            return "2024"
    else:
        return pd.NA   
    
def categorize_by_single_year_other_way(open_date):
    """Bin a station's open date (YYYY-MM-DD) by single year from 2020 on, with "Before 2020" for older stations."""
    if not pd.isna(open_date):
        year = int(open_date[:4])
        if year < 2020:
            return "Before 2020"
        elif 2020 <= year < 2021:
            return "2020"
        elif 2021 <= year < 2022:
            return "2021"
        elif 2022 <= year < 2023:
            return "2022"
        elif 2023 <= year < 2024:
            return "2023"
        elif 2024 <= year < 2025:
            return "2024"
    else:
        return pd.NA   

def has_chargers(count):
    """Return True if a charger count is present and greater than zero."""
    if (not pd.isna(count)) and (count > 0):
        return True
    else:
        return False
    
def chargers_including_combos(row):
    """Label a station as having "L2", "DC", "L2 and DC", or "no L2 or DC chargers"."""
    if row["has_L2_chargers"] & row["has_DC_chargers"]:
        return "L2 and DC"
    elif row["has_L2_chargers"]:
        return "L2"
    elif row["has_DC_chargers"]:
        return "DC"
    else:
        return "no L2 or DC chargers"

def categorize_chargers(row):
    """Bin a station's total L2 + DC port count into "5 or under", "6-10", or "11+"."""
    total_chargers = row['total_chargers']
    if total_chargers <= 5:
        return '5 or under'
    elif 5 < total_chargers <= 10:
        return '6-10'
    elif total_chargers > 10:
        return '11+'

def clean_data(df: pd.DataFrame):
    """Filter to public, open/temporarily unavailable stations in the 50 states + DC, add category columns, and save the
    cleaned data (plus row counts after each step) to SAVE_DIR."""
    step_lengths = []

    def log_length(step_name: str, dataframe: pd.DataFrame):
        """Record the number of rows remaining after a cleaning step."""
        step_lengths.append((step_name, len(dataframe)))

    log_length("starting dataframe", df)

    # getting rid of locations that aren't the 50 states + DC
    df = df[df['State'].isin(STATE_TO_REGION.keys())]
    log_length("filter to 50 states + DC", df)

    # only look at stations currently available (not planned)
    df = df[df["Status Code"].isin(["E", "T"])]
    log_length("filter status to E/T", df)

    # only look at public stations
    df = df[df["Access Code"] == "public"]
    log_length("filter access code to public", df)

    # create station age columns based on when the station was opened
    df['other_age_category'] = df['Open Date'].apply(categorize_station_age)
    log_length("create other_age_category column", df)
    df['single_year_age_category'] = df['Open Date'].apply(categorize_by_single_year)
    log_length("create single_year_age_category column", df)
    df['single_year_age_category_fewer_years'] = df['Open Date'].apply(categorize_by_single_year_other_way)
    log_length("create single_year_age_category_fewer_years column", df)

    # create region column based on state
    df['Region'] = df['State'].apply(region_categories)
    log_length("create Region column", df)

    # adding columns for whether a station has dc and/or l2 chargers
    df["has_L2_chargers"] = df[L2_NUM_CHARGERS].apply(has_chargers)
    log_length("create has_L2_chargers column", df)
    df["has_DC_chargers"] = df[DC_NUM_CHARGERS].apply(has_chargers)
    log_length("create has_DC_chargers column", df)
    # create total chargers column by summing L2 and DC chargers
    df['total_chargers'] = df[L2_NUM_CHARGERS].fillna(0) + df[DC_NUM_CHARGERS].fillna(0)
    log_length("create total_chargers column", df)
    # create station size column based on total chargers
    df["station_size"] = df.apply(categorize_chargers, axis=1)
    log_length("create station_size column", df)
    # characterizing stations based on whether they have L2, DC, or both types of chargers
    df["DC_and_L2_charger_info"] = df.apply(chargers_including_combos, axis = 1)
    log_length("create DC_and_L2_charger_info column", df)
    # getting rid of stations without any L2 or DC chargers
    df = df[df["DC_and_L2_charger_info"] != "no L2 or DC chargers"]
    log_length("filter out rows with no L2 or DC chargers", df)

    # save the lengths of the data at each cleaning step to a text file
    lengths_output_path = os.path.join(SAVE_DIR, SAVE_FILE_NAME + "_cleaning_step_lengths.txt")
    with open(lengths_output_path, "w", encoding="utf-8") as length_file:
        for step_name, row_count in step_lengths:
            length_file.write(f"{step_name}: {row_count}\n")

    # save the cleaned data to a feather file
    df.to_feather(SAVE_DIR + "/" + SAVE_FILE_NAME + ".feather")

# read in uncleaned data
df = pd.read_feather(DATA_DIR + DATA_FILE)

# getting rid of non-networked and non-API stations
df = df[df['EV Network'].isin(API_NETWORKS)]

# creating cleaned API-stations-only data file
clean_data(df)