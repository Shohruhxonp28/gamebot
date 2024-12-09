import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

# Bot uchun tokeningizni o‘rnating
BOT_TOKEN = '7024566197:AAE5MzDTLzDz7bsSiZA8gE_utum4uTBx6TE'

# Bot va dispatcher ob'yektlarini yaratamiz
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Maksimal urinishlar soni
ATTEMPTS = 5

# Foydalanuvchi uchun ma'lumotlarni saqlovchi lug‘at
user = {
    'in_game': False,          # O‘yin holati
    'secret_number': None,     # Sirli son
    'attempts': None,          # Urinishlar soni
    'total_games': 0,          # Umumiy o‘yinlar soni
    'wins': 0                  # Yutgan o‘yinlar soni
}

# Tasodifiy son yaratish funksiyasi
def get_random_number() -> int:
    return random.randint(1, 100)

# Start komandasi uchun handler
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Salom!\n"Keling, sonni topamiz!" o‘yinini o‘ynaymizmi?\n\n'
        'Qoidalar va komandalar haqida bilish uchun /help ni yuboring.'
    )

# Help komandasi uchun handler
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        f'O‘yin qoidalari:\n\nMen 1 dan 100 gacha sonni o‘ylayman, '
        f'siz uni topishingiz kerak. Sizda {ATTEMPTS} ta urinish bor.\n\n'
        f'Dastur komandalar:\n/help - yordam\n/cancel - o‘yindan chiqish\n'
        f'/stat - statistikani ko‘rish\n\nO‘ynaymizmi?'
    )

# Statistika komandasi uchun handler
@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    await message.answer(
        f'Umumiy o‘yinlar soni: {user["total_games"]}\n'
        f'Yutgan o‘yinlar: {user["wins"]}'
    )

# Cancel komandasi uchun handler
@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    if user['in_game']:
        user['in_game'] = False
        await message.answer('Siz o‘yindan chiqdingiz. Yana o‘ynashni xohlasangiz, yozing.')
    else:
        await message.answer('Biz hali o‘yin o‘ynamayapmiz. Balki o‘ynar joymiz?')

# Ijobiy javob uchun handler ("Ha", "O‘ynaymiz" va boshqalar)
@dp.message(F.text.lower().in_(['ha', 'o‘ynaymiz', 'boshlaymiz', 'o‘ynashni xohlayman']))
async def process_positive_answer(message: Message):
    if not user['in_game']:
        user['in_game'] = True
        user['secret_number'] = get_random_number()
        user['attempts'] = ATTEMPTS
        await message.answer('Ajoyib!\n\nMen 1 dan 100 gacha sonni o‘yladim. Topishga harakat qiling!')
    else:
        await message.answer('Biz o‘yinni boshlaganmiz. Faqat 1 dan 100 gacha bo‘lgan sonlarni yoki /cancel ni yuboring.')

# Salbiy javob uchun handler ("Yo‘q", "O‘ynamayman" va boshqalar)
@dp.message(F.text.lower().in_(['yo‘q', 'o‘ynamayman', 'xohlamayman']))
async def process_negative_answer(message: Message):
    if not user['in_game']:
        await message.answer('Afsus :(\nAgar o‘ynashni xohlasangiz, xabar yuboring.')
    else:
        await message.answer('Biz hozir o‘ynayapmiz. 1 dan 100 gacha son yuboring.')

# Foydalanuvchi son yuborganda ishlovchi handler
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    if user['in_game']:
        guessed_number = int(message.text)
        if guessed_number == user['secret_number']:
            user['in_game'] = False
            user['total_games'] += 1
            user['wins'] += 1
            await message.answer('Tabriklayman! Siz sonni topdingiz!\nYana o‘ynaymizmi?')
        elif guessed_number > user['secret_number']:
            user['attempts'] -= 1
            await message.answer('Men o‘ylagan son kichikroq.')
        elif guessed_number < user['secret_number']:
            user['attempts'] -= 1
            await message.answer('Men o‘ylagan son kattaroq.')

        if user['attempts'] == 0:
            user['in_game'] = False
            user['total_games'] += 1
            await message.answer(
                f'Afsus, urinishlaringiz tugadi. Siz yutqazdingiz :(\n'
                f'Men o‘ylagan son {user["secret_number"]} edi.\nYana o‘ynashni xohlaysizmi?'
            )
    else:
        await message.answer('Biz hali o‘yin boshlamadik. O‘ynashni xohlaysizmi?')

# Foydalanuvchi boshqa xabar yuborganda ishlovchi handler
@dp.message()
async def process_other_answers(message: Message):
    if user['in_game']:
        await message.answer('Biz o‘ynayapmiz. Faqat 1 dan 100 gacha sonlarni yoki /cancel ni yuboring.')
    else:
        await message.answer('Men faqat o‘yin o‘ynashni bilaman. Keling, o‘yin o‘ynaymiz!')

# Botni ishga tushirish
if __name__ == '__main__':
    dp.run_polling(bot)
