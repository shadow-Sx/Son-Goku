from aiogram import Router, types
from keyboards.admin_panel import admin_panel

router = Router()

ADMIN_ID = 123456789  # o'zingning ID'ingni qo'yasan

@router.message(commands=["admin"])
async def admin_cmd(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔ Siz admin emassiz.")
    
    await msg.answer(
        "🌸 *Anime Admin Panelga xush kelibsiz!*",
        reply_markup=admin_panel(),
        parse_mode="Markdown"
    )
