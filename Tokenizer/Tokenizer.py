import copy, re, sys
import matplotlib.pyplot as plt
from pprint import pprint

class Tokenizer():
    def __init__(self, input):
        self.file = input
        self.wordlist = []
        self.stoplist = []
        self.stemlist = []
        self.tokenizedlist = []
        self.wordfrequency = {}

    def inputFiles(self):
        # stop list
        stop = open('stopwords', 'r')
        for word in stop.readlines():
            word = word.strip('\n')
            self.stoplist.append(word)
        stop.close()

        # input file
        f = open(self.file, 'r')
        for line in f.readlines():
            line = copy.deepcopy(line.split())
            for word in line:
                self.wordlist.append(word)
        f.close()

    def tokenize(self):
        tempwordlist = []
        for word in self.wordlist:
            # change to lowercase
            word = copy.deepcopy(word.lower())

            # abbreviate
            if(self.isAbbreviation(word)):
                # strip special chars
                temp = ''
                for x in word:
                    if x.isalnum() or x == '.':
                        temp += ''.join(x)
                word = copy.deepcopy(temp)
                
                # strip dots
                temp = ''
                for item in word:
                    if not item == '.':
                        temp += ''.join(item)
                word = copy.deepcopy(temp)
                tempwordlist.append(word)

            # separate words using other chars
            else:
                temp = []
                string = ''
                for item in word:
                    if item.isalnum():
                        string += item
                    elif not item == "'":
                        temp.append(string)
                        string = ''
                temp.append(string)
                word = temp

                # remove all empty elements
                x = []
                for item in word:
                    if not item == '':
                        x.append(item)
                word = x
                tempwordlist.extend(word)

        self.wordlist = copy.deepcopy(tempwordlist)

    def isAbbreviation(self, word):
        # returns a true if an abbreviation
        count = word.count('.')
        if count > 0:
            list = word.split('.')

            # strip all the special chars
            temp = []
            for item in list:
                if item.isalnum():
                    temp.append(item)
            list = copy.deepcopy(temp)

            # checks if each item is less than 2 chars
            for chars in range(len(list)):
                if not len(list[chars]) <= 2:
                    return False
        else:
            return False
        return True

    def stopping(self):
        # use lemur word list
        temp = []
        for word in self.wordlist:
            if self.stoplist.count(word) == 0:
                temp.append(word)
        self.wordlist = copy.deepcopy(temp)

    def stemming(self):
        stem = ''
        through = False
        length = len(self.wordlist)
        f = open('output.txt', 'w')
        for index in range(length):
            stem = self.wordlist[index]
            # step 1a

            # - replace "sses" by "ss"
            pattern = r'^\w+sses$'
            match = re.search(pattern, self.wordlist[index])
            if match:
                stem = self.wordlist[index].replace('sses', 'ss')
                #print "sses: " + stem
                f.write(stem + '\n')
                through = True
                self.wordlist[index] = stem
                if stem not in self.stemlist:
                    self.stemlist.append(stem)

            # - delete 's' not imm before vowel
            passedS = True
            pattern = r'[bcdfghjklmnpqrstvwxz]+s$'
            match = re.search(pattern, self.wordlist[index])
            if match:
                match = re.search(r'us|ss$', self.wordlist[index])
                if not match:
                    stem = self.wordlist[index][:-1]
                    #print "s: " + stem
                    f.write(stem + '\n')
                    through = True
                    passedS = False
                    self.wordlist[index] = stem
                    if stem not in self.stemlist:
                        self.stemlist.append(stem)

            # - replace "ies" or "ied" by i otherwise by ie
            pattern = r'([\w]+)(ie[sd]+)$'
            match = re.search(pattern, self.wordlist[index])
            if match:
                if len(self.wordlist[index]) - 3 > 1:
                    stem = self.wordlist[index].replace(match.group(2), 'i')
                else:
                    stem = self.wordlist[index].replace(match.group(2), 'ie')
                #print "ie-s/d: " + stem
                f.write(stem + '\n')
                through = True
                self.wordlist[index] = stem
                if stem not in self.stemlist:
                    self.stemlist.append(stem)

            # step 1b
            # passed checks "ed" vs "eed" words
            passedEd = False
            # replace "eed" or "eedly" by ee
            # eedly has priority
            pattern = r'([aeiou]+)([bcdfghjklmnpqrstvwxz]*)(eed[ly]*)$'
            match = re.search(pattern, self.wordlist[index])
            if match:
                if not match.group(1) is None:
                    stem = self.wordlist[index].replace(match.group(3), "ee")
                    passedEd = False
                #print "eed: " + stem
                f.write(stem + '\n')
                through = True
                self.wordlist[index] = stem

                
            # delete "ed", "edly", "ing" or "ingly" if preceding word
            # contains a vowel
            pattern = r'[aeiou]+'
            match = re.search(pattern, self.wordlist[index])
            if match:
                current = False
                # ed(ly)
                pattern = r'(ed)([l]+[y]+)*$'
                match = re.search(pattern, self.wordlist[index])
                if match:
                    pattern = r'(e\w\w)(\w+\w+)*$'
                    match = re.search(pattern, self.wordlist[index])
                    if not match:
                        current = True
                        through = True
                        if self.wordlist[index].count("ly") == 0:
                            stem = self.wordlist[index].strip('d').strip('e')
                        else:
                            stem = self.wordlist[index].replace("ly", '').strip('d').strip('e')

                # ing(ly)
                pattern = r'(ing)([l]+[y]+)*$'
                match = re.search(pattern, self.wordlist[index])
                if match and passedS:
                    current = True
                    through = True
                    if match.group(2) is None:
                        stem = self.wordlist[index].replace("ing", '')
                        self.wordlist[index] = stem
                    else:
                        stem = self.wordlist[index].replace("ing" + match.group(2), '')
                        self.wordlist[index] = stem

               
                # check end pattern of stem word
                if current:
                    pattern = r'(a+t+)|(b+l+)|(i+z+)$'
                    match = re.search(pattern, stem)
                    if match or len(stem) < 4:
                        stem += 'e'
                        through = True
                        self.wordlist[index] = stem

                        f.write(stem + '\n')
                    #print "ed(ly) or ing(ly): " + stem

                    if len(stem) > 3:
                        # check for ! ll, ss, zz
                        x = stem[-1]
                        y = stem[-2]
                        if x == y:
                            if not (x == 'l' or x == 's' or x == 'z'):
                                stem = stem[:-1]
                                self.wordlist[index] = stem
                    f.write(stem + '\n')
                    if stem not in self.stemlist:
                        self.stemlist.append(stem)

            if not through:
                self.wordlist[index] = stem
        self.tokenizedlist = copy.deepcopy(self.wordlist)
        f.close()

    def frequency(self):
        # make dictionary
        for word in self.tokenizedlist:
            if not self.wordfrequency.has_key(word):
                self.wordfrequency[word] = self.tokenizedlist.count(word)

        # get most frequent words
        top = []
        temp = copy.deepcopy(self.wordfrequency)
        for i in range(200):
            max = [0, 0]
            for k, v in temp.iteritems():
                if max[1] < v:
                    max = [k, v]
            top.append(max)
            temp.pop(max[0])

        # write in file
        f = open('terms.txt', 'w')
        for kv in top:
            string = str(kv[0]) + '\t\t' + str(kv[1]) + '\n'
            f.write(string)
        f.close()

    def prettyPrint(self, list):
        f = open('tokenized.txt', 'w')
        for item in list:
            f.write(item + '\n')
        f.close()

if __name__ == '__main__':
    # argument clause
    if sys.argv[1] == None:
        input = 'input.txt'
    else:
        input = sys.argv[1]

    T = Tokenizer(input)
    T.inputFiles()
    T.tokenize()
    T.stopping()
    T.stemming()
    T.frequency()
    print len(T.tokenizedlist)
    print len(T.wordfrequency.keys())
    #T.prettyPrint(T.tokenizedlist)
