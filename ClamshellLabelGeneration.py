from PIL import Image, ImageDraw, ImageFont
import PIL as PIL
import Support.CalcLib as calc
import time
import sys
import Support.memory as memory
import Support.GWINSTEK as supply
import Support.KVprocess as kv
import datetime
import Support.DBinterface as DB
import numpy as np
import Support.datalog as datalog
import Support.FileLocation as FL
import serial as serialcon
import Support.ITLA_v3 as ITLA
import Support.Ptouch_conversion as ptouch
import shutil

import barcode
from barcode.writer import ImageWriter



fonts =    [ ImageFont.truetype('arialbd.ttf', 40), ImageFont.truetype('arial.ttf', 40), ImageFont.truetype('arial.ttf', 22), ImageFont.truetype('arial.ttf',32), ImageFont.truetype('arialbd.ttf', 60), ImageFont.truetype('arial.ttf', 50)]

#PORT=calc.COMPORT()
img=None
outp=None

def create_Zebra(fname,targetname):
    global img,outp
    img1= Image.open(fname+'.png')
    img=img1.rotate(-90,expand=True)
    a=img.tobytes()
    teller=0
    b=[]
    while teller<len(a):
        if a[teller]>128:b.append(0)
        else: b.append(1)
        teller=teller+1
    teller=0
    outp=''
    while teller<len(b):
        teller2=0
        sum=0
        while teller2<8:
            sum=sum*2+b[teller]
            teller2=teller2+1
            teller=teller+1
        temp=hex(sum)[2:].upper()
        if len(temp)==1:temp='0'+temp
        outp=outp+temp
    f=open('logfiles\\'+targetname,'w')
    f.write('^XA\n')
    f.write('^FO100,0^GFA,%.0f,%.0f,%.0f,' %(len(b)/8,len(b)/8,int(LABELHEIGHT/8)))
    f.write(outp)
    f.write('\n')
    f.write('^XZ\n')
    f.close()
         
    
    

def place_text_left(x,y,fontid,tekst,underline=False):
    global draw
    w,h=fonts[fontid].getsize(tekst)
    draw.text((x,y),tekst,font=fonts[fontid],fill=0)
    if underline:
        draw.line((x,y+h,x+w,y+h),width=3)
    
def place_text_center(x,y,fontid,tekst):
    global draw
    w,h=fonts[fontid].getsize(tekst)
    draw.text((x-w/2,y-h/2),tekst,font=fonts[fontid],fill=0)

# temp9=input('Press Enter if the device is powered up or M for manual input ').upper()

# if temp9!='M':
#     supply.Connect()
#     supply.TurnOff()
#     supply.SetVoltage(12,1)
#     supply.SetVoltage(0,2)
#     #Turn power on
#     time.sleep(1)
#     supply.TurnOn()
#     try:
#         memory.loadfromdevice()
#         DEVICETYPE='PPCL700'
#         if kv.serial()[0:4]=='CRTM':
#             DEVICETYPE='PPCL600'
#             kv.setDevice('ppcl600')
#             memory.loadfromdevice()
        
#         kv.print_general_info() 
#         if DEVICETYPE=='PPCL700':
#             if not DB.verifyDevice(memory.cavityid(),memory.boardid(),memory.serial()):
#                 print('')
#                 print('SOMETHING WRONG WITH DEVICE CONFIGURATION. CHECK IN DATABASE')
#                 exit()
#     except:
#         PORT=input('Which port? ')
#         time.sleep(2)
#         sercon=serialcon.Serial('\\\\.\\'+str(PORT),9600, timeout=1)#ITLA.ITLAConnect(PORT,9600)
#         #get serial
#         serial=ITLA.ITLA(sercon,ITLA.REG_Serial,0,0)
#         if serial[0:3].upper()=='CRT':
#             serial=serial[0:10]
#             kv.setDevice('ppcl600')
#             DEVICETYPE='PPCL600'
#         else:
#             kv.setDevice('ppcl700')
#             serial=serial[0:9]
#             DEVICETYPE='PPCL700'
#         kv.serial(serial)
#         print(kv.serial())
# else:
#     supply.TurnOff()
#     temp8=input('serial? ')
#     if temp8[0:4]=='PP70': 
#         kv.serial(temp8)
#         DEVICETYPE='PPCL700'
#     else: sys.exit()



# if DEVICETYPE=='PPCL700':
#     orderid=DB.findorder(None,None,None,kv.serial())
#     if len(orderid)>0: devicedetails=DB.Get_One_Device(kv.serial())[0]
# if DEVICETYPE=='PPCL600':
#     orderid=DB.DB_PPCL600OPS_orders(kv.serial())
#     if len(orderid)>0: devicedetails=[]

# if len(orderid)==0:
#     print ('Part is not assigned to order')
#     sys.exit()
# else:
#     if len(orderid)>1:
#         print('Part is assigned to multiple orders - please resolve')
#         sys.exit()
#     if DEVICETYPE=='PPCL700':configuration=DB.getorder(orderid[0][0])[0]
#     if DEVICETYPE=='PPCL600': configuration=(orderid[0][0],orderid[0][1],orderid[0][2],orderid[0][3],1,orderid[0][4],orderid[0][5],orderid[0][6],orderid[0][7],orderid[0][8],orderid[0][9],orderid[0][10],orderid[0][11],orderid[0][12],orderid[0][13],0,orderid[0][14],0,0,0,0,0,orderid[0][15],'','','',0,1,'changedate')


def PPEB250(serial,configuration)    :
    global LABELWIDTH, LABELHEIGHT,draw
    LABELWIDTH=8*int((2.0*203)/8.0)
    LABELHEIGHT=8*int(3.0*203/8.0)
    size = [LABELWIDTH, LABELHEIGHT] #maximum widht 34mm is 454 points
    img = Image.new("L", size, 255)
    draw = ImageDraw.Draw(img)
    #logo
    imglogo = Image.open('Support\\Pure Photonics logo BW.png')  # load base image
    scaling=1.2
    newSize = (int(imglogo.size[0]*scaling), int(imglogo.size[1]*scaling)) # new size will be 500 by 300 pixels, for example
    imglogo1=imglogo.resize(newSize, resample=PIL.Image.BILINEAR) # you can choose other :resample: values to get different quality/speed results
    logocenter=LABELWIDTH/6
    logowidth=imglogo1.size[0]
    draw.bitmap((LABELWIDTH/2-imglogo1.size[0]/2,10),imglogo1,fill=0)
    #header
    place_text_center(LABELWIDTH/2,370,3,'Mounting Plate')
    #partnumber
    place_text_center(LABELWIDTH/2,450,4,'PPEB250')
     
    
    #img.show()
    img.save('logfiles\\PPEB250label.png')
    del draw
    
    create_Zebra('logfiles\\PPEB250label','PPEB250.txt')

def small_label(serial,configuration)    :
    global LABELWIDTH, LABELHEIGHT,draw
    LABELWIDTH=8*int((2.0*203)/8.0)
    LABELHEIGHT=8*int(3.0*203/8.0)
    size = [LABELWIDTH, LABELHEIGHT] #maximum widht 34mm is 454 points
    img = Image.new("L", size, 255)
    draw = ImageDraw.Draw(img)
    #logo
    imglogo = Image.open('Support\\Pure Photonics logo BW.png')  # load base image
    scaling=1.2
    newSize = (int(imglogo.size[0]*scaling), int(imglogo.size[1]*scaling)) # new size will be 500 by 300 pixels, for example
    imglogo1=imglogo.resize(newSize, resample=PIL.Image.BILINEAR) # you can choose other :resample: values to get different quality/speed results
    logocenter=LABELWIDTH/6
    logowidth=imglogo1.size[0]
    draw.bitmap((LABELWIDTH/2-imglogo1.size[0]/2,10),imglogo1,fill=0)
    #header
    place_text_center(LABELWIDTH/2,370,3,'Tunable Laser Module')
    #partnumber
    place_text_center(LABELWIDTH/2,450,5,str(configuration[7]))
    #Serial
    place_text_center(LABELWIDTH/2,530,5,str(kv.serial()))
     
     
    
    #img.show()
    img.save('logfiles\\FoamSmallLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.png')
    del draw
    
    create_Zebra('logfiles\\FoamSmallLabel_'+str(kv.serial())+'_'+str(calc.timestamp()),'SmallfoamLabel.txt')
    
    
def outside_label(serial,configuration) :   
    global LABELWIDTH,LABELHEIGHT,draw
    LABELWIDTH=8*int((6.0*203)/8.0)
    LABELHEIGHT=8*int(3.0*203/8.0)
    size = [LABELWIDTH, LABELHEIGHT] #maximum widht 34mm is 454 points
    img = Image.new("L", size, 255)
    draw = ImageDraw.Draw(img)
    #logo
    imglogo = Image.open('Support\\Pure Photonics logo BW.png')  # load base image
    scaling=1.3
    newSize = (int(imglogo.size[0]*scaling), int(imglogo.size[1]*scaling)) # new size will be 500 by 300 pixels, for example
    imglogo1=imglogo.resize(newSize, resample=PIL.Image.BILINEAR) # you can choose other :resample: values to get different quality/speed results
    logocenter=LABELWIDTH/6
    logowidth=imglogo1.size[0]
    draw.bitmap((LABELWIDTH/6-imglogo1.size[0]/2,50),imglogo1,fill=0)
    #header
    place_text_left(LABELWIDTH/3,50,0,'Low Noise Tunable Laser (micro-ITLA)',True)
    #draw.line((LABELWIDTH/3,75,LABELWIDTH*5/6,75),width=3)
    #manufacturer
    place_text_left(LABELWIDTH/3,150,1,'Manufacturer')
    draw.text((LABELWIDTH*7/12,150),'Pure Photonics',font=fonts[1],fill=0)
    #partnumber
    draw.text((LABELWIDTH/3,225),'Part number',font=fonts[1],fill=0)
    draw.text((LABELWIDTH*7/12,225),str(configuration[7]),font=fonts[1],fill=0)
    #Mfg date
    draw.text((LABELWIDTH/3,300),'Mfg data',font=fonts[1],fill=0)
    if kv.serial()[0:4]=='CRTM':
        tempM=int(input('Mfg Date Month? '))
        tempD=int(input('Mfg Date Day? '))
        tempY=int(input('Mfg Date Year? '))
        if tempY<2000: tempY=tempY+2000
        temptime=datetime.datetime(tempY, tempM, tempD)
    else: temptime=datetime.datetime.today()
    draw.text((LABELWIDTH*7/12,300),"{:%d %B %Y}".format(temptime),font=fonts[1],fill=0)
    #Serial
    draw.text((LABELWIDTH/3,375),'Serial Number',font=fonts[1],fill=0)
    draw.text((LABELWIDTH*7/12,375),str(kv.serial()),font=fonts[1],fill=0)
    #1M warning
    draw.text((LABELWIDTH/3,500),'Class 1M Laser Product - Complies with FDA performance standards for laser',font=fonts[2],fill=0)
    draw.text((LABELWIDTH/3,530),'products except for deviations pursuant to laser notics No. 50, dated June 2007',font=fonts[2],fill=0)
    draw.text((LABELWIDTH/3,560),'Pure Photonics LLC, 830 Hillview Court, Suite 255, Milpitas, CA-95035, USA',font=fonts[2],fill=0)
    #USA assembled
    place_text_center(LABELWIDTH*7/12,470,3,'Assembled in the USA')
    #e0
    refy=450
    refx=logocenter-logowidth/4
    circleradius=40
    place_text_center(refx,refy,0,'e0')
    draw.arc(((refx-circleradius,refy-circleradius),(refx+circleradius,refy+circleradius)),0,360,fill=0,width=3)
    #ce
    imglogo = Image.open('Support\\ce-mark-small.png')  # load base image
    draw.bitmap((logocenter+logowidth/4-imglogo.size[0]/2,refy-imglogo.size[1]/2),imglogo,fill=0)
    #barcpde
    
    test_writer=ImageWriter()
    #test_writer.set_options(mode='RGBA')
    ean = barcode.get_barcode('Code128', str(kv.serial()), writer=test_writer)
    filename = ean.save('barcode.png',options={"write_text": False})
    imglogo1 = Image.open(filename)
    newSize = (int(imglogo1.size[0]), int(imglogo1.size[1]*0.33)) # new size will be 500 by 300 pixels, for example
    imglogo=imglogo1.resize(newSize, resample=PIL.Image.NEAREST) # yo
    #imglogo.convert('RBGA')  # load base image
    imglogo.putalpha(255)
    datas=imglogo.getdata()
    newData=[]
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255: 
            newData.append((255,255,255,0))
        else:
            newData.append(item)
    imglogo.putdata(newData)
    imglogo2=imglogo.rotate(90,expand=True)
    #imglogo.Rotation = Image.Rotation.Rotate90;
    draw.bitmap((LABELWIDTH-imglogo2.size[0]-50,LABELHEIGHT/2-imglogo2.size[1]/2),imglogo2,fill=0)
    
     
    
    #img.show()
    img.save('logfiles\\FoamShellLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.png')
    del draw
    
    create_Zebra('logfiles\\FoamShellLabel_'+str(kv.serial())+'_'+str(calc.timestamp()),'LargefoamLabel.txt')

#outside_label()
#small_label()
#shutil.copyfile('logfiles\\EnclosureLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.bin', FL.PtouchLocation())



# if temp9.upper()!='M':
#     supply.TurnOff()
#     supply.Disconnect()


#input('wait for enter')




