#!/usr/bin/python

import argparse
from time import sleep
import subprocess
import timeout
import atexit
from RPi import GPIO

GPIO.setmode(GPIO.BOARD)

def killall():
    subprocess.call("killall dsreader",shell=True)
    GPIO.cleanup()

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

motion_pin=None
gpio_pin=True

currently_recycle=0

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
    import re
    with open("/home/pi/RecycloTrash/database.txt") as f:
        database=filter(None,f.read().split("\n"))
        print database
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
    import imp
    googlevision=imp.load_source("googlevision","/home/pi/RecycloTrash/googlevision.py")
    with open("/home/pi/RecycloTrash/database2.txt") as f:
        database2=filter(None,f.read().split("\n"))
else:
    raise ValueError("No Object Identification Value")

if args.NoServo:
    verbose_print("Trash movement: None")
elif args.gpio:
    verbose_print("Trash movement: Use Servo, PIN: " + str(args.gpio))
    servo_pin=args.gpio
    GPIO.setup(servo_pin, GPIO.OUT)
    pwm=GPIO.PWM(servo_pin,50)
    gpio_imported=True
else:
    raise ValueError("No Trash Movement Value")

#Post-Init

if args.dsreader and not camera_in_use>1:
    from subprocess import Popen, PIPE
    from fcntl import fcntl, F_GETFL, F_SETFL
    from os import O_NONBLOCK, read
    p = Popen(['/home/pi/RecycloTrash/QR/dsreader'], stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False, cwd="/home/pi/RecycloTrash/QR/")
    flags = fcntl(p.stdout, F_GETFL)
    fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)    
    
while 1:
    currently_recycle=0
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
                sleep(5)
                raw_dsreader_input=read(p.stdout.fileno(), 1024)
                verbose_print(raw_dsreader_input)
            except OSError:
                raw_dsreader_input=""
                verbose_print("Datasymbol: No datasymbol")
            for raw_input in raw_dsreader_input.split("\n"):
                if raw_input=="":
                    continue
                qr=raw_input.split(" ")
                qr=" ".join(qr[2:-2])
                qr=qr.replace("*",".")
                regex = re.compile(qr)
                matches = [string for string in database if re.match(regex, string)]
                if len(matches)>0:
                    currently_recycle=1
                    verbose_print("Datasymbol: Match found")
                else:
                    verbose_print("Datasymbol: No match found") 
    if args.googlevision:
        verbose_print("Googlevision: Sending photo")
        result=googlevision.main()
        verbose_print(result)
        for r in result:
             if r in database2:
                 verbose_print("Googlevision: Match found - "+r)
                 currently_recycle=1
                 break

    if args.gpio:
        if currently_recycle == 1:
            verbose_print("Servo: Recycle")
            pwm.start(12.5)
            sleep(0.5)
            
        elif currently_recycle == 0:
            verbose_print("Servo: Trash")
            pwm.start(2.5)
            sleep(0.5)
            
        pwm.ChangeDutyCycle(7.5)
        sleep(0.5)
        
            
    

    sleep(3)
    try:
        if args.dsreader:
            read(p.stdout.fileno(), 1024)
    except OSError:
        pass
    
    print("="*20)
