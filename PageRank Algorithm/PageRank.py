import copy, time, math, sys
from pprint import pprint

'''
@author Pruthvi Desai
PageRank Algorithm
'''

class PageRank():
    def __init__(self, file, l, t):
        self.lamda = l
        self.tau = t
        self.file = file
        self.unique = 0
        self.total_urls = 0
        self.terminals = 0
        self.urls_sorted = []
        self.dict = {}
        self.urls_with_inlinks = {}

    def create_url_with_pageranks(self):
        # creates a page rank file for unique urls
        # 'r+' reading and writing, 'a' appending
        with open(self.file, 'r') as raw:
            for lines in raw:
                source,destination = lines.strip('\n').split('\t')
                for item in [source, destination]:
                    if item not in self.urls_sorted:
                        self.urls_sorted.append(item)
                        self.total_urls += 1
        # create and add to file
        pagerank = open('pageranks.txt', 'w')
        initial = str(1.0/self.total_urls)
        for url in self.urls_sorted:
            string = url + '\t' + initial + '\n'
            pagerank.write(string)
        pagerank.close()

    def create_urls_with_inlinks(self, top=50):
        # run urls parallel to links
        top_inlinks = []
        string = ""
        # obtain lines from raw file
        r = open(self.file, 'r')
        raw = r.readlines()
        r.close()
        inlink_list = [["",0]]
        with open('pageranks.txt', 'r') as urls:
            # iterates through unique urls
            for url in urls.readlines():
                remove_list = []
                split = url.strip('\n').split('\t')
                url = split[0]
                if len(split) > 2:
                    print split
                # iterates through the raw file of source, dest
                inlink_count = 0
                length = len(raw)
                for line in range(length):
                    source,destination = raw[line].strip('\n').split('\t')
                    if url == source:
                        inlink_count += 1
                        remove_list.append(line)
                    if (inlink_count > 0 and url != source) or (length == inlink_count):
                        if inlink_count > inlink_list[-1][1]:
                            if len(inlink_list) == 50:
                                inlink_list.pop(-1)
                            current = [url, inlink_count]
                            inlink_list.insert(0, current)
                        break
                # remove the lines from raw
                if len(remove_list) > 0:
                    length = len(remove_list)
                    for i in range(length):
                        raw.pop(remove_list[0])

        # add to inlink file
        with open('inlinks.txt', 'w') as inlinks:
            j = 1
            for i in inlink_list:
                string = str(j) + '\t' + i[0] + '\t' + str(i[1]) + '\n'
                inlinks.write(string)
                j += 1

    def create_urls_with_pagerank_algorithm(self):
        # 1. Calculate PR and outlinks, write to file
        # convert original file to list for easier access
        original_file = open(self.file, 'r').readlines()
        ranks_file = open('new_pageranks.txt', 'w')
        with open('pageranks.txt', 'r') as urls:
            for line in urls:
                # reset for each iteration
                url_found = False
                remove_lines = []
                outlinks_list = []
                url,rank = line.strip('\n').split('\t')
                # accessing original file for each url
                length = len(original_file)
                for i in range(length):
                    source,destination = original_file[i].strip('\n').split('\t')
                    if url == source:
                        url_found = True
                        remove_lines.append(i)
                        outlinks_list.append(destination)
                    elif url_found == True:
                        break
                # add terminals/rank sink pages
                if url_found == False:
                    self.terminals += (float)(rank)
                # delete lines from original
                length = len(remove_lines)
                for j in range(length):
                    original_file.pop(remove_lines[0])

                # write to new file
                for x in range(len(outlinks_list)):
                    string1 = str(url) + '\t' + str(outlinks_list[x]) + '\t'
                    string2 = str((float)(rank)/len(outlinks_list)) + '\n'
                    string = string1 + string2
                    ranks_file.write(string)
        ranks_file.close()

        # 2. Calculate the PageRank for each url
        # Unique urls to dicts
        url_dict = {}
        url_list = open('pageranks.txt', 'r').readlines()
        self.unique = len(url_list)
        with open('pageranks.txt', 'r') as f:
            for x in f.readlines():
                key,value = x.strip('\n').split('\t')
                url_dict[key] = float(value)

        new = 2
        old = 1
        source_list = []
        top_list = []
        while not self.convergence(old, new):
            # iterating through each url
            for urls in url_list:
                found = False
                sum = 0
                url,rank = urls.strip('\n').split('\t')
                pageranks = open('new_pageranks.txt', 'r')
                for line in pageranks.readlines():
                    source,destination,rank = line.strip('\n').split('\t')
                    if source == url:
                        found = True
                        sum += float(url_dict[destination])
                        if url not in source_list:
                            source_list.append(url)
                    elif found == True:
                        break
                if url == '!Amigos!_2046':
                    # print "Sum", sum
                    pass
                url_dict[url] = self.update_value(sum)
                pageranks.close()

            self.dict = {}
            for items in source_list:
                self.dict[items] = url_dict[items]
            # pprint(self.dict.items())


            old = copy.deepcopy(new)
            i = 0.0
            for x in range(len(top_list)):
                i += float(top_list[x][1])
            new = i
            # print old, new

        length = len(source_list)
        for i in range(length):
            max = 0
            key = ''
            for item in source_list:
                if max < self.dict[item]:
                    max = self.dict[item]
                    key = item
            if key in source_list:
                source_list.pop(source_list.index(key))
                top_list.append([key, self.dict[key]])

        # write top 50 to the pageranks file
        pageranks = open('pagerank.txt', 'w')
        top = 50
        length = len(top_list)
        for i in range(length):
            if i == top:
                break
            string = str(i+1) + '\t' + top_list[i][0] + '\t' + str(self.dict[top_list[i][0]]) + '\n'
            pageranks.write(string)
        
    def update_value(self, sum):
        return self.fraction_of_pages() + self.terminal_effect() + (self.lamda * sum)

    def fraction_of_pages(self):
        return (float)(1.0-self.lamda)/self.total_urls

    def terminal_effect(self):
        return (float)(self.lamda) * (self.terminals/self.total_urls)

    def convergence(self, old, new):
        # L2 convention sqrt(sum((xi-yi)^2))
        # we use |new - old| < tau
        if math.fabs(new - old) < self.tau:
            return True
        return False

    def make_test_file(self, lines=1000):
        count = 0
        copy = open('smalltest.txt', 'w')
        with open('links.srt', 'r') as f:
            for line in f:
                if count == lines:
                    break
                copy.write(line)
                count += 1
        copy.close()

# Main
if __name__ == '__main__':
    # add arguments
    # arg1 is lambda and arg2 is tau
    l = sys.argv[1]
    tau = sys.argv[2]
    start = time.clock()
    PR = PageRank('smalltest.txt', l , tau)
    PR.create_url_with_pageranks()
    PR.create_urls_with_inlinks()
    #PR.create_urls_with_pagerank_algorithm()
    PR.make_test_file()
    print "Time taken:" , time.clock() - start

