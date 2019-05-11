import re
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

if __name__ == "__main__":
    testing = True
    inner = re.compile("\(([^()]*)\)")
    url = "https://www.google.com/flights?hl=en#flt=CLT.DEN.2019-05-23*DEN.CLT.2019-05-27;c:USD;e:1;sd:1;t:f"
    if not testing:
        use_default = input("Do you want to use the default values for this program? Yes/No \n")
        while use_default.lower() not in ['yes', 'y', 'no', 'n']:
            use_default = input("\nDo you want to use the default values for this program? Yes/No \n")
        if use_default in ['y', 'yes']:
            use_default = True
            url = "https://www.google.com/flights?hl=en#flt=CLT.DEN.2019-05-23*DEN.CLT.2019-05-27;c:USD;e:1;sd:1;t:f"
        else:
            use_default = False

        if not use_default:
            departure = input("What airport are you wanting to leave from? (Airport 3 Character Code)\n")
            while len(departure) != 3:
                departure = input("\nWhat airport are you wanting to leave from? (Airport 3 Character Code")

            departure_date = input("When are you wanting to leave? (eg. 01/01/2019) \n")
            while len(departure_date) != 10:
                departure_date = input("\nWhen are you wanting to leave? (eg. 01/01/2019) \n")
            temp_depart = departure_date.split("/")
            depart_year = temp_depart[2]
            depart_month = temp_depart[1]
            depart_day = temp_depart[0]

            arrival = input("What airport are you wanting to arrive at? (Airport 3 Character Code) \n")
            while len(arrival) != 3:
                arrival = input("\nWhat airport are you wanting to arrive at? (Airport 3 Character Code) \n ")

            arrival_date = input("When are you wanting to arrive in {}? ".format(arrival))
            while len(arrival_date) != 10:
                arrival_date = input("\nWhen are you wanting to arrive in {}? \n".format(arrival))
            temp_arrive = arrival_date.split("/")
            arrival_year = temp_arrive[2]
            arrival_month = temp_arrive[1]
            arrival_day = temp_arrive[0]

            url = "https://www.google.com/flights?hl=en#flt={}.{}.{}-{}-{}*{}.{}.{}-{}-{};c:USD;e:1;sd:1;t:f".format(departure,arrival, depart_year, depart_month, depart_day, arrival, departure, arrival_year, arrival_month, arrival_day)
    # print("Using default? {}, here is URL: {}".format(use_default, url))
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["phantomjs.page.settings.userAgent"] = \
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/74.0.3729.131 Safari/537.36"
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              desired_capabilities=dcap,
                              service_args=['--ignore-ssl-errors=true'])
    driver.implicitly_wait(20)
    driver.get(url)
    python_button = driver.find_elements_by_xpath("//*[contains(text(), 'Price graph')]")       # Find the graph button to click
    for button in python_button:
        try:
            # Adding pauses because the clicks data isnt being populated fast enough.
            time.sleep(1)
            button.click()
            time.sleep(1)
        except Exception as err:
            print("Error when attempting to click button: ", err)

    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    prices = soup.findAll('div', attrs={'class': 'gws-flights-widgets-pricegraph__bar-item-container'})
    labels = soup.findAll('div', attrs={'class': 'pelKdaoeDW8__ylabels'})
    for t in labels:
        max_value = int(float(t.contents[-1].text.replace("$", "")) * 1.05)

    # prices = soup.findAll('div', attrs={'class': ['flt-subhead1 gws-flights-results__price',
    #                                               'flt-subhead1 gws-flights-results__price gws-flights-results__cheapest-price']})



    # prices = soup.findAll('div', attrs={'class': ['flt-subhead1 gws-flights-results__price gws-flights-results__cheapest-price',
    #                                               'flt-subhead1 gws-flights-results__price']})
    best_prices = []
    bar_height_percentages = []
    for tag in prices:
        if "style=" not in str(tag):
            continue
        else:
            temp = inner.findall(str(tag))
            temp = temp[0].split()[1]
            temp = temp.replace("%,", "")
            bar_height_percentages.append(int(temp))
    values_from_height = np.absolute((np.array(bar_height_percentages) * max_value) / 100)
        # best_prices.append(int(tag.text.replace('$', '').replace(',', '')))

    # for tag in all_price_bars:
    #     print(tag.contents)
    #     # try:
    #     #     best_prices.append(int(tag.text.replace("$", "").replace(",", "")))
    #     # except Exception as err:
    #     #     print("Error when attempting to obtain pricing information from website data. ", err)

    fares = pd.DataFrame(np.reshape(values_from_height, (-1,1)), columns=['price'])
    fig, ax = plt.subplots()
    plt.scatter(np.arange(len(fares['price'])), fares['price'])
    plt.show()
    print()
    px = [x for x in fares['price']]
    ff = pd.DataFrame(px, columns=['fare']).reset_index()
    X = StandardScaler().fit_transform(ff)
    db = DBSCAN(eps=.5, min_samples=1).fit(X)

    labels = db.labels_
    clusters = len(set(labels))
    unique_labels = set(labels)
    cmap = plt.cm.nipy_spectral(np.linspace(0, 1, len(unique_labels)))
    print()