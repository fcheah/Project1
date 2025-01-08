from PIL import Image, ImageDraw, ImageFont
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

LABELWIDTH=360#454

fonts =    [ ImageFont.truetype('arialbd.ttf', 53), ImageFont.truetype('arialbd.ttf', 50), ImageFont.truetype('arial.ttf', 30), ImageFont.truetype('arial.ttf',20)]
draw=None
# PORT=calc.COMPORT()

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

def place_text_left(x,y,fontid,tekst,underline=False):
    global draw
    w,h=fonts[fontid].getsize(tekst)
    draw.text((x,y-h/2),tekst,font=fonts[fontid],fill=0)
    if underline:
        draw.line((x,y+h/2,x+w,y+h),width=3)

def place_text_right(x,y,fontid,tekst,underline=False):
    global draw
    w,h=fonts[fontid].getsize(tekst)
    draw.text((x-w,y-h/2),tekst,font=fonts[fontid],fill=0)
    if underline:
        draw.line((x-w,y+h,x,y+h),width=3)
    
def place_text_center(x,y,fontid,tekst):
    global draw
    w,h=fonts[fontid].getsize(tekst)
    draw.text((x-w/2,y-h/2),tekst,font=fonts[fontid],fill=0)

def enclosure_label(serial,configuration):
    global draw
    size = [LABELWIDTH, 800] #maximum widht 34mm is 454 points
    img = Image.new("L", size, 255)
    draw = ImageDraw.Draw(img)
    #logo
    imglogo = Image.open('Support\\Pure Photonics logo BW.png')  # load base image
    draw.bitmap((75,15),imglogo,fill=0)
    #partnumber
    place_text_center(LABELWIDTH/2,400,0,str(configuration[7]))
    #Serialnumber
    place_text_center(LABELWIDTH/2,490,0,str(serial))
    #frequency
    place_text_center(LABELWIDTH/2,550,2,'%.2f - %.2f THz' %(float(configuration[9]),float(configuration[10])))
    #frequency
    place_text_center(LABELWIDTH/2,590,2,'7.0 - %.1f dBm'%(float(configuration[8])))
    #1M warning
    place_text_center(LABELWIDTH/2,630,2,'Class 1M Laser Product')
    #USA assembled
    place_text_center(LABELWIDTH/2,680,2,'Assembled')
    place_text_center(LABELWIDTH/2,710,2,'in the USA')
    #e0
    place_text_center(LABELWIDTH-55,695,1,'e0')
    draw.arc(((LABELWIDTH-90,660),(LABELWIDTH-20,730)),0,360,fill=0,width=3)
    #ce
    imglogo = Image.open('Support\\ce-mark-small.png')  # load base image
    draw.bitmap((15,665),imglogo,fill=0)
    #date
    place_text_center(LABELWIDTH/2,760,2,"{:%d %B %Y}".format(datetime.datetime.today()))
    #inputs
    #AM
    portcount=0
    #1cm between ports 360 dots per inch; 142 per cm
    if (configuration[17]>0 or configuration[18]>0 )and configuration[7][0:6]=='PPCL55' :
        draw.text((8,portcount*142+20),'AMP',font=fonts[3],fill=0)
        draw.text((8,portcount*142+40),'MOD',font=fonts[3],fill=0)
        portcount=portcount+1
    if configuration[19]>0 and configuration[7][0:6]=='PPCL55':
        draw.text((8,portcount*142+20),'FREQ',font=fonts[3],fill=0)
        draw.text((8,portcount*142+40),'MOD',font=fonts[3],fill=0)
        portcount=portcount+1
    if configuration[20]>0 and configuration[7][0:6]=='PPCL55':
        draw.text((8,portcount*142+20),'ANLG',font=fonts[3],fill=0)
        if configuration[20]>0:
            draw.text((8,portcount*142+40),'IN1',font=fonts[3],fill=0)
        else:
            draw.text((8,portcount*142+40),'IN ',font=fonts[3],fill=0)
        portcount=portcount+1
    if configuration[21]>0 and configuration[7][0:6]=='PPCL55':
        draw.text((8,portcount*142+20),'ANLG',font=fonts[3],fill=0)
        draw.text((8,portcount*142+40),'IN2',font=fonts[3],fill=0)
        portcount=portcount+1    
    if configuration[22]>0 and configuration[7][0:6]=='PPCL55':
        draw.text((8,portcount*142+20),'ANLG',font=fonts[3],fill=0)
        draw.text((8,portcount*142+40),'OUT ',font=fonts[3],fill=0)
        portcount=portcount+1    
    
    #img.show()
    img.save('logfiles\\EnclosureLabel_'+str(serial)+'_'+str(calc.timestamp())+'.png')
    del draw
    ptouch.convert_to_label('logfiles\\EnclosureLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.png',36,800,'EnclosureLabel.bin')

# temp=input('Send to printer (Y/N) ? ')
# if temp.upper()=='Y':
#     ptouch.convert_to_label('logfiles\\EnclosureLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.png',36,720)
#     shutil.copyfile('logfiles\\EnclosureLabel_'+str(kv.serial())+'_'+str(calc.timestamp())+'.bin', FL.PtouchLocation())

# if temp9.upper()!='M':
#     supply.TurnOff()
#     supply.Disconnect()


# input('wait for enter')




