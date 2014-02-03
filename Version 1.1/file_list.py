import glob

#### Parameters ####
path = ''

#### End Parameters ####

files = glob.glob(path+'*.mp3')

print "Content-type:text/html\r\n\r\n"

for i in range(0,len(files)):
    print files[i] + ' '
