from flask import Flask, jsonify, make_response, request
import xml.etree.ElementTree
import libvirt
import XMLEdit
import MySQLdb
import os
import pickle
import subprocess
import rados
import rbd
from random import choice



app = Flask(__name__)

@app.route("/server/vm/create",methods=['GET'])

def create():
    
    name=request.args['name']
    instance_type=int(request.args['instance_type'])
    image_id=int(request.args['image_id'])

    i=open('image_file', 'r').read()
    img=i.split('\n')


    fl = open('flavor_file', 'r').read()
    flav=eval(fl)
    
    db = MySQLdb.connect(host="localhost", 
                         user="root",
                         passwd="YOURNEWPASSWORD", 
                         db="sar")
 
    cur = db.cursor() 
    
    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    print pm
    
    gh=-1
    for i in pm:
        print "scp -3 sourav@localhost:"+img[image_id]+" "+i+":~/"
        p = subprocess.Popen(["scp","-3","sourav@localhost:"+"~/Cloud_Computing/sar2.img", i+":~/"])
        sts = os.waitpid(p.pid, 0)
        #os.system("scp -3 sourav@localhost:"+img[image_id]+" "+i+":~")
        value=XMLEdit.edit(name,flav['types'][instance_type],image_id,i)
        xmldesc=open(name+'.xml').read()

        
        conn= libvirt.open("qemu+ssh://"+i+"/system")
        try:
            

            gh+=1
            obj = conn.defineXML(xmldesc)
            obj.create()

            sc="'"
            c='INSERT INTO `VM` ( `domid`,`name`, `instance_type`, `pmid`) VALUES ( '+sc+str(obj.ID())+sc+','+sc+str(value[0])+sc+','+sc+ str(instance_type) +sc+','+ sc+str(gh)+sc+')'
            cur.execute(c);
            
            
        
            db.commit()
            cur.execute("SELECT vmid from VM where domid="+str(obj.ID())+" and pmid="+str(gh))
            
            for row in cur.fetchall():
                x=row[0]
            return jsonify(vmid=x)
        except OSError,libvirt.libvirtError:
            continue
    return "{'status' :0}"


@app.route("/server/vm/query",methods=['GET'])

def query():
    db = MySQLdb.connect(host="localhost", 
                     user="root",
                      passwd="YOURNEWPASSWORD", 
                     db="sar")
    
    cur = db.cursor()
    vmid=request.args['vmid']
    
    sc="'"
    c='select * from `VM` where `vmid`='+str(vmid)
    cur.execute(c)
    try:
        
        for row in cur.fetchall() :

            dic={'vmid':row[0],'name':row[2],'instance_type':row[3],'pmid':row[4]}
    

        return str(dic)
    except UnboundLocalError:
        return "{'status': 0}"

@app.route("/server/vm/destroy",methods=['GET'])

def destroy():
    db = MySQLdb.connect(host="localhost", 
                     user="root",
                      passwd="YOURNEWPASSWORD", 
                     db="sar")
    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    
    cur = db.cursor()
    vmid=int(request.args['vmid'])
    c='select * from `VM` where `vmid`='+str(vmid)
    cur.execute(c)
   

    try:
        for row in cur.fetchall() :
            dic={'vmid':row[0],'name':row[2],'instance_type':row[3],'pmid':row[4]}

        c="DELETE FROM `VM` WHERE `vmid` = "+str(vmid)
        print c
        cur.execute(c);
        db.commit()

        conn= libvirt.open("qemu+ssh://"+pm[row[4]]+"/system")
    
        #conn.lookupByID(row[1]).destroy()

        obj=conn.lookupByID(row[1])
        obj.destroy()
        obj.undefine()

        return "{'status':1}"
    except UnboundLocalError,libvirt.libvirtError:
        return "{'status': 0}"




@app.route("/server/vm/types")

def types():
    fl = open('flavor_file', 'r').read()
    return fl


@app.route("/server/pm/list")

def list():
    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    l = range(len(pm)-1)
    dic={"pmids":l}
    return str(dic) 

@app.route("/server/pm/listvms",methods=['GET'])

def listvms():
    pmid=request.args['pmid']
    c="SELECT vmid from `VM` where `pmid`="+pmid
    db = MySQLdb.connect(host="localhost", 
                     user="root",
                      passwd="YOURNEWPASSWORD", 
                     db="sar")
    cur = db.cursor()
    cur.execute(c)
    q=cur.fetchall()
    lists=[]
    for row in q:
        lists.append(row[0])
    
    dic={"vmids":lists}
    return str(dic)

@app.route("/server/pm/query",methods=['GET'])

def pm_query():
    pmid=request.args['pmid']
    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    ip=pm[int(pmid)]

    conn= libvirt.open("qemu+ssh://"+ip+"/system")
    maxcpu=conn.getMaxVcpus(None)
    st=open("/proc/meminfo","r").read()
    memdata=st.split()
    maxmem=memdata[1]
    memfree=memdata[4]
    print maxmem,memfree

    c="SELECT vmid from `VM` where `pmid`="+pmid
    db = MySQLdb.connect(host="localhost", 
                     user="root",
                      passwd="YOURNEWPASSWORD", 
                     db="sar")
    cur = db.cursor()
    cur.execute(c)
    q=cur.fetchall()
    lists=[]
    for row in q:
        lists.append(row[0])
    ter=len(row)

    dic={"pmid":int(pmid),
    "capacity":{
"cpu": maxcpu,
"ram": maxmem,
"disk": 154
},
"free":{
"cpu": maxcpu-ter,
"ram": memfree,
"disk": 150
},
"vms": ter
    }



    

    return str(dic)

@app.route("/server/image/list",methods=['GET'])

def image_list():
    i=open('image_file', 'r').read()
    img=i.split('\n')
    l=[]
    intu=0
    for i in img:
        l.insert(-1,{"id":intu,"name":i.split("/")[-1].split(".")[0]})
        intu+=1
    dic={"images":l}

    return str(dic)
VM_id = 38201
VOL_id = 157
CONF_FILE = "/etc/ceph/ceph.conf"
HOST = 'tg'
BLOCK_XML = ""
VOL_Names = []
POOL='testpool'
@app.route("/server/volume/create",methods=['GET'])

def vol_create():
    name=str(request.args['name'])
    size=int(request.args['size'])*(1024**3)
    global VOL_Names
    if name in VOL_Names:
        return jsonify(volumeid=0)
    global rbdInstance
    global ioctx
    try:
        rbdInstance.create(ioctx, name, size)
        os.system('sudo rbd map %s --pool %s --name client.admin'%(name,POOL))
    except:
        print "hrllo"
        return jsonify(volumeid=0)

    volDetails = {}
    c=db.cursor()
    query = "SELECT * from `volume`"
    c.execute(query)
    db.commit()
    volumeID  =VOL_id + int(c.rowcount)
    sc="'"
    devname=getDeviceName()
    query='INSERT INTO `volume` ( `volume_id`,`name`, `size`, `status`,`vmid`,`dev_name`) VALUES ( '+sc+str(volumeID)+sc+','+sc+str(name)+sc+','+sc+ str(size) +sc+','+ sc+str("available")+sc+','+sc+str(-1)+sc+','+sc+str(devname)+sc+')'
    print query
    c=db.cursor()
    c.execute(query)
    db.commit()
    return jsonify(volumeid=volumeID)

@app.route("/server/volume/query",methods=['GET'])
def vol_query():
    volumeID=int(request.args['volumeid'])
    cur = db.cursor()    
    sc="'"
    c='select * from `volume` where `volume_id`='+str(volumeID)
    print c
    cur.execute(c)
    try:
        for row in cur.fetchall() :
            dic={'volumeid':row[0],'name':row[1],'size':row[2],'status':row[3],'vmid':row[4]}
        return str(dic)
    except UnboundLocalError:
        return jsonify(error = "volumeid : %s does not exist"%(volumeIDtoquery))


@app.route("/server/volume/destroy",methods=['GET'])
def vol_destroy():
    volumeID=int(request.args['volumeid'])
    cur = db.cursor()    
    sc="'"
    c='select * from `volume` where `volume_id`='+str(volumeID)
    print c
    cur.execute(c)
    for row in cur.fetchall():
        print "ht"
        imageName=row[1]
    #try:
    os.system('sudo rbd unmap /dev/rbd/%s/%s'%(POOL,imageName))
    rbdInstance.remove(ioctx,imageName)
    c="DELETE FROM `volume` WHERE `volume_id` = "+str(volumeID)
    print c
    cur.execute(c);
    db.commit()
    return jsonify(status=1)
    '''except:
        return jsonify(status=0)'''

@app.route("/server/volume/attach",methods=['GET'])
def vol_attach():
    arguments = request.args
    vmid = int(arguments['vmid'])
    volid = int(arguments['volumeid'])
    i=open('image_file', 'r').read()
    img=i.split('\n')

    fl = open('flavor_file', 'r').read()
    flav=eval(fl)

    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    c='select * from `volume` where `volume_id`='+str(volid)
    print c
    cur = db.cursor()    
    cur.execute(c)
    for row in cur.fetchall() :
        Image_name=row[1]
        dev=row[5]
    c='select * from `VM` where `vmid`='+str(vmid)
    cur = db.cursor()    
    cur.execute(c)
    for row in cur.fetchall() :
        VM_name=row[2]
        pmid=row[4]

    connection= libvirt.open("qemu+ssh://"+pm[int(pmid)]+"/system")
    dom = connection.lookupByName(str(VM_name))
    confXML = getXML(str(Image_name), str(HOST), str(POOL), str(dev))
    #try:
    dom.attachDevice(confXML)
    sc="'"
    c='UPDATE `volume` SET `status`='+sc+str("attached")+sc+' AND `vmid`='+str(vmid)+'  WHERE `volume_id` ='+str(volid)
    print c
    cur = db.cursor() 
    cur.execute ("""
UPDATE volume
SET status=%s, vmid=%s WHERE volume_id=%s
""", (str("attached"),str(vmid),str(volid)))   
    db.commit()
    connection.close()
    return jsonify(status=1)
    '''except:
        connection.close()
        return jsonify(status=0)'''

@app.route("/server/volume/detach",methods=['GET'])
def vol_detach():
    arguments = request.args
    volid = int(arguments['volumeid'])
    i=open('image_file', 'r').read()
    img=i.split('\n')

    fl = open('flavor_file', 'r').read()
    flav=eval(fl)
    
    p=open('pm_file', 'r').read()
    pm=p.split('\n')
    c='select * from `volume` where `volume_id`='+str(volid)
    print c
    cur = db.cursor()    
    cur.execute(c)
    for row in cur.fetchall() :
        Image_name=row[1]
        vmid=row[4]
        dev=row[5]
    c='select * from `VM` where `vmid`='+str(vmid)
    cur = db.cursor()    
    cur.execute(c)
    for row in cur.fetchall() :
        VM_name=row[2]
        pmid=row[4]
    connection = libvirt.open("qemu+ssh://" + pm[int(pmid)] + "/system")
    dom = connection.lookupByName(VM_name)
    confXML = getXML(str(Image_name), str(HOST), str(POOL), str(dev))
    try:
        dom.detachDevice(confXML)
        #connection.close()
        c='UPDATE volume SET `status`='+"available"+' AND `vmid`='+str(-1)+'  WHERE `volume_id` ='+str(volid)
        cur = db.cursor()    
        cur.execute ("""
       UPDATE volume
       SET status=%s, vmid=%s WHERE volume_id=%s
    """, (str("available"),str(-1),str(volid)))   
        db.commit()
        connection.close()
        return jsonify(status=1)
    except:
        connection.close()
        return jsonify(status=0)





def get_db():
    db = MySQLdb.connect(host="localhost", 
                     user="root",
                      passwd="YOURNEWPASSWORD", 
                     db="sar")
    return db

def establish_connection():
    cluster = rados.Rados(conffile=CONF_FILE)
    cluster.connect()
    if POOL not in cluster.list_pools():
        cluster.create_pool(POOL)
    global ioctx
    ioctx = cluster.open_ioctx(POOL)
    global rbdInstance
    rbdInstance = rbd.RBD()

def getDeviceName():
    alpha = choice('efghijklmnopqrstuvwxyz')
    numeric = choice([x for x in range(1,10)])
    return 'sd' + str(alpha) + str(numeric)

def getXML(imageName, host, pool, dev):
    xml = """<disk type='block' device='disk'>
                <driver name='qemu' type='raw'/>
                <source protocol='rbd' dev='/dev/rbd/%s/%s'>
                     <host name='%s' port='6789'/>
                </source>
                <target dev='%s' bus='virtio'/>
            </disk>"""%(pool, imageName, host, dev)
    return xml

def getHostName():
    global HOST
    monProc = subprocess.Popen("ceph mon_status", shell=True, bufsize=0, stdout=subprocess.PIPE, universal_newlines=True)
    monDict = eval(monProc.stdout.read())
    HOST = monDict['monmap']['mons'][0]['name']

if __name__=="__main__":
    db=get_db()
    establish_connection()
    getHostName()
    app.run(debug=True)
