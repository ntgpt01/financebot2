from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("⚠️ Không có thao tác nào đang diễn ra.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Đồng ý huỷ", callback_data="cancel_yes"),
        InlineKeyboardButton("❌ Quay lại", callback_data="cancel_no")
    )
    await message.answer(
        "❓ Bạn có chắc muốn huỷ thao tác hiện tại không?",
        reply_markup=keyboard
    )

async def confirm_cancel(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup()  # Xoá nút
    if query.data == "cancel_yes":
        await state.finish()
        await query.message.answer("❌ Đã huỷ thao tác hiện tại.")
    elif query.data == "cancel_no":
        await query.message.answer("🔄 Tiếp tục thao tác hiện tại.")
