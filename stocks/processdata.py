import asyncio
import json
import os
from datetime import datetime, timedelta

# Environment setup
before_days = 30
after_days = 30
repeat_times = before_days + after_days


def sleep(ms):
    return asyncio.sleep(ms / 1000)


def add_one_day(date, days=1):
    new_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")


def minus_one_day(date, days=1):
    new_date = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=days)
    return new_date.strftime("%Y-%m-%d")


def filter_data(earnings, stocklist):
    if earnings:
        earnings = json.loads(earnings)
    else:
        return []

    if not earnings.get("data"):
        print(f"Filtering date {earnings['date']} error: Looks like it is weekend, no earnings data available.")
        return []

    stock_map = {item['symbol']: item for item in stocklist}
    filtered_earnings = [item for item in earnings['data'] if item['symbol'] in stock_map]

    return [
        {
            'symbol': earning['symbol'],
            'date': earnings['date'],
            'marketCap': earning.get('marketCap', 'N/A'),
            'fiscalQuarterEnding': earning.get('fiscalQuarterEnding', ''),
            'time': '盘前' if earning.get('time') == 'time-pre-market' else '盘后' if earning.get(
                'time') == 'time-after-hours' else '',
            'epsForecast': earning.get('epsForecast', ''),
            'noOfEsts': earning.get('noOfEsts', ''),
            'companyName': stock_map[earning['symbol']].get('companyName', earning.get('name', 'N/A')),
            'industry': stock_map[earning['symbol']].get('industry', 'N/A')
        }
        for earning in filtered_earnings
    ]


def filter_data_all(earnings):
    if earnings:
        earnings = json.loads(earnings)
    else:
        return []

    if not earnings.get("data"):
        print(f"Filtering date {earnings['date']} error: Looks like it is weekend, no earnings data available.")
        return []

    return [
        {
            'symbol': earning['symbol'],
            'date': earnings['date'],
            'marketCap': earning.get('marketCap', 'N/A'),
            'fiscalQuarterEnding': earning.get('fiscalQuarterEnding', ''),
            'time': '盘前' if earning.get('time') == 'time-pre-market' else '盘后' if earning.get(
                'time') == 'time-after-hours' else '',
            'epsForecast': earning.get('epsForecast', ''),
            'noOfEsts': earning.get('noOfEsts', ''),
            'companyName': earning.get('name', 'N/A'),
            'industry': 'N/A'
        }
        for earning in earnings['data']
    ]


def format_data(datas):
    result = []
    for sub_array in datas:
        if sub_array:
            result.extend(sub_array)
    unique_data = {item['symbol']: item for item in result}.values()
    sorted_data = sorted(unique_data, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
    return sorted_data


async def fetch_local_data(date):
    date_parts = date.split('-')
    year = date_parts[0]
    month = date_parts[1].zfill(2)
    file_path = f"./storedData/{year}/{month}/{date}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    else:
        print(f"No data found for {date}, skipped")
        return None


async def read_data(date, list):
    new_date = minus_one_day(date, before_days)
    datas = []
    for _ in range(repeat_times):
        data = await fetch_local_data(new_date)
        if data:
            if list is None:
                data = filter_data_all(data)
            else:
                data = filter_data(data, list)
            await sleep(50)
            if data:
                datas.append(data)
                print(f'Reading date {new_date} done')
        new_date = add_one_day(new_date)
    return datas


async def process_data(date, list):
    try:
        datas = await read_data(date, list)
        final_data = format_data(datas)
        return final_data
    except Exception as error:
        print(f'Failed to process data: {error}')
        raise


# If this script is being run as the main program
if __name__ == "__main__":
    # You would typically pass in the actual date and list you want to process
    asyncio.run(process_data("2023-06-20", None))
