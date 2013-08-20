import os
import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    tree = ET.ElementTree(file='subscriptions.xml')
    root = tree.getroot()

    w_file = open("greader2xmltmp.txt", "w")
    category = []
    o = 1
    for elem in tree.iter(tag='outline'):
        if 'type' in elem.attrib.keys():
            strtmp = '+'.join(category)
            strtmp += ' ' + elem.attrib['title'] 
            strtmp += ' ' + elem.attrib['xmlUrl'] 
            w_file.write(strtmp+'\n')
            o = 1
        else:
            if o == 1:
                category = []
            category.append(elem.attrib['text'])
            o = 0

if __name__ == '__main__':
    main()

