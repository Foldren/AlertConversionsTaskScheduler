from os import getcwd
import aiofiles
import httpx
from datetime import date
import asyncio
import flag

IS_LOCAL = 'Pycharm' in getcwd()
CHAT_ID_USERS = [578648976, 953807532, 306451894, 1325619459]
API_KEY = 'a46db90c1f5feb3656511408416498a1'
BOT_TOKEN = '5859076754:AAEQq_uybluFi4Vp55BQyQOGZO1K6LieGPE' if IS_LOCAL else '6244210256:AAFzG20Cw3eMXt920j0SfdlfOj4ovWhVS44'
URL = 'https://api-cpacash.affise.com/3.0/stats/conversions'
OFFER_ID = 680  # 680
PARTNER_ID = [1464]  # 1464
STATUS = [1, 2]  # Регистрации и депозиты
STATUS_C = {"confirmed": "reg🆗", "pending": "Deposit✅", "declined": 3, "hold": 5}


async def get_conversion_index(conversions: list[dict], id_conv: str) -> int:
    index_conv = 0
    for conv in conversions:
        if conv['id'] == id_conv:
            return index_conv
        index_conv += 1


async def main():
    print("BOT STARTED")
    while True:
        async with aiofiles.open("last_partner_id.txt", mode="r") as file:
            last_conversion_id = await file.read()

        client = httpx.AsyncClient()

        p_get_conv_rq = {
            'date_from': date.today(),
            'date_to': date.today(),
            'timezone': 'Europe/Moscow',
            'offer[]': OFFER_ID,
            'status[]': STATUS,
            'partner[]': PARTNER_ID,
        }
        r_conversions = await client.get(url=URL, headers={'API-Key': API_KEY}, params=p_get_conv_rq)

        if "conversions" in r_conversions.json():
            if r_conversions.json()["conversions"]:
                conversions = r_conversions.json()["conversions"]
                fst_conversion = conversions[0]['id']

                if fst_conversion != last_conversion_id:
                    last_conversion_id_for_f = fst_conversion

                    # Берем только те что еще не отправлялись и сортируем по дате отправки
                    number_not_alert_convs = await get_conversion_index(conversions, last_conversion_id)
                    conversions = conversions[:number_not_alert_convs]
                    conversions.reverse()
                    print(f"NUMBER NOT ALERT CONVS: {number_not_alert_convs}")

                    for conv in conversions:
                        # Отправляем флаг страны, страну, статус конверсии и id игрока
                        c_message = f'{STATUS_C[conv["status"]]}\n' \
                                    f'geo{flag.flag(conv["country"])}\n' \
                                    f'🆔{conv["custom_field_1"]}\n' \
                                    f'Sub: {conv["sub1"]}'

                        print(f"SEND MESSAGES")
                        for chat_id in CHAT_ID_USERS:
                            p_send_m_rq = {
                                'chat_id': chat_id,
                                'text': c_message,
                            }
                            await client.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=p_send_m_rq)

                    # Обновляем последний id
                    async with aiofiles.open("last_partner_id.txt", mode="w") as file:
                        await file.write(last_conversion_id_for_f)

        await client.aclose()
        await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
