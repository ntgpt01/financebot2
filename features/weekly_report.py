from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from datetime import datetime, timedelta
from weekly_db import get_weekly_info, insert_weekly_report, get_weekly_report, get_all_weeks
from db import connect
from init_weekly_info import run_init
import asyncio

# === Rate overrides ===
rate_overrides = {}

# === FSM States ===
class WeeklyReportState(StatesGroup):
    choosing_person = State()
    entering_amount = State()
    adding_member_name = State()
    adding_member_group = State()
    adding_member_rate = State()

# === Utils tuần ===
def get_week_range(date=None):
    if date is None:
        date = datetime.today()
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}"

def get_week_key(date=None):
    if date is None:
        date = datetime.today()
    monday = date - timedelta(days=date.weekday())
    return monday.strftime("%Y-%m-%d")

# === /init_weekly_info ===
async def handle_init(message: types.Message):
    run_init()
    await message.answer("✅ Done init weekly_info.")

# === Menu ===
async def weekly_menu(query: CallbackQuery):
    await query.answer()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📝 Kết Tuần", callback_data="weekly_start"),
        InlineKeyboardButton("📅 History", callback_data="weekly_history"),
        InlineKeyboardButton("📂 Tất cả các tuần", callback_data="weekly_all_history")
    )
    await query.message.edit_text("📊 Báo Cáo Tuần gồm:", reply_markup=keyboard)

# === Bắt đầu ===
async def start_weekly_report(query: CallbackQuery, state: FSMContext):
    await query.answer()
    info_data = get_weekly_info()
    members = list(info_data.keys())
    await state.update_data(remaining_members=members.copy(), report_data={}, current_person=None)
    await query.message.delete()
    await show_member_buttons(query.message, state)

async def show_member_buttons(message, state: FSMContext):
    data = await state.get_data()
    remaining = data.get("remaining_members", [])
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(name, callback_data=f"choose_{name}") for name in remaining]
    for i in range(0, len(buttons), 3):
        keyboard.row(*buttons[i:i+3])
    keyboard.add(
        InlineKeyboardButton("➕ Thêm người", callback_data="add_member"),
        InlineKeyboardButton("✅ Hoàn thành báo cáo", callback_data="finish_report")
    )
    sent = await message.answer("Chọn người cần nhập:", reply_markup=keyboard)
    await state.update_data(last_member_message_id=sent.message_id)
    await WeeklyReportState.choosing_person.set()

async def handle_choose_person(query: CallbackQuery, state: FSMContext):
    await query.answer()
    name = query.data.split("choose_")[-1]
    await state.update_data(current_person=name)
    last_msg_id = (await state.get_data()).get("last_member_message_id")
    if last_msg_id:
        try:
            await query.bot.delete_message(query.message.chat.id, last_msg_id)
        except:
            pass
    info = get_weekly_info()
    default_rate = info.get(name, {}).get("rate", 0)
    rate_overrides[name] = default_rate
    await state.update_data(current_rate=default_rate)
    await query.message.answer(f"👤 {name} (tỷ lệ: {default_rate}%)\n💵 Nhập số tiền:", reply_markup=types.ForceReply(selective=True))
    await WeeklyReportState.entering_amount.set()

# === FSM: Thêm người mới ===
async def handle_add_member_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.answer("✏️ Gõ tên thành viên mới:")
    await WeeklyReportState.adding_member_name.set()
GROUP_CHOICES = ["TH01", "TH02", "TH04"]

async def add_member_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Tên không hợp lệ.")
        return

    await state.update_data(new_member_name=name)

    keyboard = InlineKeyboardMarkup(row_width=2)
    for grp in GROUP_CHOICES:
        keyboard.add(InlineKeyboardButton(grp, callback_data=f"group_{grp}"))

    await message.answer(f"📌 Chọn group_master cho **{name}**:", reply_markup=keyboard)
    await WeeklyReportState.adding_member_group.set()
async def add_member_group_cb(query: CallbackQuery, state: FSMContext):
    await query.answer()
    group = query.data.split("group_")[-1]
    await state.update_data(new_member_group=group)
    await query.message.answer(f"💯 Nhập rate (%) cho nhóm **{group}**:")
    await WeeklyReportState.adding_member_rate.set()
async def add_member_rate(message: types.Message, state: FSMContext):
    try:
        rate = int(message.text.strip())
    except:
        await message.answer("⚠️ Rate không hợp lệ.")
        return

    data = await state.get_data()
    name = data["new_member_name"]
    group = data["new_member_group"]

    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weekly_info (name, group_master, rate)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (name, group, rate))
        conn.commit()

    remaining = data.get("remaining_members", [])
    remaining.append(name)
    rate_overrides[name] = rate

    await state.update_data(current_person=name, remaining_members=remaining, current_rate=rate)
    await message.answer(f"✅ Đã thêm **{name}** ({group} - {rate}%)\n💵 Nhập số tiền:")
    await WeeklyReportState.entering_amount.set()


# === Nhập số tiền ===
async def enter_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("current_person"):
        return await message.answer("⚠️ Bạn chưa chọn người.")
    try:
        amount = int(message.text.replace(",", "").replace(".", ""))
    except:
        return await message.answer("⚠️ Nhập số không hợp lệ.")
    person = data["current_person"]
    info = get_weekly_info()
    rate = rate_overrides.get(person) or info.get(person, {}).get("rate", 0)
    tientuan = round(amount - amount * rate / 100)
    await message.answer(f"👤 {person}\n{amount:,} - {rate}% ➜ {'Bù' if tientuan > 0 else 'Thu'} {tientuan:,}")
    report_data = data.get("report_data", {})
    report_data[person] = {"amount": amount, "rate": rate, "tientuan": tientuan}
    remaining = data.get("remaining_members", [])
    if person in remaining:
        remaining.remove(person)
    await state.update_data(report_data=report_data, remaining_members=remaining, current_person=None)
    if not remaining:
        await finish_weekly_report(message, state)
    else:
        await show_member_buttons(message, state)

# === Kết tuần ===
async def finish_report_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if not (await state.get_data()).get("report_data"):
        await query.message.answer("⚠️ Chưa nhập dữ liệu.")
        return
    await query.message.delete()
    await finish_weekly_report(query.message, state)

async def finish_weekly_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report_data = data.get("report_data", {})
    if not report_data:
        await message.answer("❌ Không có dữ liệu để lưu.")
        return
    week_key = get_week_key()
    for person, entry in report_data.items():
        await asyncio.get_running_loop().run_in_executor(None, insert_weekly_report, week_key, person, entry["amount"], entry["rate"], entry["tientuan"])
    week_title = f"🗓️ Lịch Sử Tuần {get_week_range()}"
    header = "ID | Name       | Type | Amount"
    lines = []
    for idx, (person, entry) in enumerate(report_data.items(), 1):
        icon = "🟢" if entry["tientuan"] > 0 else "🔴"
        label = "Bù" if entry["tientuan"] > 0 else "Thu"
        lines.append(f"{idx:02} | {person:<10} | {icon} {label:<3} | {entry['tientuan']:,} VNĐ")
    total_bu = sum(x["tientuan"] for x in report_data.values() if x["tientuan"] > 0)
    total_thu = sum(x["tientuan"] for x in report_data.values() if x["tientuan"] < 0)
    delta = total_bu + total_thu
    summary = f"\n\nTổng Kết: 🔴 Thu {total_thu:,} | 🟢 Bù +{total_bu:,} | ⚖️ Chênh lệch: {'+' if delta >= 0 else ''}{delta:,} VNĐ"
    await message.answer(f"<pre>{week_title}\n{header}\n" + "\n".join(lines) + summary + "</pre>", parse_mode="HTML")
    await state.finish()

# === History ===
async def show_history_menu(query: CallbackQuery):
    await query.answer()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📅 Tuần này", callback_data="history_this_week"),
        InlineKeyboardButton("📆 Tuần trước", callback_data="history_last_week")
    )
    await query.message.edit_text("🕓️ Chọn tuần:", reply_markup=keyboard)

async def show_history_detail(query: CallbackQuery):
    await query.answer()
    date = datetime.today() if query.data == "history_this_week" else datetime.today() - timedelta(days=7)
    week_key = get_week_key(date)
    rows = get_weekly_report(week_key)
    if not rows:
        await query.message.edit_text("⚠️ Không có dữ liệu tuần này.")
        return
    week_title = f"🗓️ Lịch Sử Tuần {get_week_range(date)}"
    header = "ID | Name       | Type | Amount"
    lines = []
    for idx, row in enumerate(rows, 1):
        icon = "🟢" if row["tientuan"] > 0 else "🔴"
        label = "Bù" if row["tientuan"] > 0 else "Thu"
        lines.append(f"{idx:02} | {row['person']:<10} | {icon} {label:<3} | {row['tientuan']:,} VNĐ")
    await query.message.edit_text(f"<pre>{week_title}\n{header}\n" + "\n".join(lines) + "</pre>", parse_mode="HTML")

async def show_all_weeks_report(query: CallbackQuery):
    await query.answer()
    rows = get_all_weeks()
    if not rows:
        await query.message.answer("⚠️ Không có dữ liệu.")
        return
    lines = ["<b>Tổng hợp các tuần:</b>"]
    for row in rows:
        lines.append(f"🗓️ {row['week_key']} | {'+' if row['total'] > 0 else ''}{row['total']:,} VNĐ")
    await query.message.answer("\n".join(lines), parse_mode="HTML")

# === Register ===
def register(dp):
    # Khởi tạo DB
    dp.register_message_handler(handle_init, commands="init_weekly_info")

    # Menu chính
    dp.register_callback_query_handler(weekly_menu, lambda c: c.data == "weekly_menu")
    dp.register_callback_query_handler(start_weekly_report, lambda c: c.data == "weekly_start")
    dp.register_callback_query_handler(show_history_menu, lambda c: c.data == "weekly_history")

    # Chọn người & nhập số tiền
    dp.register_callback_query_handler(handle_choose_person, lambda c: c.data.startswith("choose_"), state=WeeklyReportState.choosing_person)
    dp.register_message_handler(enter_amount, state=WeeklyReportState.entering_amount)

    # Thêm người mới
    dp.register_callback_query_handler(handle_add_member_callback, lambda c: c.data == "add_member", state=WeeklyReportState.choosing_person)
    dp.register_message_handler(add_member_name, state=WeeklyReportState.adding_member_name)
    dp.register_callback_query_handler(add_member_group_cb, lambda c: c.data.startswith("group_"), state=WeeklyReportState.adding_member_group)
    dp.register_message_handler(add_member_rate, state=WeeklyReportState.adding_member_rate)

    # Kết thúc
    dp.register_callback_query_handler(finish_report_callback, lambda c: c.data == "finish_report", state=WeeklyReportState.choosing_person)

    # History
    dp.register_callback_query_handler(show_history_detail, lambda c: c.data in ["history_this_week", "history_last_week"])
    dp.register_callback_query_handler(show_all_weeks_report, lambda c: c.data == "weekly_all_history")
