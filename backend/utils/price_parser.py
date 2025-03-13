import requests
import urllib.request

from urls import BASE_PRICE_URL
from bs4 import BeautifulSoup


def get_prices(part_number: str) -> list[float]:
    url = f"{BASE_PRICE_URL}/{part_number}/"

    response = requests.get(url)
    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.read()
    
    if content.status_code != 200:
        raise Exception("No")
    
    #BeautifulSoup.
    

    #return price_list

def get_average_price() -> float:
    pass

if __name__ == "__main__":
    print(get_prices("51350SAAE01"))