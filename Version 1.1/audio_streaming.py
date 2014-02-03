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
server_url = ''

#### End Parameters ####

def errorLog (message):
    'Log an error message to file'
    now = str(datetime.datetime.now())[:19]
    message = now + '  -  ' + message + '\n'
    try:
        errlog = open('Error Log.txt', 'a')
        errlog.write(message)
        errlog.close()
    except:
        print '\nFailed to log error:',message,'\n'

def play(arg1, arg2):
    'Play through downloaded audio files'
    global playing
    global paused
    global PID

    #Get list of downloadd files:
    file_list = glob.glob('*.mp3')
    print file_list  #Debugging
    if file_list != None:
        for i in range(0,len(file_list)):
            
            process = subprocess.Popen(['mpg321',file_list[i]], stderr=subprocess.PIPE)
            PID = process.pid
            playing = True
            paused = False

            process.wait()
            del process
            err_check = os.remove(file_list[i])
            print err_check
            if err_check != 0:
                print 'Failed to delete ', file_list[i]
                errorLog('Failed to delete '+ file_list[i])
        else:
            process = subprocess.Popen(['mplayer','no_messages.ogg'], stderr=subprocess.PIPE)
            PID = process.pid
            playing = True
            paused = False
            process.wait()
            
                    
    playing = False
    paused = False
    
def pause():
    'Pause current audio file'
    global PID
    global paused
    print 'received signal to pause'  #debuggin
    os.kill(PID, signal.SIGSTOP)
    paused = True

def unpause():
    'Resume play of audio'
    global PID
    global paused
    print 'received signal to resume'  #debugging
    os.kill(PID, signal.SIGCONT)
    paused = False

def determine_action(channel):
    'Choose action to take when button is pressed'
    global playing
    global paused
    print'Received button signal'  #debugging
    if playing==False and paused==False:
        thread = threading.Thread(target=play, args=(0,0))
        thread.start()

    elif playing==True and paused==False:
        pause()

    elif playing==True and paused==True:
        unpause()

def get_audio(url):
    'Fetch audio files from server'
    request = urllib2.urlopen(url+'file_list.py')
    response = request.read()
    file_list = response.split()

    for i in range(0,len(file_list)):
        err_check = os.system('wget '+url+file_list[i])
        if err_check != 0:
            errorLog('Failed to download '+file_list[i])
        else:
            purge_server(url+'purge_files.py',file_list[i])

def purge_server(url,file_name):
    'Send request to server to delete downloaded files'
    req_args = {'file_name':file_name}
    data = urllib.urlencode(req_args)
    request = urllib2.Request(url, data)
    response = urllib2.urlopen(request)
#    response = urllib2.urlopen(url+'?file_name='+file_name)
    err_check = response.read()
    print err_check  #debugging

    if err_check != 'Complete\n':
        errorLog('The server failed to delete '+file_name)


def main(arg1,arg2):
    'Run main loop'
    global server_url
    while 1:
        get_audio(server_url)
        time.sleep(300)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(22, GPIO.IN)
GPIO.add_event_detect(22, GPIO.FALLING, callback=determine_action, bouncetime=1000)

playing = False
paused = False
PID = 0

print 'Initiating Program'
main = threading.Thread(target=main, args=(0,0))
main.start()
main.join()

print 'Exiting Program'
GPIO.cleanup()
