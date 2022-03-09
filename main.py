from bs4 import BeautifulSoup
import requests
import pickle
import string


class ItemOdds:
    kniv = 0.0025575
    covert = 0.0063939
    classified = 0.0319693
    restricted = 0.1598466
    milspec = 0.792327
    stattrak = 0.1


class FloatOdds:
    fn = 0.07
    mw = 0.08
    ft = 0.22
    ww = 0.07
    bs = 0.56


floatbase = {
    "Factory New": 0.07,
    "Minimal Wear": 0.08,
    "Field-Tested": 0.22,
    "Well-Worn": 0.07,
    "Battle-Scarred": 0.56
}


class Case:
    def __init__(self, name, weapons, price):
        self.name = name
        self.weapons = weapons
        self.price = price


class Weapon:
    def __init__(self, name, float_min, float_max, prices, stprices):
        self.name = name  # STR
        self.float_min = float_min
        self.float_max = float_max
        self.prices = prices  # DICT KEY=FLOATBASE | VALUE=PRICE IN EURO
        self.stprices = stprices


def collect_case_links():
    page = BeautifulSoup(requests.get("https://csgostash.com").content, 'html.parser')
    case_links = []
    price = None
    for i in page.find_all('a', href=True):
        if "/case/" in i['href']:
            case_links.append(str(i['href']))
    return case_links


def collect_case_info(case_link):
    page = BeautifulSoup(requests.get(case_link).content, 'html.parser')
    name = case_link.split("/")[len(case_link.split("/"))-1].replace("-", " ")
    weapons = []
    price = float(
        str(page.find("a", class_="btn btn-default market-button-item").contents[0]).split('€')[0].replace(",", ".")
    )
    for i in page.find_all('a', class_="price-st"):
        weapons.append(collect_wpn_info(i['href']))
    return Case(name, weapons, price)


def collect_wpn_info(wpn_link):
    page = BeautifulSoup(requests.get(wpn_link).content, 'html.parser')
    name = str(page.find("title").contents[0]).replace(" - CS:GO Stash", '')
    floats = []
    for cursor in page.find_all('div', class_="marker-value cursor-default"):
        floats.append(float(cursor.contents[0]))
    float_min = floats[0]
    float_max = floats[1]
    prices = {}
    stprices = {}
    for i in page.find_all("a", class_="market-button-skin"):
        if "Market Listings" not in i.contents[0]:
            conditions = i.find_all("span", class_="pull-left")
            if len(conditions) > 1:
                key = conditions[1].contents[0]
                try:
                    value = float(i.find("span", class_="pull-right").contents[0].replace(",", ".").split('€')[0])
                except ValueError:
                    if "o" not in str(i.find("span", class_="pull-right").contents[0]):
                        value = float(i.find("span", class_="pull-right").contents[0].split(",")[0])
                    else:
                        value = None
                stprices[key] = value
            elif conditions:
                key = conditions[0].contents[0]
                try:
                    value = float(i.find("span", class_="pull-right").contents[0].replace(",", ".").split('€')[0])
                except ValueError:
                    if "o" not in str(i.find("span", class_="pull-right").contents[0]):
                        value = float(i.find("span", class_="pull-right").contents[0].split(",")[0])
                    else:
                        value = None
                prices[key] = value
            else:
                break
    return Weapon(name, float_min, float_max, prices, stprices)


def load_from_file():
    try:
        with open("savefile.pkl") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return False


def save_file(saveinfo):
    with open("savefile.pkl", "w") as f:
        pickle.dump(saveinfo, f)


def __main__():
    case_links = collect_case_links()
    print(case_links)
    cases = []
    for i in range(0, len(case_links)):
        case = collect_case_info(case_links[i])
        cases.append(case)
        print(f"{case.name} Completed!")
    print("Scraping complete!")
    while True:
        for i in range(0, len(cases)):
            print(f"{i}: {cases[i].name}")
        choice = cases[int(input("Choose case: "))]
        for i in range(0, len(choice.weapons)):
            print(f"{i}: {cases[i].name}")
        choice = choice.weapons[int(input("Choose weapon: "))]
        print(f"ST Prices: {choice.stprices}")
        print(f"Prices: {choice.prices}")
        input("...")


if __name__ == "__main__":
    __main__()
