#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DS18B20.h>
#include <DHT11.h>

// 板子上的灯，显示信息用的
#define LED_Board 2
// 定义DS18B20和DHT11的引脚
#define DHT11_pin 17
#define DS18B20_pin 16
// 设置NTP服务器
#define NTP "ntp.aliyun.com"
// 初始化引脚
DHT11 dht11(DHT11_pin);
DS18B20 ds18b20(DS18B20_pin);

const char *position = "1";
// 定义 WiFi 名与密码
const char *ssid = "Tenda_9C8F60";
const char *password = "password";

// 请求的URL
String url = "http://192.168.10.104:8080";

// 写点常量
struct tm timeinfo;

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
		digitalWrite(LED_Board, HIGH);
		delay(100);
		digitalWrite(LED_Board, LOW);
		delay(100);
	}

	Serial.println("连接成功");
	Serial.print("IP 地址：");
	Serial.println(WiFi.localIP());
	digitalWrite(LED_Board, LOW);
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
		configTime(8 * 3600, 0, NTP);
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

	time_init();
	float TempC = ds18b20.getTempC();
	Serial.println(TempC);
	delay(10000);
}
