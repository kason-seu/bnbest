import asyncio
import os
from datetime import datetime
from get_stocks_msg import get_stocks_details_list, get_files_name_list  # Assuming these are adapted to Python
from processdata import process_data  # Assuming this is adapted to Python
from generate_ics import generate_earnings_ics_calendar  # Assuming this is adapted to Python

today = datetime.now().strftime("%Y-%m-%d")
selected = []
should_gen_selected = os.getenv('SHOULD_GEN_SELECTED', 'false') == 'true'
should_gen_all = os.getenv('SHOULD_GEN_ALL', 'false') == 'true'


async def gen_all_ics():
    stock_list = await get_stocks_details_list() or {}
    names = await get_files_name_list() or []

    for name in names:
        item = stock_list.get(name, {})
        if isinstance(item, dict):
            stock_array = list(item.values())
        elif isinstance(item, list):
            stock_array = item
        else:
            print(f"Error: Unexpected data type for {name}: {type(item)}")
            continue

        selected.extend(stock_array)
        print(f'Processing {name}...')
        final_data = await process_data(today, stock_array)
        await generate_earnings_ics_calendar(today, final_data, name)

    if should_gen_selected:
        await generate_earnings_ics_calendar(today, selected, 'selected')

    if should_gen_all:
        await generate_earnings_ics_calendar(today, None, 'all')

    print('All done.')


# Example of how to use this function
if __name__ == "__main__":
    asyncio.run(gen_all_ics())
