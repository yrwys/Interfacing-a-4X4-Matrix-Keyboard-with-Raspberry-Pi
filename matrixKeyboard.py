import RPi.GPIO as GPIO
import time
import lcddriver
from pad4pi import rpi_gpio

GPIO.setwarnings(False)

KEYPAD = [
    [1, 2, 3, "A"],
    [4, 5, 6, "B"],
    [7, 8, 9, "C"],
    ["*", 0, "#", "D"]
]

ROW_PINS = [17, 27, 22, 5] 
COL_PINS = [23, 24, 25, 16]

password_length = 3
password = "123"
user_input = ""
access_granted = False

display = lcddriver.Lcd()

def cleanup():
    GPIO.cleanup()
    display.lcd_clear()

def lcd_display(data, position=2, input_password=False, input_character=False, duration=1):
    display.lcd_clear()

    if input_password:
        display.lcd_display_string(" Enter the password", 1)
        display.lcd_display_string("    and press #", 2)
        display.lcd_display_string("Password: " + user_input, 4)
        time.sleep(0.1)
    
    if input_character:
        display.lcd_display_string("  To exit, press *", 1)
        display.lcd_display_string("> " + user_input, 3)
        time.sleep(0.1)

    if data is not None:
        display.lcd_display_string(data, position)
    if duration is not None:
        time.sleep(duration)

def init_keypad_driver():
    factory = rpi_gpio.KeypadFactory()
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS, key_delay=100)
    keypad.registerKeyPressHandler(handle_keypad_press)

def handle_keypad_press(key):
    global user_input, access_granted

    is_valid = validate_keycode(user_input)

    if key == '*':
        user_input = ""
        access_granted = False
        lcd_display(None, None, input_password=True, input_character=False)
    elif key == '#':
        if len(user_input.strip()) < password_length:
            lcd_display("Incomplete Password!", 1, input_password=False, input_character=False, duration=1)
            lcd_display(None, None, input_password=True, input_character=False)
            return

        if is_valid:
            lcd_display("  Success! Welcome", 2, input_password=False, input_character=False, duration=2)
            user_input = ""
            access_granted = True 
            lcd_display(None, None, input_password=False, input_character=True)
        else:
            lcd_display(" Invalid  Password!", 3, input_password=False, input_character=False, duration=1)
            user_input = ""
            lcd_display(None, None, input_password=True, input_character=False)
    elif access_granted:
        user_input += str(key)
        lcd_display(None, None, input_password=False, input_character=True, duration=0.2)
    else:
        if len(user_input.strip()) == password_length:
            lcd_display("  Input  Exceeded!", 4, input_password=False, input_character=False, duration=1)
            lcd_display(None, None, input_password=True, input_character=False)
            return
        user_input += str(key)
        lcd_display(None, None, input_password=True, input_character=False, duration=0.2)
                
def validate_keycode(keycode):
    return keycode == password

def main():
    init_keypad_driver()
    lcd_display(None, None, input_password=True, input_character=False)

if __name__ == "__main__":
    try:
        main()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

