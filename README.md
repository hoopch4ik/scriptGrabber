

--- Скрипт Граббер Постов С Телеграм Каналов или Групп ---


ДЛЯ НАЧАЛА ВАМ НУЖНО ПОЛУЧИТЬ API_ID И API_HASH ТЕЛЕГРАММ АККАУНТА (link: https://my.telegram.org/auth?to=apps) <br/>
ПРИ ПЕРВОМ ЗАПУСКЕ ПОТРЕБУЕТСЯ ВВЕСТИ НОМЕР ТЕЛЕФОНА, КОД (ПРИЛЕТИТ В ТЕЛЕГРАМ) И ПАРОЛЬ ЕСЛИ 2FA


НАСТРОЙКА КОНФИГУРАЦИИ:

    Директория "grabber/config":

        info_channels.txt => каналы источники
        to_channels.txt => каналы назначения

        ---

        !!! Одна строчка - Один канал
        !!! Если канал закрытый - то вписываете id канала (например, этот бот выдаёт id - @UserInfoToBot)


ЧЕРЕДА КОММАНД (Windows):

    (обязательно должен стоять python3^)
<ul>
    <li>python -m venv .venv <span>(или вместо python -> python3, py)</span></li>
    <li>.venv/Scripts/activate</li>
    <li>pip install -r requirements.txt</li>
    <li>python main.py</li>
</ul>


