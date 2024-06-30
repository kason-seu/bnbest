import asyncio
import json
import requests
import os
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y-%m-%d")


def add_one_day(date, days=1):
    new_date = datetime.strptime(date, "%Y-%m-%d")
    new_date += timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")


def minus_one_day(date, days=1):
    new_date = datetime.strptime(date, "%Y-%m-%d")
    new_date -= timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")


def extract_date_simple(date_string):
    print("Processing date:", date_string)  # Debug: print the problematic string
    # Extended list of date formats to try
    date_formats = [
        "%b %d, %Y",  # "Dec 31, 2022"
        "%Y-%m-%d",  # "2022-12-31"
        "%a, %b %d, %Y"  # "Wed, Jul 24, 2024"
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue  # If it doesn't match, try the next format

    # If no known formats match, raise an error
    raise ValueError(f"Date format not recognized for string: {date_string}")


async def sleep(ms):
    await asyncio.sleep(ms / 1000)


async def fetch_earnings_data(date):
    url = f"https://api.nasdaq.com/api/calendar/earnings?date={date}"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.nasdaq.com',
        'Referer': 'https://www.nasdaq.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56'
    }
    response = await asyncio.get_event_loop().run_in_executor(
        None, lambda: requests.get(url, headers=headers))
    data = response.json()
    try:
        _date = extract_date_simple(data['data']['asOf'])
    except ValueError as e:
        print(e)
        return None  # or handle the error as needed
    _data = data['data']['rows']
    return {'date': _date, 'data': _data}


async def get_after_datas(plus_date, days):
    for i in range(days):
        data = await fetch_earnings_data(plus_date)
        save_data(plus_date, data)  # Note: save_data is still synchronous
        await sleep(100)
        plus_date = add_one_day(plus_date)


async def fetch_earnings_calendar_data(date=today):
    try:
        before_days = 1
        after_days = 31
        new_date = minus_one_day(date, before_days)
        await get_after_datas(new_date, after_days)
    except Exception as error:
        print('Failed to fetch earnings calendar:', error)
        raise


def save_data(date, data):
    year, month, _ = date.split('-')
    dir_path = f"./storedData/{year}/{month.zfill(2)}"
    os.makedirs(dir_path, exist_ok=True)
    file_path = f"{dir_path}/{date}.json"
    with open(file_path, 'w') as file:
        file.write(json.dumps(data, indent=2))
    print('Data saved to', file_path)


# Example of how to use this function in an async environment
if __name__ == "__main__":
    asyncio.run(fetch_earnings_calendar_data())
