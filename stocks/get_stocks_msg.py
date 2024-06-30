import asyncio
import os
import json


# 获取股票文件名称 如纳斯达克、标普500文件名
async def get_files_name_list():
    # Retrieve all JSON file names from the './api/datas/' directory
    files = os.listdir('./datas')
    list_files = [file.replace('.json', '') for file in files if file.endswith('.json')]
    return list_files


# 获取股票的具体msg信息
async def get_stocks_details_list():
    # Get filenames from the get_list function
    filenames = await get_files_name_list()
    data = {}
    for filename in filenames:
        with open(f'./datas/{filename}.json', 'r') as file:
            data[filename] = json.load(file)
    return data


# If you want to use these functions in other parts of your code, you might structure it like this:
if __name__ == "__main__":
    # This is just for demonstration; typically, you might not call get_data() directly like this.
    result = asyncio.run(get_stocks_details_list())
    print(result)  # To see the result of the get_data function

# You can also create a separate module for these functions if you plan to reuse them elsewhere.
