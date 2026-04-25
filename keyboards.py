from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from locales import _

def initial_language_selection() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Русский 🇷🇺"), KeyboardButton(text="English 🇬🇧")],
        [KeyboardButton(text="O'zbekcha 🇺🇿")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def main_menu(lang: str) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=_( 'about', lang)), KeyboardButton(text=_( 'services', lang))],
        [KeyboardButton(text=_( 'review', lang)), KeyboardButton(text=_( 'change_lang', lang))],
        [KeyboardButton(text=_( 'change_name', lang))]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def service_menu(lang: str) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text=_( 'service_pediatrician', lang), callback_data="srv_pediatrician"),
         InlineKeyboardButton(text=_( 'service_dentist', lang), callback_data="srv_dentist")],
        [InlineKeyboardButton(text=_( 'service_ent', lang), callback_data="srv_ent"),
         InlineKeyboardButton(text=_( 'service_orthopedist', lang), callback_data="srv_orthopedist")],
        [InlineKeyboardButton(text=_( 'service_allergist', lang), callback_data="srv_allergist"),
         InlineKeyboardButton(text=_( 'service_massage', lang), callback_data="srv_massage")],
        [InlineKeyboardButton(text=_( 'service_diagnostics', lang), callback_data="srv_diagnostics")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def rating_menu() -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=str(i) + " ⭐", callback_data=f"rate_{i}") for i in range(1, 6)]]
    return InlineKeyboardMarkup(inline_keyboard=kb)
