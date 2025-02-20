from .grabber.config import API_ID, API_HASH, SESSION_NAME
from .grabber.utils.parserPosts import MyParser

import os
import threading
import asyncio

telegram_data = {
    "api_id": API_ID,
    "api_hash": API_HASH,
    "session_name": SESSION_NAME
}



async def main():
    
    # Открываем файл info_channels для чтения (в нём лежать каналы, группы источники)
    with open(os.path.join('app/config', 'info_channels.txt'), 'r') as f:
        f.seek(0)
        readlines = f.readlines()
        info_channels = []
        # Пробуем преобразовать каждую строчку в число, если это не получается, то оставляем строчку как есть.
        for line in readlines:
            try:
                info_channels.append(int(line.strip()))
            except ValueError:
                info_channels.append(line.strip())
    
    # Открываем файл to_channels для чтения (в нём лежат каналы, группы назначения)
    with open(os.path.join('app/config', 'to_channels.txt'), 'r') as f:
        f.seek(0)
        readlines = f.readlines()
        to_channels = []
        # Пробуем преобразовать каждую строчку в число, если это не получается, то оставляем строчку как есть.
        for line in readlines:
            try:
                to_channels.append(int(line.strip()))
            except ValueError:
                to_channels.append(line.strip())

    # print(info_channels)
    # print(to_channels)

    # Создаем экземпляр класса MyParser с входными параметрами
    parser = MyParser(**telegram_data)
    # Запускаем парсер постов из каналов info_channels и отправляем в каналы to_channels
    await parser.parse(info_channels, to_channels)


if __name__ == '__main__':
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
    except Exception as e:
        print('Error: %s' % e)
    