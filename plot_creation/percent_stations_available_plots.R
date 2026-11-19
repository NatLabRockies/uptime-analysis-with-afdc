###
# Title: GitHub Repo for the paper titled, "Alternative Fuels Data Center:
  # A New Resource to Measure the Uptime of Public EV Charging Stations"
# Contact: Robin.Steuteville@nlr.gov
# Creating percent stations operational over time plots
# Last updated: November 2026
###

require("rstudioapi")
# set the working directory to this script's folder, whether run in RStudio or via Rscript # nolint: line_length_linter.
if (rstudioapi::isAvailable()) {
  setwd(dirname(getActiveDocumentContext()$path))
} else {
  script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE) # nolint
  if (length(script_arg) > 0) setwd(dirname(normalizePath(sub("^--file=", "", script_arg)))) # nolint
}

# Load required libraries and set up the environment for plotting
require("formatR")
require("tidyr")
require("ggplot2")
library(dplyr)
library(forcats)
library(viridis)
library(glue)
library(grid)
library(ggpubr)


# ggplot theme used for most plots: minimal style, angled x-axis labels, legend on top # nolint

plot_theme <- function(x_axis, legend, legend_individual) {
  theme_minimal(base_family = "Helvetica") %+replace%
    theme(
      plot.title = element_text(size = 25, hjust = 0.5),
      axis.text.x = element_text(size = 18, hjust = 1, vjust = 1, angle = 45),
      axis.text.y = element_text(size = 18),
      axis.title.x = element_text(size = 23, face = "bold", vjust = -0.5),
      axis.title.y = element_text(
        size = 23, face = "bold", hjust = 0.5, vjust = 1.2, angle = 90
      ),
      legend.position = "top",
      legend.text = element_text(size = 16),
      legend.title = element_text(size = 23, face = "bold"),
      plot.margin = margin(5.5, 40, 5.5, 5.5),
    )
}

# same as plot_theme, but with the legend on the right side of the plot
plot_theme_side_legend <- function(x_axis, legend, legend_individual) {
  theme_minimal(base_family = "Helvetica") %+replace%
    theme(
      plot.title = element_text(size = 25, hjust = 0.5),
      axis.text.x = element_text(size = 18, hjust = 1, vjust = 1, angle = 45),
      axis.text.y = element_text(size = 18),
      axis.title.x = element_text(size = 23, face = "bold", vjust = -0.5),
      axis.title.y = element_text(size = 23, face = "bold", hjust = 0.5, vjust = 1.2, angle = 90), # nolint
      legend.text = element_text(size = 18),
      legend.title = element_text(size = 23, face = "bold"),
    )
}

# Record today's date to include in plot filenames
DATE <- format(Sys.Date(), "%m_%d_%y") # nolint

# Directory to save the finalized plots into
outdir <- "../results/plots"

# Create the output directory if it doesn't exist
if (!(file.exists(outdir))) {
  dir.create(file.path(outdir), recursive = TRUE)
}

# output of analysis/percent_stations_available_analysis.py, run on the example data # nolint

data_dir <- "../results/percentages_by_day/"

# Read in the processed data for plotting
df <- read.csv(paste0(data_dir, "all_data_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint
other_age_df <- read.csv(paste0(data_dir, "age_data_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint
yearly_age_df <- read.csv(paste0(data_dir, "age_data_percent_by_day_single_year.csv"), stringsAsFactors = FALSE) # nolint
other_yearly_age_df <- read.csv(paste0(data_dir, "age_data_percent_by_day_single_year_fewer_years.csv"), stringsAsFactors = FALSE) # nolint
network_df <- read.csv(paste0(data_dir, "network_data_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint
top_5_network_df <- read.csv(paste0(data_dir, "network_data_percent_by_day_top_5.csv"), stringsAsFactors = FALSE) # nolint
charger_df <- read.csv(paste0(data_dir, "charger_type_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint
region_df <- read.csv(paste0(data_dir, "region_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint
charger_num_df <- read.csv(paste0(data_dir, "num_chargers_percent_by_day.csv"), stringsAsFactors = FALSE) # nolint

# Convert the Date columns to Date objects for proper plotting
df$Date <- as.Date(df$Date, format = "%Y-%m-%d")
other_age_df$Date <- as.Date(other_age_df$Date, format = "%Y-%m-%d")
yearly_age_df$Date <- as.Date(yearly_age_df$Date, format = "%Y-%m-%d")
other_yearly_age_df$Date <- as.Date(other_yearly_age_df$Date, format = "%Y-%m-%d") # nolint
network_df$Date <- as.Date(network_df$Date, format = "%Y-%m-%d")
top_5_network_df$Date <- as.Date(top_5_network_df$Date, format = "%Y-%m-%d")
charger_df$Date <- as.Date(charger_df$Date, format = "%Y-%m-%d")
region_df$Date <- as.Date(region_df$Date, format = "%Y-%m-%d")
charger_num_df$Date <- as.Date(charger_num_df$Date, format = "%Y-%m-%d")

# Create x-axis scales for the plots
plot_x_axis <- scale_x_date(
  name = "Date",
  breaks = seq(min(df$Date), max(df$Date), by = "1 day"),
  labels = function(x) paste0( # nolint
    format(x, "%b. "), as.integer(format(x, "%d")), ",\n", format(x, "%Y")
  ),
  limits = range(df$Date),
  expand = c(0, 0)
)

# Identify the networks, excluding the "Average" category for plotting purposes
other_networks <- setdiff(unique(network_df$Network), "Average")
other_networks_top_5 <- setdiff(unique(top_5_network_df$Network), "Average")

# Overall: percent of all stations operational each day
plot <- ggplot(df, aes(x = Date, y = percent_available)) +
  plot_theme() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Station Open Year") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("overall_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint: line_length_linter.

# Station age: percent operational by station open year, in two-year bins
other_age_df$open_year <- factor(
  other_age_df$open_year,
  levels = c("2023 - 2024", "2021 - 2022", "2019 - 2020", "2017 - 2018", "2015 - 2016", "Before 2015") # nolint
)
plot <- ggplot(other_age_df, aes(x = Date, y = percent_available, group = open_year, color = open_year)) + # nolint
  plot_theme_side_legend() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Station\nOpen Year") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(
  plot,
  filename = paste0("age_percent_stations_available_", DATE, ".jpeg"),
  path = outdir,
  width = 3456,
  height = 2234,
  dpi = 254,
  units = "px",
  device = "jpeg"
)

# Station age: percent operational by single station open year (2015 on)
yearly_age_df$open_year <- factor(
  yearly_age_df$open_year,
  levels = c("2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "Before 2015") # nolint
)

plot <- ggplot(
  yearly_age_df,
  aes(x = Date, y = percent_available, group = open_year, color = open_year)
) +
  plot_theme() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Station Open Year") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("yearly_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint

# Station age: percent operational by single station open year (2020 on)
other_yearly_age_df$open_year <- factor(
  other_yearly_age_df$open_year,
  levels = c("2024", "2023", "2022", "2021", "2020", "Before 2020")
)

plot <- ggplot(other_yearly_age_df, aes(x = Date, y = percent_available, group = open_year, color = open_year)) + # nolint
  plot_theme_side_legend() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Station\nOpen Year") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(
  plot,
  filename = paste0("yearly_percent_stations_available_fewer_years_", DATE, ".jpeg"), # nolint
  path = outdir,
  width = 3456,
  height = 2234,
  dpi = 254,
  units = "px",
  device = "jpeg"
)


# Network: percent operational for each network, with the overall average in black # nolint
# (long network names are wrapped onto two lines for the legend)
network_avg <- df |>
  mutate(Network = "Average")

network_df_with_avg <- bind_rows(network_df, network_avg) |>
  mutate(Network = ifelse(Network == "MERCEDES_BENZ", "MERCEDES\nBENZ", Network)) %>% # nolint
  mutate(Network = ifelse(Network == "RIVIAN_ADVENTURE", "RIVIAN\nADVENTURE", Network)) %>% # nolint
  mutate(Network = ifelse(Network == "RIVIAN_WAYPOINTS", "RIVIAN\nWAYPOINTS", Network)) # nolint
other_networks <- ifelse(other_networks == "MERCEDES_BENZ", "MERCEDES\nBENZ", other_networks) # nolint
other_networks <- ifelse(other_networks == "RIVIAN_ADVENTURE", "RIVIAN\nADVENTURE", other_networks) # nolint
other_networks <- ifelse(other_networks == "RIVIAN_WAYPOINTS", "RIVIAN\nWAYPOINTS", other_networks) # nolint

plot <- ggplot(network_df_with_avg, aes(x = Date, y = percent_available, group = Network, color = Network)) + # nolint
  plot_theme() +
  geom_line(linewidth = 1) +
  scale_color_manual(
    values = c("Average" = "black", setNames(scales::hue_pal()(length(other_networks)), other_networks)), # nolint
    breaks = c("Average", other_networks)
  ) +
  ylab("Percent of stations operational") +
  labs(color = "Network") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("network_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint

# Top 5 networks: percent operational for the 5 networks with the most station-days, with their average in black # nolint
plot <- ggplot(top_5_network_df, aes(x = Date, y = percent_available, group = Network, color = Network)) + # nolint
  plot_theme() +
  geom_line(linewidth = 1) +
  scale_color_manual(
    values = c("Average" = "black", setNames(scales::hue_pal()(length(other_networks_top_5)), other_networks_top_5)), # nolint
    breaks = c("Average", other_networks_top_5)
  ) +
  ylab("Percent of stations operational") +
  labs(color = "Network") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("top_5_network_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint


# Charger type: percent operational for stations with L2 only, DC only, or both # nolint
plot <- ggplot(charger_df, aes(x = Date, y = percent_available, group = DC_and_L2_charger_info, color = DC_and_L2_charger_info)) + # nolint
  plot_theme() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Power Level") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("charge_level_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint

# Region: percent operational by US Census region
plot <- ggplot(region_df, aes(x = Date, y = percent_available, group = Region, color = Region)) + # nolint
  plot_theme() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Region") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("region_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint

# Station size: percent operational by number of ports (5 or under, 6-10, 11+)
charger_num_df$charger_num <- factor(
  charger_num_df$charger_num,
  levels = c("5 or under", "6-10", "11+")
)

plot <- ggplot(charger_num_df, aes(x = Date, y = percent_available, group = charger_num, color = charger_num)) + # nolint
  plot_theme() +
  geom_line(linewidth = 1) +
  ylab("Percent of stations operational") +
  labs(color = "Number of Ports") +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  plot_x_axis

ggsave(plot, filename = paste0("charger_num_percent_stations_available_", DATE, ".jpeg"), path = outdir, width = 3456, height = 2234, dpi = 254, units = "px", device = "jpeg") # nolint
