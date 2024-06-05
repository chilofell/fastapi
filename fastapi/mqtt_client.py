import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(self, broker_address="5.23.53.69", broker_port=1883):
        self.client = mqtt.Client()
        self.client.on_connect = MqttClient.on_connect
        self.client.on_message = MqttClient.on_message
        self.client.connect(broker_address, broker_port, 80)
        self.client.loop_start()

    # Функция, вызываемая при подключении к брокеру MQTT
    @staticmethod
    def on_connect(client, rc):
        print("Connected with result code " + str(rc))
        # Подписываемся на темы для получения команд
        client.subscribe("home/calibrate")
        client.subscribe("home/close")
        client.subscribe("home/open")
        client.subscribe("home/сopcontrol_illuminationen")
        client.subscribe("home/control_temperature")
        client.subscribe("home/value")

    # Функция, вызываемая при получении сообщения от брокера MQTT
    @staticmethod
    def on_message( msg):
        print(msg.topic + " " + str(msg.payload))
        # Проверяем тему и выполняем соответствующие действия
        if msg.topic == "home/control_illumination":
            print('Получили данные об уровне освещённости, данные занесены в базу данных.')
        elif msg.topic == "home/control_temperature":
            print('Получили данные об уровне температуры, данные занесены в базу данных.')
        elif msg.topic == "home/value":
            print('Получили данные о положении шторы, данные занесены в базу данных.')
        else:
            print("Получена неизвестная команда.")

    def send_topic(self, topic, data=None):
        self.client.publish(topic, data)
