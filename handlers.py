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

class ReviewFSM(StatesGroup):
    choosing_service = State()
    choosing_rating = State()
    writing_comment = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Register the user in the database
    await db.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        "Пожалуйста, выберите язык:\n\nPlease choose your language:\n\nIltimos, tilni tanlang:",
        reply_markup=kb.initial_language_selection()
    )
    await state.set_state(RegistrationFSM.choosing_language)

@router.message(RegistrationFSM.choosing_language, F.text.in_(["Русский 🇷🇺", "English 🇬🇧", "O'zbekcha 🇺🇿"]))
async def language_chosen(message: Message, state: FSMContext):
    lang_map = {
        "Русский 🇷🇺": "ru",
        "English 🇬🇧": "en",
        "O'zbekcha 🇺🇿": "uz"
    }
    lang = lang_map[message.text]
    await db.set_user_language(message.from_user.id, lang)
    await message.answer(_('welcome', lang), reply_markup=kb.main_menu(lang))
    await state.clear()

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

# Review FSM
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
    
    # Ensure user is registered even if they started the bot before the DB update
    await db.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await db.save_review(message.from_user.id, service_name, rating, review_text)
    
    lang = await db.get_user_language(message.from_user.id)
    await message.answer(_('review_saved', lang), reply_markup=kb.main_menu(lang))
    await state.clear()
