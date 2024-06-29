# Horae

一个做着玩的气象站，项目名来自希腊神话中的天气女神

受群友的[UMD](<https://github.com/ExDragine/UMD-Client>)影响而想去制作的一个小玩具

---

以下是各个文件夹的作用

- arduino中记入烧录到传感器中的程序
  - arduino.ino是烧录到esp32中的程序
  - 其他文件是各种各样的前置库
- server中的程序用于接收接收器收集的数据
  - simple_http_server.py是服务器的后端
  - index.html作为前端用于向用户展示
    - 在script里面有个常量，叫server_URL，请改成自己的服务端地址,原文长这样`const server_URL="http://192.168.10.11:8080"`

---

以下是使用的材料：

| 类型 | 型号 | 价格（CNY） | 备注 |
| :----: | :----: | :----: | :----: |
| 开发板 | ESP32-WROOM-32E | 20 |      |
| 温湿度传感器 | DHT11 | 7.9 | |
| 温度传感器 | DS18B20 | 4.26 | DHT11灵敏度不足 |
| 面包板 | | 4.66 | |
| 杜邦线 | | 8.67 | 这是一组的价格 |
| 外置电源 | ESP32两路18650电池模块2节 | 17.65 | |
| 电池 | 18650平头电池2节 | 10.8 | |

