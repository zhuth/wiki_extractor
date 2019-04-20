from xml.sax import handler, make_parser
import os
import zipfile
from collections import defaultdict
import unwiki

def convhans(sentence):
    from langconv import Converter
    sentence = Converter('zh-hans').convert(sentence)
    return sentence


class PageHandler(handler.ContentHandler):
    def __init__(self, storage, tester):
        self.tester = tester
        self.storage = storage
        self.tags = []
        self.page = defaultdict(str)
        self.z = zipfile.ZipFile(self.storage, 'w')
    
    def startElement(self, name, attr):
        if name == 'page':
            self.page = defaultdict(str)
        self.tags.append(name)

    def endElement(self, name):
        if name == 'page':
            print(self.page['title'], self.page['id'])
            for _ in ['text', 'title']:
                self.page[_] = convhans(unwiki.loads(self.page[_].strip()))

            if self.tester(self.page):
                self.z.writestr('{title}_{id}.txt'.format(**self.page), 
                    '''{title}\n===========\n\n{text}\nhttps://zh.wikipedia.org/wiki/{title}\n'''.format(**self.page))
            
        self.tags.pop()

    def characters(self, content):
        if self.tags[-1] == 'text':
            self.page[self.tags[-1]] += content
        else:
            if self.tags[-1] not in self.page:
                self.page[self.tags[-1]] = content

    def endDocument(self):
        self.z.close()

if __name__ == "__main__":
    import sys
    kw = sys.argv[1]
    xmlparse = make_parser()
    xmlparse.setContentHandler(PageHandler(sys.argv[2], lambda d: kw in d['text']))
    xmlparse.parse(sys.stdin)
