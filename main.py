#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(description="Control the RecycloTrash")

parser.add_argument('-v', '--verbose', action='store_true')

group_motion = parser.add_mutually_exclusive_group(required=True)
group_qr = parser.add_mutually_exclusive_group(required=True)
group_cv = parser.add_mutually_exclusive_group(required=True)
group_servo = parser.add_mutually_exclusive_group(required=True)

group_motion.add_argument('--NoMotion', action='store_true', help="Skip motion detection")
group_motion.add_argument('--camera', action='store_true', help="Use camera to detect motion")
group_motion.add_argument('--pir', action='store_true', help="Use infrared motion detector")
group_qr.add_argument('--NoneT', action='store_true', help="Assume trash")
group_qr.add_argument('--NoneR', action='store_true', help="Assume recycle")
group_qr.add_argument('--NoneRand', action='store_true', help="Randomize between trash and recycle")
group_qr.add_argument('--dsreader', action='store_true', help="Use dsreader to find QR/Barcode")
group_qr.add_argument('--image', action='store_true',help="Take photo to find QR/Barcode")
group_cv.add_argument('--NoCV', action='store_true',help="Skip Computer Vision")
group_cv.add_argument('--googlevision', action='store_true',help="Use Google Vision")
group_servo.add_argument('--NoServo', action='store_true', help="Skip servo")
group_servo.add_argument('--gpio', type=int, help="Use GPIO to control servo")

args=parser.parse_args()

#SETUP

gpio_imported=False
motion_pin=None
gpio_pin=True

def verbose_print(str):
    if args.verbose:
        print(str)

verbose_print(args)

if args.NoMotion:
    verbose_print("Motion: No Motion")
elif args.camera:
    verbose_print("Motion: Use PiCamera")
elif args.pir:
    verbose_print("Motion: Use PIR Motion Detector, PIN: "+args.pir)
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    motion_pin=args.pir
    GPIO.setup(motion_pin, GPIO.IN)
    gpio_imported=True
else:
    raise ValueError("No Motion Value")

if args.NoneT:
    verbose_print("Object Identification: Assume Trash")
elif args.NoneR:
    verbose_print("Object Identification: Assume Recycle")
elif args.NoneRand:
    verbose_print("Object Identification: Randomly pick")
elif args.dsreader:
    verbose_print("Object Identification: Use dsreader with video0")
elif args.image:
    verbose_print("Object Identification: Take photo to find QR/Barcode")
else:
    raise ValueError("No Object Identification Value")

if args.NoCV:
    verbose_print("Computer Vision: None")
elif args.googlevision:
    verbose_print("Computer Vision: Use Google Vision")
else:
    raise ValueError("No Object Identification Value")

if args.NoServo:
    verbose_print("Trash movement: None")
elif args.gpio:
    verbose_print("Trash movement: Use Servo, PIN: " + args.gpio)
    if not gpio_imported:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
    servo_pin=args.gpio
    GPIO.setup(servo_pin, GPIO.OUT)
    gpio_imported=True
else:
    raise ValueError("No Trash Movement Value")
