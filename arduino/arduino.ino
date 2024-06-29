#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <DS18B20.h>
#include <DHT11.h>
#include <WiFi.h>
#include <time.h>

// 板子上的灯，显示信息用的
#define LED_Board 2
// 定义DS18B20和DHT11的引脚
#define DHT11_pin 17
#define DS18B20_pin 16
// 定义时区（东）
#define timeZone 8
// 设置NTP服务器
#define NTP "ntp.aliyun.com"
//设置采样频率（每多少毫秒）
#define delayTime 10000

// 初始化引脚
DHT11 dht11(DHT11_pin);
DS18B20 ds18b20(DS18B20_pin);

// 定义 WiFi 名与密码
const char *ssid = "Tenda_9C8F60";
const char *password = "password";

// 请求的URL
const String URL = "http://192.168.10.11:8080";

const char *position = "1";

// 写点常量
struct tm timeinfo;
time_t myTime;

// 整点json用的
String defaultRecord = "{\"time\":0,\"pisition\":0,\"temperature\":0,\"humidity\":0,\"pressure\":0,\"wind_speed\":0,\"noise\":0,\"rain\":0,\"pm2dot5\":0,\"pm10\":0}";
DynamicJsonDocument doc(1024);
String lastData;

void wifi_init()
{

	// 连接 WiFi
	WiFi.begin(ssid, password);
	Serial.print("正在连接 Wi-Fi");

	// 检测是否连接成功
	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.print(".");
	}

	Serial.println("连接成功");
	Serial.print("IP 地址：");
	Serial.println(WiFi.localIP());
	// digitalWrite(LED_Board, LOW);
}

void time_init()
{
	// 获取本地时间
	if (!getLocalTime(&timeinfo))
	{
		Serial.println("获取本地时间失败");
		// 连接 WiFi
		wifi_init();
		// 从 NTP 服务器获取时间并设置
		configTime(timeZone * 3600, 0, NTP);
		return;
	}

	// 输出时间
	// Serial.println(timeinfo.tm_year)
	Serial.println(&timeinfo, "%F %A %T");
}

void setup()
{
	// 初始化串口
	Serial.begin(9600);

	// 初始化引脚
	pinMode(LED_Board, OUTPUT);

	wifi_init();
}

void loop()
{
	// 初始化http
	HTTPClient http;
	http.begin(URL);
	http.addHeader("Content-Type", "application/json");

	// 还是json
	deserializeJson(doc, defaultRecord);
	JsonObject obj = doc.as<JsonObject>();

	obj["pisition"] = "1";
	// 以上这俩不能在函数外声明

	time_init();
	float TempC = ds18b20.getTempC();
	int Humidity = dht11.readHumidity();

	myTime = time(NULL);

	obj["time"] = myTime;
	obj["temperature"] = TempC;
	obj["humidity"] = Humidity;

	serializeJson(doc, lastData);
	Serial.println(lastData);

	if (myTime > 100000)
	{
		int httpResponseCode = http.POST(lastData);
		Serial.println(httpResponseCode);
	}
  else{
    Serial.println("NO Send");
  }

	delay(delayTime);
}
