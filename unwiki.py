import re

RE = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
        \[\[[^|^\]]+\||
        \[\[|
        \]\]|
        \'{2,5}|
        (<s>|<!--)[\s\S]+(</s>|-->)|
        {{[\s\S\n]+?}}|
        <ref>[\s\S]+</ref>|
        ={1,6}""", re.VERBOSE)


def loads(wiki, compress_spaces=None):
    '''
    Parse a string to remove and replace all wiki markup tags
    '''
    result = RE.sub('', wiki)
    if compress_spaces:
        result = re.sub(r' +', ' ', result)

    return result


def load(stream, compress_spaces=None):
    '''
    Parse the content of a file to un-wikified text
    '''
    return loads(stream.read(), compress_spaces=compress_spaces)
