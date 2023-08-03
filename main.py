import hmac
import base64
import datetime
import requests
from setings import *
import telebot


class cex_sell_okx:

    def data(self, secret_key, passphras, request_path="/api/v5/asset/balances", body='', meth="GET"):

        try:
            def signature(
                timestamp: str, method: str, request_path: str, secret_key: str, body: str = ""
            ) -> str:
                if not body:
                    body = ""

                message = timestamp + method.upper() + request_path + body
                mac = hmac.new(
                    bytes(secret_key, encoding="utf-8"),
                    bytes(message, encoding="utf-8"),
                    digestmod="sha256",
                )
                d = mac.digest()
                return base64.b64encode(d).decode("utf-8")

            dt_now = datetime.datetime.utcnow()
            ms = str(dt_now.microsecond).zfill(6)[:3]
            timestamp = f"{dt_now:%Y-%m-%dT%H:%M:%S}.{ms}Z"

            base_url = "https://www.okx.cab"
            headers = {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": cex_keys["okx"]["apiKey"],
                "OK-ACCESS-SIGN": signature(timestamp, meth, request_path, secret_key, body),
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": passphras,
                'x-simulated-trading': '0'
            }
        except Exception as ex:
            print(ex, '--')

        return base_url, request_path, headers

    def get_balance_Funding(self, token):

        try:
            _, _, headers = cex_sell_okx.data(cex_keys["okx"]["apiKey"], cex_keys["okx"]["secret_key"], cex_keys["okx"]["password"], request_path=f"/api/v5/asset/balances?ccy={token}")
            spot_balance = requests.get(f"https://www.okx.cab/api/v5/asset/balances?ccy={token}", timeout=10, headers=headers)


            return spot_balance.json()['data'][0]['bal']

        except Exception as e:
            return loguru.logger.error(f"Error {e}")

    def get_balance_Trading(self, token):

        try:
            _, _, headers = cex_sell_okx.data(cex_keys["okx"]["apiKey"], cex_keys["okx"]["secret_key"], cex_keys["okx"]["password"], request_path=f"/api/v5/account/balance?ccy={token}")
            spot_balance = requests.get(f"https://www.okx.cab/api/v5/account/balance?ccy={token}", timeout=10, headers=headers)

            if len(spot_balance.json()['data'][0]['details']) == 0:
                return "Balance 0"
            else:
                return spot_balance.json()['data'][0]['details'][0]['cashBal']

        except Exception as e:
            return loguru.logger.error(f"Error {e}")

def main_():

    @bot.message_handler(commands=["start"])
    def main(message):
        bot.send_message(message.chat.id, text="Start bot | active")

    bot.send_message(chat_id, f"Start bot | active")
    while True:
        if float(sui_unlock.get_balance_Trading(coin)) > float(5):
            bot.send_message(chat_id, f"{sui_unlock.get_balance_Trading(coin)} | Trading ")
            break


        if float(sui_unlock.get_balance_Funding(coin)) > float(5):
            bot.send_message(chat_id, f"{sui_unlock.get_balance_Funding(coin)} | Funding ")
            break

    bot.send_message(chat_id, f"Stop bot | non-active")
    bot.polling()

if __name__ == '__main__':
    try:
        sui_unlock = cex_sell_okx()

        token = telegram_token
        bot = telebot.TeleBot(token)
        chat_id = chat_id

        main_()

    except Exception as e:
        print(f"Error - {e}")


