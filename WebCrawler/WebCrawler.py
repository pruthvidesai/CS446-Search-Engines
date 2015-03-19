import urlparse, urllib2
import os, re, copy
from pprint import pprint
from time import sleep

class WebCrawler():
    def __init__(self, seeds):
        self.pages = 0
        self.delay = None
        self.visited = []
        self.URLQueue = [seeds.strip('/')]
        self.robots = None
        self.restriction = r'umass.edu'
        self.Crawl(self.URLQueue)
        self.writeToFile()

    def getRobots(self, seeds):
        domain = urlparse.urlparse(seeds)
        robots = domain.scheme + "://" + domain.netloc + '/robots.txt'
        self.robots = urllib2.urlopen(robots).read().split('Disallow: ')
        for x in self.robots:
            if 'Crawl-delay' in x:
                match = re.findall(r'\d+', x)
                self.delay = match[0]
        temp = []
        for item in self.robots:
            temp.append(item.strip('\n').strip('\r'))
        self.robots = copy.deepcopy(temp)
        return self.robots

    def Crawl(self, seeds):
        for urllink in self.URLQueue:
            sleep(self.delay)
            #print len(self.URLQueue)
            if len(self.URLQueue) > 10:
                break
            request = urllib2.Request(urllink)
            try:
                req = urllib2.urlopen(request)
                robots = self.getRobots(urllink)
            except urllib2.URLError, err:
                continue
            html = req.read()
            self.visited.append(urllink)
            urls = self.addURLs(html, req, robots)
            self.pages += 1
        '''
        print "No of unique links: ", len(self.URLQueue)
        print "No of documents downoaded: ", self.pages
        print "No of visited links: "
        pprint(self.visited)
        '''

    def writeToFile(self):
        file = open("urls.txt", 'w')
        for x in range(100):
            file.write(self.URLQueue[x] + '\n')
        file.close()
        file = open("links-visited.txt", 'w')
        for x in range(len(self.visited)):
            file.write(self.visited[x] + '\n')
        file.close()
            
    def addURLs(self, html, request, robots):
        #variable to save all links
        sub_url_queue = []

        #pattern = r'href=\"*\'*[\w.-/?]*[-.:?]*[\w.-?/#]*\"*\'*'
        pattern = "(?i)href\s*=\s*\"[^\"]*\"|\'[^\']*\'"
        urls = re.findall(pattern, html)
        temp = []
        #clean the urls
        for url in urls:
            match = re.search(r'\s+|.jpg|.mov|.ico|.css|.php', url)
            if not match:
                temp.append(url.lstrip('href=').strip('"').strip("'"))

        urls = copy.deepcopy(temp)

        #checking the url in robots
        #re
        temp = []
        for pattern in robots:
            for url in urls:
                try:
                    match = re.search(pattern.strip('/'), url)
                    if match:
                        temp.append(url)
                except re.error:
                    continue
        for t in temp:
            try:
                urls.remove(t)
            except ValueError, e:
                continue

        #url algorithm for forming a url
        for url in urls:
            if self.URLQueue.count(url.strip('/')) == 0:
                base = request.geturl()
                parse = urlparse.urlparse(url)
                if parse.netloc != '':
                    match = re.search(self.restriction, parse.netloc)
                    if match:
                        self.URLQueue.append(url.strip('/'))
                        sub_url_queue.append(url.strip('/'))
                else:
                    split_url = url.split('/')
                    no_backdirs = split_url.count('..')
                    for _ in range(no_backdirs):
                        split_url.remove('..')
                    temp_base = urlparse.urlparse(base)
                    match = re.search(r'[\w-]+', temp_base.path)

                    #split_url
                    string_split_url = ""
                    for x in range(len(split_url)):
                        if split_url[x] is not '':
                            string_split_url += '/' + split_url[x]
                    base_url = temp_base.scheme + '://' + temp_base.netloc

                    if match:
                        base_path = temp_base.path.split('/')
                        #remove empty strings
                        for _ in range(base_path.count('')):
                            base_path.remove('')
                        #go back no of dirs
                        for _ in range(no_backdirs):
                            base_path.pop(-1)
                        #to make complete url: base.netloc + base_path + split_url
                        paths = ""
                        for y in range(len(base_path)):
                            paths += '/' + base_path[y]
                        #final
                        complete_url =  base_url + paths + string_split_url
                    else:
                        complete_url = base_url + string_split_url
                    #check if doesn't exist in original queue
                    if self.URLQueue.count(complete_url.strip('/')) == 0:
                        parsed = urlparse.urlparse(complete_url)
                        match = re.search(self.restriction,parsed.netloc)
                        if match:
                            self.URLQueue.append(complete_url.strip('/'))
                            sub_url_queue.append(complete_url.strip('/'))
        return sub_url_queue

seeds = "https://cs.umass.edu/"
Web = WebCrawler(seeds)
