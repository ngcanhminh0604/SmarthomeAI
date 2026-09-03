# HaNoi FireWatch AI

Du an dieu khien nha thong minh bang Raspberry Pi. File chinh la
`smarthome.py`, dung de doc cam bien, hien thi trang thai len LCD va dieu
khien quat, den LED, servo cua theo dieu kien moi truong.

## Chuc nang chinh

- Doc nhiet do va do am tu cam bien AHTx0.
- Doc nong do khi gas qua module ADS1115.
- Doc cam bien chuyen dong PIR.
- Doc cam bien anh sang de tu dong bat/tat den.
- Quet the RFID MFRC522 qua giao tiep I2C de mo cua.
- Dieu khien servo dong/mo cua.
- Dieu khien quat khi nhiet do, do am hoac gas vuot nguong.
- Hien thi trang thai he thong tren LCD 16x2 I2C.
- Tu dong dong cua sau mot khoang thoi gian neu khong co canh bao gas.

## Phan cung su dung

- Raspberry Pi co ho tro GPIO va I2C.
- Cam bien nhiet do/do am AHTx0.
- Module ADS1115 de doc tin hieu analog.
- Cam bien gas noi vao kenh A0 cua ADS1115.
- Module RFID MFRC522 dung I2C.
- LCD 16x2 I2C dung PCF8574.
- Servo dieu khien cua.
- Quat hoac relay quat.
- Den LED hoac relay den.
- Cam bien PIR.
- Cam bien anh sang digital.

## Cau hinh chan va dia chi

Mac dinh trong `smarthome.py`:

| Thiet bi | Cau hinh |
| --- | --- |
| LCD I2C | `0x21` |
| RFID I2C | `0x2C` |
| ADS1115 I2C | `0x49` |
| Quat | GPIO 20 |
| Servo | GPIO 19 |
| PIR | GPIO 5 |
| Cam bien anh sang | GPIO 8 |
| LED | GPIO 23 |
| Cam bien gas | ADS1115 kenh A0 |

Neu phan cung cua ban dung dia chi I2C hoac chan GPIO khac, hay sua cac hang
trong phan `CONFIG` cua file `smarthome.py`.

## Nguong dieu khien

| Gia tri | Mac dinh | Y nghia |
| --- | ---: | --- |
| `TEMP_THRESHOLD` | `30.0` | Bat quat khi nhiet do lon hon 30 do C |
| `HUMI_THRESHOLD` | `85.0` | Bat quat khi do am lon hon 85% |
| `GAS_THRESHOLD` | `2.0` | Canh bao gas khi dien ap cam bien lon hon 2.0V |
| `OPEN_ANGLE` | `90` | Goc servo khi mo cua |
| `CLOSE_ANGLE` | `0` | Goc servo khi dong cua |
| `DOOR_OPEN_TIME` | `5` | Tu dong dong cua sau 5 giay |

## Cai dat thu vien

Nen chay tren Raspberry Pi OS. Bat I2C truoc khi su dung:

```bash
sudo raspi-config
```

Vao `Interface Options` va bat `I2C`.

Cai cac thu vien Python can thiet:

```bash
pip3 install RPi.GPIO adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-ads1x15 smbus2 RPLCD
```

Kiem tra cac thiet bi I2C:

```bash
i2cdetect -y 1
```

Dam bao LCD, RFID va ADS1115 hien dung dia chi nhu cau hinh.

## Cach chay

Chay chuong trinh:

```bash
python3 smarthome.py
```

Khi chuong trinh dang chay:

- Quet the RFID de mo cua.
- Neu gas vuot nguong, he thong mo cua va bat quat.
- Neu nhiet do hoac do am vuot nguong, he thong bat quat.
- Neu troi toi, he thong bat LED.
- LCD hien thi trang thai uu tien theo canh bao gas, cua dang mo, nhiet/do am
  cao, chuyen dong, troi toi hoac thong tin nhiet do/do am.

Dung chuong trinh bang `Ctrl + C`. Khi dung, chuong trinh se tat quat, tat LED,
dong cua, tat servo, xoa LCD va cleanup GPIO.

## Luu y an toan

- Kiem tra ky day noi truoc khi cap nguon cho Raspberry Pi va cac module.
- Neu dieu khien quat/dien xoay chieu qua relay, can cach ly va dau noi an toan.
- Khong cam/thao cam bien khi mach dang cap nguon.
- Nen thu tung module rieng le truoc khi chay toan bo he thong.

## Cau truc tep

```text
Smarthome/
|-- smarthome.py   # Chuong trinh dieu khien chinh
|-- README.md      # Tai lieu huong dan
```

