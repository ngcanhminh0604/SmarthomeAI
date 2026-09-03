# -*- coding: utf-8 -*-

import time
import sys

import RPi.GPIO as GPIO
import board
import busio
import adafruit_ahtx0

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from smbus2 import SMBus
from RPLCD.i2c import CharLCD

# ==================================================
# CONFIG
# ==================================================

LCD_ADDRESS = 0x21

FAN_PIN = 20
SERVO_PIN = 19

PIR_PIN = 5
LIGHT_PIN = 8

LED_PIN = 23

RFID_ADDR = 0x2C
ADS_ADDR = 0x49

TEMP_THRESHOLD = 30.0
HUMI_THRESHOLD = 85.0
GAS_THRESHOLD = 2.0

OPEN_ANGLE = 90
CLOSE_ANGLE = 0

DOOR_OPEN_TIME = 5

# ==================================================
# GPIO
# ==================================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LIGHT_PIN, GPIO.IN)

GPIO.setup(SERVO_PIN, GPIO.OUT)

GPIO.output(FAN_PIN, GPIO.LOW)
GPIO.output(LED_PIN, GPIO.LOW)

# ==================================================
# SERVO
# ==================================================

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

def set_servo_angle(angle):

    duty = 2.5 + (angle / 180.0) * 10

    servo.ChangeDutyCycle(duty)

    time.sleep(0.7)

    servo.ChangeDutyCycle(0)

def open_door():

    print(">>> MO CUA")

    set_servo_angle(OPEN_ANGLE)

def close_door():

    print("<<< DONG CUA")

    set_servo_angle(CLOSE_ANGLE)

# ==================================================
# LCD
# ==================================================

lcd = CharLCD(
    i2c_expander='PCF8574',
    address=LCD_ADDRESS,
    port=1,
    cols=16,
    rows=2,
    charmap='A00',
    expander_params={
        'rs': 0,
        'rw': 1,
        'e': 2,
        'data': [4, 5, 6, 7],
        'backlight': 3
    }
)

def lcd_show(line1, line2):

    lcd.cursor_pos = (0, 0)
    lcd.write_string(line1[:16].center(16))

    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2[:16].center(16))

# ==================================================
# RFID I2C
# ==================================================

class MFRC522_I2C:

    OK = 1
    ERR = 0

    CommandReg = 0x01
    ComIEnReg = 0x02
    ComIrqReg = 0x04

    FIFODataReg = 0x09
    FIFOLevelReg = 0x0A

    BitFramingReg = 0x0D

    ModeReg = 0x11
    TxControlReg = 0x14
    TxASKReg = 0x15

    VersionReg = 0x37

    def __init__(self, bus_num=1, address=0x2C):

        self.addr = address

        try:

            self.bus = SMBus(bus_num)

            self.bus.read_byte_data(
                self.addr,
                self.VersionReg
            )

        except Exception:

            print("[RFID] Loi ket noi I2C")

            sys.exit(1)

        self.init_device()

    def wreg(self, reg, val):

        try:

            self.bus.write_byte_data(
                self.addr,
                reg,
                val
            )

        except OSError:

            pass

    def rreg(self, reg):

        try:

            return self.bus.read_byte_data(
                self.addr,
                reg
            )

        except OSError:

            return 0

    def init_device(self):

        self.wreg(self.CommandReg, 0x0F)

        time.sleep(0.05)

        self.wreg(self.ModeReg, 0x3D)

        self.wreg(self.TxASKReg, 0x40)

        val = self.rreg(self.TxControlReg)

        if not (val & 0x03):

            self.wreg(
                self.TxControlReg,
                val | 0x03
            )

    def to_card(self, command, send_data):

        recv_data = []

        irq_en = 0x77 if command == 0x0C else 0x00
        wait_irq = 0x30 if command == 0x0C else 0x00

        self.wreg(
            self.ComIEnReg,
            irq_en | 0x80
        )

        self.wreg(
            self.ComIrqReg,
            self.rreg(self.ComIrqReg) & (~0x80)
        )

        self.wreg(
            self.FIFOLevelReg,
            self.rreg(self.FIFOLevelReg) | 0x80
        )

        self.wreg(self.CommandReg, 0x00)

        for d in send_data:

            self.wreg(self.FIFODataReg, d)

        self.wreg(self.CommandReg, command)

        if command == 0x0C:

            self.wreg(
                self.BitFramingReg,
                self.rreg(self.BitFramingReg) | 0x80
            )

        start = time.time()

        while True:

            if time.time() - start > 0.1:

                return self.ERR, []

            n = self.rreg(self.ComIrqReg)

            if n & wait_irq:

                break

            if n & 0x01:

                return self.ERR, []

        self.wreg(
            self.BitFramingReg,
            self.rreg(self.BitFramingReg) & (~0x80)
        )

        n = self.rreg(self.FIFOLevelReg)

        for _ in range(n):

            recv_data.append(
                self.rreg(self.FIFODataReg)
            )

        return self.OK, recv_data

    def read_uid(self):

        self.wreg(self.BitFramingReg, 0x07)

        stat, _ = self.to_card(
            0x0C,
            [0x26]
        )

        if stat != self.OK:

            return None

        self.wreg(self.BitFramingReg, 0x00)

        stat, recv = self.to_card(
            0x0C,
            [0x93, 0x20]
        )

        if stat != self.OK:

            return None

        if len(recv) >= 4:

            return ":".join(
                "{:02X}".format(x)
                for x in recv[:4]
            )

        return None

# ==================================================
# I2C SENSOR
# ==================================================

i2c = busio.I2C(board.SCL, board.SDA)

aht_sensor = adafruit_ahtx0.AHTx0(i2c)

ads = ADS.ADS1115(
    i2c,
    address=ADS_ADDR
)

gas_sensor = AnalogIn(ads, 0)

rfid = MFRC522_I2C(address=RFID_ADDR)

# ==================================================
# SYSTEM
# ==================================================

door_open = False
door_open_time = 0

last_uid = None
last_scan_time = 0

close_door()

print("=== SMART HOME START ===")

try:

    lcd.clear()

    while True:

        # ======================================
        # DOC CAM BIEN
        # ======================================

        temp = aht_sensor.temperature

        humi = aht_sensor.relative_humidity

        gas = gas_sensor.voltage

        motion = GPIO.input(PIR_PIN)

        dark = GPIO.input(LIGHT_PIN)

        uid = rfid.read_uid()

        # ======================================
        # RFID
        # ======================================

        current_time = time.time()

        if uid:

            if uid != last_uid or current_time - last_scan_time > 2:

                print("[RFID]", uid)

                open_door()

                door_open = True

                door_open_time = current_time

                last_uid = uid

                last_scan_time = current_time

        # ======================================
        # GAS
        # ======================================

        gas_alert = gas > GAS_THRESHOLD

        if gas_alert:

            GPIO.output(FAN_PIN, GPIO.HIGH)

            open_door()

            door_open = True

            door_open_time = current_time

        else:

            # ==================================
            # TEMP + HUMI
            # ==================================

            if temp > TEMP_THRESHOLD or humi > HUMI_THRESHOLD:

                GPIO.output(FAN_PIN, GPIO.HIGH)

            else:

                GPIO.output(FAN_PIN, GPIO.LOW)

        # ======================================
        # AUTO CLOSE DOOR
        # ======================================

        if door_open and not gas_alert:

            if current_time - door_open_time > DOOR_OPEN_TIME:

                close_door()

                door_open = False

        # ======================================
        # LED
        # ======================================

        # Chi bat LED khi troi toi

        if dark == 0:

            GPIO.output(LED_PIN, GPIO.HIGH)

        else:

            GPIO.output(LED_PIN, GPIO.LOW)

        # ======================================
        # LCD
        # ======================================

        if gas_alert:

            lcd_show(
                "NGUY HIEM GAS",
                "MO CUA BAT QT"
            )

        elif door_open:

            lcd_show(
                "XIN MOI VAO",
                "CUA DANG MO"
            )

        elif temp > TEMP_THRESHOLD or humi > HUMI_THRESHOLD:

            lcd_show(
                "NHIET/AM CAO",
                "BAT QUAT"
            )

        elif motion:

            lcd_show(
                "CO CHUYEN DONG",
                "PIR PHAT HIEN"
            )

        elif dark == 0:

            lcd_show(
                "TROI TOI",
                "BAT DEN"
            )

        else:

            line2 = "T%.1fC H%.0f%%" % (temp, humi)
            lcd_show(
                "EDISON ACADEMY",
                line2
            )

        # ======================================
        # DEBUG
        # ======================================

        print(
            "Temp=%.1fC | Humi=%.1f%% | Gas=%.2fV | PIR=%s | Dark=%s"
            % (
                temp,
                humi,
                gas,
                motion,
                dark
            )
        )

        time.sleep(0.5)

except KeyboardInterrupt:

    print("\nDang dung...")

finally:

    GPIO.output(FAN_PIN, GPIO.LOW)

    GPIO.output(LED_PIN, GPIO.LOW)

    close_door()

    servo.stop()

    lcd.clear()

    lcd.backlight_enabled = False

    GPIO.cleanup()

    print("Da tat he thong")