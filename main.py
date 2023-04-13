from kivy.app import App
from kivy.base import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, FadeTransition,SwapTransition, NoTransition
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import json
import os

import bluetooth


#Bluetooth code from line 194 to 269
#There are 3 important methods for sending with PyBluez:
#Connect, Send, and disconnect
#The more generic code is commented, other code only applies to this app



class blankPage(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class welcomePage(Widget):
    
    okButton = ObjectProperty(None)

    def okPressed(self):
        controlApp.screen_manager.current='settingsPage'

class settingsInfoPage(Widget):
    def switchToControlPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'up')
        controlApp.screen_manager.current = 'controlPage'
    def switchToSettingsPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'up')
        controlApp.screen_manager.current = 'settingsPage'
    def switchToControlInfoPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'right')
        controlApp.screen_manager.current = 'controlInfoPage'

class controlInfoPage(Widget):
    instructions = """1. Connect to your RoboRoller using the connect button.
    This will connect it via Bluetooth.\nBefore connecting through the app, you must
    connect to your RoboRoller through Bluetooth settings of your device.\n
    2. Create a sequence/queue of commands by clicking the arrows.
    Each command corresponds to a movement the robot will make.
    You can view your command queue in the upper right corner.
    You can have a maximum of 35 commands.
    If you want to delete the last command in the list, click the backspace button.
    To delete all your commands, click the garbage can at the bottom.\n
    3. When you are read to run your program, click the play button.\n
    4. You can disconnect from your RoboRoller at any time and change settings as well.
    """
    def switchToControlPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'up')
        controlApp.screen_manager.current = 'controlPage'
    def switchToSettingsPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'up')
        controlApp.screen_manager.current = 'settingsPage'
    def switchToSettingsInfoPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'left')
        controlApp.screen_manager.current = 'settingsInfoPage'


class settingsPage(Widget):
    speedSlider = ObjectProperty(None)
    distanceSlider = ObjectProperty(None)
    trimSlider = ObjectProperty(None)
    lightOn = ObjectProperty(None)
    turnTimeSlider = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            with open(controlApp.settings_filename, 'r') as file_object:
                self.settings = json.load(file_object)
            self.speedSlider.value = self.settings[0]
            self.distanceSlider.value = self.settings[1]
            self.trimSlider.value = self.settings[2]
            self.lightOn.state = self.settings[3]
            self.turnTimeSlider.value = self.settings[4]
        except FileNotFoundError:
            pass

    def switchToControlPage(self, *clock):
        controlApp.screen_manager.transition = SwapTransition(duration= 0.7)
        controlApp.screen_manager.current = 'controlPage'

    def switchToSettingsInfoPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'down')
        controlApp.screen_manager.current = 'settingsInfoPage'
        self.saveData()

    def resetTrim(self, *event):
        self.trimSlider.value = 0

    def saveButtonPressed(self):
        self.saveData()        
        Clock.schedule_once(self.switchToControlPage, 0.5)
    
    def saveData(self, *clock):
        self.settings = [int(self.speedSlider.value), int(self.distanceSlider.value), int(self.trimSlider.value), self.lightOn.state, int(self.turnTimeSlider.value)]#state gives "down" or "up"

        with open(controlApp.settings_filename, 'w') as fileObject:
            json.dump(self.settings, fileObject)

class controlPage(Widget):
    connectionMessage = ObjectProperty(None)
    connectButton = ObjectProperty(None)
    commandsLabel = ObjectProperty(None)
    x_offset = 0.04-0.2
    speedValue = 0
    steerValue = 0
    device_name = "RoboRoller"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self.socket = None
    def forwardButtonPressed(self, *event):
        self.data.append(1)
        self.updateCommands()
    def backwardButtonPressed(self, *event):
        self.data.append(2)
        self.updateCommands()
    def rightButtonPressed(self, *event):
        self.data.append(3)
        self.updateCommands()
    def leftButtonPressed(self, *event):
        self.data.append(4)
        self.updateCommands()
    def spinButtonPressed(self, *event):
        self.data.append(5)
        self.updateCommands()
    
    def updateCommands(self):
        if self.data[len(self.data)-1] == 1:
            self.lastCommand = "Forward"
        if self.data[len(self.data)-1] == 2:
            self.lastCommand = "Backward"
        if self.data[len(self.data)-1] == 3:
            self.lastCommand = "Right"
        if self.data[len(self.data)-1] == 4:
            self.lastCommand = "Left"
        if self.data[len(self.data)-1] == 5:
            self.lastCommand = "Spin"
        if self.commandsLabel.text != "":
            self.commandsLabel.text += ", "
            self.commandsLabel.text += self.lastCommand
        else:
            self.commandsLabel.text = self.lastCommand
        if len(self.data)>35:
            self.connectionMessage.text = "You can only have 35 instructions!\nDeleting!"
            Clock.schedule_once(self.deleteConnectionMessage, 3)
            Clock.schedule_once(self.deleteAllButtonPressed, 3)

    def backspaceButtonPressed(self, *event):
        if len(self.data)>1:
            self.data.pop(len(self.data)-1)
            while self.commandsLabel.text[len(self.commandsLabel.text)-1] != ',':
                self.commandsLabel.text = self.commandsLabel.text[:-1]
            self.commandsLabel.text = self.commandsLabel.text[:-1]
        else:
            self.deleteAllButtonPressed()
    def deleteAllButtonPressed(self, *event):
        self.data = []
        self.commandsLabel.text = ""

    def switchToSettingsPage(self):
        controlApp.screen_manager.transition=SlideTransition(direction = 'left')
        controlApp.screen_manager.current='settingsPage'
    
    def switchToControlInfoPage(self, *event):
        controlApp.screen_manager.transition = SlideTransition(direction= 'down')
        controlApp.screen_manager.current = 'controlInfoPage'

    def infoButtonPressed(self, *event):
        if self.connectButton.text == "CONNECT":
            self.switchToControlInfoPage()
        else:
            self.disconnect()
            self.switchToControlInfoPage()

    def settingsCogPressed(self):
        if self.connectButton.text == "CONNECT":
            self.switchToSettingsPage()
        else:
            self.disconnect()
            self.switchToSettingsPage()

    def connectButtonPressed(self, *instance):
        if self.connectButton.text == "CONNECT":
            self.connectionMessage.text = "Connecting..."
            Clock.schedule_once(self.connect)
        else:
            self.disconnect()

    def connect(self, *instance):
        with open(controlApp.settings_filename, 'r') as file_object:
                self.settings = json.load(file_object)
        self.settingsString = ""
        self.settingsString += str(self.settings[0])
        self.settingsString += "," 
        self.settingsString += str(self.settings[1])
        self.settingsString += ","
        self.settingsString += str(self.settings[2])
        self.settingsString += "," 
        if(self.settings[3] == 'down'):
            self.settingsString += "1,"
        else:
            self.settingsString += "0,"
        self.settingsString += str(self.settings[4])

        #Important code below
        nearby_devices = bluetooth.discover_devices()#Get a list of nearby devices (Those that are connected in settings)
        self.device_found = False
        try:
            for device in nearby_devices:
                name = bluetooth.lookup_name(device)
                if name == self.device_name:#If the device with the specified name is found, connect to it.
                    self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.socket.connect((device, 1))
                    self.device_found = True#If the device is not found, a different loop runs later.  This is not necessary if you don't want an error message or something like that
                    #End of generic code for connect

                    self.send_mode = Clock.schedule_interval(self.set_mode_and_settings, 0.07)
                    Clock.schedule_once(self.start_dataflow, 2)
                    self.connectionMessage.text = "Connected Successfully!"
                    self.connectButton.text = "DISCONNECT"
                    Clock.schedule_once(self.deleteConnectionMessage, 15)
                    break

        except OSError:
            self.deleteConnectionMessage()
            controlApp.screen_manager.transition = SwapTransition(duration = 1)
            controlApp.screen_manager.current = 'connectionErrorPage'

        if self.device_found == False:
            self.deleteConnectionMessage()
            controlApp.screen_manager.transition = SwapTransition(duration = 1)
            controlApp.screen_manager.current = 'connectionErrorPage'

    def send_data(self, *clock):
        self.dataString = ""
        for command in self.data:
            self.dataString += str(command)
            self.dataString += ","

        #Important code below

        if self.socket is not None:
            #print(self.dataString)
            self.dataString = "    " + self.dataString[0:(len(self.dataString)-1)] + ";"
            try:
                self.socket.send(self.dataString.encode())
            except OSError:
                self.disconnect()
                self.connectionMessage.text = "ERROR:\nRoboRoller Disconnected"
                Clock.schedule_once(self.deleteConnectionMessage, 5)

            #End of important code in this method

    #Important disconnect method
    def disconnect(self, *instance):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
            #End of important code

        self.connectButton.text = "CONNECT"

    def set_mode_and_settings(self, *clock):
        if self.socket is not None:
            self.mode_and_settings = "   1089,"
            self.mode_and_settings += self.settingsString
            self.mode_and_settings += ";"
            try:
                self.socket.send(self.mode_and_settings.encode())
            except OSError:
                self.disconnect()
                self.deleteConnectionMessage()
                controlApp.screen_manager.transition = SwapTransition(duration = 1)
                controlApp.screen_manager.current = 'connectionErrorPage'

    def start_dataflow(self, *clock):
        self.send_mode.cancel()

    def runButtonPressed(self, *event):
        if self.socket is not None:
            if self.data != []:
                self.send_data()
            else:
                self.connectionMessage.text = "No commands added to queue!"
                Clock.schedule_once(self.deleteConnectionMessage, 3)
        else:
            self.connectionMessage.text = "Please connect before running commands."
            Clock.schedule_once(self.deleteConnectionMessage, 3)

    def deleteConnectionMessage(self, *clock):
        self.connectionMessage.text = ""
            
class connectionErrorPage(Widget):

    def goBack(self, *event):
        controlApp.screen_manager.transition = SwapTransition(duration = 1)
        controlApp.screen_manager.current = 'controlPage'

class RCcontrollerApp(App):

    settings_filename = 'RCCarControllerSettingsDesktop.json'
    
    def build(self):
        Builder.load_file("RCcontrol.kv")
        self.settingsExist = os.path.exists(self.settings_filename)
        self.screen_manager = ScreenManager()

        self.blankPage = blankPage()
        self.screen = Screen(name = 'blankPage')
        self.screen.add_widget(self.blankPage)
        self.screen_manager.add_widget(self.screen)


        self.welcomePage = welcomePage()
        self.screen = Screen(name = 'welcomePage')
        self.screen.add_widget(self.welcomePage)
        self.screen_manager.add_widget(self.screen)

        self.settingsInfoPage = settingsInfoPage()
        self.screen = Screen(name = 'settingsInfoPage')
        self.screen.add_widget(self.settingsInfoPage)
        self.screen_manager.add_widget(self.screen)

        self.controlInfoPage = controlInfoPage()
        self.screen = Screen(name = 'controlInfoPage')
        self.screen.add_widget(self.controlInfoPage)
        self.screen_manager.add_widget(self.screen)

        self.settingsPage = settingsPage()
        self.screen = Screen(name = 'settingsPage')
        self.screen.add_widget(self.settingsPage)
        self.screen_manager.add_widget(self.screen)

        self.controlPage = controlPage()
        self.screen = Screen(name = 'controlPage')
        self.screen.add_widget(self.controlPage)
        self.screen_manager.add_widget(self.screen)

        self.connectionErrorPage = connectionErrorPage()
        self.screen = Screen(name = 'connectionErrorPage')
        self.screen.add_widget(self.connectionErrorPage)
        self.screen_manager.add_widget(self.screen)

        self.screen_manager.transition = NoTransition()
        self.screen_manager.current = 'blankPage'

        Clock.schedule_once(self.start, 0.1)

        
        #Clock.schedule_interval(self.controlPage.printValues, 1)

        return self.screen_manager
    def start(self, *clock):
        self.screen_manager.transition=FadeTransition(duration = 0.4)

        if self.settingsExist:
            self.screen_manager.current='controlPage'
        else:
            self.screen_manager.current='welcomePage'

if __name__=="__main__":
    controlApp = RCcontrollerApp()
    controlApp.run()
