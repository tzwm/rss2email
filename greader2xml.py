import os
import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from xml.dom import minidom

def getItem(root, body):
    for elem in root:
        if 'type' in elem.attrib.keys():
            node = ET.SubElement(body, 'item')
            node.set('text', elem.attrib['text'])
            node.set('type', elem.attrib['type'])
            node.set('htmlUrl', elem.attrib['htmlUrl'])
            node.set('rssUrl', elem.attrib['xmlUrl'])
        else:
            node = ET.SubElement(body, 'tag')
            node.set('text', elem.attrib['text'])
            getItem(elem, node) 
            elem.clear()

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')

    tree_input = ET.ElementTree(file='subscriptions.xml')

    root_output = ET.Element('root')
    head_output = ET.SubElement(root_output, 'head')
    title = ET.SubElement(head_output, 'title')
    title.text = 'subscriptions for rss2email'
    body_output = ET.SubElement(root_output, 'body')

    getItem(tree_input.iter(tag='outline'), body_output)

    tree_output = ET.ElementTree(root_output)
    xml_string = ET.tostring(root_output)
    doc = minidom.parseString(xml_string)
    o_file = open('rsslist.xml', 'w')
    o_file.write(doc.toprettyxml())

if __name__ == '__main__':
    main()

