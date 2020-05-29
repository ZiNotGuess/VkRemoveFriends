import configparser

config = configparser.ConfigParser()
config.read("settings.ini")


def settingsReader(arg):
    """
    :param arg: имя параметра из настроек
    :return: значение
    """
    answer = config["Vk"][arg]
    return answer
