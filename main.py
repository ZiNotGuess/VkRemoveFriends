import configparser
import time
import requests
from datetime import datetime


class Vk:
    def __init__(self, token: str, version: str):
        """
        :param token: access_token пользователя
        :param version: версия API
        """
        self.url = 'https://api.vk.com/method/'
        self.access_token = token
        self.apiVersion = version

    def method(self, methodName: str, methodParams: dict = None) -> dict or list or str or int:
        """
        :param methodName: название метода
        :param methodParams: параметры метода
        :return: ответ ВКонтакте
        """
        if methodParams is None:
            methodParams = {}
        methodParams['v'] = self.apiVersion
        methodParams['access_token'] = self.access_token
        r = requests.post(self.url + methodName, methodParams)
        r_json = r.json()
        if 'error' in r_json:
            raise Exception(f'[{r_json["error"]["error_code"]}] {r_json["error"]["error_msg"]}')
        return r_json['response']


config = configparser.ConfigParser()
config.read("settings.ini")


def settingsReader(arg: str) -> str:
    """
    :param arg: имя параметра из настроек
    :return: значение
    """
    return config["Vk"][arg]


def right_case(t: int, text_forms: list) -> str:
    """
    :param t: число
    :param text_forms: массив
    :return: правильная форма из массива
    """
    t = t % 100
    t1 = t % 10
    if 10 < t < 20:
        return text_forms[2]
    if 1 < t1 < 5:
        return text_forms[1]
    if t1 == 1:
        return text_forms[0]
    return text_forms[2]


deleteMessage = "Привет. Это сообщение прислал тебе скрипт от моего лица.\n" \
                "Мы долго не общались, поэтому скрипту пришлось удались тебя из друзей😶"
userCountRemove = 0

access_token = settingsReader("access_token")
apiVersion = settingsReader("apiVersion")
userTime = settingsReader("time")
botTime = datetime.strptime(userTime, "%d.%m.%Y %H:%M:%S")
unixTime = time.mktime(botTime.timetuple())

vk = Vk(access_token, apiVersion)

userFriendsList = vk.method("friends.get", {"count": 10000, "name_case": "acc", "fields": "domain"})
print(f'У вас {userFriendsList["count"]} {right_case(userFriendsList["count"], ["друг", "друга", "друзей"])}. '
      'Начинаю сортировку. Сейчас я выдам список тех, кто писал тебе раньше, чем ты указал в настройках и спрошу: '
      '"удалить этого пользователя из друзей?"\n'
      'Y - да, N - нет')

userFriendsListID = userFriendsList['items']
for i in userFriendsListID:
    try:
        lastMessageId = vk.method("messages.getConversationsById", {"peer_ids": i['id']})['items'][0]['last_message_id']
    except Exception:
        print("Произошла ошибка! Скрипт останавливается на 5 секунд и пропускает пользователя")
        time.sleep(5)
        continue
    if lastMessageId == 0:
        lastMessageTime = 0
    else:
        try:
            lastMessageTime = vk.method("messages.getById", {"message_ids": lastMessageId})['items'][0]['date']
        except Exception:
            print("Произошла ошибка! Скрипт останавливается на 5 секунд и пропускает пользователя")
            time.sleep(5)
            continue

    if lastMessageTime < unixTime:
        removeUser = input(f"Удалить {i['first_name']} {i['last_name']} (https://vk.com/{i['domain']}) из друзей? ")
        if removeUser.lower() == "y":
            userCountRemove += 1
            print("Пользователь удалён из друзей!")
            try:
                vk.method("messages.send", {"user_id": i['id'], "message": deleteMessage, "random_id": 0})
            except Exception:
                pass
            try:
                vk.method("friends.delete", {"user_id": i['id']})
            except Exception:
                print("Произошла ошибка! Скрипт останавливается на 5 секунд и пропускает пользователя")
                time.sleep(5)
                continue

print(f"Список ваших друзей закончился! Вы удалили {userCountRemove} "
      f"{right_case(userCountRemove, ['друга', 'друзей', 'друзей'])}")
