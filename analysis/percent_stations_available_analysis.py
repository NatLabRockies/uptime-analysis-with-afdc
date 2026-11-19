# ruff: noqa: INP001
###
# Title: GitHub Repo for the paper titled, "Alternative Fuels Data Center: A New Resource to Measure the Uptime of Public EV Charging Stations"
# Contact: Robin.Steuteville@nlr.gov
# Last updated: November 2026
###

# import libraries
from pathlib import Path

import pandas as pd

# reads the output of data_cleaning/clean_data_for_percent_stations_available_analysis.py
DATA_DIR = "../results/cleaned_data/"
SAVE_DIR = "../results/percentages_by_day"
MIN_UNIQUE_DATES = 365
if not Path(SAVE_DIR).exists():
    Path(SAVE_DIR).mkdir(parents=True)

sub_df_length_records = []


def record_sub_df_length(
    group_name: str,
    category: object,
    sub_df: pd.DataFrame,
) -> None:
    """Record the number of rows in a grouping's subset (written to sub_df_lengths.txt at the end)."""
    sub_df_length_records.append(f"{group_name}\t{category}\t{len(sub_df)}")


# Cleaned file name
file_name = "example_data_2023_01_cleaned.feather"

# Read in the cleaned data
df = pd.read_feather(DATA_DIR + file_name)

# Create empty DataFrames for storing percent available by day for different categories
all_data_percent_by_day = pd.DataFrame(
    columns=["Date", "percent_available", "percent_unavailable"],
)
age_data_percent_by_day = pd.DataFrame(
    columns=["open_year", "Date", "percent_available", "percent_unavailable"],
)
age_data_percent_by_day_single_year = pd.DataFrame(
    columns=["open_year", "Date", "percent_available", "percent_unavailable"],
)
age_data_percent_by_day_single_year_fewer_years = pd.DataFrame(
    columns=["open_year", "Date", "percent_available", "percent_unavailable"],
)
network_data_percent_by_day = pd.DataFrame(
    columns=["Network", "Date", "percent_available", "percent_unavailable"],
)
network_data_percent_by_day_top_5 = pd.DataFrame(
    columns=["Network", "Date", "percent_available", "percent_unavailable"],
)
charger_type_percent_by_day = pd.DataFrame(
    columns=[
        "DC_and_L2_charger_info",
        "Date",
        "percent_available",
        "percent_unavailable",
    ],
)
region_percent_by_day = pd.DataFrame(
    columns=["Region", "Date", "percent_available", "percent_unavailable"],
)
num_chargers_percent_by_day = pd.DataFrame(
    columns=["charger_num", "Date", "percent_available", "percent_unavailable"],
)
num_chargers_percent_by_day_for_comb = pd.DataFrame(
    columns=["charger_num", "Date", "percent_available", "percent_unavailable"],
)


def create_percent_by_day(
    df: pd.DataFrame,
    percent_df: pd.DataFrame,
    other_category: str = "",
) -> pd.DataFrame:
    """
    Append daily station availability percentages to `percent_df`.

    The percentages cover available (E) and temporarily unavailable (T) stations in
    `df`; `other_category` labels each appended date when provided.
    """
    for date in df["DATE"].unique():
        df_date: pd.DataFrame = df[df["DATE"] == date]
        percent_available = (
            df_date["Status Code"].value_counts(normalize=True) * 100
        ).get("E", 0)
        percent_unavailable = (
            df_date["Status Code"].value_counts(normalize=True) * 100
        ).get("T", 0)
        if other_category == "":
            percent_df.loc[len(percent_df)] = [
                date,
                percent_available,
                percent_unavailable,
            ]
        else:
            percent_df.loc[len(percent_df)] = [
                other_category,
                date,
                percent_available,
                percent_unavailable,
            ]

    percent_df["Date"] = percent_df["Date"].astype(str)
    percent_df["percent_available"] = percent_df["percent_available"].astype(float)
    percent_df["percent_unavailable"] = percent_df["percent_unavailable"].astype(float)
    return percent_df


# create percent available by day df for all data
all_data_percent_by_day = create_percent_by_day(df, all_data_percent_by_day)

all_data_percent_by_day.to_csv(SAVE_DIR + "/all_data_percent_by_day.csv", index=False)

# create percent available by day df by network
for network in df["EV Network"].unique():
    network_df = df[df["EV Network"] == network]
    record_sub_df_length("EV Network", network, network_df)
    network_data_percent_by_day = create_percent_by_day(
        network_df,
        network_data_percent_by_day,
        other_category=network,
    )

network_data_percent_by_day.to_csv(
    SAVE_DIR + "/network_data_percent_by_day.csv",
    index=False,
)

# create percent available by day df for top 5 networks
top_5_networks = df["EV Network"].value_counts().head(5).index

top_5_networks_df = df[df["EV Network"].isin(top_5_networks)]

# calculate average for top 5 networks
for date in top_5_networks_df["DATE"].unique():
    df_date: pd.DataFrame = top_5_networks_df[top_5_networks_df["DATE"] == date]
    percent_available = (df_date["Status Code"].value_counts(normalize=True) * 100).get(
        "E",
        0,
    )
    percent_unavailable = (
        df_date["Status Code"].value_counts(normalize=True) * 100
    ).get("T", 0)
    network_data_percent_by_day_top_5.loc[len(network_data_percent_by_day_top_5)] = [
        "Average",
        date,
        percent_available,
        percent_unavailable,
    ]

network_data_percent_by_day_top_5["Date"] = network_data_percent_by_day_top_5[
    "Date"
].astype(str)
network_data_percent_by_day_top_5["percent_available"] = (
    network_data_percent_by_day_top_5["percent_available"].astype(float)
)
network_data_percent_by_day_top_5["percent_unavailable"] = (
    network_data_percent_by_day_top_5["percent_unavailable"].astype(float)
)

for network in top_5_networks_df["EV Network"].unique():
    network_df = top_5_networks_df[top_5_networks_df["EV Network"] == network]
    record_sub_df_length("Top 5 EV Network", network, network_df)
    network_data_percent_by_day_top_5 = create_percent_by_day(
        network_df,
        network_data_percent_by_day_top_5,
        other_category=network,
    )

network_data_percent_by_day_top_5.to_csv(
    SAVE_DIR + "/network_data_percent_by_day_top_5.csv",
    index=False,
)

# create percent available by day df by age category
for year_category in df["other_age_category"].unique():
    year_df = df[df["other_age_category"] == year_category]
    record_sub_df_length("other_age_category", year_category, year_df)
    age_data_percent_by_day = create_percent_by_day(
        year_df,
        age_data_percent_by_day,
        other_category=year_category,
    )

age_data_percent_by_day.to_csv(SAVE_DIR + "/age_data_percent_by_day.csv", index=False)

# create percent available by day df by single year age category
for year_category in df["single_year_age_category"].unique():
    year_df = df[df["single_year_age_category"] == year_category]
    record_sub_df_length("single_year_age_category", year_category, year_df)
    age_data_percent_by_day_single_year = create_percent_by_day(
        year_df,
        age_data_percent_by_day_single_year,
        other_category=year_category,
    )

age_data_percent_by_day_single_year.to_csv(
    SAVE_DIR + "/age_data_percent_by_day_single_year.csv",
    index=False,
)

# create percent available by day df by single year age category with fewer years
for year_category in df["single_year_age_category_fewer_years"].unique():
    year_df = df[df["single_year_age_category_fewer_years"] == year_category]
    record_sub_df_length("single_year_age_category_fewer_years", year_category, year_df)
    age_data_percent_by_day_single_year_fewer_years = create_percent_by_day(
        year_df,
        age_data_percent_by_day_single_year_fewer_years,
        other_category=year_category,
    )

age_data_percent_by_day_single_year_fewer_years.to_csv(
    SAVE_DIR + "/age_data_percent_by_day_single_year_fewer_years.csv",
    index=False,
)

# create percent available by day df by charger type
for charger_category in df["DC_and_L2_charger_info"].unique():
    charger_df = df[df["DC_and_L2_charger_info"] == charger_category]
    record_sub_df_length("DC_and_L2_charger_info", charger_category, charger_df)
    charger_type_percent_by_day = create_percent_by_day(
        charger_df,
        charger_type_percent_by_day,
        other_category=charger_category,
    )

charger_type_percent_by_day.to_csv(
    SAVE_DIR + "/charger_type_percent_by_day.csv",
    index=False,
)

# create percent available by day df by region
for region in df["Region"].unique():
    region_df = df[df["Region"] == region]
    record_sub_df_length("Region", region, region_df)
    region_percent_by_day = create_percent_by_day(
        region_df,
        region_percent_by_day,
        other_category=region,
    )

region_percent_by_day.to_csv(SAVE_DIR + "/region_percent_by_day.csv", index=False)

# create percent available by day df by number of chargers
for charge_num in df["station_size"].unique():
    charge_num_df = df[df["station_size"] == charge_num]
    record_sub_df_length("station_size", charge_num, charge_num_df)
    num_chargers_percent_by_day = create_percent_by_day(
        charge_num_df,
        num_chargers_percent_by_day,
        other_category=charge_num,
    )

num_chargers_percent_by_day.to_csv(
    SAVE_DIR + "/num_chargers_percent_by_day.csv",
    index=False,
)

# more granular look at number of chargers
for charge_num in df["total_chargers"].dropna().unique():
    charge_num_df = df[df["total_chargers"] == charge_num]
    record_sub_df_length("total_chargers", charge_num, charge_num_df)
    num_chargers_percent_by_day_for_comb = create_percent_by_day(
        charge_num_df,
        num_chargers_percent_by_day_for_comb,
        other_category=charge_num,
    )

num_chargers_percent_by_day_mean = (
    num_chargers_percent_by_day_for_comb.groupby("charger_num")["percent_available"]
    .mean()
    .reset_index()
)

num_stations_at_each_charger_num = df["total_chargers"].value_counts().reset_index()
num_stations_at_each_charger_num.columns = ["charger_num", "num_total_station_days"]
num_chargers_percent_by_day_mean = num_chargers_percent_by_day_mean.merge(
    num_stations_at_each_charger_num,
    on="charger_num",
    how="outer",
)

num_chargers_percent_by_day_mean.to_csv(
    SAVE_DIR + "/perc_avail_by_num_chargers.csv",
    index=False,
)

# more granular look at number of chargers, only including port numbers with sufficient data

# NOTE: This code is included to show the approach for analyzing uptime by port size,
# but with the small example dataset all data is excluded since one of the requirements
# for inclusion for each port size was to have at least one year of data (365 unique dates) and the example
# data only includes one week of data.

station_days_per_port_num = df.groupby(["total_chargers", "DATE"]).size().reset_index()
station_days_per_port_num.columns = ["charger_num", "DATE", "num_stations"]
station_days_per_port_num.to_csv(
    SAVE_DIR + "/station_days_per_port_num.csv",
    index=False,
)

unique_dates_per_port = (
    station_days_per_port_num.groupby("charger_num")["DATE"].nunique().reset_index()
)
unique_dates_per_port.columns = ["charger_num", "num_unique_dates"]

avg_stations_per_date = (
    station_days_per_port_num.groupby("charger_num")["num_stations"]
    .mean()
    .reset_index()
)
avg_stations_per_date.columns = ["charger_num", "avg_stations_per_date"]

info_by_port_no = unique_dates_per_port.merge(avg_stations_per_date, on="charger_num")

info_by_port_no = info_by_port_no.merge(
    num_chargers_percent_by_day_mean,
    on="charger_num",
)

info_by_port_no.to_csv(SAVE_DIR + "/info_by_port_no_before_filtering.csv", index=False)

info_by_port_no = info_by_port_no[
    info_by_port_no["num_unique_dates"] >= MIN_UNIQUE_DATES
]  # at least 1 year of data

info_by_port_no.to_csv(
    SAVE_DIR + "/info_by_port_no_after_date_filtering_for_1_year_of_data.csv",
    index=False,
)

info_by_port_no = info_by_port_no[
    info_by_port_no["avg_stations_per_date"] >= 10
]  # at least 10 stations reporting on average per day

info_by_port_no.to_csv(SAVE_DIR + "/info_by_port_no.csv", index=False)

# Record the number of data points in each category
with (Path(SAVE_DIR) / "sub_df_lengths.txt").open("w") as f:
    f.write("group\tcategory\trow_count\n")
    f.write("\n".join(sub_df_length_records))
