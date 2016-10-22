import subprocess
from time import sleep
import timeout

python_path="/usr/bin/python"
motion_path="/home/pi/RecycloTrash/motion.py"
dsreader_path="/home/pi/RecycloTrash/QR/dsreader"
sample_dsreader_path="/home/pi/sampledsreader.py"
sh_path="/bin/sh"

motion=[python_path,motion_path]
dsreader=dsreader_path
sample_dsreader=[python_path,sample_dsreader_path]

qr_detection_time_limit=10

qr_database=[]

camera_present=False
servo_present=False

while 1:
    #MOTION DETECTION
    if camera_present:
        subprocess.check_output(motion)
    print "Motion Detected"
    #QR CODE DETECTION
    qr=None
    try:
        with timeout.time_limit(qr_detection_time_limit):
            if not camera_present:
                p=subprocess.Popen(dsreader,stdout=subprocess.PIPE,cwd="/home/pi/RecycloTrash/QR/")
            else:
                p=subprocess.Popen(sample_dsreader,stdout=subprocess.PIPE)
            qr=p.stdout.readline()
            print "qr found:" + qr
            sleep(60)
    except timeout.TimeoutException, msg:
        print "no QR?"
    p.terminate()
    #Isolate the real value of qr
    if qr != None:
        #Isolate the real value of qr
        if qr in qr_database:
            recycle=True
        else:
            recycle=False
    else:
        recycle=False
    
    print "move to location"
    sleep(1)
