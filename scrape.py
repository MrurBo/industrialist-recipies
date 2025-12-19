#!/.venv/bin/python3
"""
Made my MrurBo (welp.2564)

Licenced under GPLv3
"""

import requests
import bs4
import json
import time
from pathlib import Path
import sys

base = "https://industrialist.fandom.com"
CACHE_TTL = 60 * 60 * 24
EXCLUDE = [
    "/wiki/Breaker_Box",
    "/wiki/Tree_Farm",
    "/wiki/Modular_Diesel_Engine",
    "/wiki/Modular_Turbine",
    "/wiki/Modular_Research_Station",
    "/wiki/Research_Tracking_Panel",
]


class Cache:
    def __init__(self, filepath, ttl):
        self.ttl = ttl
        self.path = Path(filepath)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self):
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {}

    def _write(self, obj):
        self.path.write_text(json.dumps(obj, indent=2))

    def get(self, key):
        cache = self._read()
        entry = cache.get(key)

        if not entry:
            return None

        if entry["expires"] < time.time():
            del cache[key]
            self._write(cache)
            return None

        return entry["value"]

    def set(self, key, value):
        cache = self._read()
        cache[key] = {
            "expires": time.time() + self.ttl,
            "value": value,
        }
        self._write(cache)


cache = Cache("tmp/cache.json", CACHE_TTL)


def echo(r=None):
    return r


def get_links_for_categories(page):
    url = base + page

    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")

    galleries = soup.select('div[id^="gallery-"]')
    links = []
    for gallery in galleries:
        for row in gallery.find_all(recursive=False):
            if not "wikia-gallery-row" in list(row.get("class")):
                continue
            for item in row.find_all(recursive=False):
                links.append(
                    item.find("div", {"class": "thumb"})
                    .find("div")
                    .find("a")
                    .get("href")
                )
    return links


def get_all_machines():
    cached = cache.get("machines")
    if cached:
        return cached

    res = {}
    links = get_links_for_categories("/wiki/Machines_%26_Models")

    for link in links:
        res[link] = get_links_for_categories(link)

    cache.set("machines", res)
    return res


def get_recipe(machine):
    url = base + machine
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    recipies = []
    for recipe in soup.find_all("div", class_="production-rectangle"):
        arrow = recipe.select_one(".arrow-container")
        if not arrow:
            continue  # safety

        # --- INPUTS (before arrow) ---
        inputs = []
        for box in arrow.find_previous_siblings("div", class_="icon-box"):
            tmp = box.select_one(".unit-number")
            if not tmp:
                tmp = 1
            else:
                tmp = tmp.text.strip()

            inputs.append(
                {
                    "link": box.select_one("a")["href"],
                    "amount": tmp,
                }
            )
        inputs.reverse()  # keep visual order

        # --- OUTPUTS (after arrow) ---
        outputs = []
        for box in arrow.find_next_siblings("div", class_="icon-box"):
            tmp = box.select_one(".unit-number")
            if not tmp:
                tmp = 1
            else:
                tmp = tmp.text.strip()

            outputs.append(
                {
                    "link": box.select_one("a")["href"],
                    "amount": tmp,
                }
            )

        # --- TIME + ENERGY ---
        arrow_texts = arrow.select(".arrow-text")
        time = arrow_texts[0].text.strip() if len(arrow_texts) > 0 else None
        energy = arrow_texts[1].text.strip() if len(arrow_texts) > 1 else None

        result = {
            "inputs": inputs,
            "outputs": outputs,
            "time": time,
            "energy": energy,
        }

        recipies.append(result)
    return recipies


def get_machine_data(machine):
    cache_key = f"machine:{machine}"

    cached = cache.get(cache_key)
    if cached:
        # print("getting cached")
        return cached
    url = base + machine
    r = requests.get(url)
    if r.status_code != 200:
        print("ERROR: Invalid response code: " + str(r.status_code))
        sys.exit(-1)
    soup = bs4.BeautifulSoup(r.text, "html.parser")

    data = {"name": None, "attributes": {}, "sections": {}, "recipies": []}

    # ---------- CASE 1: portable infobox ----------
    infobox = soup.find("aside", class_="portable-infobox")
    if infobox:
        # NAME
        title = infobox.find("h2", class_="pi-title")
        if title:
            data["name"] = title.get_text(strip=True)

        current_section = None

        for item in infobox.find_all("section", class_="pi-group"):
            header = item.find("h2", class_="pi-header")
            section_name = header.get_text(strip=True) if header else "General"

            section_data = {}

            for row in item.find_all("div", class_="pi-data"):
                label_div = row.find("h3", class_="pi-data-label")
                value_div = row.find("div", class_="pi-data-value")

                if not label_div or not value_div:
                    continue

                label = label_div.get_text(" ", strip=True)
                value = value_div.get_text(" ", strip=True)

                section_data[label] = value

            data["sections"][section_name] = section_data

        # also grab top-level attributes (Tier, Category, etc.)
        for row in infobox.find_all("div", class_="pi-data", recursive=False):
            label_div = row.find("h3", class_="pi-data-label")
            value_div = row.find("div", class_="pi-data-value")
            if label_div and value_div:
                label = label_div.get_text(" ", strip=True)
                value = value_div.get_text(" ", strip=True)
                data["attributes"][label] = value
        data["recipies"] = get_recipe(machine)
        cache.set(cache_key, data)
        return data

    # ---------- CASE 2: legacy machine_infobox ----------
    infobox = soup.find("div", class_="machine_infobox")
    if not infobox:
        return None

    # NAME
    data["name"] = (
        infobox.find("div", class_="title").find(string=True, recursive=False).strip()
    )

    # remove everything before category
    for child in list(infobox.find_all(recursive=False)):
        classes = child.get("class", [])
        child.decompose()
        if "category" in classes:
            break

    # ATTRIBUTES
    for item in infobox.find_all(recursive=False):
        classes = item.get("class", [])
        if "information" not in classes:
            continue

        header_div = item.find("div", class_="header")
        label = header_div.get_text(" ", strip=True) if header_div else None

        value = None

        input_div = item.find("div", class_="input")
        if input_div:
            value = input_div.get_text(" ", strip=True)

        if value is None:
            p_input = item.select_one(".mobile_fix p.input")
            if p_input:
                value = p_input.get_text(strip=True)

        if label:
            data["attributes"][label] = value
    data["recipies"] = get_recipe(machine)
    cache.set(cache_key, data)
    return data


def get_all_machine_data():

    categories = get_all_machines()
    res = []
    # print(categories)
    for _, category in categories.items():
        # print(category)
        for machine in category:
            # print(machine)
            if "Upload" in machine:
                continue
            if machine in EXCLUDE:
                continue
            data = get_machine_data(machine)
            res.append(data)

    return res


data = get_all_machine_data()

path = Path("./data.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.touch()
with open("./data.json", "w") as f:
    json.dump(data, f)
# print(get_machine_data("/wiki/Geothermal_Well"))
