#Python Regular Expression
import re
import urllib2

def RegEx():
    #string = '<h1 class="heading"><a href="../about/">Pruthvi<span class="desai"> Desai </span></a></h1>'
    #string = "<h1 class='heading'><a href='http://ciir.cs.umass.edu/personnel/index.html'>Pruthvi<span class='desai'> Desai </span></a></h1>"
    #pattern = r'[\w/:]*[\w\.-]+\.[\w\.-]+[\w/.]+'
    #pattern = r'href=\"*\'*[\w.-:/?,=]*\"*\'*'
    #product = re.findall(pattern, string)
    #for item in product:
    #    item = item.strip('href').strip('=')
    #    print item
    try:
        url = urllib2.urlopen("http://localhost:8000")
        print "yo"
    except:
        print "Bad"


RegEx()