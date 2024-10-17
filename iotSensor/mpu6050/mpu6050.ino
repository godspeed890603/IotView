#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_Sensor.h>

#define SDA_PIN 1  // 自定义的 SDA 引脚
#define SCL_PIN 2  // 自定义的 SCL 引脚

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);
  
  // 自定义 I2C 引脚
  Wire.begin(SDA_PIN, SCL_PIN);

  // 初始化 MPU6050
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
    while (1) {
      delay(10);
    }
  }
  
  Serial.println("MPU6050 found!");

  // 设置加速度计和陀螺仪的量程
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
}

void loop() {
  // 创建事件对象
  sensors_event_t a, g, temp;

  // 从 MPU6050 读取数据
  mpu.getEvent(&a, &g, &temp);

  // 输出加速度计数据
  Serial.print("Accel X: ");
  Serial.print(a.acceleration.x);
  Serial.print(", Y: ");
  Serial.print(a.acceleration.y);
  Serial.print(", Z: ");
  Serial.print(a.acceleration.z);
  Serial.println(" m/s^2");

  // 输出陀螺仪数据
  Serial.print("Gyro X: ");
  Serial.print(g.gyro.x);
  Serial.print(", Y: ");
  Serial.print(g.gyro.y);
  Serial.print(", Z: ");
  Serial.print(g.gyro.z);
  Serial.println(" rad/s");

  // 输出温度数据
  Serial.print("Temp: ");
  Serial.print(temp.temperature);
  Serial.println(" C");

  delay(500);  // 延迟 500 毫秒
}





// #include <Wire.h>
// #include <MPU6050.h>

// #define SDA_PIN 1  // 自定义的 SDA 引脚
// #define SCL_PIN 2  // 自定义的 SCL 引脚

// MPU6050 mpu;

// void setup() {
//     Serial.begin(115200);  // 初始化串口
//     Wire.begin(SDA_PIN, SCL_PIN);  // 初始化 I2C，并指定 SDA 和 SCL 引脚

//     Serial.println("Initializing MPU6050...");
//     mpu.initialize();  // 初始化 MPU6050

//     // 检查 MPU6050 是否正常工作
//     if (mpu.testConnection()) {
//         Serial.println("MPU6050 connection successful.");
//     } else {
//         Serial.println("MPU6050 connection failed.");
//     }
// }

// void loop() {
//     int16_t ax, ay, az;
//     int16_t gx, gy, gz;

//     // 读取加速度计和陀螺仪数据
//     mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

//     // 打印数据到串口监视器
//     Serial.print("Accelerometer: ");
//     Serial.print("X: "); Serial.print(ax);
//     Serial.print(" | Y: "); Serial.print(ay);
//     Serial.print(" | Z: "); Serial.println(az);

//     // Serial.print("Gyroscope: ");
//     // Serial.print("X: "); Serial.print(gx);
//     // Serial.print(" | Y: "); Serial.print(gy);
//     // Serial.print(" | Z: "); Serial.println(gz);

//     delay(500);  // 延迟 500 毫秒
// }
