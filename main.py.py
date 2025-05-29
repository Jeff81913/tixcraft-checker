
import time
import requests
from bs4 import BeautifulSoup
from plyer import notification

# ====== Discord Webhook URL ======
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1376936753469984768/c5W1T69kOiEFQkea-uK5kvxJtz8rH-FodWr7be4vK61yKdlRLQUqC67L1vPBNRzKSnev"

# ====== 要監控的 Tixcraft 網址清單（已指定場次） ======
TIXCRAFT_URLS = {
    "6/29 BABYMONSTER": "https://tixcraft.com/ticket/area/25_bm/19396",
    "6/28 BABYMONSTER": "https://tixcraft.com/ticket/area/25_bm/19207"
}

# ====== 檢查間隔（秒）======
CHECK_INTERVAL = 3

# ====== 發送狀態紀錄與每小時通知追蹤 ======
last_status = {}
last_notify_time = {}

def send_discord_message(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("✅ Discord 通知已發送")
        else:
            print(f"⚠️ Discord 通知失敗：{response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ 發送 Discord 發生錯誤：{e}")

def check_tickets(event_name, url):
    global last_status, last_notify_time
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        keywords = ["立即訂票", "選擇座位", "可售票區", "剩餘", "可選擇"]
        has_ticket = any(keyword in page_text for keyword in keywords)
        now = time.time()

        if has_ticket:
            if last_status.get(event_name) != "有票":
                print(f"🎫 [{event_name}] 有票啦！！")
                notification.notify(
                    title=f"🎉 {event_name} 有票啦！",
                    message="快去 Tixcraft 抢票！",
                    timeout=10
                )
                send_discord_message(f"🎫 **{event_name} 有票啦！**\n👉 {url}")
                last_status[event_name] = "有票"
        else:
            print(f"⏳ [{event_name}] 尚無票可購買...")
            if (last_status.get(event_name) != "沒票" or
                now - last_notify_time.get(event_name, 0) >= 3600):
                send_discord_message(f"🔕 **{event_name} 尚無票**（每小時通知）\n👉 {url}")
                last_notify_time[event_name] = now
                last_status[event_name] = "沒票"

    except Exception as e:
        print(f"⚠️ [{event_name}] 發生錯誤：{e}")

# ====== 主執行迴圈 ======
if __name__ == "__main__":
    print("🚀 開始監控以下 BABYMONSTER 場次：")
    for name in TIXCRAFT_URLS:
        print(f" - {name}")

    while True:
        for name, url in TIXCRAFT_URLS.items():
            check_tickets(name, url)
        time.sleep(CHECK_INTERVAL)
