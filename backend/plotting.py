import matplotlib.pyplot as plt
import logging
from datetime import datetime
import pandas as pd


def plot_added_dates(added_dates):
    dates = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") for date in added_dates]

    # Create a DataFrame to group by month and year
    df = pd.DataFrame(dates, columns=["date"])
    df["year_month"] = df["date"].dt.to_period("M")
    grouped = df.groupby("year_month").size()

    # Plotting
    plt.figure(figsize=(10, 5))
    grouped.plot(kind="bar", edgecolor="black")
    plt.title("Tracks Added by Month")
    plt.xlabel("Month")
    plt.ylabel("Number of Tracks")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_path = "static/plot.png"
    plt.savefig(plot_path)
    plt.close()
    logging.info(f"Plot saved as {plot_path}")
    return plot_path
