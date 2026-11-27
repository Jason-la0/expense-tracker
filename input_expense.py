import csv
import os
from datetime import datetime

DATA_FILE = "expenses.csv"
FIELDNAMES = ["date", "amount", "category", "note"]


def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def get_valid_date():
    today = datetime.now().strftime("%Y-%m-%d")
    while True:
        date_str = input(f"日期 (YYYY-MM-DD，直接按 Enter 預設今天 {today}): ").strip()
        if not date_str:
            return today
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("日期格式錯誤，請輸入 YYYY-MM-DD（例如 2026-11-27）。")


def get_valid_amount():
    while True:
        raw = input("金額 (正數): ").strip()
        try:
            amount = float(raw)
            if amount > 0:
                return amount
            print("金額必須大於 0。")
        except ValueError:
            print("請輸入有效的數字。")


def get_valid_category():
    while True:
        category = input("分類 (例如 飲食、交通、娛樂、購物): ").strip()
        if category:
            return category
        print("分類不可為空白。")


def add_expenses():
    init_csv()
    print("=== 記帳輸入工具 ===")
    while True:
        date_str = get_valid_date()
        amount = get_valid_amount()
        category = get_valid_category()
        note = input("備註 (選填，可直接按 Enter 略過): ").strip()

        with open(DATA_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow({
                "date": date_str,
                "amount": amount,
                "category": category,
                "note": note,
            })
        print(f"已儲存：{date_str} | {category} | ${amount:.0f} | {note}\n")

        cont = input("是否繼續新增下一筆？(y/n): ").strip().lower()
        if cont != "y":
            print("結束記帳輸入。")
            break


if __name__ == "__main__":
    add_expenses()