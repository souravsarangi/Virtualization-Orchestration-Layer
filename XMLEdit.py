from xml.dom.minidom import parseString
import sys
import uuid

def edit(vmname,inst_type,img_id,pmid):
 
    
    i=open('image_file', 'r').read()
    img=i.split('\n')
    p=open('pm_file', 'r').read()
    pm=p.split('\n')

    xml=open('sar2.xml').read()
    
    doc = parseString(xml)
    uid=str(uuid.uuid1())

    name=doc.getElementsByTagName('name')[0]
    name.firstChild.replaceWholeText(vmname)

    name=doc.getElementsByTagName('uuid')[0]
    name.firstChild.replaceWholeText(uid)
    
    name=doc.getElementsByTagName('memory')[0]
    name.firstChild.replaceWholeText(str(inst_type['ram']*1024))

    name=doc.getElementsByTagName('currentMemory')[0]
    name.firstChild.replaceWholeText(str(inst_type['ram']*1024))

    name=doc.getElementsByTagName('vcpu')[0]
    name.firstChild.replaceWholeText(str(inst_type['cpu']))

    name=doc.getElementsByTagName('currentMemory')[0]
    name.firstChild.replaceWholeText(str(inst_type['ram']*1024))
    op=img[img_id].split("/")
    print op[-1]

    doc.getElementsByTagName('devices')[0].getElementsByTagName('disk')[0].getElementsByTagName('source')[0].setAttribute('file',"/home/"+pmid.split('@')[0]+"/"+op[-1])
    f = open(vmname+'.xml', 'w')
    f.write(doc.toxml())
    f.close()
    return [vmname,inst_type,0]
