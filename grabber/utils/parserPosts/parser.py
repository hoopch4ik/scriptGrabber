from telethon import TelegramClient


# классы для работы с каналами
# from telethon.tl.functions.channels import GetParticipantsRequest
# from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    InputPhoto,
    InputDocument,
    Message,
    MessageMediaWebPage
)
from telethon.errors.rpcerrorlist import MediaCaptionTooLongError


from config import LOGGING_INFO_FILE, LAST_ID_POSTS_FILE


import json
import os
import logging
import asyncio

logging.basicConfig(
    filename=LOGGING_INFO_FILE,
    level=logging.INFO,
    encoding='utf-8'
)

LOGS_DIR = os.getcwd()+"/grabber/utils/temp/"
OFFSET_MSG = 0
MAX_CAPTION_LENGTH = 1024





class Logs:
    
    
    def writeLastPostId(self, my_channel_peer:str|int, to_channel_peer:str|int, new_last_post_id:int)->bool:
        my_channel_peer = str(my_channel_peer)
        to_channel_peer = str(to_channel_peer)
        
        try:
            with open(os.path.join(LOGS_DIR, LAST_ID_POSTS_FILE), 'a+', encoding='utf-8') as f:
                try:
                    f.seek(0)
                    content = f.read()
                    if not content:
                        content = "{}"
                        
                    json_data: dict = json.loads(content)
                    json_data_to_channels = json_data.get(my_channel_peer) or {}
                    
                    json_data = {**json_data,
                        my_channel_peer: {
                            **json_data_to_channels,
                            to_channel_peer:new_last_post_id
                        }
                    }
                    
                    
                    f.truncate(0)
                    f.write(json.dumps(json_data, indent=4))
                except json.JSONDecodeError as e:
                    # f.write(json.dumps({channelId: new_last_post_id}))
                    # logging.info(e.msg)
                    logging.error(e.msg)
                    print(e)
                    
            return True
        except FileNotFoundError:
            with open(os.path.join(LOGS_DIR, LAST_ID_POSTS_FILE), 'a+', encoding='utf-8') as f:
                pass
            return self.writeLastPostId(my_channel_peer, to_channel_peer, new_last_post_id)

        except Exception as e:
            logging.error(e)
            print(e)
            return False

    def getLastPostId(self, my_channel_peer:str|int, to_channel_peer:str|int)->int|bool:
        my_channel_peer = str(my_channel_peer)
        to_channel_peer = str(to_channel_peer)
        
        try:
            with open(os.path.join(LOGS_DIR, LAST_ID_POSTS_FILE), 'r', encoding='utf-8') as f:
                content = f.read()
                if not content:
                    return False

                json_data:dict = json.loads(content)
                
                if json_data:
                    to_channels = json_data.get(my_channel_peer)
                    if to_channels:
                        last_post_id = to_channels.get(to_channel_peer)
                        if last_post_id:
                            return int(last_post_id)

                return False
                
        except FileNotFoundError:
            return False
        except Exception as e:
            logging.error(e)
            return False




class SessionConnect:
    
    api_id:int
    api_hash:str
    session_name:str
    
    def __init__(self,session_name,
        api_id,
        api_hash):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
    
    async def __call__(self):
        self.client = TelegramClient(
            self.session_name,
            self.api_id,
            self.api_hash,
            device_model = "iPhone 13 Pro Max",
            system_version = "14.8.1",
            app_version = "8.4",
            lang_code = "en",
            system_lang_code = "en-US"
        )
        await self.client.start()
        await self._main()

    async def _main(self):
        pass


class MiddleWare:
    
    def sendPost(self, id_channel):
        print(f'''
*** Спарсен новый пост с канала: {id_channel} ***
''')
    

# async def send_photo_to_channel(client: TelegramClient, target_channel_id, media_list, caption=""):
#     """Отправляет фото в целевой канал."""
#     try:

#         # Явно указываем тип InputMediaPhoto
#         await client.send_file(
#             entity=target_channel_id,
#             file=media_list,  # Отправляем один объект InputMediaPhoto
#             caption=caption,
#         )
#         print("Фото успешно отправлено!")
#     except Exception as e:
#         print(f"Ошибка при отправке фото: {e}")


class ParserActions(MiddleWare, SessionConnect, Logs):
    
    limit_msg: int
    info_channels:list
    to_channels:list
    
    def __init__(self,
        info_channels:list,
        to_channels:list,
        limit:int=5,
        timeout:int=15
    ):
        """
            Инициализирует входные аргументы
            Апгументы:
            
                info_channels (list): список каналов(групп)-источников
                to_channels (list): список каналов(групп)-получателей
                limit (int) = 5: начальныя точка старта граббера постов ((id последнего поста) - 5 => с этого поста идет запуск)
                timeout (int) = 15: Интервал между парсингом постов в секундах
                
        """
        self.info_channels = info_channels
        self.to_channels = to_channels
        self.limit_msg = limit
        self.timeout = timeout
    
    
    
    async def __get_history(self, channel_peer) -> dict[int, dict]:
        history = await self.client(GetHistoryRequest(
            peer=channel_peer,
            offset_id=OFFSET_MSG,
            offset_date=None, add_offset=0,
            limit=self.limit_msg, max_id=0, min_id=0,
            hash=0
        ))

        __messages: list[Message] = history.messages
        messages: list[Message] = []
        result_messages: dict[int, dict] = {}

        for message in __messages:
            if message.id == 1:
                continue
            messages.insert(0, message)

        for message in messages:
            
            grouped_id: int | None = message.grouped_id # Используем .get()
            mixed_id = str(grouped_id or message.id)

            media = message.media  # Безопасное получение media

            if isinstance(media, MessageMediaDocument):
                media = InputDocument(media.document.id, media.document.access_hash, media.document.file_reference)
            elif isinstance(media, MessageMediaPhoto):
                media = InputPhoto(media.photo.id, media.photo.access_hash, media.photo.file_reference)
            elif isinstance(media, MessageMediaWebPage):
                media = None
            else:
                logging.error("Неожидаемый тип документа: " + str(type(media)))
                media = None
                # raise TypeError("Неожидаемый тип документа" + str(type(media)))


            if result_messages.get(mixed_id):
                if media:
                    result_messages[mixed_id]["album_media"].append(media)
                result_messages[mixed_id]["id"] = message.id
                if message.message:
                    result_messages[mixed_id]["message"] = message
                continue

            res_message = {
                "id": message.id,
                "channel_id": message.peer_id.channel_id,
                "grouped_id": grouped_id,
                "message": message,
                "album_media": [media] if media else []  # Добавляем InputMedia
            }

            result_messages[mixed_id] = res_message

        return result_messages
        
    
    async def dump_all_messages(self):

        for channel in self.info_channels:
            logging.info(f'Запуск парсинга канала: {channel}')

            
            try:
                messages = await self.__get_history(channel)
            except:
                continue
            messages = list(messages.values())


            for message in messages:
                to_channel_id = message['channel_id']
                message_id = message['id']

                for my_channel_peer in self.to_channels:
                    last_post_id = self.getLastPostId(my_channel_peer, to_channel_id)
                    
                    if not last_post_id or message_id > last_post_id:
                        try:
                            media_list: list = message["album_media"]
                            # await send_photo_to_channel(self.client, my_channel_peer, media_list, "Тестовое сообщение")
                            # return

                            await self.client.send_message(
                                my_channel_peer,
                                message["message"],
                                file=media_list if len(media_list) else None,
                                parse_mode="markdown",
                            )
                            
                            MiddleWare.sendPost(self, to_channel_id)
                            self.writeLastPostId(my_channel_peer, to_channel_id, message_id)
                        except MediaCaptionTooLongError:
                            print("Сообщение превысило допустимую длину! Оно не опубликовалось.")
                            logging.error("Сообщение превысило допустимую длину! Оно не опубликовалось.")

                        except Exception as e:
                            logging.error(f"Ошибка при отправке сообщения: {e}")
                            print(f"Ошибка при отправке сообщения: {e}")


                await asyncio.sleep(self.timeout)


class MyParser(ParserActions):

    def __init__(self, session_name,
        api_id,
        api_hash):
        SessionConnect.__init__(self, session_name, api_id, api_hash)
    
    async def _main(self):
        while True:
            # С помощью метода self.client.get_entity(channel) ложим в список информацию о каждом канале
            self.info_channels = [await self.client.get_entity(channel) for channel in self.info_channels]
            # Запускаем функцию для дампа сообщений из каналов
            await self.dump_all_messages()
            await asyncio.sleep(self.timeout) # Задержка между парсингом каналов в секундах
    
    async def parse(self, info_channels:list, to_channels:list, limit:int=5, timeout:int=5):
        ParserActions.__init__(self, info_channels, to_channels, limit, timeout)
        await SessionConnect.__call__(self)
        
