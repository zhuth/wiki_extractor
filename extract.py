from xml.sax import handler, make_parser
import os
import sys
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
        self.page = {}
        self._fields = ['text', 'title', 'id']
        self.z = zipfile.ZipFile(self.storage, 'w')
    
    def startElement(self, name, attr):
        if name == 'page':
            self.page = defaultdict(str)
        self.tags.append(name)

    def endElement(self, name):
        if name == 'page':
            for _ in ['text', 'title']:
                self.page[_] = convhans(unwiki.loads(self.page[_].strip()))

            if self.tester(self.page):
                print(self.page['title'], self.page['id'])
                self.z.writestr('{title}_{id}.txt'.format(**self.page), 
                    '''{title}\n===========\n\n{text}\nhttps://zh.wikipedia.org/wiki/{title}\n'''.format(**self.page))
            
        self.tags.pop()

    def characters(self, content):
        tag = self.tags[-1]
        if tag in self._fields:
            if tag == 'text':
                self.page[tag] = self.page.get(tag, '') + content
            elif tag not in self.page:
                self.page[tag] = content
        
    def endDocument(self):
        self.z.close()

def extract(zfile, tester, sin=sys.stdin):
    xmlparse = make_parser()
    xmlparse.setContentHandler(PageHandler(sys.argv[2], tester))
    xmlparse.parse(sys.stdin)

if __name__ == "__main__":

    kw = sys.argv[1]
    zf = sys.argv[2]
    
    def _tester(d):
        if ':' not in d['title'] and '/' not in d['title'] and 'text' in d and kw in d['text']:
            return True
    
    extract(zf, _tester)
