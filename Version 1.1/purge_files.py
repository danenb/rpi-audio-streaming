import cgi, os

#### Parameters ####
path = ''

#### End Parameters ####

POST = cgi.FieldStorage()

file_name = POST.getvalue('file_name')
print "Content-type:text/html\r\n\r\n"
if file_name != None:
    err_check = os.remove(path+file_name)

    if err_check != 0:
        print 'Complete'
    else:
        print 'Failed'
else:
    print 'Invalid file name'
