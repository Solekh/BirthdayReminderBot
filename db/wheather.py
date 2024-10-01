import json
import aiofiles
import requests
import asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from os.path import join

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = join(BASE_DIR, 'db')


class Weather:
    def __init__(self, city: str = None, link: str = None):
        self.city = city
        self.link = link

    @property
    async def objects(self):
        file_name = self.__class__.__name__.lower() + "s.json"
        response = requests.get("https://obhavo.uz/")
        html_doc = response.text

        soup = BeautifulSoup(html_doc, 'html.parser')
        cities_data = []

        city_list = soup.find('ul', class_='list-c')
        for city_item in city_list.find_all('li'):
            city_name = city_item.find('a').text
            city_link = city_item.find('a')['href']

            city_info = {
                'city': city_name,
                'link': city_link
            }
            cities_data.append(city_info)

        with open(join(DB_PATH, file_name), 'w') as outfile:
            json.dump(cities_data, outfile, indent=3)

        async with aiofiles.open(join(DB_PATH, file_name), 'r') as f:
            data = await f.read()
            data = json.loads(data)

        return [self.__class__(city=i['city'], link=i['link']) for i in data]  # Pass city and link to Weather()

    async def city_link(self, city_name):
        cities: list[Weather] = await Weather().objects
        for city in cities:
            if city.city == city_name:
                return city.link

    async def city_forecast(self, city_link):
        response = requests.get(city_link)
        html_doc = response.text
        soup = BeautifulSoup(html_doc, "html.parser")
        block = soup.find(class_='padd-block')
        city = block.find('h2').text
        current_day = block.find(class_='current-day').text
        current_temp = soup.find("div", class_="current-forecast").find_all("span")[1].text.strip()
        current_temp2 = soup.find("div", class_="current-forecast").find_all("span")[2].text.strip()
        current_description = soup.find("div", class_="current-forecast-desc").text.strip()
        printed_data = f"""
        {city}
        {current_day}
        kunduzi: {current_temp}, kechasi: {current_temp2}
        Izoh: {current_description}
        """
        return printed_data

    async def weekly_forecast(self, city_link):
        response = requests.get(city_link)
        html_doc = response.text
        soup = BeautifulSoup(html_doc, "html.parser")
        weekly = soup.find(class_='grid-2 cont-block')
        rows = weekly.find_all('tr')

        res = []
        for row in rows[1:]:  # Skip the first row (header row)
            day = row.find('strong').get_text()
            date = row.find('div').get_text()
            day_temp = row.find(class_='forecast-day').get_text()
            night_temp = row.find(class_='forecast-night').get_text()
            desc = row.find(class_='weather-row-desc').get_text().strip()
            res.append(f"{day}: {date} kunduzi: {day_temp}, kechasi: {night_temp}, {desc}")

        return "\n\n".join(res)

