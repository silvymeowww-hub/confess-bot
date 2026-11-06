import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = "ТУТ_ВСТАВЬТЕ_ТОКЕН_ВАШЕГО_БОТА"
MODERATION_CHAT_ID = -1004322773670

logging.basicConfig(level=logging.INFO)
router = Router()

class Form(StatesGroup):
    waiting_for_text = State()
    waiting_for_choice = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    text = (
        "𝅄      ִㅤ Здравствуйте ! Напишите ваш тейк.  ៸៸ㅤ Пожалуйста, во избежание проблем, "
        "предварительно ознакомьтесь с правилами тейков៸, которые вы можете найти в нашем телеграмм канале! ͜͡꒱          ֹ"
    )
    await message.answer(text)
    await state.set_state(Form.waiting_for_text)

@router.message(Form.waiting_for_text, F.content_type.in_({'text', 'photo', 'video', 'document', 'animation'}))
async def receive_take(message: Message, state: FSMContext):
    await state.update_data(
        message_id=message.message_id,
        from_chat_id=message.chat.id,
        caption=message.caption or message.text or ""
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="꒰ 𝅄    Анонимно  ྀི", callback_data="anon")],
            [InlineKeyboardButton(text="‌     ‌   Не анонимно   ୧      ׄ", callback_data="no_anon")]
        ]
    )

    prompt_text = "𓏵   Выберите, как должен быть отправлен ваш тейк ִ  𝅄  ⊹   ‌   ‌ִ"
    await message.answer(prompt_text, reply_markup=keyboard)
    await state.set_state(Form.waiting_for_choice)

@router.callback_query(Form.waiting_for_choice, F.data.in_({'anon', 'no_anon'}))
async def process_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    if callback.data == "anon":
        header = "໒꒰ ⑅  ｡⁠ ꞈ ｡ ꒱ ͡   #анон ⌣⏜ #тейк
 ׄ  @rpptcfᅠ 𝆹𝅥̼  @rpptcfbot   ദ"
    else:
        author_info = f"Автор: @{user.username}" if user.username else f"Автор: {user.full_name}"
        header = f"໒꒰ ⑅  ｡⁠ ꞈ ｡ ꒱ ͡   #неанон ⌣⏜  #тейк
 ׄ  @rpptcfᅠ 𝆹𝅥̼  @rpptcfbot   ദ
{author_info}"

    original_caption = data.get("caption", "")
    final_text = f"{header}

{original_caption}"

    try:
        if callback.message.reply_to_message and callback.message.reply_to_message.text:
            await callback.bot.send_message(chat_id=MODERATION_CHAT_ID, text=final_text)
        else:
            await callback.bot.copy_message(
                chat_id=MODERATION_CHAT_ID,
                from_chat_id=data['from_chat_id'],
                message_id=data['message_id'],
                caption=final_text
            )
    except Exception as e:
        logging.error(f"Ошибка при отправке в группу: {e}")

    await callback.message.answer("ᅠ₍っ  ₎ა    Спасибо за тейк! 🍥‌꒱")
    await callback.answer()
    await state.clear()

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен и ждет сообщения!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
