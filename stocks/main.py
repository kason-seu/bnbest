import os
from flask import Flask, send_from_directory
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from automation import gen_all_ics  # Assuming this is adapted to Python and is asynchronous
from stock_fetch_utils import fetch_earnings_calendar_data  # Assuming this is asynchronous

app = Flask(__name__, static_folder='static')
port = os.getenv('PORT', 18302)


@app.route('/')
def serve_static():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/ics/<filename>')
def download_file(filename):
    directory = './docs/ics/'  # 替换为你的文件所在目录
    return send_from_directory(directory, filename, as_attachment=True)


# Setup AsyncIO Scheduler
scheduler = AsyncIOScheduler()


async def schedule_jobs():
    # Schedule jobs to run immediately upon startup
    await fetch_earnings_calendar_data()
    await gen_all_ics()

    # Schedule recurring jobs
    scheduler.add_job(fetch_earnings_calendar_data, 'cron', hour=18, minute=17)
    scheduler.add_job(gen_all_ics, 'cron', hour=18, minute=20)

    # Start the scheduler
    scheduler.start()


def start_app():
    app.run(host='0.0.0.0', port=port)
    print(f"Server running on http://localhost:{port}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_jobs())
    loop.create_task(start_app())
    loop.run_forever()
