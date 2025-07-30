

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import get_accounts, add_account, get_members, add_member, save_transaction, get_transactions

class FundState(StatesGroup):
    choosing_type = State()
    choosing_category = State()  # ✅ Thêm bước chọn danh mục
    choosing_account = State()
    choosing_member = State()
    entering_amount = State()
    adding_account = State()
    adding_member = State()

# ✅ Menu chính quản lý quỹ
async def fund_menu(query: CallbackQuery):
    await query.answer()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📅 Ghi nhận Quỹ", callback_data="fund_record"),
        InlineKeyboardButton("📊 Báo Cáo Quỹ", callback_data="fund_report"),
        InlineKeyboardButton("📈 Thống Kê", callback_data="fund_stats")  # ✅ Menu thống kê
    )
    await query.message.edit_text("💰 Chọn chức năng quản lý Quỹ:", reply_markup=keyboard)

# ✅ Xử lý callback từ menu chính
async def handle_fund_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "fund_record":
        await select_type(query.message, state)
    elif query.data == "fund_report":
        await fund_report(query.message)
    elif query.data == "fund_stats":
        await select_stats_category(query.message)  # ✅ menu thống kê theo danh mục

# ✅ Bước 1: Chọn loại giao dịch (thu/chi)
async def select_type(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🟢 Thu Quỹ", callback_data="type_thu"),
        InlineKeyboardButton("🔴 Chi Quỹ", callback_data="type_chi")
    )
    await FundState.choosing_type.set()
    await message.edit_text("Chọn loại giao dịch:", reply_markup=keyboard)

# ✅ Bước 2: Chọn danh mục (Cá nhân/Business)
async def select_category(query: CallbackQuery, state: FSMContext):
    await state.update_data(txn_type=query.data)  # Lưu 'type_thu' hoặc 'type_chi'
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 Cá nhân", callback_data="cat_personal"),
        InlineKeyboardButton("🏢 Business", callback_data="cat_business")
    )
    await FundState.choosing_category.set()
    await query.message.edit_text("Chọn danh mục giao dịch:", reply_markup=keyboard)

# ✅ Menu thống kê – chọn danh mục
async def select_stats_category(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 Cá nhân", callback_data="stat_personal"),
        InlineKeyboardButton("🏢 Business", callback_data="stat_business")
    )
    await message.edit_text("Chọn danh mục cần thống kê:", reply_markup=keyboard)

async def handle_type_callback(query: CallbackQuery, state: FSMContext):
    if query.data in ["type_thu", "type_chi"]:
        fund_type = "Thu" if query.data == "type_thu" else "Chi"
        await state.update_data(fund_type=fund_type)
        await select_category(query, state)

# ✅ Callback chọn danh mục → sang bước chọn tài khoản
# async def handle_category_callback(query: CallbackQuery, state: FSMContext):
#     if query.data in ["cat_personal", "cat_business"]:
#         category = query.data.replace("cat_", "")
#         await state.update_data(category=category)
#         await select_account(query.message)
async def handle_category_callback(query: CallbackQuery, state: FSMContext):
    if query.data in ["cat_personal", "cat_business"]:
        category = query.data.replace("cat_", "")
        await state.update_data(category=category)

        accounts = get_accounts()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for acc in accounts:
            keyboard.insert(InlineKeyboardButton(acc, callback_data=f"acc_{acc}"))
        keyboard.add(InlineKeyboardButton("➕ Thêm tài khoản", callback_data="add_account"))

        await query.message.edit_text("Chọn tài khoản:", reply_markup=keyboard)
        await FundState.choosing_account.set()


async def handle_type_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    fund_type = "Thu" if query.data == "type_thu" else "Chi"
    await state.update_data(fund_type=fund_type)
    accounts = get_accounts()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for acc in accounts:
        keyboard.insert(InlineKeyboardButton(acc, callback_data=f"acc_{acc}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm tài khoản", callback_data="add_account"))
    await query.message.edit_text("Chọn tài khoản:", reply_markup=keyboard)
    await FundState.choosing_account.set()

async def handle_account_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "add_account":
        await query.message.answer("Gõ tên tài khoản mới:")
        await FundState.adding_account.set()
        return

    account = query.data.replace("acc_", "")
    await state.update_data(account=account)

    members = get_members()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for mem in members:
        keyboard.insert(InlineKeyboardButton(mem, callback_data=f"mem_{mem}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm người", callback_data="add_member"))
    await query.message.edit_text("Chọn người thực hiện:", reply_markup=keyboard)
    await FundState.choosing_member.set()

async def handle_member_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "add_member":
        await query.message.answer("Gõ tên người mới:")
        await FundState.adding_member.set()
        return

    if query.data.startswith("mem_"):
        member = query.data.replace("mem_", "")
        await state.update_data(member=member)
        await query.message.delete()
        await query.message.answer("Nhập số tiền:")
        await FundState.entering_amount.set()

# async def save_transaction_handler(message: types.Message, state: FSMContext):
#     try:
#         amount = int(message.text.replace(",", "").replace(".", ""))
#     except ValueError:
#         await message.answer("⚠️ Số tiền không hợp lệ. Nhập lại:")
#         return

#     data = await state.get_data()
#     save_transaction(data["fund_type"], data["account"], data["member"], amount)

#     icon = "🟢" if data["fund_type"] == "Thu" else "🔴"
#     msg = (
#         "✅ Giao dịch thành công!\n\n"
#         f"{icon} Loại:       {data['fund_type']}\n"
#         f"🏦 Tài khoản:  {data['account']}\n"
#         f"💵 Số tiền:    {amount:,} VNĐ\n"
#         f"👤 Người:      {data['member']}"
#     )
#     await message.answer(msg)
#     await state.finish()
async def save_transaction_handler(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(",", "").replace(".", ""))
    except ValueError:
        await message.answer("⚠️ Số tiền không hợp lệ. Nhập lại:")
        return

    data = await state.get_data()
    fund_type = data.get("fund_type")
    account = data.get("account")
    member = data.get("member")
    category = data.get("category")  # ✅ lấy category đã chọn

    # ✅ Ghi nhận giao dịch có thêm category
    save_transaction(fund_type, account, member, amount, category)

    icon = "🟢" if fund_type == "Thu" else "🔴"
    msg = (
        "✅ Giao dịch thành công!\n\n"
        f"{icon} Loại:       {fund_type}\n"
        f"🏦 Tài khoản:  {account}\n"
        f"💵 Số tiền:    {amount:,} VNĐ\n"
        f"👤 Người:      {member}\n"
        f"📂 Danh mục:   {'Cá nhân' if category == 'personal' else 'Business'}"
    )
    await message.answer(msg)
    await state.finish()

from db import get_transactions, get_accounts
from aiogram import types

# XÓA đoạn async def fund_report(...) bên trong

async def fund_report(message: types.Message):
    txs = get_transactions()
    if not txs:
        await message.answer("📭 Hiện chưa có giao dịch nào.")
        return

    thu = sum(t['amount'] for t in txs if t['type'] == 'Thu')
    chi = sum(t['amount'] for t in txs if t['type'] == 'Chi')
    sodu = thu - chi

    acc_balance = {}
    for t in txs:
        acc = t['account']
        amt = t['amount'] if t['type'] == 'Thu' else -t['amount']
        acc_balance[acc] = acc_balance.get(acc, 0) + amt

    msg = "📉 Tổng Hợp Thu Chi\n"
    msg += "Loại | Số tiền\n"
    msg += "-------------------------\n"
    msg += f"🟢 Thu  | {thu:,} VNĐ\n"
    msg += f"🔴 Chi  | {chi:,} VNĐ\n"
    msg += f"💰 Số dư | {sodu:,} VNĐ\n\n"

    msg += "💼 Số Dư Theo Nguồn Tiền\n"
    msg += "-------------------------\n"
    for acc, val in acc_balance.items():
        msg += f"🏦 {acc:<6} : 💰 {val:,} VNĐ\n"

    msg += "\n🧾 Lịch Sử Quỹ:\n"
    msg += "-------------------------\n"
    msg += "ID | Time      | Type | Amount | Mem\n"
    for i, t in enumerate(txs, 1):
        icon = "🟢 T" if t["type"] == "Thu" else "🔴 C"
        msg += f"{i:02} | {t['time']} | {icon} | {t['amount']:,} | 👤 {t['member']}\n"

    await message.answer(f"<code>{msg}</code>", parse_mode="HTML")

    
async def handle_stats_callback(query: CallbackQuery):
    await query.answer()
    category = query.data.replace("stat_", "")  # 'personal' hoặc 'business'
    txs = get_transactions()
    filtered = [t for t in txs if t.get("category") == category]
    if not filtered:
        await query.message.answer("📭 Không có giao dịch trong danh mục này.")
        return

    thu = sum(t['amount'] for t in filtered if t['type'] == 'Thu')
    chi = sum(t['amount'] for t in filtered if t['type'] == 'Chi')
    sodu = thu - chi

    acc_balance = {}
    for t in filtered:
        acc = t['account']
        amt = t['amount'] if t['type'] == 'Thu' else -t['amount']
        acc_balance[acc] = acc_balance.get(acc, 0) + amt

    msg = f"📈 Thống kê danh mục: {'Cá nhân' if category == 'personal' else 'Business'}\n"
    msg += "-------------------------\n"
    msg += f"🟢 Thu: {thu:,} VNĐ\n"
    msg += f"🔴 Chi: {chi:,} VNĐ\n"
    msg += f"💰 Số dư: {sodu:,} VNĐ\n\n"
    msg += "🏦 Theo tài khoản:\n"
    for acc, val in acc_balance.items():
        msg += f"- {acc}: {val:,} VNĐ\n"

    await query.message.answer(f"<code>{msg}</code>", parse_mode="HTML")
<<<<<<< HEAD
=======
    await query.message.edit_reply_markup(reply_markup=None)
>>>>>>> 197f807 (➕ Thêm danh mục Cá nhân/Business khi ghi nhận quỹ và thống kê theo danh mục)

async def add_account_handler(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Tên không hợp lệ.")
        return
    add_account(name)
    await state.update_data(account=name)
    members = get_members()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for mem in members:
        keyboard.insert(InlineKeyboardButton(mem, callback_data=f"mem_{mem}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm người", callback_data="add_member"))
    await message.answer("✅ Đã thêm tài khoản.")
    await message.answer("Chọn người thực hiện:", reply_markup=keyboard)
    await FundState.choosing_member.set()

async def add_member_handler(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Tên không hợp lệ.")
        return
    add_member(name)
    await state.update_data(member=name)
    await message.answer("✅ Đã thêm người.")
    await message.answer("Nhập số tiền:")
    await FundState.entering_amount.set()

def register(dp):
    dp.register_callback_query_handler(fund_menu, lambda c: c.data == "fund_menu")
    dp.register_callback_query_handler(handle_fund_callback, lambda c: c.data.startswith("fund"))
    dp.register_callback_query_handler(handle_type_callback, lambda c: c.data.startswith("type"), state=FundState.choosing_type)
    dp.register_callback_query_handler(handle_account_callback, lambda c: c.data.startswith("acc") or c.data == "add_account", state=FundState.choosing_account)
    dp.register_callback_query_handler(handle_member_callback, lambda c: c.data.startswith("mem") or c.data == "add_member", state=FundState.choosing_member)
    dp.register_message_handler(save_transaction_handler, state=FundState.entering_amount)
    dp.register_message_handler(add_account_handler, state=FundState.adding_account)
    dp.register_message_handler(add_member_handler, state=FundState.adding_member)
    dp.register_callback_query_handler(handle_category_callback, lambda c: c.data.startswith("cat_"), state=FundState.choosing_category)
    dp.register_callback_query_handler(handle_stats_callback, lambda c: c.data.startswith("stat_"))

<<<<<<< HEAD
=======



from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import get_accounts, add_account, get_members, add_member, save_transaction, get_transactions

class FundState(StatesGroup):
    choosing_type = State()
    choosing_category = State()  # ✅ Thêm bước chọn danh mục
    choosing_account = State()
    choosing_member = State()
    entering_amount = State()
    adding_account = State()
    adding_member = State()

# ✅ Menu chính quản lý quỹ
async def fund_menu(query: CallbackQuery):
    await query.answer()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📅 Ghi nhận Quỹ", callback_data="fund_record"),
        InlineKeyboardButton("📊 Báo Cáo Quỹ", callback_data="fund_report"),
        InlineKeyboardButton("📈 Thống Kê", callback_data="fund_stats")  # ✅ Menu thống kê
    )
    await query.message.edit_text("💰 Chọn chức năng quản lý Quỹ:", reply_markup=keyboard)

# ✅ Xử lý callback từ menu chính
async def handle_fund_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "fund_record":
        await select_type(query.message, state)
    elif query.data == "fund_report":
        await fund_report(query.message)
    elif query.data == "fund_stats":
        await select_stats_category(query.message)  # ✅ menu thống kê theo danh mục

# ✅ Bước 1: Chọn loại giao dịch (thu/chi)
async def select_type(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🟢 Thu Quỹ", callback_data="type_thu"),
        InlineKeyboardButton("🔴 Chi Quỹ", callback_data="type_chi")
    )
    await FundState.choosing_type.set()
    await message.edit_text("Chọn loại giao dịch:", reply_markup=keyboard)

# ✅ Bước 2: Chọn danh mục (Cá nhân/Business)
async def select_category(query: CallbackQuery, state: FSMContext):
    await state.update_data(txn_type=query.data)  # Lưu 'type_thu' hoặc 'type_chi'
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 Cá nhân", callback_data="cat_personal"),
        InlineKeyboardButton("🏢 Business", callback_data="cat_business")
    )
    await FundState.choosing_category.set()
    await query.message.edit_text("Chọn danh mục giao dịch:", reply_markup=keyboard)

# ✅ Menu thống kê – chọn danh mục
async def select_stats_category(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("👤 Cá nhân", callback_data="stat_personal"),
        InlineKeyboardButton("🏢 Business", callback_data="stat_business")
    )
    await message.edit_text("Chọn danh mục cần thống kê:", reply_markup=keyboard)

async def handle_type_callback(query: CallbackQuery, state: FSMContext):
    if query.data in ["type_thu", "type_chi"]:
        fund_type = "Thu" if query.data == "type_thu" else "Chi"
        await state.update_data(fund_type=fund_type)
        await select_category(query, state)

# ✅ Callback chọn danh mục → sang bước chọn tài khoản
# async def handle_category_callback(query: CallbackQuery, state: FSMContext):
#     if query.data in ["cat_personal", "cat_business"]:
#         category = query.data.replace("cat_", "")
#         await state.update_data(category=category)
#         await select_account(query.message)
async def handle_category_callback(query: CallbackQuery, state: FSMContext):
    if query.data in ["cat_personal", "cat_business"]:
        category = query.data.replace("cat_", "")
        await state.update_data(category=category)

        accounts = get_accounts()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for acc in accounts:
            keyboard.insert(InlineKeyboardButton(acc, callback_data=f"acc_{acc}"))
        keyboard.add(InlineKeyboardButton("➕ Thêm tài khoản", callback_data="add_account"))

        await query.message.edit_text("Chọn tài khoản:", reply_markup=keyboard)
        await FundState.choosing_account.set()


async def handle_type_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    fund_type = "Thu" if query.data == "type_thu" else "Chi"
    await state.update_data(fund_type=fund_type)
    accounts = get_accounts()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for acc in accounts:
        keyboard.insert(InlineKeyboardButton(acc, callback_data=f"acc_{acc}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm tài khoản", callback_data="add_account"))
    await query.message.edit_text("Chọn tài khoản:", reply_markup=keyboard)
    await FundState.choosing_account.set()

async def handle_account_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "add_account":
        await query.message.answer("Gõ tên tài khoản mới:")
        await FundState.adding_account.set()
        return

    account = query.data.replace("acc_", "")
    await state.update_data(account=account)

    members = get_members()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for mem in members:
        keyboard.insert(InlineKeyboardButton(mem, callback_data=f"mem_{mem}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm người", callback_data="add_member"))
    await query.message.edit_text("Chọn người thực hiện:", reply_markup=keyboard)
    await FundState.choosing_member.set()

async def handle_member_callback(query: CallbackQuery, state: FSMContext):
    await query.answer()
    if query.data == "add_member":
        await query.message.answer("Gõ tên người mới:")
        await FundState.adding_member.set()
        return

    if query.data.startswith("mem_"):
        member = query.data.replace("mem_", "")
        await state.update_data(member=member)
        await query.message.delete()
        await query.message.answer("Nhập số tiền:")
        await FundState.entering_amount.set()

# async def save_transaction_handler(message: types.Message, state: FSMContext):
#     try:
#         amount = int(message.text.replace(",", "").replace(".", ""))
#     except ValueError:
#         await message.answer("⚠️ Số tiền không hợp lệ. Nhập lại:")
#         return

#     data = await state.get_data()
#     save_transaction(data["fund_type"], data["account"], data["member"], amount)

#     icon = "🟢" if data["fund_type"] == "Thu" else "🔴"
#     msg = (
#         "✅ Giao dịch thành công!\n\n"
#         f"{icon} Loại:       {data['fund_type']}\n"
#         f"🏦 Tài khoản:  {data['account']}\n"
#         f"💵 Số tiền:    {amount:,} VNĐ\n"
#         f"👤 Người:      {data['member']}"
#     )
#     await message.answer(msg)
#     await state.finish()
async def save_transaction_handler(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(",", "").replace(".", ""))
    except ValueError:
        await message.answer("⚠️ Số tiền không hợp lệ. Nhập lại:")
        return

    data = await state.get_data()
    fund_type = data.get("fund_type")
    account = data.get("account")
    member = data.get("member")
    category = data.get("category")  # ✅ lấy category đã chọn

    # ✅ Ghi nhận giao dịch có thêm category
    save_transaction(fund_type, account, member, amount, category)

    icon = "🟢" if fund_type == "Thu" else "🔴"
    msg = (
        "✅ Giao dịch thành công!\n\n"
        f"{icon} Loại:       {fund_type}\n"
        f"🏦 Tài khoản:  {account}\n"
        f"💵 Số tiền:    {amount:,} VNĐ\n"
        f"👤 Người:      {member}\n"
        f"📂 Danh mục:   {'Cá nhân' if category == 'personal' else 'Business'}"
    )
    await message.answer(msg)
    await state.finish()

from db import get_transactions, get_accounts
from aiogram import types

# XÓA đoạn async def fund_report(...) bên trong

async def fund_report(message: types.Message):
    txs = get_transactions()
    if not txs:
        await message.answer("📭 Hiện chưa có giao dịch nào.")
        return

    thu = sum(t['amount'] for t in txs if t['type'] == 'Thu')
    chi = sum(t['amount'] for t in txs if t['type'] == 'Chi')
    sodu = thu - chi

    acc_balance = {}
    for t in txs:
        acc = t['account']
        amt = t['amount'] if t['type'] == 'Thu' else -t['amount']
        acc_balance[acc] = acc_balance.get(acc, 0) + amt

    msg = "📉 Tổng Hợp Thu Chi\n"
    msg += "Loại | Số tiền\n"
    msg += "-------------------------\n"
    msg += f"🟢 Thu  | {thu:,} VNĐ\n"
    msg += f"🔴 Chi  | {chi:,} VNĐ\n"
    msg += f"💰 Số dư | {sodu:,} VNĐ\n\n"

    msg += "💼 Số Dư Theo Nguồn Tiền\n"
    msg += "-------------------------\n"
    for acc, val in acc_balance.items():
        msg += f"🏦 {acc:<6} : 💰 {val:,} VNĐ\n"

    msg += "\n🧾 Lịch Sử Quỹ:\n"
    msg += "-------------------------\n"
    msg += "ID | Time      | Type | Amount | Mem\n"
    for i, t in enumerate(txs, 1):
        icon = "🟢 T" if t["type"] == "Thu" else "🔴 C"
        msg += f"{i:02} | {t['time']} | {icon} | {t['amount']:,} | 👤 {t['member']}\n"

    await message.answer(f"<code>{msg}</code>", parse_mode="HTML")

    
async def handle_stats_callback(query: CallbackQuery):
    await query.answer()
    category = query.data.replace("stat_", "")  # 'personal' hoặc 'business'
    txs = get_transactions()
    filtered = [t for t in txs if t.get("category") == category]
    if not filtered:
        await query.message.answer("📭 Không có giao dịch trong danh mục này.")
        return

    thu = sum(t['amount'] for t in filtered if t['type'] == 'Thu')
    chi = sum(t['amount'] for t in filtered if t['type'] == 'Chi')
    sodu = thu - chi

    acc_balance = {}
    for t in filtered:
        acc = t['account']
        amt = t['amount'] if t['type'] == 'Thu' else -t['amount']
        acc_balance[acc] = acc_balance.get(acc, 0) + amt

    msg = f"📈 Thống kê danh mục: {'Cá nhân' if category == 'personal' else 'Business'}\n"
    msg += "-------------------------\n"
    msg += f"🟢 Thu: {thu:,} VNĐ\n"
    msg += f"🔴 Chi: {chi:,} VNĐ\n"
    msg += f"💰 Số dư: {sodu:,} VNĐ\n\n"
    msg += "🏦 Theo tài khoản:\n"
    for acc, val in acc_balance.items():
        msg += f"- {acc}: {val:,} VNĐ\n"

    await query.message.answer(f"<code>{msg}</code>", parse_mode="HTML")
    await query.message.edit_reply_markup(reply_markup=None)

async def add_account_handler(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Tên không hợp lệ.")
        return
    add_account(name)
    await state.update_data(account=name)
    members = get_members()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for mem in members:
        keyboard.insert(InlineKeyboardButton(mem, callback_data=f"mem_{mem}"))
    keyboard.add(InlineKeyboardButton("➕ Thêm người", callback_data="add_member"))
    await message.answer("✅ Đã thêm tài khoản.")
    await message.answer("Chọn người thực hiện:", reply_markup=keyboard)
    await FundState.choosing_member.set()

async def add_member_handler(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Tên không hợp lệ.")
        return
    add_member(name)
    await state.update_data(member=name)
    await message.answer("✅ Đã thêm người.")
    await message.answer("Nhập số tiền:")
    await FundState.entering_amount.set()

def register(dp):
    dp.register_callback_query_handler(fund_menu, lambda c: c.data == "fund_menu")
    dp.register_callback_query_handler(handle_fund_callback, lambda c: c.data.startswith("fund"))
    dp.register_callback_query_handler(handle_type_callback, lambda c: c.data.startswith("type"), state=FundState.choosing_type)
    dp.register_callback_query_handler(handle_account_callback, lambda c: c.data.startswith("acc") or c.data == "add_account", state=FundState.choosing_account)
    dp.register_callback_query_handler(handle_member_callback, lambda c: c.data.startswith("mem") or c.data == "add_member", state=FundState.choosing_member)
    dp.register_message_handler(save_transaction_handler, state=FundState.entering_amount)
    dp.register_message_handler(add_account_handler, state=FundState.adding_account)
    dp.register_message_handler(add_member_handler, state=FundState.adding_member)
    dp.register_callback_query_handler(handle_category_callback, lambda c: c.data.startswith("cat_"), state=FundState.choosing_category)
    dp.register_callback_query_handler(handle_stats_callback, lambda c: c.data.startswith("stat_"))

>>>>>>> 197f807 (➕ Thêm danh mục Cá nhân/Business khi ghi nhận quỹ và thống kê theo danh mục)
