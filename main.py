import time
import asyncio
import cloudscraper
import schedule
import json
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timezone, timedelta

# 从 config.json 加载配置
with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['TOKEN']
CHAT_ID = config['CHAT_ID']

def convert_to_east8(time_str):
    try:
        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S%z')
        dt_east8 = dt.astimezone(ZoneInfo('Asia/Hong_Kong'))
        return dt_east8.strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"Failed to parse time: {time_str}, error: {e}")
        return None

def is_same_day_in_hk(datetime_str):
    try:
        input_dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        now_hk = datetime.now(ZoneInfo('Asia/Hong_Kong'))
        return (input_dt.year, input_dt.month, input_dt.day) == (now_hk.year, now_hk.month, now_hk.day)
    except Exception as e:
        print(f"Failed to parse time: {datetime_str}, error: {e}")
        return False

def crawl_codeforces():
    url = 'https://codeforces.com/contests'
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code != 200:
        print('Failed to fetch contests page')
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    contests = []

    # 找到所有的比赛表格
    datatables = soup.find_all('div', class_='datatable')

    # 通常第一个表格是当前和即将开始的比赛
    if datatables:
        table = datatables[0].find('table')
        if table:
            rows = table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    name_cell = cols[0]
                    name = name_cell.text.strip().split('\n')[0]
                    link_tag = name_cell.find('a')
                    link = 'https://codeforces.com' + link_tag['href'] if link_tag else None

                    writers = [a.text.strip() for a in cols[1].find_all('a')]
                    start_time_str = cols[2].text.strip()
                    duration = cols[3].text.strip()
                    status = cols[4].text.strip()

                    try:
                        utc_time = datetime.strptime(start_time_str, '%b/%d/%Y %H:%M')
                        hk_time = utc_time + timedelta(hours=5)
                        start_time = hk_time.strftime('%Y-%m-%d %H:%M')
                    except Exception as e:
                        print(f"Failed to parse time: {start_time_str}, error: {e}")
                        start_time = start_time_str  # 如果解析失败，就保留原字符串

                    contests.append({
                        'name': name,
                        'link': link,
                        'writers': writers,
                        'start_time': start_time,
                        'duration': duration,
                        'status': status
                    })
    return contests

def crawl_atcoder():
    url = 'https://atcoder.jp/contests'
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    contests = []

    # 找到Upcoming Contests那部分
    upcoming = soup.find('div', id='contest-table-upcoming')
    if upcoming:
        table = upcoming.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    time = cols[0].text.strip()
                    time = convert_to_east8(time)
                    link_tag = cols[1].find('a')
                    if link_tag and link_tag.has_attr('href'):
                        name = link_tag.text.strip()
                        link = 'https://atcoder.jp' + link_tag['href']
                        contests.append({'name': name, 'time': time, 'link': link})
    return contests

# 发送消息
async def send_daily_message(chat_id, context):
    contests_cf = crawl_codeforces()
    cfMessage = "CF TODAY:"
    for contest in contests_cf:
        if is_same_day_in_hk(contest['start_time']):
            cfMessage += "\n" + contest['name'] + contest['start_time']
    print(cfMessage)

    contest_at = crawl_atcoder()
    atMessage = "AT TODAY:"
    for contest in contest_at:
        if is_same_day_in_hk(contest['time']):
            atMessage += "\n" + contest['name'] + contest['time']
    print(atMessage)
    sendMessage = cfMessage + "\n" + atMessage

    if(cfMessage != "CF TODAY:"):
        await context.bot.send_message(chat_id = chat_id, text = cfMessage)
    if(atMessage != "AT TODAY:"):
        await context.bot.send_message(chat_id = chat_id, text = atMessage)

async def run_schedule(app):
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def beijing_time_now():
    return datetime.utcnow() + timedelta(hours=8)

def schedule_beijing(job_func, beijing_time_str):
    # 解析要安排的北京时间，比如"08:00"
    hour, minute = map(int, beijing_time_str.split(":"))

    async def check_and_run():
        while True:
            now = beijing_time_now()
            if now.hour == hour and now.minute == minute and now.second == 0:
                await job_func()
                await asyncio.sleep(1)  # 防止重复触发
            await asyncio.sleep(1)

    return check_and_run

async def main():
    contest_cf = crawl_codeforces()
    contest_at = crawl_atcoder()
    #print(contest_cf)
    #print(contest_at)

    app = ApplicationBuilder().token(TOKEN).build()

    print("Bot has been started...")

    #await send_daily_message(CHAT_ID, app)

    async def send_job():
        await send_daily_message(CHAT_ID, app)

    # 用北京时间的逻辑安排任务
    asyncio.create_task(schedule_beijing(send_job, "08:00")())

    await run_schedule(app)

# 使用 asyncio 运行主程序
if __name__ == "__main__":
    asyncio.run(main())
