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
        self.current_tag = ''
        self.page = defaultdict(str)
        self.z = zipfile.ZipFile(self.storage, 'w')
    
    def startElement(self, name, attr):
        if name == 'page':
            self.page = defaultdict(str)
        self.current_tag = name

    def endElement(self, name):
        if name == 'page':
            print(self.page)
            for _ in ['text', 'title']:
                self.page[_] = convhans(unwiki.loads(self.page.get(_, '')).strip())

            if self.tester(self.page):
                self.z.writestr('{}.txt'.format(self.page['title']), 
                    '''{title}\n===========\n\n{text}\nhttps://zh.wikipedia.org/wiki/{title}\n'''.format(**self.page))
            
        self.in_quote = False

    def characters(self, content):
        self.page[self.current_tag] += content

    def endDocument(self):
        self.z.close()

if __name__ == "__main__":
    import sys
    kw = sys.argv[1]
    xmlparse = make_parser()
    xmlparse.setContentHandler(PageHandler('zhwiki_{}.zip'.format(kw), lambda d: kw in d['text']))
    xmlparse.parse(sys.stdin)
