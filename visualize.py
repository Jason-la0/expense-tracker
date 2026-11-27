"""成員 B：讀取 CSV，依分類加總金額並輸出圓餅圖。"""

import argparse
import csv
import re
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
FIELDS = ["date", "amount", "category", "notes"]
CATEGORIES = ["飲食", "交通", "購物", "娛樂", "生活", "其他"]


def load_totals(csv_path):
    """驗證每筆資料後加總；有錯誤就停止，避免畫出不完整的統計。"""
    totals = {category: Decimal("0.00") for category in CATEGORIES}
    count = 0
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != FIELDS:
            raise ValueError("CSV 第一列必須依序為：date,amount,category,notes")

        for row in reader:
            line = reader.line_num
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV 第 {line} 行的欄位數不正確。")
            date = row["date"].strip()
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
                raise ValueError(f"CSV 第 {line} 行：日期須使用 YYYY-MM-DD。")
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as error:
                raise ValueError(f"CSV 第 {line} 行：日期不存在。") from error

            amount_text = row["amount"].strip()
            if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", amount_text):
                raise ValueError(f"CSV 第 {line} 行：金額須為正數，最多兩位小數。")
            try:
                amount = Decimal(amount_text)
                # 以整數分驗證，避免極端金額在加總或繪圖時溢位。
                if not Decimal("0") < amount <= Decimal("999999999999.99"):
                    raise ValueError(f"CSV 第 {line} 行：金額須大於 0 且不超過 999999999999.99。")
            except InvalidOperation as error:
                raise ValueError(f"CSV 第 {line} 行：金額無效。") from error

            category = row["category"].strip()
            if category not in CATEGORIES:
                raise ValueError(f"CSV 第 {line} 行：分類須為「{'、'.join(CATEGORIES)}」其中之一。")

            totals[category] += amount
            count += 1

    if count == 0:
        raise ValueError("目前沒有支出資料，請先執行 A 的輸入程式新增支出。")
    return {name: value for name, value in totals.items() if value > 0}, count


def configure_font(plt, font_manager):
    """優先尋找 Windows、macOS、Linux 常見的中文字型。"""
    candidates = [
        "Microsoft JhengHei", "Microsoft YaHei", "PingFang TC",
        "Heiti TC", "Noto Sans CJK TC", "Noto Sans CJK JP", "SimHei",
    ]
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = [name]
            plt.rcParams["axes.unicode_minus"] = False
            return
    raise ValueError("找不到中文字型。Windows 請確認微軟正黑體可用；其他系統可安裝 Noto Sans CJK TC 後重開程式。")


def draw_chart(totals, count, output_path, show=True):
    # 延後匯入，缺少套件時能顯示容易理解的安裝提示。
    try:
        import matplotlib
        if not show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except ImportError as error:
        raise ValueError("請先安裝套件：python -m pip install -r requirements.txt") from error

    configure_font(plt, font_manager)
    labels = list(totals)
    values = [float(totals[label]) for label in labels]
    total = sum(totals.values(), Decimal("0.00"))
    palette = dict(zip(CATEGORIES, ["#4C78A8", "#F2A541", "#59A14F", "#B279A2", "#E87878", "#72B7B2"]))

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    wedges, _, _ = ax.pie(
        values, labels=labels, autopct="%1.1f%%", startangle=90,
        colors=[palette[label] for label in labels],
        pctdistance=0.70, labeldistance=1.08,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11},
    )
    ax.axis("equal")
    ax.set_title("各分類支出比例", fontsize=20, pad=22)
    ax.legend(
        wedges, [f"{label}：NT$ {totals[label]:,.2f}" for label in labels],
        title="分類金額", loc="center left", bbox_to_anchor=(1.03, 0.5),
        frameon=False,
    )
    fig.text(0.5, 0.04, f"總支出：NT$ {total:,.2f}　｜　共 {count} 筆", ha="center", fontsize=12)
    fig.subplots_adjust(left=0.06, right=0.68, bottom=0.12, top=0.85)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
        print(f"\n圓餅圖已儲存：{output_path}")
        if show:
            plt.show()
    finally:
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="成員 B：讀取支出 CSV，產生分類圓餅圖。")
    parser.add_argument("--data", type=Path, default=BASE_DIR / "expenses.csv", help="資料檔案（預設為程式旁的 expenses.csv）")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "screenshots" / "piechart.png", help="輸出 PNG 路徑")
    parser.add_argument("--no-show", action="store_true", help="只儲存圖片，不開啟視窗")
    args = parser.parse_args()

    try:
        if args.output.suffix.lower() != ".png":
            raise ValueError("輸出檔名請使用 .png 副檔名。")
        if args.data.resolve() == args.output.resolve():
            raise ValueError("輸出圖片不可覆蓋資料檔案。")
        totals, count = load_totals(args.data)
        total = sum(totals.values(), Decimal("0.00"))
        print(f"讀取資料：{args.data.resolve()}")
        print(f"支出筆數：{count}")
        for name, amount in totals.items():
            print(f"{name}：NT$ {amount:,.2f}（{amount / total * 100:.2f}%）")
        print(f"總支出：NT$ {total:,.2f}")
        draw_chart(totals, count, args.output.resolve(), show=not args.no_show)
    except FileNotFoundError:
        print(f"錯誤：找不到資料檔 {args.data}。請先由 A 新增支出，或用 --data 指定 sample_expenses.csv。", file=sys.stderr)
        return 1
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        print(f"錯誤：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
