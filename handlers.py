from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import database as db
import keyboards as kb
from locales import _

router = Router()

class RegistrationFSM(StatesGroup):
    choosing_language = State()
    entering_first_name = State()
    entering_surname = State()

class EditNameFSM(StatesGroup):
    entering_first_name = State()
    entering_surname = State()

class ReviewFSM(StatesGroup):
    choosing_service = State()
    choosing_rating = State()
    writing_comment = State()


# =====================================================================
#  /start — Returning users go straight to menu, new users register
# =====================================================================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    fully_registered = await db.is_fully_registered(message.from_user.id)
    
    if fully_registered:
        # ✅ Returning user → instant personalized welcome + main menu
        lang = await db.get_user_language(message.from_user.id)
        user_info = await db.get_user_info(message.from_user.id)
        name = user_info['first_name'] if user_info else ''
        welcome = _('welcome_name', lang).format(name=name)
        await message.answer(welcome, reply_markup=kb.main_menu(lang))
        await state.clear()
    else:
        # 🆕 New user → language selection first
        await message.answer(
            "🏥 <b>Welcome to Kids Doctor Clinic!</b>\n"
            "🏥 <b>Kids Doctor klinikasiga xush kelibsiz!</b>\n"
            "🏥 <b>Добро пожаловать в клинику Kids Doctor!</b>\n\n"
            "Please choose your language:\n"
            "Iltimos, tilni tanlang:\n"
            "Пожалуйста, выберите язык:",
            reply_markup=kb.initial_language_selection()
        )
        await state.set_state(RegistrationFSM.choosing_language)


# =====================================================================
#  Language Selection → for new users, proceed to name collection
# =====================================================================

@router.message(RegistrationFSM.choosing_language, F.text.in_(["Русский 🇷🇺", "English 🇬🇧", "O'zbekcha 🇺🇿"]))
async def language_chosen(message: Message, state: FSMContext):
    lang_map = {
        "Русский 🇷🇺": "ru",
        "English 🇬🇧": "en",
        "O'zbekcha 🇺🇿": "uz"
    }
    lang = lang_map[message.text]
    await db.set_user_language(message.from_user.id, lang)
    await state.update_data(lang=lang)
    
    fully_registered = await db.is_fully_registered(message.from_user.id)
    
    if fully_registered:
        # Returning user just changing language → welcome + menu
        user_info = await db.get_user_info(message.from_user.id)
        name = user_info['first_name'] if user_info else ''
        welcome = _('welcome_name', lang).format(name=name)
        await message.answer(welcome, reply_markup=kb.main_menu(lang))
        await state.clear()
    else:
        # New user → ask for first name (keyboard removed!)
        await message.answer(
            _('ask_first_name', lang),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(RegistrationFSM.entering_first_name)


# =====================================================================
#  Registration — First Name → Surname → Welcome + Menu
# =====================================================================

@router.message(RegistrationFSM.entering_first_name)
async def process_first_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    await state.update_data(first_name=message.text.strip())
    await message.answer(
        _('ask_surname', lang),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationFSM.entering_surname)

@router.message(RegistrationFSM.entering_surname)
async def process_surname(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    first_name = data['first_name']
    surname = message.text.strip()
    
    # Save the user
    await db.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=first_name,
        surname=surname
    )
    
    # Show personalized welcome + main menu immediately
    welcome = _('welcome_name', lang).format(name=first_name)
    await message.answer(welcome, reply_markup=kb.main_menu(lang))
    await state.clear()


# =====================================================================
#  Edit Name — allows users to fix their first name and surname
# =====================================================================

@router.message(F.text.in_([
    _('change_name', 'uz'), _('change_name', 'en'), _('change_name', 'ru')
]))
async def handle_change_name(message: Message, state: FSMContext):
    lang = await db.get_user_language(message.from_user.id)
    await state.update_data(lang=lang)
    await message.answer(
        _('ask_new_first_name', lang),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditNameFSM.entering_first_name)

@router.message(EditNameFSM.entering_first_name)
async def edit_first_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    
    await state.update_data(first_name=message.text.strip())
    await message.answer(
        _('ask_new_surname', lang),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(EditNameFSM.entering_surname)

@router.message(EditNameFSM.entering_surname)
async def edit_surname(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    first_name = data['first_name']
    surname = message.text.strip()
    
    # Update the user's names
    await db.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=first_name,
        surname=surname
    )
    
    # Confirm + return to menu
    confirm = _('name_updated', lang).format(first_name=first_name, surname=surname)
    await message.answer(confirm, reply_markup=kb.main_menu(lang))
    await state.clear()


# =====================================================================
#  Main Menu Handlers
# =====================================================================

@router.message(F.text.in_([
    _('about', 'uz'), _('about', 'en'), _('about', 'ru')
]))
async def handle_about(message: Message):
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(_('about_text', lang))

@router.message(F.text.in_([
    _('services', 'uz'), _('services', 'en'), _('services', 'ru')
]))
async def handle_services(message: Message):
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(_('services_text', lang))

@router.message(F.text.in_([
    _('change_lang', 'uz'), _('change_lang', 'en'), _('change_lang', 'ru')
]))
async def handle_change_language(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, выберите язык:\n\nPlease choose your language:\n\nIltimos, tilni tanlang:",
        reply_markup=kb.initial_language_selection()
    )
    await state.set_state(RegistrationFSM.choosing_language)


# =====================================================================
#  Review FSM
# =====================================================================

@router.message(F.text.in_([
    _('review', 'uz'), _('review', 'en'), _('review', 'ru')
]))
async def start_review(message: Message, state: FSMContext):
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(_('choose_service', lang), reply_markup=kb.service_menu(lang))
    await state.set_state(ReviewFSM.choosing_service)

@router.callback_query(ReviewFSM.choosing_service, F.data.startswith("srv_"))
async def review_service_chosen(callback: CallbackQuery, state: FSMContext):
    service = callback.data.split("_")[1]
    await state.update_data(service_name=service)
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(_('choose_rating', lang), reply_markup=kb.rating_menu())
    await state.set_state(ReviewFSM.choosing_rating)
    await callback.answer()

@router.callback_query(ReviewFSM.choosing_rating, F.data.startswith("rate_"))
async def review_rating_chosen(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)
    lang = await db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(_('leave_comment', lang))
    await state.set_state(ReviewFSM.writing_comment)
    await callback.answer()

@router.message(ReviewFSM.writing_comment)
async def review_comment_written(message: Message, state: FSMContext):
    data = await state.get_data()
    service_name = data['service_name']
    rating = data['rating']
    review_text = message.text
    
    # Safety net: ensure user record exists (never overwrites real names)
    await db.ensure_user_exists(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    
    await db.save_review(message.from_user.id, service_name, rating, review_text)
    
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(_('review_saved', lang), reply_markup=kb.main_menu(lang))
    await state.clear()
