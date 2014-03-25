import RPi.GPIO as GPIO
import subprocess
import signal
import os
import time
import datetime
import urllib2
import urllib
import glob
import threading

#### Parameters ####

server = 'http://thetinkerer.net/cgi-bin/'
wait_time = 30

#### End Parameters ####

def errorLog (message):
    'Log an error message to file'
    now = str(datetime.datetime.now())[:19]
    message = now + '  -  ' + message + '\n'
    try:
        errlog = open('Error Log.txt', 'a')
        errlog.write(message)
        errlog.close()
        del errlog
    except:
        print '\nFailed to log error:',message,'\n'
        pass

def log_pid():
    'Log the process ID for early-termination checking'
    try:
        self_PID = os.getpid()
        f = open('PID.dat','w')
        f.write(str(self_PID))
        f.close()
    except:
        errorLog('Unable to save PID to temporary file')


def play(arg1, arg2):
    'Play through downloaded audio files'
    global playing
    global paused
    global PID

    #Empty trash to avoid playing of old cached files:
    err_check = os.system('rm -rf ~/.local/share/Trash/files/*')
    err_check2 = os.system('rm -rf ~/.local/share/Trash/info/*')

    #Get list of downloadd files:
    file_list = glob.glob('*.mp3*')
    if len(file_list) > 0:
        for i in range(0,len(file_list)):
            GPIO.output(12, 1)
            process = subprocess.Popen(['mpg321','-g','20',file_list[i]], stderr=subprocess.PIPE)
            PID = process.pid
            playing = True
            paused = False

            process.wait()
            del process
            os.remove(file_list[i])
            time.sleep(2)
    else:
        GPIO.output(12, 1)
        process = subprocess.Popen(['mplayer','no_messages.ogg'], stderr=subprocess.PIPE)
        PID = process.pid
        playing = True
        paused = False
        process.wait()
        GPIO.output(12, 0)
        
    playing = False
    paused = False
    GPIO.output(12, 0)

    
def pause():
    'Pause current audio file'
    global PID
    global paused
    os.kill(PID, signal.SIGSTOP)
    paused = True
    GPIO.output(12, 0)


def unpause():
    'Resume play of audio'
    global PID
    global paused
    os.kill(PID, signal.SIGCONT)
    paused = False
    GPIO.output(12, 1)


def determine_action(channel):
    'Choose action to take when button is pressed'
    global playing
    global paused
    if playing==False and paused==False:
        thread = threading.Thread(target=play, args=(0,0))
        thread.start()

    elif playing==True and paused==False:
        pause()

    elif playing==True and paused==True:
        unpause()


def get_audio(url):
    'Fetch audio files from server'
    global connected

    if connected==True:
        request = urllib2.urlopen(url+'file_list.py')
        response = request.read()
        file_list = response.split(',')
        if len(file_list) >0:

            for i in range(0,len(file_list)):
                if len(file_list[i])<4:
                    continue
                err_check = os.system('wget "'+url+file_list[i]+'" -P /downloaded/')
                if err_check != 0:
                    errorLog('Failed to download '+file_list[i])
                else:
                    purge_server(url+'purge_files.py',file_list[i])
                    string = 'mv /downloaded/"'+file_list[i]+'" "'+str(datetime.datetime.now())[:19].replace(':','.')+'.mp3"'
                    err_check = os.system(string)
                    if err_check !=0:
                        errorLog('Failed to rename '+file_list[i])


def purge_server(url,file_name):
    'Send request to server to delete downloaded files'
    req_args = {'file_name':file_name}
    data = urllib.urlencode(req_args)
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)
    err_check = response.read()
    if err_check != 'complete':
        errorLog('The server failed to delete '+file_name)

def connectivity_check():
    'Check for internet connectivity and launch hotspot if none found'
    global connected
    while 1:
        response = subprocess.check_output(['hostname','-I'])
        if response=='192.168.42.1':
            connected = False
            response = 0
        if len(response) < 8 and connected==True:
            errorLog('No internet connection... Check again in 2 min')
            time.sleep(120)
            response = subprocess.check_output(['hostname','-I'])
            if len(response) < 8:
                connected = False
                errorLog('launching hotspot script')
                os.system('sudo /home/pi/audio_streaming/network_check')
        elif: len(response) > 8 and connected==False:
            connected = True

        time.sleep(600)


def main(server,delay):
    'Run main loop'
    while 1:
        get_audio(server)
        time.sleep(delay)


# Set working directory and configure audio output
os.chdir('/home/pi/audio_streaming/')
log_pid()
err_check = os.system('amixer cset numid=3 1')
if err_check != 0:
    errorLog('failed to set output to jack')

# Configure I/O pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(12, GPIO.OUT, initial=0)
GPIO.add_event_detect(11, GPIO.FALLING, callback=determine_action, bouncetime=1000)

playing = False
paused = False
PID = 0

print 'Initiating audio streaming utility'
main = threading.Thread(target=main, args=(server,wait_time))
main.start()
main.join()

print 'Exiting Program'
GPIO.cleanup()
