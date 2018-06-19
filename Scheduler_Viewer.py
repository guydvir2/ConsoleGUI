import gpiozero
from gpiozero import OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from tkinter import *
from tkinter import ttk
import socket
import urllib.request

class HWRemoteOutput:

#This Class creates Hardware state of ""gpio_pins"" of RPi at "ip"
    def __init__(self, ip, output_pins):
        factory = PiGPIOFactory(host=ip)
        self.output_pins= ["Pin_"+str(output_pins[i]) for i in range(len(output_pins))]
        for sw in range(len(self.output_pins)):
            self.output_pins[sw] = OutputDevice(output_pins[sw], pin_factory=factory,initial_value=False)

    #Make the switch
    def set_state(self, sw, state):
        if sw >len(self.output_pins):
            print("No such Switch")
        if state == "on":
            self.output_pins[sw].on()
        elif state == "off":
            self.output_pins[sw].off()

    #Inquiry
    def get_state(self):
        stat=[]
        for sw in range(len(self.output_pins)):
            stat.append([sw, self.output_pins[sw].value])
        return stat


class HWRemoteInput:
    #This class create a link between input_pins(HW buttons) to output pins
    def __init__(self, master, ip, input_pins):
        self.master = master
        factory = PiGPIOFactory(host=ip)

        self.input_pins= ["Pin_"+str(input_pins[i]) for i in range(len(input_pins))]
        for sw in range(len(self.input_pins)):
            self.input_pins[sw] = gpiozero.Button(input_pins[sw], pin_factory=factory)
            self.input_pins[sw].when_pressed = lambda arg=sw :self.pressed(arg)

    #Detect press and make switch
    def pressed(self,i):
        if str(self.master.output_HardWare.get_state()[i][1]) == 'False':
            state='on'
        else:
            state="off"
        #make an output switch
        self.master.output_HardWare.set_state(i,state)


    def get_state(self):
        stat=[]
        for sw in range(len(self.input_pins)):
            stat.append([sw, self.input_pins[sw].value])
        return stat


class HWstateGUI:
    #This Class create GUI indicators of HW state of "gpio_pins" "Red/Green" + "On/Off" text
    def __init__(self,master, gpio_pins,xspace=40,switch_names=[],ip=[]):
        self.master = master
        self.gpio_pins = gpio_pins

        if switch_names==[]:
            switch_names=['Switch'+str(i) for i in range(len(gpio_pins))]
        self.build_gui(xspace, switch_names, ip)


    def build_gui(self,xspace, switch_names, ip):
        self.frame = ttk.Frame(self.master, padding=10)
        self.indicators = []
        self.frame.grid()

        for i in range(len(self.gpio_pins)):
            txtvar = StringVar()
            txtvar.set("null")
            indicator_label = ttk.Label(self.frame, width=10, textvariable=txtvar, relief=SUNKEN, border=3)
            indicator_label.grid(row=0, column=i, padx=xspace)
            self.indicators.append([indicator_label,txtvar])
            indicator_name=ttk.Label(self.frame, text=switch_names[i])
            indicator_name.grid(row=1, column=i, pady=5)

        ip_label = ttk.Label(self.frame,text="IP of Remote GPIO: %s"%ip)
        ip_label.grid(row = 2, columnspan = 5, sticky = E+W)


    def get_state(self, state_list):
        for i in range(len(state_list)):
            if str(state_list[i][1]) == "True":
                bg1='Green.TLabel'
                text1="ON"
            elif str(state_list[i][1]) == "False":
                bg1="Red.TLabel"
                text1="OFF"
            self.indicators[i][0].configure(style=bg1)
            self.indicators[i][1].set(text1)


class SFButtonsGUI:
    def __init__(self, master, frame, num_of_buttons):
        self.master = master
        self.status = []
        self.buts = []
        self.leds = []
        bg_window = "DeepSkyBlue4"
        self.framein = ttk.Frame(frame)
        self.framein.grid(padx=5, pady=5)
        self.build_gui(num_of_buttons)
        for t in range(num_of_buttons):
            self.switch(t,'off')

        #self.switch()

    def build_gui(self, num_of_buttons):
        #Create Widgets of buttons
        for i in range(num_of_buttons):
            button_var = StringVar()
            entry_var = IntVar()
            led_var = StringVar()

            led = ttk.Label(self.framein, textvariable=led_var, width=3, border=3 ,relief="ridge")
            led_var.set(" ")
            led.grid(row=0, column=i, pady=0, sticky=W)


            c = ttk.Checkbutton(self.framein, text="Switch " + str(i), variable=button_var,width=8, onvalue="on", offvalue="off",command=lambda arg=[i, button_var, entry_var]: self.cb(arg))
            c.grid(column=i, pady=5, padx=30, row=0, sticky=E)
            button_var.set("off")

            ent = ttk.Entry(self.framein, textvariable=entry_var, width=3, justify="center")
            ent.grid(column=i, row=1)
            mins = ttk.Label(self.framein, text="off timer:", width=7, justify="center")
            mins.grid(column=i, row=1, sticky=W)

            self.status.append([button_var, led_var, entry_var])
            self.buts.append(c)
            self.leds.append(led)


    def switch(self,num,state):
        if state=='on':
            stl='Green.TLabel'
        if state=='off':
            stl='Red.TLabel'

        self.leds[num].configure(style=stl)
        self.status[num][1].set(state)


    def cb(self, but, state='', a=''):
        # but = [ switch#, switch state, delay] ## explanatory
        #
        ##In use only in CB_DELAYED
        if state != '':
            but[1].set(state)

        self.switch(but[0],but[1].get())

        if not but[2].get()==0 and but[1].get() == "on":
            a = ", Auto shutdown in %s minutes." % (but[2].get())
            self.switch(but[0],but[1].get())
            print("Delayed", but[1].get())
            self.cb_delayed(but)
        else:
            self.switch(but[0],but[1].get())
        self.master.output_HardWare.set_state(but[0],but[1].get())


    def cb_delayed(self, but):
        self.framein.after(but[2].get() * 1000, self.cb, but, "off")


class SplashWindow(Toplevel):
    def __init__(self,master,bg):
        Toplevel.__init__(self, master)
        self.master = master
        splash_style = ttk.Style()
        self.title(app_name)
        splash_style.theme_use('clam')
        self.configure(background=bg)
        splash_style.configure('Title.TLabel',font=('Helvetica',14),foreground="midnight blue")
        splash_style.configure('.',background=bg)

        self.build_gui()

    def build_gui(self):
        frame1 = ttk.Frame(self, padding=5)
        frame1.grid(pady=10)
        frame2 = ttk.Frame(self, padding=10, relief=SUNKEN)
        frame2.grid(row=1, column=0, pady=10,padx=10)
        ypad=10
        self.checks=[]

        header1 = ttk.Label(frame1, text=app_name+"Viewer", style='Title.TLabel')
        header1.grid(row=0, column=0)
        header2 = ttk.Label(frame1, text="Enter IP of station, and select GUI components", justify=CENTER)
        header2.grid(row=1, column=0)

        local_ip=self.get_ip()[0]

        ip_label = ttk.Label(frame2, text="Enter IP:")
        ip_label.grid(row=0, column=0)
        ent_var=StringVar()
        ent_var.set(local_ip)
        ip_entry= ttk.Entry(frame2, textvariable= ent_var, width=12)
        ip_entry.grid(row=0, column=1, pady=ypad)

        c1_var=IntVar()
        c1_var.set(1)
        c1 = ttk.Checkbutton(frame2, text="Buttons", variable=c1_var)
        c1.grid(row=0, column=2, pady =ypad)

        c2_var=IntVar()
        c2_var.set(0)
        c2 = ttk.Checkbutton(frame2, text="Input State",variable=c2_var)
        c2.grid(row=0, column=3)

        c3_var=IntVar()
        c3_var.set(1)
        c3 = ttk.Checkbutton(frame2, text="Output State",variable=c3_var)
        c3.grid(row=0, column=4)

        but1 = ttk.Button(frame2,text="Continue", command=self.close_window)
        but1.grid(row=2, column=4)
        but2 = ttk.Button(frame2,text="Abort", command=self.master.destroy)
        but2.grid(row=2, column=3)
        self.checks.append([ent_var,c1_var,c2_var,c3_var])

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal_ip=s.getsockname()[0]
        s.close()
        external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')

        return internal_ip, external_ip

    def close_window(self):
        global var
        var=self.checks[0]
        self.destroy()


class ContorlGPIOWindow:
    def __init__(self,master,bg, ip='', output_pins=[13,17,6,26],input_pins = [21,4,5,27],with_sf_bt=0 , with_hw_bt=0,with_hw_st=1, switch_names=[]):

        self.master = master
        if ip == '':
            ip = self.get_ip()[0]
        self.styles(bg)
        self.master.config(bg=bg)

        #This value from popup window
        if with_hw_st == 1:
            self.create_output(ip, output_pins, switch_names)
        if with_hw_bt == 1:
            self.create_input(ip, input_pins, switch_names)
        if with_sf_bt == 1:
            self.create_SFButtons(output_pins)

        self.update_gui()

    def create_output(self, ip, output_pins, switch_names):
        frame1= ttk.LabelFrame(self.master,text='Hardware OutPut State',padding = 8)
        frame1.grid(row = 0, column= 0, padx=20, pady=20)
        self.output_HardWare = HWRemoteOutput(ip, output_pins)
        self.output_GUI = HWstateGUI(frame1, output_pins,switch_names=switch_names,ip=ip)

    def create_input(self, ip, input_pins, switch_names):
        frame2= ttk.LabelFrame(self.master,text='Hardware Input State',padding = 8)
        frame2.grid(row = 1, column= 0, padx=20, pady=20)
        self.input_HardWare = HWRemoteInput(self, ip, input_pins)
        self.input_GUI = HWstateGUI(frame2,input_pins,ip=ip)

    def create_SFButtons(self, output_pins):
        frame3= ttk.LabelFrame(self.master, text="Software Buttons")
        frame3.grid(row = 2, column = 0, pady = 20)
        self.SFButs = SFButtonsGUI(self, frame3,len(output_pins))


    def styles(self,bg):
        bg_labelframe = bg
        style=ttk.Style()
        style.theme_use('default')
        style.configure('TLabel', anchor=CENTER, font=('Times', 10))
        style.configure('Green.TLabel',background="green", forground='black')
        style.configure('Red.TLabel',background="red", foreground='black')
        style.configure('TLabelframe',background=bg_labelframe)
        style.configure('.',background=bg_labelframe)


    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal_ip=s.getsockname()[0]
        s.close()
        external_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')

        return internal_ip, external_ip


    def update_gui(self):
        try:
            self.output_GUI.get_state(self.output_HardWare.get_state())
        except: AttributeError

        try:
            self.input_GUI.get_state(self.input_HardWare.get_state())
        except: AttributeError

        root.after(500,self.update_gui)


root = Tk()
root.withdraw()
app_name = 'Schduler Plus'
backg_color = 'whitesmoke'
var=[]
#output_gpioPins = [4,22,6,26] #input_gpioPins = [3,21,5,27]
RPis={"ChildRoom Window":'192.168.2.112',"Parents Room Window":'192.168.2.113',"LivingRoom Window":'192.168.2.114'}
splash = SplashWindow(root,backg_color)
root.wait_window(splash)

App = ContorlGPIOWindow(root,backg_color, ip = var[0].get(), with_sf_bt=var[1].get(), with_hw_bt=var[2].get(), with_hw_st= var[3].get(), switch_names=['Light Kitchen','Light Room1', 'Window1', 'Window2'])

root.deiconify()
root.mainloop()
