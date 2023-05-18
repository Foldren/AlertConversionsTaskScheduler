import httpx
from datetime import date
import asyncio
import flag

CHAT_ID_USERS = [1325619459, 306451894, 503638369]
API_KEY = 'a46db90c1f5feb3656511408416498a1'
BOT_TOKEN = '6244210256:AAFzG20Cw3eMXt920j0SfdlfOj4ovWhVS44'
URL = 'https://api-cpacash.affise.com/3.0/stats/conversions'
OFFER_ID = 664
PARTNER_ID = 1464
STATUS = [1, 2]  # Регистрации и депозиты
STATUS_C = {"confirmed": 1, "pending": 2, "declined": 3, "hold": 5}


async def main():
    last_conversion_id = 0
    print("BOT STARTED")
    while True:
        print(last_conversion_id)
        client = httpx.AsyncClient()

        p_get_conv_rq = {
            'date_from': date.today(),
            'offer': OFFER_ID,
            # 'partner': [1464],
            'status': STATUS,
        }
        r_conversions = await client.get(url=URL, headers={'API-Key': API_KEY}, params=p_get_conv_rq)
        conversions = r_conversions.json()["conversions"]

        if conversions:
            last_conversion_partner: dict
            for element in conversions:
                if element['partner_id'] == PARTNER_ID:
                    last_conversion_partner = element
                    break
            if last_conversion_partner['id'] != last_conversion_id:
                last_conversion_id = last_conversion_partner['id']
                c_country = last_conversion_partner["country"]
                # Отправляем флаг страны, страну, статус конверсии и id игрока
                c_message = f'{flag.flag(c_country)}{c_country}:{STATUS_C[last_conversion_partner["status"]]}:{last_conversion_partner["clickid"]}'
                for chat_id in CHAT_ID_USERS:
                    p_send_m_rq = {
                        'chat_id': chat_id,
                        'text': c_message,
                    }
                    await client.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=p_send_m_rq)
                    
        await client.aclose()
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
