import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from mqtt_init import *
import requests




import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import ssl



#from PyQt5.QtCore import QTimer

# Creating Client name - should be unique 
global clientname, CONNECTED, we_current
CONNECTED = False
r=random.randrange(1,10000000)
clientname="IOT_client-Id234-"+str(r)
DHT_topic = 'IoT/final_project/alex_lir_kesem'
update_rate = 5000 # in msec
we_current = 5000

class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic=''
        self.port='' 
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        
    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self,value):
        self.broker= value         
    def get_port(self):
        return self.port
    def set_port(self,value):
        self.port= value     
    def get_clientName(self):
        return self.clientName
    def set_clientName(self,value):
        self.clientName= value        
    def get_username(self):
        return self.username
    def set_username(self,value):
        self.username= value     
    def get_password(self):
        return self.password
    def set_password(self,value):
        self.password= value         
    def get_subscribeTopic(self):
        return self.subscribeTopic
    def set_subscribeTopic(self,value):
        self.subscribeTopic= value        
    def get_publishTopic(self):
        return self.publishTopic
    def set_publishTopic(self,value):
        self.publishTopic= value         
    def get_publishMessage(self):
        return self.publishMessage
    def set_publishMessage(self,value):
        self.publishMessage= value 
        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        if rc==0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form();            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        CONNECTED = False
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class        
        self.client = mqtt.Client(self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)        
        print("Connecting to broker ",self.broker)        
        self.client.connect(self.broker,self.port)     #connect to broker
    
    def disconnect_from(self):
        self.client.disconnect()                   
    
    def start_listening(self):        
        self.client.loop_start()        
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connecection should be established first")         
        
              
    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic,message)
        else:
            print("Can't publish. Connecection should be established first")            
      
class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self,mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        #self.mc.set_on_disconnect_to_form(self.disconnected)
        self.eHostInput=QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
        self.ePort=QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID=QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName=QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword=QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive=QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL=QCheckBox()
        
        self.eCleanSession=QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn=QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")

        self.Cutoff=QPushButton("Disable connect" , self)
        self.Cutoff.setToolTip("click me to stop")
        self.Cutoff.clicked.connect(self.on_button_disconnect_click)
        self.Cutoff.setStyleSheet("background-color: gray")


        
        self.ePublisherTopic=QLineEdit()
        self.ePublisherTopic.setText(DHT_topic)

  
        self.Weight=QLineEdit()
        self.Weight.setText('')

        

        formLayot=QFormLayout()       
        formLayot.addRow("Turn On",self.eConnectbtn)
        formLayot.addRow("Turn Off", self.Cutoff)
        formLayot.addRow("Pub topic",self.ePublisherTopic)
        formLayot.addRow("Weight",self.Weight)
        # formLayot.addRow("Humidity",self.Humidity)
        # self.turn_off_button2 = QPushButton("Turn Off 2")
        # formLayot.addRow("Turn Off 2", self.turn_off_button2)
        # self.setLayout(formLayot)



        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
        self.Weight.setEnabled(True)  # מאפשר עריכה בשדה המשקל




        

                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        self.Weight.setEnabled(True)  # מאפשר עריכה בשדה המשקל






    def on_button_disconnect_click(self):
        try:
            if hasattr(self, 'client'):  # בדיקה אם האובייקט קיים
                self.mc.stop_listening()  # עצירת האזנה ל-MQTT
                self.mc.disconnect_from()
                self.Cutoff.setText("Reconnect")  # שינוי טקסט הכפתור
                self.Cutoff.setEnabled(False)  # השבתת הכפתור

            else:
                print("No connection to disconnect.")
        except AttributeError:
            print("Error disconnecting: client object not found.")
        

    def push_button_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":1')
     
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate) # in msec
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 600, 300, 150)
        self.setWindowTitle('Gas weight')        

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

    def update_data(self):
        global we_current
        print('Next update')
        we_current=we_current-random.randrange(1,10)/10
        threshold = 4990
        if(we_current > 4990):

            bot_token= "7327997608:AAFUFrsXXkufPwaGKEVTtxGPVQoc4VeTn4w"
            chat_id = "718108373"
            message = f"הערך הנוכחי {we_current} חרג מהסף {threshold}."
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            params = {"chat_id": chat_id, "text": message}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                print("send massege to telegram")
            else:
                print("no send massege to telegtram:", response.text)

            
            # message = MIMEMultipart()
            # email_sender= "temp@gmail.com"
            # email_password = os.environ.get("EMAIL_PASWWORD")
            # receiver_email = "alexanderno@my.hit.ac.il"

            # subject = "התראה! ערך חרג מהסף"
            # body = """
            # "הערך הנוכחי הוא: {we_current}. חרג מהסף המוגדר."
            # """
            # em = EmailMessage()
            # em["from"] = email_sender
            # em["To"] = receiver_email
            # message["Subject"] = subject
            
            # em.set_content(body)
            # context= ssl.create_default_context()
            # context.verify_mode = ssl.CERT_NONE
            # context.check_hostname = False
            # with smtplib.SMTP_SSL('smtp.gmail.com', 465, context= context) as smtp:
            #     smtp.login(email_sender, email_password)
            #     smtp.sendmail(email_sender, receiver_email , em.as_string())


        current_data='Weight: '+str(we_current)
        self.connectionDock.Weight.setText(str(we_current))        
        self.mc.publish_to(DHT_topic,current_data)
        


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()

