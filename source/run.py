import datetime
import traceback
from os import getcwd
import aiofiles
import httpx
from datetime import date, timedelta
import asyncio
import flag

IS_LOCAL = 'Pycharm' in getcwd()
GROUP_ID_MULTIPLE = [] if IS_LOCAL else ['-1001814724514']
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
    return index_conv


async def main():
    print("BOT STARTED")

    while True:
        try:
            last_conversion_id: str = ''

            async with aiofiles.open("last_partner_id.txt", mode="r") as file:
                last_conversion_id = await file.read()

            client = httpx.AsyncClient()

            p_get_conv_rq = {
                'date_from[]': date.today() - timedelta(days=4),
                'date_to[]': date.today() + timedelta(days=1),
                'timezone[]': 'Europe/Moscow',
                'offer[][]': OFFER_ID,
                'status[][]': STATUS,
                'partner[][]': PARTNER_ID,
            }
            r_conversions = await client.get(url=URL, headers={'API-Key': API_KEY}, params=p_get_conv_rq)
            response_affise = r_conversions
            print("LAST CONVERSION: " + str(datetime.datetime.today()) + "|" + last_conversion_id)
            print("FIRST CONVERSION: " + str(datetime.datetime.today()) + "|" + r_conversions.json()["conversions"][0][
                'id'])

            if "conversions" in r_conversions.json():
                if r_conversions.json()["conversions"]:
                    conversions = r_conversions.json()["conversions"]
                    fst_conversion = conversions[0]['id']

                    if response_affise.json()["status"] != 1 or response_affise.json()["conversions"] == []:
                        raise Exception(response_affise.json())

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
                                try:
                                    response_telegram = await client.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=p_send_m_rq)
                                except:
                                    pass
                                # if not response_telegram.json()["ok"] or response_telegram.json()["result"] == {}:
                                #     print(chat_id)
                                #     raise Exception(response_telegram.json())

                            for group_id in GROUP_ID_MULTIPLE:
                                p_send_m_rq = {
                                    'chat_id': group_id,
                                    'text': c_message,
                                }
                                response_telegram = await client.get(
                                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=p_send_m_rq)
                                if not response_telegram.json()["ok"] or response_telegram.json()["result"] == {}:
                                    raise Exception(response_telegram.json())

                        # Обновляем последний id
                        async with aiofiles.open("last_partner_id.txt", mode="w") as file:
                            await file.write(last_conversion_id_for_f)

                        await client.aclose()

        except Exception as E:
            print(E)
            print(traceback.format_exc())
            loop.stop()
        await asyncio.sleep(30)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
