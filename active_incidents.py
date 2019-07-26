"""Script checks the HPD Active incidents site for any active incidents
within a set radius of location and returns the details of any events that
fall within the radius.

Notes:
    - [ ] may wish to also search twitter using data from site
"""

import requests  # from pathlib import Path
import bs4  # beautiful soup 4
import sqlite3


def get_incidents(data_source="all"):
    """Scrape HPD active incidents for current incidents.

    Returns (tuple):
        headings (list): data headings scraped from site
        data_list (list): list of row lists containing the actual data

    """

    active_incidents_base_url = r"https://cohweb.houstontx.gov/ActiveIncidents/"

    active_incidents_end = r"Combined.aspx?agency="

    # human readable agency= suffixes
    AGENCY_CODES = {"all": "%", "HFD": "F", "HPD": "P"}

    request_url = (
        active_incidents_base_url + active_incidents_end + AGENCY_CODES[data_source]
    )

    # get the URL from website
    res = requests.get(active_incidents_base_url + active_incidents_end)
    # kill script if an error occurs
    res.raise_for_status()

    # get the raw html from requests object
    html = bs4.BeautifulSoup(res.text, features="html.parser")

    # the grid of data is in a table with id='GridView2' and this grabs rows
    data_table = html.select("#GridView2 > tr")

    # the first row contains the table headings as inner html
    headings_html = data_table[0]

    # create a list of headings found in the table
    headings = []
    for heading in headings_html.select("th"):
        headings.append(heading.getText())

    num_columns = len(headings)

    # container for rows of data
    data_list = []

    # populate the data list with rows of lists
    for row_html in data_table[1:]:
        data_row = []
        for datum in row_html.select("td"):
            data_row.append(datum.getText())
        data_list.append(data_row)

    return headings, data_list


def lists_to_db():
    """Save list of lists to SQLite database"""
    pass


if __name__ == "__main__":
    incident_data = get_incidents()
