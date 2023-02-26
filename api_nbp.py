import requests
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
from prettytable import PrettyTable

# Create a welcoming sentense to greet the user
input("Welcome to the investment analysis program for USD, EUR, and HUF currencies over a 30-day period. To begin, please press the 'Enter' key.")

# Retrieve the correct investment start date
while True:
    input_date = input("Enter a start date of the investment in the ISO 8601 format (YYYY-MM-DD): ")

    if len(input_date) == 10 and input_date[4] == "-" and input_date[7] == "-":
        try:
            start_date = datetime.strptime(input_date, '%Y-%m-%d').date()
            if (datetime.now().date() - start_date).days >= 30:
                break
            else:
                print("Invalid date. Enter a date that is at least 30 days old.")
        except ValueError:
            print("Date is not in the ISO 8601 format. Enter the date as YYYY-MM-DD.")
    else:
        print("Date is not in the ISO 8601 format. Enter the date as YYYY-MM-DD.")

# Retrieve the correct percentage for each currency
while True:
    try:
        usd_pct_start = float(input("Enter the percentage of USD (range of values from 0.0 to 1.0): "))
        eur_pct_start = float(input("Enter the percentage of EUR (range of values from 0.0 to 1.0): "))
        huf_pct_start = float(input("Enter the percentage of HUF (range of values from 0.0 to 1.0): "))

        if 0 <= usd_pct_start <= 1 and 0 <= eur_pct_start <= 1 and 0 <= huf_pct_start <= 1 and abs(usd_pct_start + eur_pct_start + huf_pct_start - 1) < 1e-10:
            break
        else:
            print("Incorrect value. The sum of the percentages of USD, EUR and HUF must be equal to 1.0")
    except ValueError:
        print("Invalid input. Please enter a valid number. Please note that the sum of the percentages of USD, EUR and HUF must be equal to 1.0")


# Construct the main function
def simulate_investment(start_date, usd_pct_start, eur_pct_start, huf_pct_start):

    # Set up investment parameter
    investment_amount_start = 1000.0
    end_date = start_date + timedelta(days=30)

    # Retrieve exchange rates for each currency
    usd_response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/A/USD/{start_date}/{end_date}/")
    eur_response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/A/EUR/{start_date}/{end_date}/")
    huf_response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/A/HUF/{start_date}/{end_date}/")

    # Extract all exchange rates from responses
    usd_rates_all = [rate["mid"] for rate in usd_response.json()["rates"]]
    eur_rates_all = [rate["mid"] for rate in eur_response.json()["rates"]]
    huf_rates_all = [rate["mid"] for rate in huf_response.json()["rates"]]

    # Define exchange rates for start_date and end_date
    usd_rate_start = usd_rates_all[0]
    eur_rate_start = eur_rates_all[0]
    huf_rate_start = huf_rates_all[0]

    usd_rate_end = usd_rates_all[-1]
    eur_rate_end = eur_rates_all[-1]
    huf_rate_end = huf_rates_all[-1]

    # Calculate investment values for each currency
    usd_investment = investment_amount_start * usd_pct_start / usd_rate_start
    eur_investment = investment_amount_start * eur_pct_start / eur_rate_start
    huf_investment = investment_amount_start * huf_pct_start / huf_rate_start

    # Convert investment values back to PLN after 30 days
    usd_investment_pln = usd_investment * usd_rate_end
    eur_investment_pln = eur_investment * eur_rate_end
    huf_investment_pln = huf_investment * huf_rate_end

    # Calculate end investment value in PLN
    investment_amount_end = usd_investment_pln + eur_investment_pln + huf_investment_pln

    # Calculate the percentage for each currency after the 30-day investment period
    usd_pct_end = usd_investment_pln / investment_amount_end
    eur_pct_end = eur_investment_pln / investment_amount_end
    huf_pct_end = huf_investment_pln / investment_amount_end

    # Calculate the profit or loss of an investment
    profit_or_loss = round(investment_amount_end - investment_amount_start, 2)

    # Create a table containing analysis of investment
    table = PrettyTable()
    table.field_names = ["Parameter", "Start Value", "End Value"]

    table.add_row(["Date", start_date, end_date])
    table.add_row(["USD Rates", usd_rate_start, usd_rate_end])
    table.add_row(["EUR Rates", eur_rate_start, eur_rate_end])
    table.add_row(["HUF Rates", round(huf_rate_start, 4), round(huf_rate_end, 4)])
    table.add_row(["USD pct", round(usd_pct_start, 2), round(usd_pct_end, 2)])
    table.add_row(["EUR pct", round(eur_pct_start, 2), round(eur_pct_end, 2)])
    table.add_row(["HUF pct", round(huf_pct_start, 2), round(huf_pct_end, 2)])
    table.add_row(["Investment Amount", investment_amount_start, round(investment_amount_end, 2)])
    table.add_row(["Profit / Loss", "-", profit_or_loss])


    # Create charts to visualize investment analysis results for USD, EUR, and HUF currencies
    # Create figure and subplots
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))

    # Create Percentage Distribution subplot
    pct_labels = ["USD", "EUR", "HUF"]
    start_pct = [usd_pct_start, eur_pct_start, huf_pct_start]
    end_pct = [usd_pct_end, eur_pct_end, huf_pct_end]

    x = np.arange(len(pct_labels))
    width = 0.45

    # Create two sets of bar charts, one for the initial percentage distribution (rects1) and one for the final percentage distribution (rects2)

    start_bars = axs[0].bar(x - width/2, start_pct, width, label='Start')
    end_bars = axs[0].bar(x + width/2, end_pct, width, label='End', alpha=0.5)

    # Attach a text label above each bar displaying its height
    for bar in start_bars + end_bars:
        height = bar.get_height()
        axs[0].annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    axs[0].set_xticks(x)
    axs[0].set_xticklabels(pct_labels)
    axs[0].set_title("Percentage Distribution")
    axs[0].set_ylim([0, 1])
    axs[0].legend()
    axs[0].set_ylabel('pct')

    # Create Exchange Rates subplot
    rate_labels = ["USD", "EUR", "HUF"]
    start_rates = [usd_rate_start, eur_rate_start, huf_rate_start]
    end_rates = [usd_rate_end, eur_rate_end, huf_rate_end]

    x = np.arange(len(rate_labels))
    width = 0.45

    # Create two sets of bar charts, one for the initial exchange rates (rects1) and one for the final exchange rates (rects2)

    start_bars = axs[1].bar(x - width/2, start_rates, width, label='Start')
    end_bars = axs[1].bar(x + width/2, end_rates, width, label='End', alpha=0.5)

    # Attach a text label above each bar displaying its height
    for bar in start_bars + end_bars:
        height = bar.get_height()
        axs[1].annotate(f"{height:.3f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    axs[1].set_xticks(x)
    axs[1].set_xticklabels(rate_labels)
    axs[1].set_title("Exchange Rates")
    axs[1].set_ylim([0, max(max(start_rates), max(end_rates))*1.1])
    axs[1].legend()
    axs[1].set_ylabel('PLN')

    # Create Investment Amount subplot
    inv_labels = ["Start", "End"]
    inv_values = [investment_amount_start, investment_amount_end]

    start_bars = axs[2].bar(inv_labels, inv_values, color=[start_bars[0].get_facecolor(), end_bars[0].get_facecolor()])

    # Attach a text label above each bar displaying its height
    for bar in start_bars:
        height = bar.get_height()
        axs[2].annotate(f"{height:.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    axs[2].set_title("Investment Amount")
    axs[2].set_ylim([0, max(inv_values)*1.1])
    axs[2].set_ylabel('PLN')

    # Add a title for the whole figure
    fig.suptitle(f"Investment Analysis - duration 30 days\nStart: {start_date} End: {end_date}")

    # Adjust spacing between subplots
    plt.tight_layout()

    # Display the plot
    plt.show()

    # Provide additional functionality for exporting obtained data to a JSON file
    # Create a list of dictionaries containing the data for each date
    data = [
        {
            "date": start_date.strftime("%Y-%m-%d"),
            "investment_amount": investment_amount_start,
            "usd_pct": usd_pct_start,
            "eur_pct": eur_pct_start,
            "huf_pct": huf_pct_start,
            "usd_rate": usd_rate_start,
            "eur_rate": eur_rate_start,
            "huf_rate": huf_rate_start
        },
        {
            "date": end_date.strftime("%Y-%m-%d"),
            "investment_amount": investment_amount_end,
            "usd_pct": usd_pct_end,
            "eur_pct": eur_pct_end,
            "huf_pct": huf_pct_end,
            "usd_rate": usd_rate_end,
            "eur_rate": eur_rate_end,
            "huf_rate": huf_rate_end
        }
    ]

    # Save data as JSON file
    with open("exchange_rates.json", "w") as f:
        json.dump(data, f)
    
    return table

answer = simulate_investment(start_date, usd_pct_start, eur_pct_start, huf_pct_start)
print(answer)