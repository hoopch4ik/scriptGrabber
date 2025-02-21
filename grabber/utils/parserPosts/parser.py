from telethon import TelegramClient


# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

from grabber.config import LOGGING_INFO_FILE, LAST_ID_POSTS_FILE


from datetime import date, datetime
import json
import os
import logging
import asyncio

logging.basicConfig(
    filename=LOGGING_INFO_FILE,
    level=logging.INFO,
    encoding='utf-8'
)

logs = "grabber"

class Logs:
    
    def writeLastPostId(self, channelId:str, new_last_post_id:int)->bool:
        channelId = str(channelId)
        try:
            with open(os.path.join(logs, LAST_ID_POSTS_FILE), 'a+', encoding='utf-8') as f:
                try:
                    f.seek(0)
                    content = f.read()
                    last_posts_ids = json.loads(content)
                    last_posts_ids[channelId]=new_last_post_id
                    f.truncate(0)
                    f.write(json.dumps(last_posts_ids))
                except json.JSONDecodeError as e:
                    f.write(json.dumps({channelId: new_last_post_id}))
                    logging.info(e.msg)
            return True
        except FileNotFoundError:
            with open(os.path.join(logs, LAST_ID_POSTS_FILE), 'a+', encoding='utf-8') as f:
                pass
            logging.error(f'Файл {LAST_ID_POSTS_FILE} не найден. Создал новый')
            return self.writeLastPostId(channelId, new_last_post_id)

        except Exception as e:
            logging.error(e)
            return False

    def getLastPostId(self, channelId:str)->int|bool:
        channelId = str(channelId)
        try:
            with open(os.path.join(logs, LAST_ID_POSTS_FILE), 'r', encoding='utf-8') as f:
                last_posts_ids:dict = json.loads(f.read())
                return int(last_posts_ids[channelId])
        except FileNotFoundError:
            logging.error(f'Файл {LAST_ID_POSTS_FILE} не найден')
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
    
    async def dump_all_messages(self):
        offset_msg = 0

        for channel in self.info_channels:
            logging.info(f'Запуск парсинга канала: {channel}')

            try:
                history = await self.client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_msg,
                offset_date=None, add_offset=0,
                limit=self.limit_msg, max_id=0, min_id=0,
                hash=0
                ))
            except Exception as e:
                logging.error(f'Ошибка при получении истории постов канала: {channel}, {e}')
                continue

            messages = history.messages
            i = len(messages)-1

            while i > -1:
                try:
                    channel_id = messages[i].to_dict()['peer_id']['channel_id']
                    post_id = messages[i].to_dict()['id']
                except Exception as e:
                    logging.error(f'Ошибка при получении id поста: {e}')
                    continue
                last_post_id = self.getLastPostId(channel_id)

                
                if not last_post_id or post_id > last_post_id:
                    for my_channel_id in self.to_channels:
                        try:
                            await self.client.send_message(my_channel_id, messages[i])
                        except Exception as e:
                            continue
                        MiddleWare.sendPost(self, channel_id)
                        await asyncio.sleep(self.timeout)
                    self.writeLastPostId(channel_id, post_id)
                    continue
                i-=1



class MyParser(ParserActions):

    def __init__(self, session_name,
        api_id,
        api_hash):
        SessionConnect.__init__(self, session_name, api_id, api_hash)
    
    async def _main(self):
        while True:
            try:
                # С помощью метода self.client.get_entity(channel) ложим в список информацию о каждом канале
                self.info_channels = [await self.client.get_entity(channel) for channel in self.info_channels]
            except Exception as e:
                logging.error(f'Ошибка при получении информации о каналах: {e}')
                continue
            # Запускаем функцию для дампа сообщений из каналов
            try:
                await self.dump_all_messages()
            except Exception as e:
                logging.error(f'Ошибка при парсинге каналов: {e}')
                continue
            await asyncio.sleep(self.timeout) # Задержка между парсингом каналов в секундах
    
    async def parse(self, info_channels:list, to_channels:list, limit:int=5, timeout:int=15):
        ParserActions.__init__(self, info_channels, to_channels, limit, timeout)
        await SessionConnect.__call__(self)
        
