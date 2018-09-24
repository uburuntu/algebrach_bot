import asyncio
from math import ceil

from aiogram import types
from peewee import DoesNotExist

from algebrach.config import PAGINATION_LIMIT
from algebrach.data.models import GifResponse, ImageResponse, ManageMessageModel, StickerResponse, TextResponse, \
    UiMessage
from algebrach.utils import create_collage, divide_text, error_log, my_bot

CALLBACK_MODELS_DICT = {'text': TextResponse, 'image': ImageResponse,
                        'gif': GifResponse, 'sticker': StickerResponse}


async def init_ui(message: types.Message):
    chat_id = message.chat.id
    message_id = message.message_id + 1  # Because message.message_id is an id of /init_ui command

    UiMessage.get_or_create(chat_id=chat_id, message_id=message_id, state='init')

    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(*[types.InlineKeyboardButton(btn_text, callback_data='ui:'+btn_text.lower())
                          for btn_text in ['Text', 'Image', 'Sticker', 'Gif']])

    await message.reply("Выберите категорию:", reply_markup=inline_keyboard)


async def clenup_tmp_messages(ui_message):
    if ui_message.temp_message_ids:
        for msg_id in ui_message.temp_message_ids.split(';'):
            await my_bot.delete_message(ui_message.chat_id, int(msg_id))
            await asyncio.sleep(1)
        ui_message.temp_message_id_with_inline_btns = None
        ui_message.temp_message_ids = ''
        ui_message.save()


async def clenup_manage_messages(chat_id):
    q = ManageMessageModel.select().where(ManageMessageModel.chat_id == chat_id)
    for m in q:
        m.delete_instance()
        await my_bot.delete_message(chat_id, m.message_id)
        await asyncio.sleep(1)


async def render_page(ui_message, chat_id):
    response_class, response_type = ui_message.state.split(':')
    model = CALLBACK_MODELS_DICT[response_class]
    query = model.select().where(model.type == response_type)
    responses = query.paginate(ui_message.page, PAGINATION_LIMIT)

    await clenup_tmp_messages(ui_message)

    if responses:
        inline_keyboard = types.InlineKeyboardMarkup()

        inline_keyboard.row(types.InlineKeyboardButton("Добавить", callback_data='ui:add'),
                            types.InlineKeyboardButton("Удалить", callback_data='ui:delete'))

        inline_keyboard.row(types.InlineKeyboardButton("◀️", callback_data='ui:-'),
                            types.InlineKeyboardButton("Назад️", callback_data='ui:back'),
                            types.InlineKeyboardButton("▶️️", callback_data='ui:+'))

        btn_count = int(ceil(query.count()/PAGINATION_LIMIT))
        inline_keyboard.add(*[types.InlineKeyboardButton(str(x+1), callback_data='ui:'+str(x+1))
                            for x in range(btn_count)])

        ui_text = f"Количество записей в базе: {query.count()}\n\n"

        if response_class == 'text':
            ui_text += '\n'.join(
                (f"{i+1}. [{resp.id}] | {resp.content}" for i, resp in enumerate(responses))
            )

            if len(ui_text) > 4096:
                text_chunks = list(divide_text(ui_text, 4096))
                await my_bot.edit_message_text(text_chunks[0], chat_id, ui_message.message_id)
                tmp_messages = []

                if len(text_chunks) > 2:
                    for msg in text_chunks[1:-1]:
                        r = await my_bot.send_message(chat_id, msg)
                        tmp_messages.append(r.message_id)
                        await asyncio.sleep(1)

                r = await my_bot.send_message(chat_id, text_chunks[-1], reply_markup=inline_keyboard)
                tmp_messages.append(r.message_id)
                ui_message.temp_message_id_with_inline_btns = r.message_id
                ui_message.temp_message_ids = ';'.join([str(x) for x in tmp_messages])
                ui_message.save()
            else:
                await my_bot.edit_message_text(ui_text, chat_id, ui_message.message_id, reply_markup=inline_keyboard)

        elif response_class == 'image':
            raw_collage = create_collage([(x.content, x.id) for x in responses])
            photo_msg = await my_bot.send_photo(chat_id, raw_collage)
            ui_text += f'Страница: {ui_message.page}'

            ManageMessageModel.create(
                type='image',
                chat_id=photo_msg.chat.id,
                message_id=photo_msg.message_id,
                response_class=response_class,
                response_type=response_type
            )

            await my_bot.edit_message_text(ui_text, chat_id, ui_message.message_id, reply_markup=inline_keyboard)

        elif response_class == 'sticker':
            collage_tiles = []
            for response in responses:
                sticker_file = await my_bot.download_file_by_id(response.content)
                collage_tiles.append((sticker_file.read(), response.id))

            raw_collage = create_collage(collage_tiles)
            photo_msg = await my_bot.send_photo(chat_id, raw_collage)
            ui_text += f'Страница: {ui_message.page}'

            ManageMessageModel.create(
                type='sticker',
                chat_id=photo_msg.chat.id,
                message_id=photo_msg.message_id,
                response_class=response_class,
                response_type=response_type
            )

            await my_bot.edit_message_text(ui_text, chat_id, ui_message.message_id, reply_markup=inline_keyboard)

        elif response_class == 'gif':
            ui_text += '\n'.join(
                f"{i+1}. [{resp.id}] | {int(len(resp.content)/1024)} Kb" for i, resp in enumerate(responses)
            )
            ui_text += "\n\nИзвините, но просмотр недоступен. Только добавление или удаление"
            await my_bot.edit_message_text(ui_text, chat_id, ui_message.message_id, reply_markup=inline_keyboard)


async def check_neighbour_pages(ui_message, direction):
    """Check whether previous or next page exists """
    response_class, response_type = ui_message.state.split(':')
    model = CALLBACK_MODELS_DICT[response_class]
    query = model.select().where(model.type == response_type)

    if direction == '+':
        if query.paginate(ui_message.page + 1, PAGINATION_LIMIT):
            return True
        else:
            return False

    elif direction == '-':
        if ui_message.page <= 1:
            return False
        else:
            return True


async def process_ui_callback(callback_query: types.CallbackQuery):
    """Handle all callback data with ui prefix"""
    cb_type, cmd = callback_query.data.split(':')
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    try:
        ui_message = UiMessage.get(chat_id=chat_id, message_id=message_id)  # Callback data
    except DoesNotExist:
        ui_message = UiMessage.get(chat_id=chat_id, temp_message_id_with_inline_btns=message_id)

    if cb_type == 'ui':
        if cmd in CALLBACK_MODELS_DICT.keys():
            response_class = cmd
            model = CALLBACK_MODELS_DICT[response_class]

            ui_message.state = response_class + ':choosing_type'
            ui_message.save()

            aviable_types = [x.type for x in model.select(model.type).group_by(model.type).distinct()]
            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.add(*[types.InlineKeyboardButton(btn_text, callback_data='ui:type-' + btn_text.lower())
                                  for btn_text in aviable_types])

            await my_bot.answer_callback_query(callback_query.id)
            await my_bot.edit_message_text('Выберите тип:', chat_id, message_id, reply_markup=inline_keyboard)

        elif cmd.split('-')[0] == 'type' and ui_message.state.split(':')[-1] == 'choosing_type':
            response_type = cmd.split('-')[1]
            response_class = ui_message.state.split(':')[0]

            ui_message.state = response_class + ':' + response_type
            ui_message.save()

            await render_page(ui_message, chat_id)

        elif cmd in ['+', '-']:
            if await check_neighbour_pages(ui_message, cmd):
                if cmd == '+':
                    ui_message.page += 1
                    ui_message.save()

                elif cmd == '-':
                    ui_message.page -= 1
                    ui_message.save()

                await clenup_manage_messages(chat_id)
                await render_page(ui_message, chat_id)
            else:
                await my_bot.answer_callback_query(callback_query.id, text='Дальше пусто')

        elif cmd == 'back':
            ui_message.state = 'init'
            ui_message.save()
            await clenup_tmp_messages(ui_message)
            await clenup_manage_messages(chat_id)

            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.add(*[types.InlineKeyboardButton(btn_text, callback_data='ui:' + btn_text.lower())
                                  for btn_text in ['Text', 'Image', 'Sticker', 'Gif']])

            await my_bot.edit_message_text("Выберите категорию:", chat_id, ui_message.message_id,
                                           reply_markup=inline_keyboard)

        elif cmd.isdigit():
            ui_message.page = int(cmd)
            ui_message.save()
            await clenup_manage_messages(chat_id)
            await render_page(ui_message, chat_id)

        elif cmd == 'add':
            state_args = ui_message.state.split(':')
            if len(state_args) == 2:
                response_class, response_type = state_args
                msg = await my_bot.send_message(ui_message.chat_id, "В ответ на это сообщение пришлите то, " 
                                                                    "что хотите добавить:")

                ManageMessageModel.create(
                    type='add',
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    response_class=response_class,
                    response_type=response_type
                )

        elif cmd == 'delete':
            state_args = ui_message.state.split(':')
            if len(state_args) == 2:
                response_class, response_type = state_args
                msg = await my_bot.send_message(ui_message.chat_id, "В ответ на это сообщение пришлите id, "
                                                                    "записи которую хотите удалить "
                                                                    "(в квадратных скобках):")

                ManageMessageModel.create(
                    type='delete',
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    response_class=response_class,
                    response_type=response_type
                )


async def deserialize_add_message(message: types.Message, response_class):
    if response_class in CALLBACK_MODELS_DICT.keys():
        model = CALLBACK_MODELS_DICT[response_class]
        model = model()
        content = None

        if response_class == 'text':
            content = message.text

        elif response_class == 'sticker':
            if message.sticker:
                content = message.sticker.file_id

        elif response_class == 'image':
            if message.photo:
                image_fileobj = await my_bot.download_file_by_id(message.photo[-1].file_id)
                content = image_fileobj.read()

        elif response_class == 'gif':
            if message.document:
                image_fileobj = await my_bot.download_file_by_id(message.document.file_id)
                content = image_fileobj.read()

        if content:
            model.content = content
            return model


async def add_message(message: types.Message):
    if message.reply_to_message:
        chat_id = message.chat.id
        add_message_id = message.reply_to_message.message_id

        try:
            msg = ManageMessageModel.get(chat_id=chat_id, message_id=add_message_id)
        except DoesNotExist:
            error_log('Add message not found')
            return

        response_class = msg.response_class

        if msg.type == 'add':
            response_model = await deserialize_add_message(message, response_class)
            if response_model:
                response_model.type = msg.response_type
                response_model.save()
                await my_bot.edit_message_text('Успешно добавлен контент, вы не рагуль.', chat_id=chat_id,
                                               message_id=add_message_id)
            else:
                await my_bot.edit_message_text('Неправильный тип, вы рагуль.', chat_id=chat_id,
                                               message_id=add_message_id)
            msg.delete_instance()

        elif msg.type == 'delete':
            model = CALLBACK_MODELS_DICT.get(response_class)
            response_id = message.text.strip()

            if model and response_id.isdigit():
                try:
                    response_to_delete = model.get(id=response_id)
                    response_to_delete.delete_instance()
                    await my_bot.edit_message_text('Успешно удалён контент, вы не рагуль.', chat_id=chat_id,
                                                   message_id=add_message_id)

                except DoesNotExist:
                    await my_bot.edit_message_text('Вы рагуль, ибо id не валидный.', chat_id=chat_id,
                                                   message_id=add_message_id)
            else:
                await my_bot.edit_message_text('Вы рагуль, ибо id не валидный.', chat_id=chat_id,
                                               message_id=add_message_id)
            msg.delete_instance()

