#!/usr/bin/python

import argparse
from time import sleep
import subprocess
import timeout
import atexit

def killall():
    subprocess.call("killall dsreader",shell=True)

atexit.register(killall)

parser = argparse.ArgumentParser(description="Control the RecycloTrash")

parser.add_argument('-v', '--verbose', action='store_true')

group_motion = parser.add_mutually_exclusive_group(required=True)
group_qr = parser.add_mutually_exclusive_group(required=True)
group_cv = parser.add_mutually_exclusive_group(required=True)
group_servo = parser.add_mutually_exclusive_group(required=True)

group_motion.add_argument('--NoMotion', action='store_true', help="Skip motion detection")
group_motion.add_argument('--camera', action='store_true', help="Use camera to detect motion")
group_motion.add_argument('--pir', type=int, help="Use infrared motion detector")
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

camera_in_use=0

def verbose_print(str):
    if args.verbose:
        print(str)

verbose_print(args)

if args.NoMotion:
    verbose_print("Motion: No Motion")
elif args.camera:
    verbose_print("Motion: Use PiCamera")
    camera_in_use+=1
elif args.pir:
    verbose_print("Motion: Use PIR Motion Detector, PIN: "+str(args.pir))
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
    camera_in_use+=1
elif args.image:
    verbose_print("Object Identification: Take photo to find QR/Barcode")
    camera_in_use+=1
else:
    raise ValueError("No Object Identification Value")

if args.NoCV:
    verbose_print("Computer Vision: None")
elif args.googlevision:
    verbose_print("Computer Vision: Use Google Vision")
    camera_in_use+=1
else:
    raise ValueError("No Object Identification Value")

if args.NoServo:
    verbose_print("Trash movement: None")
elif args.gpio:
    verbose_print("Trash movement: Use Servo, PIN: " + str(args.gpio))
    if not gpio_imported:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
    servo_pin=args.gpio
    GPIO.setup(servo_pin, GPIO.OUT)
    gpio_imported=True
else:
    raise ValueError("No Trash Movement Value")

#Post-Init

if not camera_in_use>1:
    from subprocess import Popen, PIPE
    from fcntl import fcntl, F_GETFL, F_SETFL
    from os import O_NONBLOCK, read
    p = Popen(['/home/pi/RecycloTrash/QR/dsreader'], stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False, cwd="/home/pi/RecycloTrash/QR/")
    flags = fcntl(p.stdout, F_GETFL)
    fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)    
    
while 1:
    if args.pir:
        verbose_print("Motion: Start PIR")
#        while GPIO.input(motion_pin):            sleep(0.3)
        verbose_print("Motion: Looking for new motion")
        while not GPIO.input(motion_pin):
            sleep(0.3)
        verbose_print("Motion: Motion found")
    if args.camera:
        verbose_print("Motion: Start PiCamera")
        subprocess.check_output(["/usr/bin/python","/home/pi/RecycloTrash/motion.py"])
        verbose_print("Motion: Motion found")
    if args.dsreader:
        if camera_in_use>1:
            raise ValueError("Not Implemented")
        if not camera_in_use>1:
            try:
                verbose_print("Datasymbol: Begin search")
                sleep(10)
                raw_dsreader_input=read(p.stdout.fileno(), 1024)
                verbose_print(raw_dsreader_input)
            except OSError:
                raw_dsreader_input=""
                verbose_print("Datasymbol: No datasymbol")
            #qr=raw_dsreader_input.split
    sleep(3)
    read(p.stdout.fileno(), 1024)
    print("="*20)
