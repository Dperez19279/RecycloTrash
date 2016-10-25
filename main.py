#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser(description="Control the RecycloTrash")

group_motion = parser.add_mutually_exclusive_group(required=True)
group_qr = parser.add_mutually_exclusive_group(required=True)
group_servo = parser.add_mutually_exclusive_group(required=True)

group_motion.add_argument('--NoMotion', action='store_true', help="Skip motion detection")
group_motion.add_argument('--camera', action='store_true', help="Use camera to detect motion")
group_motion.add_argument('--pir', action='store_true', help="Use infrared motion detector")
group_qr.add_argument('--NoneT', action='store_true', help="Assume trash")
group_qr.add_argument('--NoneR', action='store_true', help="Assume recycle")
group_qr.add_argument('--NoneRand', action='store_true', help="Randomize between trash and recycle")
group_qr.add_argument('--dsreader', action='store_true', help="Use dsreader to find QR/Barcode")
group_qr.add_argument('--image', action='store_true',help="Take photo to find QR/Barcode")
group_servo.add_argument('--NoServo', action='store_true', help="Skip servo")
group_servo.add_argument('--gpio', type=int, help="Use GPIO to control servo")

args=parser.parse_args()

print args.NoMotion,args.camera
