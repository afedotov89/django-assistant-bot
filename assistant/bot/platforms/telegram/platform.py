import logging
import telegram
from telegram import Update as TelegramUpdate, Bot, ReplyKeyboardRemove
from rest_framework.request import Request

from assistant.bot.domain import BotPlatform, Update, User, SingleAnswer, Photo, UnknownUpdate
from assistant.bot.exceptions import UserUnavailableError
from assistant.bot.platforms.telegram.format import TelegramMarkdownV2FormattedText

logger = logging.getLogger(__name__)


class TelegramBotPlatform(BotPlatform):

    @property
    def codename(self) -> str:
        return 'telegram'

    def __init__(self, token: str):
        self.bot = Bot(token=token)

    async def convert_telegram_update(self, telegram_update: TelegramUpdate) -> Update:
        """Convert a Telegram update to our Update object."""
        if telegram_update.message:
            user_data = telegram_update.message.from_user
        elif telegram_update.callback_query:
            user_data = telegram_update.callback_query.from_user
        else:
            user_data = None

        user = User(
            id=str(user_data.id),
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            language_code=user_data.language_code
        ) if user_data else None

        photo = None
        phone_number = None

        if telegram_update.message:
            chat_id = telegram_update.message.chat_id
            message_id = telegram_update.message.message_id
            text = telegram_update.message.text

            # Extract phone number from contact message
            if telegram_update.message.contact:
                phone_number = telegram_update.message.contact.phone_number

            if telegram_update.message.photo:
                photo = telegram_update.message.photo[-1]
                photo_file = await self.bot.get_file(photo.file_id)
                photo_bytearray = await photo_file.download_as_bytearray()
                photo = Photo(
                    file_id=photo.file_unique_id,
                    extension=photo_file.file_path.split('.')[-1],
                    content=photo_bytearray
                )
                if not text:
                    text = telegram_update.message.caption
        elif telegram_update.callback_query:
            chat_id = telegram_update.callback_query['from']['id']
            message_id = telegram_update.callback_query['message']['message_id']
            text = telegram_update.callback_query.data
        else:
            raise UnknownUpdate('Unknown update type')

        return Update(
            chat_id=str(chat_id),
            message_id=message_id,
            text=text,
            photo=photo,
            user=user,
            phone_number=phone_number,
        )

    async def get_update(self, request: Request) -> Update:
        logger.debug(f'Got Telegram request: {request.data}')
        telegram_update = TelegramUpdate.de_json(request.data, self.bot)
        return await self.convert_telegram_update(telegram_update)

    async def post_answer(self, chat_id: str, answer: SingleAnswer):
        logger.info(f"Answer Text: {answer.text}, Audio Present: {answer.audio is not None}")

        if answer.buttons:
            reply_markup = telegram.InlineKeyboardMarkup(
                [
                    [
                        telegram.InlineKeyboardButton(
                            button.text, callback_data=button.callback_data, url=button.url,
                        )
                        for button in button_row
                    ]
                    for button_row in answer.buttons
                ]
            )
        elif answer.reply_keyboard:
            all_buttons = [button for button_row in answer.reply_keyboard for button in button_row]
            request_contact = any(button.request_contact for button in all_buttons)
            request_location = any(button.request_location for button in all_buttons)
            reply_markup = telegram.ReplyKeyboardMarkup(
                [
                    [
                        telegram.KeyboardButton(
                            text=button.text,
                            request_contact=request_contact,
                            request_location=request_location
                        ) for button in button_row
                    ]
                    for button_row in answer.reply_keyboard
                ],
                one_time_keyboard=request_contact or request_location,
                resize_keyboard=True,
            )
        else:
            reply_markup = ReplyKeyboardRemove()

        text_content = TelegramMarkdownV2FormattedText(answer.text) if answer.text else None
        audio_sent = False
        text_sent = False
        error_occurred = False

        if answer.audio:
            try:
                audio_reply_markup = reply_markup if not text_content else None
                logger.debug(f'Sending Telegram audio to {chat_id}')
                await self.bot.send_audio(
                    chat_id=chat_id,
                    audio=answer.audio.content,
                    filename=answer.audio.filename,
                    reply_markup=audio_reply_markup,
                )
                audio_sent = True
            except telegram.error.Forbidden as e:
                logger.warning(f'Audio sending forbidden to {chat_id}: {e}')
                error_message = e.message.lower()
                if not ('bot was kicked' in error_message or
                        'group chat was deleted' in error_message or
                        'user is deactivated' in error_message):
                    logger.warning(f'User {chat_id} likely unavailable. Raising UserUnavailableError.')
                    error_occurred = True
                    raise UserUnavailableError(chat_id) from e
                else:
                    logger.warning(f'Audio sending forbidden for chat_id {chat_id}, specific reason: {e.message}. Not raising UserUnavailableError.')
                    error_occurred = True
            except telegram.error.BadRequest as e:
                logger.error(f"Failed to send audio to {chat_id} due to BadRequest: {e}")
                error_occurred = True
            except Exception as e:
                logger.exception(f"Unexpected error sending audio to {chat_id}: {e}")
                error_occurred = True
                raise

        if text_content and not isinstance(error_occurred, UserUnavailableError):
            for parse_mode in ('MarkdownV2', None):
                try:
                    logger.debug(f'Sending Telegram message to {chat_id} with parse_mode={parse_mode}:\n{text_content}')
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=text_content,
                        reply_markup=reply_markup,
                        parse_mode=parse_mode,
                        disable_web_page_preview=answer.disable_web_page_preview,
                    )
                    text_sent = True
                    error_occurred = False
                    break
                except telegram.error.BadRequest as e:
                    if "Can't parse" in e.message and parse_mode == 'MarkdownV2':
                        logger.warning(f'Can\'t parse message with parse_mode=MarkdownV2: {e}. Retrying without parse mode.')
                        continue
                    else:
                        logger.error(f"Failed to send message to {chat_id} with parse_mode={parse_mode} due to BadRequest: {e}")
                        error_occurred = True
                        break
                except telegram.error.Forbidden as e:
                    logger.warning(f'Message sending forbidden to {chat_id}: {e}')
                    error_message = e.message.lower()
                    if not ('bot was kicked' in error_message or
                            'group chat was deleted' in error_message or
                            'user is deactivated' in error_message):
                        logger.warning(f'User {chat_id} likely unavailable. Raising UserUnavailableError.')
                        error_occurred = True
                        raise UserUnavailableError(chat_id) from e
                    else:
                        logger.warning(f'Message sending forbidden for chat_id {chat_id}, specific reason: {e.message}. Not raising UserUnavailableError.')
                        error_occurred = True
                        break
                except Exception as e:
                    logger.exception(f"Unexpected error sending message to {chat_id} with parse_mode={parse_mode}: {e}")
                    error_occurred = True
                    raise

        if not audio_sent and not text_sent and not error_occurred:
            logger.warning(f"No audio or text content provided for chat_id {chat_id}, or sending failed without error raise. Nothing sent.")

    async def action_typing(self, chat_id):
        await self.bot.send_chat_action(chat_id=chat_id, action='typing')
