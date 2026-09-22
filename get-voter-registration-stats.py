import csv
import os
import re
import time
from datetime import date

import requests

from config import EVENT_IDS

URL = "https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics"
PROVINCE_DROPDOWN = "ctl00$MainContent$ddlProvinces"
MUNICIPALITY_DROPDOWN = "ctl00$MainContent$ddlMunicipalities"
AGE_GROUPS = {
    "18": "18-19",
    "20": "20-29",
    "30": "30-39",
    "40": "40-49",
    "50": "50-59",
    "60": "60-69",
    "70": "70-79",
    "80": "80+",
}
SECONDS_BETWEEN_REQUESTS = 1

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (OpenUp IEC data scraper)"


def hidden_fields(html):
    return dict(
        re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html)
    )


def options(html, dropdown_id):
    select = re.search(rf'id="{dropdown_id}".*?</select>', html, re.S).group(0)
    return [
        (value, name.strip())
        for value, name in re.findall(r'<option[^>]*value="([^"]+)"[^>]*>([^<]*)', select)
        if value != "-1"
    ]


def post_back(html, target, province_id, municipality_id="-1"):
    time.sleep(SECONDS_BETWEEN_REQUESTS)
    data = hidden_fields(html)
    data.update(
        {
            "__EVENTTARGET": target,
            "__EVENTARGUMENT": "",
            PROVINCE_DROPDOWN: province_id,
            MUNICIPALITY_DROPDOWN: municipality_id,
        }
    )
    response = session.post(URL, data=data)
    response.raise_for_status()
    return response.text


def age_gender_counts(html):
    """{("20", "Male"): 129951, ..., ("Overall", "Female"): 1115674}"""
    counts = {}
    for age_group, gender, count in re.findall(
        r'id="MainContent_uxAgeGroup(\d+|Overall)[A-Za-z]*?ProgressChart(Male|Female)Totals"'
        r"[^>]*>\s*([\d,]+)\s*<",
        html,
    ):
        counts.setdefault((age_group, gender), int(count.replace(",", "")))
    return counts


def save_html(html, directory, filename):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{filename}.html", "w") as file:
        file.write(html)


def write_csv(rows, output_directory, filename):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open(f"{output_directory}/{filename}", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_directory}/{filename}")


scraped_on = date.today().isoformat()
gender_rows = []
age_rows = []


def add_rows(html, level, province_id="", province="", municipality_id="", municipality=""):
    counts = age_gender_counts(html)
    if ("Overall", "Male") not in counts:
        print(f"Warning: no figures found for {level} {province} {municipality}")
        return

    place = {
        "Level": level,
        "ProvinceID": province_id,
        "Province": province,
        "MunicipalityID": municipality_id,
        "Municipality": municipality,
    }
    male = counts[("Overall", "Male")]
    female = counts[("Overall", "Female")]
    gender_rows.append(
        {**place, "Male": male, "Female": female, "Total": male + female, "ScrapedOn": scraped_on}
    )
    for key, age_group in AGE_GROUPS.items():
        male = counts.get((key, "Male"), "")
        female = counts.get((key, "Female"), "")
        age_rows.append(
            {
                **place,
                "AgeGroup": age_group,
                "Male": male,
                "Female": female,
                "Total": male + female if male != "" and female != "" else "",
                "ScrapedOn": scraped_on,
            }
        )


for event_id in EVENT_IDS:
    html_directory = f"data/{event_id}/voter-registration/{scraped_on}"
    output_directory = f"output/pre-election/{event_id}"

    national_html = session.get(URL).text
    save_html(national_html, html_directory, "national")
    add_rows(national_html, "National")

    for province_id, province in options(national_html, "MainContent_ddlProvinces"):
        print(f"{province_id} {province}")
        province_html = post_back(national_html, PROVINCE_DROPDOWN, province_id)
        save_html(province_html, html_directory, f"province-{province_id}")
        add_rows(province_html, "Province", province_id, province)

        for municipality_id, municipality in options(province_html, "MainContent_ddlMunicipalities"):
            print(f"  {municipality_id} {municipality}")
            municipality_html = post_back(
                province_html, MUNICIPALITY_DROPDOWN, province_id, municipality_id
            )
            save_html(municipality_html, html_directory, f"municipality-{municipality_id}")
            add_rows(
                municipality_html, "Municipality", province_id, province, municipality_id, municipality
            )

    write_csv(gender_rows, output_directory, "registered-voters-by-gender.csv")
    write_csv(age_rows, output_directory, "registered-voters-by-age.csv")
