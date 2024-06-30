from ics import Calendar, Event
from datetime import datetime
import os
from processdata import process_data  # Assuming you've translated this module to Python


async def generate_earnings_ics_calendar(date, list, filename):
    try:
        print(f'Generating earnings calendar for {date}')
        earnings_data = await process_data(date, list)  # Process data to get earnings information

        calendar = Calendar()
        for entry in earnings_data:
            event = Event()
            event.name = f"{entry['companyName']} {entry['time']}发布财报"
            event.begin = datetime(int(entry['date'].split('-')[0]), int(entry['date'].split('-')[1]),
                                   int(entry['date'].split('-')[2]))
            event.description = (f"财务季度：{entry['fiscalQuarterEnding']}。\n代码：{entry['symbol']}，公司："
                                 f"{entry['companyName']}，行业: {entry['industry']}。\n预计每股收益: "
                                 f"{entry['epsForecast']}，当前市值: {entry['marketCap']}。\n ~~~~~~~~~~~~ \n"
                                 f"在股票 app 打开： stocks://?symbol={entry['symbol']} \n"
                                 f"在富途查看：https://www.futunn.com/hk/stock/{entry['symbol']}-US ")
            event.make_all_day()
            event.status = 'CONFIRMED'
            event.transparent = True  # This corresponds to the 'FREE' busy status in the JS version

            calendar.events.add(event)

        # Save the calendar to a file
        file_path = f"./docs/ics/{filename}.ics"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.writelines(calendar)
        print(f"Earnings calendar .ics file has been saved to {file_path}.")

    except Exception as error:
        print(f'Error generating earnings ICS calendar: {error}')

# Ensure this function is called from an async capable environment, if using asyncio to manage asynchronous calls.
