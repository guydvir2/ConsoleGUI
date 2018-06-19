import ButtonLib2
import tkinter as tk
from tkinter import ttk
import readfile_ssh
import datetime




class AllButtons_GUI(ttk.Frame):
    """AllButtons GUI Class"""
    
    def __init__(self,master,mainframe):

        self.master = master
        self.mframe = mainframe
        ttk.Frame.__init__(self, master)
        self.reachable_ips=['192.168.2.113','192.168.2.114','192.168.2.115']
        self.master.write2log("Valid IP's to load:"+str(self.reachable_ips))

        self.reload_all()

    def reload_data_files(self):
        #self.master.save_data_to_file()
        self.master.FileManButs.save_to_file(mat=self.master.ButConfigTable.extract_data_from_gui())
        self.master.read_data_from_files()


    def load_buttons_defs(self):
          
        #keys "hw_in","hw_out","dimension" - get special treatment in next for loop in extracting string values
        self.button_keys=['type','nickname','ip_out','hw_out', 'ip_in', 'hw_in', 'dimension']

        #create KWargs for GUIButtons Read But Defs from file
        self.args=[] # Dict! of loaded buttons definitions.
        for i,but_defs in enumerate(self.master.buts_defs):#.data_from_file:
            #self.button_in_use.append([but_defs[1], but_defs[3], but_defs[8]])
            c,t, temp={},2 ,''
            for m in self.button_keys[1:7]:
                if t == self.button_keys.index('hw_out')+1 or t == self.button_keys.index('hw_in')+1:
                    c[m] = self.master.xtrct_nums(but_defs[t])
                elif t== self.button_keys.index('dimension')+1 :
                    if not but_defs[t] == '':

                        if not self.master.xtrct_nums(but_defs[t])[1] == []:
                             c['height'] = self.master.xtrct_nums(but_defs[t])[1]
                        else:
                            c['height']=''
                            
                        if not self.master.xtrct_nums(but_defs[t])[0] == []:
                            c['width']= self.master.xtrct_nums(but_defs[t])[0]
                        else :
                            c['width']=''

                    else: pass 
                        
                else :  c[m] = but_defs[t]
                t +=1
                
            self.args.append(c) # contains all argument to load button


    def get_sched_defs(self):
        #Import sched file to define button's sched
        dev_names=[] #Alias of device
        off_list = [] # items that are OFF in TimeTable GUI
        for i,current_task in enumerate(self.master.sched_file):
            if current_task[1] == "Off" or not all(current_task[0:6]): off_list.append(i)
            self.sched_vector.append(current_task[3:6])
            self.sched_vector[i][0] = self.master.xtrct_nums(current_task[3])
            dev_names.append(current_task[2])

        #Create a list- including buttons and ALL sched in sched_vector ( multilpe values)
        self.device_list_sched=[] # this list contain index of buttons in sched list
        for x,dev in enumerate(list(set(dev_names))):
            self.device_list_sched.append([dev]) # name of device
            self.device_list_sched[x].append([]) # index
            self.device_list_sched[x].append([]) # sched_vector

            for i, u in enumerate(self.master.sched_file):
                if dev in u and i not in off_list:
                    self.device_list_sched[x][1].append(i)
                    self.device_list_sched[x][2].append(self.sched_vector[i])

        for x,args in enumerate(self.args):
            for t,sched in enumerate(self.device_list_sched):
                if sched[0] in args['nickname']:
                    args['sched_vector'] = self.device_list_sched[t][2]


    def checkFalse_err(self):
        # Fix err in combobox ( if saved as err and not err in current run )
        for i,onoff_box in enumerate (self.master.ButConfigTable.RowClassCreator.all_sched_vars):
            if i in [x[0] for x in self.but_not2load]:
                print("box",i,'set to err')
                self.master.ButConfigTable.RowClassCreator.all_sched_vars[i][8].set('err')
            elif onoff_box[8].get()== 'err' and i not in [x[0] for x in self.but_not2load]:
                print("not err box",i)
                self.master.ButConfigTable.RowClassCreator.all_sched_vars[i][8].set('On')
                self.master.buts_defs[i][8]='On'


    def build_gui(self):
        
        self.buts, x=[], 0
        for l,current_button in enumerate(self.master.buts_defs):
            try:#load button if it in allowed ip list and not off in table
                if current_button[3] in self.reachable_ips:
                    self.buts.append('but_'+str(x))
                    
                    if current_button[8] =='On':
                        self.buts[x] = getattr(ButtonLib2,current_button[1])(self.mainframe, **self.args[l])
                        self.loaded_buts.append([x,self.args[l]['nickname']])
                    else:
                        self.buts[x] = getattr(ButtonLib2,'ErrBut')(self.mainframe,name=current_button[2])
                        self.loaded_buts.append([x,"ErrorBut"])

                    self.buts[x].grid(row=0, column=x)
                    x +=1
            except  ValueError:
                self.master.write2log("Error loading Button"+str(l))
        self.master.write2log("Buttons loaded successfully: "+ str([x[1] for x in self.loaded_buts]))

        ttk.Button(self.mainframe,text="close",command=lambda :self.stop_start_but([0])).grid()
        #  lambda :self.close_spec_button(0))

    def list_buts_to_load(self):
        #loads only buttons complies certain IP as in self.readchable_ips
        self.but2load = [[i, current_but[2], current_but[3]] for i,current_but in enumerate(self.master.buts_defs) if current_but[3] in self.reachable_ips]

        self.but_not2load = [[i, current_but[2], current_but[3]] for i,current_but in enumerate(self.master.buts_defs) if not current_but[3] in self.reachable_ips]

        self.master.write2log("Trying to load:"+str([loaded[1] for i,loaded in enumerate(self.but2load)]))
        self.master.write2log("Not trying to load:"+str([loaded[1] for i,loaded in enumerate(self.but_not2load)]))

    def prep_buttons(self):
        self.reload_data_files()
        self.list_buts_to_load()
        self.checkFalse_err()
        self.reload_data_files()        
        self.load_buttons_defs()
        self.get_sched_defs()
        
    def reload_all(self):
        self.mainframe = ttk.LabelFrame(self.mframe, text="Button")
        self.mainframe.grid(padx=5,pady=5)
        
        self.loaded_buts,self.sched_vector, self.but2load=[], [], []
        
        self.prep_buttons()
        self.build_gui()

    def close_for_reload(self):
        for but in self.buts:
            but.close_all()
        self.mainframe.destroy()

        self.master.write2log("Shutting all buttons...Done!")

    def close_spec_button(self,x=None):
        if x in range(len(self.master.buts_defs)):
            self.buts[x].close_all()
            print("close",x)
            print(self.args[0],self.master.buts_defs[0])
            self.prep_buttons()
            self.buts[x] = getattr(ButtonLib2,self.master.buts_defs[x][1])(self.mainframe, **self.args[int(self.master.buts_defs[x][0])])
            self.buts[x].grid(row=0, column=x)

    def update_schedule(self):
        self.prep_buttons()
        x=2
        #print(self.args[x]['sched_vector'])
        #self.buts[x].update_schedule(self.args[x]["sched_vector"])
        self.buts[x].close_all()
        self.buts[x] = getattr(ButtonLib2,self.master.buts_defs[x][1])(self.mainframe, **self.args[int(self.master.buts_defs[x][0])])
        self.buts[x].grid(row=0, column=x)

    def stop_start_but(self,buts=[]):
        self.prep_buttons()
        
        for but in buts:
            self.buts[but].close_all()
            if self.master.buts_defs[but][8]=='On':
                self.buts[but] = getattr(ButtonLib2,self.master.buts_defs[but][1])(self.mainframe, **self.args[int(self.master.buts_defs[but][0])])
            else:
                self.buts[but] = getattr(ButtonLib2,'ErrBut')(self.mainframe,name=self.master.buts_defs[but][2])
                self.loaded_buts.append([but,"ErrorBut"])
                
            self.buts[but].grid(row=0, column=but)
        
        



class TimeTable_RowConfig(ttk.Frame):
    # Create GUI of Rows #Change THIS class to change Table's UI content

    class ListPopUpWindow(tk.Toplevel):
        #Creates only popup windows in some Entries

        def __init__(self,master,list1=["1","2","3"],text1='Enter Text', var='', title=[],bg='', multi='no'):
            tk.Toplevel.__init__(self, master)
            self.master = master
            self.external_var = var
            self.title(title)
            self.list1=list1
            
            if multi == 'yes':
                self.selmode = {'selectmode':tk.MULTIPLE}
            elif multi == 'no' or multi ==None:
                self.selmode = {'selectmode':tk.SINGLE}
                
            self.build_gui(list1, text1)
        
        def build_gui(self, list1, text1):
            self.frame = ttk.Frame(self)
            self.frame.grid(row=0, column=0)

            label1 = ttk.Label(self.frame,text=text1)
            label1.grid(row=0, column=0, columnspan=2, pady= 10)
            self.listbox = tk.Listbox(self.frame, width=10, height = len(list1)+1, **self.selmode)
            self.listbox.grid(row=1, column=0)
            for j in range(len(list1)):
                self.listbox.insert(tk.END, list1[j])

            ok_button = ttk.Button(self.frame,width=5, text="OK", command=self.update_selection)
            ok_button.grid(row=1, column=1, sticky=tk.N, padx=20)

            cancel_button = ttk.Button(self.frame,width=5, text="Exit", command=self.destroy)
            cancel_button.grid(row=1, column=1)

            label2 = ttk.Label(self.frame,text="Hello World !", relief=tk.FLAT,border=3, justify=tk.CENTER)
            label2.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E)

        def update_selection(self):
            self.items_selected = self.listbox.curselection()
            self.external_var.set(list(self.items_selected))
            self.destroy()


    def __init__(self, master, data_from_file, titles=[], connected_devices=[]):
        ttk.Frame.__init__(self, master)
        self.master = master

        self.mainframe = ttk.Frame(self)
        self.mainframe.grid()
        self.time_left_vector=[]
        self.all_sched_vars=[]
        self.build_gui(data_from_file, titles, connected_devices)
        self.update_time_table()
        

    def build_gui(self, data_from_file, title=[], connected_devices=[]):
        
        def headers(m,n):

            titles = title

            for i in range(len(titles)):
                ttk.Label(inner_frame,text=titles[i], style ='Title.TLabel').grid(row=m, column=n+i, padx=5, pady=5)

        def pop_days(event, days_var):
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            a= self.ListPopUpWindow(self, list1=days,title='Days Selection', text1="Select days to current schedule task:", var=days_var, multi='yes')
            a.grid()

        inner_frame = ttk.Frame(self)
        inner_frame.grid()
        
        # Create Table Header
        headers(0,0)
        
        # Create Rows in Table
        devs = connected_devices
        for i in range (len(data_from_file)):
            
            #Task#
            self.var=[]
            self.var=[tk.StringVar()]
            self.var[0].set(i)
            task_num = ttk.Label(inner_frame, textvariable=self.var[0], justify=tk.CENTER)
            task_num.grid(row=i+1, column=0)

            #On/Off
            self.var.append(tk.StringVar())
            self.var[1].set(data_from_file[i][1])
            on_off_box = ttk.Combobox(inner_frame, width=5, textvariable=self.var[1], values=['On','Off'],state='readonly', justify=tk.CENTER)
            on_off_box.bind('<<ComboboxSelected>>',lambda event, arg=i: self.on_off_bind(event, arg))
            on_off_box.grid(row=i+1, column=1)

            #Device
            self.var.append(tk.StringVar())
            self.var[2].set(data_from_file[i][2])
            device_entry = ttk.Combobox(inner_frame, width=12, textvariable=self.var[2], values=devs, state='readonly', justify=tk.CENTER)
            device_entry.grid(row=i+1, column=2, padx=8)

            #Day
            self.var.append(tk.StringVar())
            self.var[3].set(data_from_file[i][3])
            days_entry = ttk.Entry(inner_frame, width=12, textvariable=self.var[3], justify=tk.CENTER)
            days_entry.grid(row=i+1, column=3, padx=8)

            #start
            self.var.append(tk.StringVar())
            self.var[4].set(data_from_file[i][4])
            time_on_entry = ttk.Entry(inner_frame, width=9, textvariable=self.var[4], justify=tk.CENTER)
            time_on_entry.grid(row=i+1, column=4, padx=8)

            #Stop
            self.var.append(tk.StringVar())
            self.var[5].set(data_from_file[i][5])
            time_off_entry = ttk.Entry(inner_frame, width=9, textvariable=self.var[5], justify=tk.CENTER)
            time_off_entry.grid(row=i+1, column=5, padx=8)

            #TimeLeft
            self.var.append(tk.StringVar())
            self.var[6].set('No Schedule/ Off')#data_from_file[i][6])
            time_left_entry = ttk.Entry(inner_frame, width=15, textvariable=self.var[6], justify=tk.CENTER)
            time_left_entry.grid(row=i+1, column=6, padx=8)

            #Skip
            self.var.append(tk.StringVar())
            self.var[7].set('On')
            skip_button = ttk.Combobox(inner_frame, width=5, textvariable=self.var[7], values=['On','Off'],state='readonly', justify=tk.CENTER)
            skip_button.bind('<<ComboboxSelected>>',lambda event, x=i: self.but_callback(event,x))
            skip_button.grid(row=i+1, column=7, padx=8)
            
            self.time_left_vector.append(time_left_entry)
            self.all_sched_vars.append(self.var)


    def on_off_bind(self,event, i):
        self.reload_time_table()
        self.master.master.master.master.master.master.master.disable_sched_in_gui([self.all_sched_vars[i][2].get(),self.all_sched_vars[i][1].get(),self.all_sched_vars[i][0].get()])


    def but_callback(self,event,x):
        #This method create skip (self.task_state) of sched task
        #Each time entering to this method it changes state from on to off.
        # additinal use is when task is active and in On state, pressing SKIP
        # will cancel this task. it is not reversible for now
        result_vector = []
        MainGUI = self.master.master.master.master.master.master.master
        #What device was selected in time table GUI 
        selected_device_in_gui = self.all_sched_vars[x][2].get()

        #get # of task vector of selected device
        for i, current_sch_task in enumerate(self.all_sched_vars):
            if selected_device_in_gui == current_sch_task[2].get():
                result_vector.append(i)
                
        dev_task_num = result_vector.index(int(self.all_sched_vars[x][0].get()))

        #match device in GUI with loaded devices
        for i,current_loaded_device in enumerate(MainGUI.ButConfigTable.RowClassCreator.all_sched_vars):
            #disable/enable state of task
            if current_loaded_device[2].get() == selected_device_in_gui:
                if MainGUI.ButtonNote.buts[i].SchRun.get_state()[0][0]==1 and MainGUI.ButtonNote.buts[i].SchRun.get_state()[0][1] == dev_task_num:
                    sw_vector=MainGUI.ButtonNote.buts[i].SchRun.sw
                    if MainGUI.ButtonNote.buts[i].task_state[dev_task_num]==1:
                        MainGUI.ButtonNote.buts[i].ext_press(sw=sw_vector[dev_task_num],state=0,type_s='UI-Skip')
                #Change state of task_state from off to on
                elif MainGUI.ButtonNote.buts[i].task_state[dev_task_num]==0:
                    MainGUI.ButtonNote.buts[i].task_state[dev_task_num]=1
                #Change state of task_state from on to off    
                elif MainGUI.ButtonNote.buts[i].task_state[dev_task_num]==1:
                    MainGUI.ButtonNote.buts[i].task_state[dev_task_num]=0


    def update_time_table(self):
        def update_run():
            #goes thru only On tasks
            for i, current_task in enumerate(relations_vector):
                try:
                    Sched_Current_button = MainGUI.ButtonNote.buts[current_task[3]].SchRun
                        #current_task[0] - task # timetable
                        #current_task[1] - task # of schedule
                        #current_task[2] - on/off of button
                        #current_task[3] - buttin # in config table
                except AttributeError:
                    print('But with no SchRun')


                if current_task[2]=='On':
                    pass
                    #self.all_sched_vars[current_task[0]][6].set(Sched_Current_button.get_state()[1][current_task[1]])
               
                    ##Color of text:
                    ##print(i,Sched_Current_button.get_state()[0][0],Sched_Current_button.master.task_state[current_task[1]])
                    #if Sched_Current_button.get_state()[0][0] == 1:
                    ##Task_state in 1 ( task enabled )- check master's state directly
                        #if Sched_Current_button.master.task_state[current_task[1]]==1:
                            ## This is the task wich is On ( button may have more that one schd task)
                            #if current_task[1] == Sched_Current_button.get_state()[0][1]:
                                #self.time_left_vector[i].config(foreground='green')
                            #else:
                                #self.time_left_vector[i].config(foreground='red')
                        #else:
                            #self.time_left_vector[i].config(foreground='orange')
                    #else:
                        #if Sched_Current_button.master.task_state[current_task[1]]==0:
                            #self.time_left_vector[i].config(foreground='orange')
                        #else:
                            #self.time_left_vector[i].config(foreground='red')
                        
        
                ###When Schd is Off
                ##if Sched_Current_button.get_state()[0][0] == -1:
                #else:
                    #self.time_left_vector[i].config(foreground='red')
                    ###if Sched_Current_button.master.task_state[current_task[1]]==0:
                        ###self.time_left_vector[i].config(foreground='orange')
                        
            self.run_id = self.after(1000,update_run)

        #Shortcut to Main
        MainGUI = self.master.master.master.master.master.master.master
        temp_list, relations_vector=[], []
        
        #list in weekly schedule
        for i,current_timetable_row in enumerate(self.all_sched_vars):
            #list of run buttons
            for m,current_button in enumerate(MainGUI.ButtonNote.loaded_buts):
                if current_timetable_row[2].get()==current_button[1]:
                    #if current_timetable_row[1].get() == 'On':
                        #temp_list store device's name to count repititions
                    temp_list.append(current_timetable_row[2].get())
                    relations_vector.append([i,temp_list.count(temp_list[-1])-1,current_timetable_row[1].get(),current_button[0]])
                    #else:
                        ##when task is off relation_vector[1]='' - not counted as another task
                        #relations_vector.append([i,'',current_timetable_row[1].get(),current_button[0]])
        update_run()
        
    def reload_time_table(self):
        self.after_cancel(self.run_id)
        self.update_time_table()
        


class Buttons_RowConfig(ttk.Frame):
       # Create GUI of Rows #Change THIS class to change Table's UI content

    def __init__(self, master, data_from_file, titles=[], buttons_type={}):
        ttk.Frame.__init__(self, master)
        self.master = master
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid()       
        self.all_sched_vars=[]
        self.build_gui(data_from_file, titles, buttons_type)

    def build_gui(self, data_from_file, title=[],buttons_type={}):
        
        def headers(m,n):
            titles = title
            for i in range(len(titles)):
                ttk.Label(inner_frame,text=titles[i], style ='Title.TLabel').grid(row=m, column=n+i, padx=5, pady=5)
        inner_frame = ttk.Frame(self)
        inner_frame.grid()
        
        # Create Table Header
        headers(0,0)
        
        # Create Rows in Table
        for i in range (len(data_from_file)):
            
            #No#
            self.var=[]
            self.var=[tk.StringVar()]
            self.var[0].set(i)
            task_num = ttk.Label(inner_frame, textvariable=self.var[0], justify=tk.CENTER)
            task_num.grid(row=i+1, column=0)

            
            #Device Type
            self.var.append(tk.StringVar())
            self.var[1].set(data_from_file[i][1])
            device_entry = ttk.Combobox(inner_frame, width=12, textvariable=self.var[1], values=list(buttons_type.values()) ,state='readonly', justify=tk.CENTER)
            device_entry.grid(row=i+1, column=2, padx=8)
            
            #Alias
            self.var.append(tk.StringVar())
            self.var[2].set(data_from_file[i][2])
            alias_entry = ttk.Entry(inner_frame, width=18, textvariable=self.var[2], justify=tk.CENTER)
            alias_entry.grid(row=i+1, column=3)

            #IP OUT
            self.var.append(tk.StringVar())
            self.var[3].set(data_from_file[i][3])
            ip_out_entry = ttk.Entry(inner_frame, width=12, textvariable=self.var[3], justify=tk.CENTER)
            ip_out_entry.grid(row=i+1, column=4, padx=8)

            #GPIO OUT
            self.var.append(tk.StringVar())
            self.var[4].set(data_from_file[i][4])
            gpio_out_entry = ttk.Entry(inner_frame, width=8, textvariable=self.var[4], justify=tk.CENTER)
            gpio_out_entry.grid(row=i+1, column=5, padx=8)

            #IP IN
            self.var.append(tk.StringVar())
            self.var[5].set(data_from_file[i][5])
            ip_in_entry = ttk.Entry(inner_frame, width=12, textvariable=self.var[5], justify=tk.CENTER)
            ip_in_entry.grid(row=i+1, column=6, padx=8)

            #GPIO IN
            self.var.append(tk.StringVar())
            self.var[6].set(data_from_file[i][6])
            gpio_in_entry = ttk.Entry(inner_frame, width=8, textvariable=self.var[6], justify=tk.CENTER)
            gpio_in_entry.grid(row=i+1, column=7, padx=5)

            #Button's dimensiob
            self.var.append(tk.StringVar())
            self.var[7].set(data_from_file[i][7])
            dimen_entry = ttk.Entry(inner_frame, width=5, textvariable=self.var[7])
            dimen_entry.grid(row=i+1, column=8, padx=8)

            #Device on/off
            self.var.append(tk.StringVar())
            self.var[8].set(data_from_file[i][8])
            self.onoff_var=tk.StringVar()
            device_entry = ttk.Combobox(inner_frame, width=4, textvariable=self.var[8], values=['On','Off'] ,state='readonly', justify=tk.CENTER)
            device_entry.grid(row=i+1, column=1, padx=8)
            device_entry.bind('<<ComboboxSelected>>',lambda event, arg=i: self.switch_sched_off(event, arg))

            self.all_sched_vars.append(self.var)
            
    def switch_sched_off(self, event,i):
        #print(self.all_sched_vars[i][8].get())
        self.master.master.master.master.master.master.master.bind_on_off([self.all_sched_vars[i][2].get(),self.all_sched_vars[i][8].get()])


class Generic_UI_Table(ttk.Frame):


    def __init__(self,master, RowClass, titles=[], path='',filename='', defaults=[], header='',data=[],**kwargs):
        
        ttk.Frame.__init__(self,master)
        self.class_frame = ttk.LabelFrame(self, text= header)
        self.class_frame.grid(padx=10, pady=10)
        self.Rows = RowClass
        self.init_styles()
        self.kwargs=kwargs

        self.addrow = 0
        self.titles=titles
        self.path=path
        self.filename=filename
        self.defaults=defaults
        self.data=data
        self.FileManager = None
        
        self.rebuild_table()
    

    def build_gui(self):

        self.build_rows()
        self.create_buttons()


    def rebuild_table(self):
        self.data_from_file = []
        if self.data == []:
            self.load_data()
        else:
            self.data_from_file=self.data
        self.build_gui()
    

    def load_data(self):
        titles = self.titles
        path = self.path
        filename = self.filename
        defaults = self.defaults
        #self.master.master.master.master.FileManButs
        self.FileManager =  readfile_ssh.LoadFile(path=path, filename=filename, titles=titles, defaults=defaults)
        self.data_from_file = self.FileManager.data_from_file

        if self.addrow == 1: self.data_from_file.append(['' for i in range(len(self.data_from_file[0]))])


    def save_data(self):
        if self.FileManager != None:
            self.FileManager.save_to_file(mat=self.extract_data_from_gui())
            self.load_data()
            

    def add_row(self):

        self.addrow =1
        self.rows_frame.destroy()
        self.rebuild_table()

        print("row added")


    def exit_cb(self):

        self.master.destroy()


    def del_row(self):
        
        del self.data_from_file[self.class_frame.focus_get().grid_info().get('row') -1]
        self.save_data()
        self.rows_frame.destroy()
        self.rebuild_table()

        print("row deleted")


    def init_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel',font=('Helvetica',11),foreground="midnight blue")

    
    def build_rows(self):

        self.rows_frame = ttk.Frame(self.class_frame)
        self.rows_frame.grid(row=0, column=0)
        
        titles= self.titles
        self.RowClassCreator = self.Rows(self.rows_frame, self.data_from_file, titles,**self.kwargs)
        self.RowClassCreator.grid(row=0, column = 0 )

    
    def create_buttons(self):

        buttons_frame = ttk.Frame(self.class_frame)
        buttons_frame.grid(row=0, column=1, sticky=tk.S, padx =5)
        
        update_table_button = ttk.Button(buttons_frame, width=10, text="Save&Upade", command=self.save_data)
        update_table_button.grid(row=0, column=0, pady=5, padx= 5)

        new_row_button = ttk.Button(buttons_frame, width=10, text="Add Row", command=self.add_row)
        new_row_button.grid(row=1, column=0, pady=5, padx= 5)

        del_row_button = ttk.Button(buttons_frame, width=10, text="Delete Row", takefocus=False, command=self.del_row)
        del_row_button.grid(row=2, column=0, pady=5, padx= 5)

        #exit_button = ttk.Button(buttons_frame, width=10, text="Exit", command=self.extract_data_from_gui)
        #exit_button.grid(row=0, column=1, pady=5, padx= 5)

    def extract_data_from_gui(self):
        temp=[]
        for r,current_row in enumerate(self.RowClassCreator.all_sched_vars):
            temp.append([])
            for c,current_col in enumerate(current_row):
                temp[-1].append(current_col.get())
        return temp


class MainGUI(ttk.Frame):
    """ This MainGui Class"""
    
    def __init__(self,master):
        ttk.Frame.__init__(self, master)
        
        self.path = '/home/guy/PythonProjects/'
        self.but_filename = 'ButtonsDef.csv'
        self.sched_filename = 'Schedule.csv'
        self.app_name='Pi Scheduler'
        master.title(self.app_name)

        self.reload_all()
        

    def read_data_from_files(self):
        self.FileManButs = readfile_ssh.LoadFile(filename=self.but_filename, path=self.path)
        self.buts_defs = self.FileManButs.data_from_file
        
        self.FileManSched=readfile_ssh.LoadFile(filename=self.sched_filename, path=self.path)
        self.sched_file= self.FileManSched.data_from_file

    #save both file
    def save_data_to_file(self):
        self.FileManButs.save_to_file(mat=self.ButConfigTable.extract_data_from_gui())
        self.FileManSched.save_to_file(mat=self.WeekSched_TimeTable.extract_data_from_gui())
        
        
    def reload_all(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid()
        
        self.connected_devices= []
        self.sched_vector = []
        self.read_data_from_files()
        self.build_gui()

    def close_for_reload(self):
        self.ButtonNote.close_for_reload()
        self.main_frame.destroy()
        self.reload_all()
 
        
    def build_gui(self):
        notebook = ttk.Notebook(self.main_frame)
        self.sched_tab= ttk.Frame(notebook)
        self.config_but_tab= ttk.Frame(notebook)
        self.buttons_tab= ttk.Frame(notebook)
        self.activity_log_tab= ttk.Frame(notebook)
        notebook.add(self.sched_tab, text = "Weekly Schedule", compound=tk.TOP)
        notebook.add(self.buttons_tab, text = "Buttons", compound=tk.TOP)
        notebook.add(self.config_but_tab, text = "Hardware Config", compound=tk.TOP)
        notebook.add(self.activity_log_tab, text = "Activity Log", compound=tk.TOP)
        notebook.grid()
        
        self.log_window()
        self.write2log("Boot")
        self.butt_config_gui(2,0)
        self.buttons_gui(1,0)
        self.weekly_sched_gui(0,0)

        

    def weekly_sched_gui(self,r=0, c=0):
        
        header='Weekly Schedule'
        titles = ['Task #', 'On/Off','Device','Day','Start Time', 'Stop Time', 'Time Left', 'Skip Run']
        path = self.path
        filename = self.sched_filename
        defaults = [1, 1, 1,[3,4,5,6], "23:07:00", "01:08:00",'','Hi!']

        #import configured devices names into timetable
        dev_names = readfile_ssh.LoadFile(filename=self.but_filename, path=self.path).data_from_file
        for dev in dev_names: #device's Aliases to show in timetable
            self.connected_devices.append(dev[2])

        #method does not load file ( it can), but it uses data already loaded
        self.WeekSched_TimeTable= Generic_UI_Table(self.sched_tab, TimeTable_RowConfig, titles=titles, path=path, filename='', defaults=defaults, header=header, data=self.sched_file, connected_devices=self.connected_devices)
        self.WeekSched_TimeTable.grid(row=r, column=c)

        ttk.Button(self.sched_tab,text="Close&Open All GUI", command=self.close_for_reload).grid(row=1, column=0)
        ttk.Button(self.sched_tab,text="Save Schedule", command=self.save_data_to_file).grid(row=1, column=1)

        self.write2log("Weekly schedule GUI started")


    def butt_config_gui(self,r=0,c=0):
        
        header='Button Configuration- Local'
        titles= ['No.','On/Off','Type','Alias', 'IP out','GPIO out','IP in*',' GPIO in*','HxW*']
        filename= self.but_filename
        path = self.path
        defaults = ["A" for i in range(len(titles))]

        buttons_type = getattr(ButtonLib2,'button_list') # Get Button type from ButtonLib

        #method does not load file ( it can), but it uses data already loaded
        self.ButConfigTable= Generic_UI_Table(self.config_but_tab, Buttons_RowConfig, titles=titles, path=path, filename='', defaults=defaults, header=header, data=self.buts_defs, buttons_type=buttons_type)
        self.ButConfigTable.grid(row=r, column=c)
        self.write2log("Buttons config GUI loaded")


    def buttons_gui(self,r=0,c=0):
        
        self.ButtonNote = AllButtons_GUI(self, self.buttons_tab)
        self.ButtonNote.grid(row=0, column=0)

        ttk.Button(self.buttons_tab, text="Disconnect Buttons", command=self.ButtonNote.close_for_reload).grid(row=0,column=1)
        ttk.Button(self.buttons_tab, text="Reload Buttons", command=self.ButtonNote.reload_all).grid(row=0,column=2)

        self.write2log("Buttons GUI loaded")

    #A bind to change on/off in timetable AFTER changes by user in button config.
    def bind_on_off(self,args):
        print(args[0],"is set to",args[1] )
        for i, current_device in enumerate (self.WeekSched_TimeTable.RowClassCreator.all_sched_vars):
            if args[0] == current_device[2].get():
                self.WeekSched_TimeTable.RowClassCreator.all_sched_vars[i][1].set(args[1])
                print("Schedule Task #",self.WeekSched_TimeTable.RowClassCreator.all_sched_vars[i][0].get(), "set to",args[1])
            
        self.FileManButs.save_to_file(mat=self.ButConfigTable.extract_data_from_gui())
        self.read_data_from_files()
        
    #A bind to change verify if valid to change timetable GUI according state of buttonconfig
    def disable_sched_in_gui(self,args):
        for i,current_but in enumerate(self.ButConfigTable.RowClassCreator.all_sched_vars):
            if current_but[2].get()==args[0]:
                break
                
         #In case and bituuon if not off or err       
        if self.ButConfigTable.RowClassCreator.all_sched_vars[i][8].get() in ['Off','err']:
            self.WeekSched_TimeTable.RowClassCreator.all_sched_vars[int(args[2])][1].set('Off')


        self.FileManSched.save_to_file(mat=self.WeekSched_TimeTable.extract_data_from_gui())
        self.read_data_from_files()
        
    def log_window (self):
        #Create log Tab
        self.text_tab = tk.Text(self.activity_log_tab, width=145, height=16, bg='yellow')
        self.text_tab.grid(row=0, column=0, sticky= tk.E+tk.W)
        scrollbar = ttk.Scrollbar(self.activity_log_tab)
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        scrollbar.config(command=self.text_tab.yview)
        self.text_tab.config(yscrollcommand=scrollbar.set)
        self.text_tab.config(state=tk.DISABLED)

        log_button = ttk.Button(self.activity_log_tab, text="Save log")#, command=self.save_log)
        log_button.grid(row=1, column=0, sticky=tk.E, pady=10)


    def write2log(self,text_in):
        self.text_tab.config(state=tk.NORMAL)
        time2log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        start = tk.END
        self.text_tab.insert(start, "[" + str(time2log) + "] " + text_in + "\n")
        self.text_tab.config(state=tk.DISABLED)

    def xtrct_nums(self, lista):
        # make a list from str or list comb iwth strings
        new_list = []
        def xtrct_str(listb):
            new_lst = []
            temp = ''

            for i in range(len(listb)):
                try:
                    int(listb[i])  # try in int
                    temp = temp + listb[i]  # use is as char !
                except ValueError:
                    if not temp == '':
                        new_lst.append(int(temp))
                        temp = ''
                # for last number in str
                if i == len(listb) - 1 and not temp == '':
                    new_lst.append(int(temp))

            return new_lst

        if type(lista) is str:
            new_list = xtrct_str(lista)

        elif type(lista) is list:
            for item in lista:
                if type(item) is int:
                    new_list.append(item)
                elif type(item).__name__ == 'str':
                    z = xtrct_str(item)
                    if not z == []: new_list.append(xtrct_str(item)[0])

        return new_list


root = tk.Tk()

app = MainGUI(root)
app.grid()

root.mainloop()
