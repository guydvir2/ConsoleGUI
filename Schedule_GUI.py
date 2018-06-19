import ButtonLib2
import readfile_ssh
import tablegui
import tkinter as tk
from tkinter import ttk
import datetime
import numpy as np
from sys import platform


class ButtonsGUI(ttk.Frame):
    """AllButtons GUI Class"""

    def __init__(self, master, mainframe):
        self.master = master
        self.mframe = mainframe
        ttk.Frame.__init__(self, master)
        self.reachable_ips = ['192.168.2.113', '192.168.2.114']
        self.master.write2log("Valid IP's to load:" + str(self.reachable_ips))
        self.max_buts_in_row=5

        self.reload_all()

    def zero_vars(self):
        self.args, self.buts, self.but2load = [], [], []
        self.loaded_buts, self.sched_vector, self.device_list_sched = [], [], []

    def reload_all(self):
        self.zero_vars()
        self.mainframe = ttk.LabelFrame(self.mframe, text="Button")
        self.mainframe.grid(padx=5, pady=5)

        self.load_buttons_defs()
        self.get_sched_defs()
        self.build_gui()

    def load_buttons_defs(self):
        # keys "hw_in","hw_out","dimension" - get special treatment in next for
        # loop in extracting string values
        self.button_keys = ['id', 'on_off', 'type', 'nickname', 'ip_out', 'hw_out', 'hw_in', 'ip_in', 'dimension']

        start_key = 1
        for i, but_defs in enumerate(self.master.buts_defs):
            c, t = {}, start_key
            for m in self.button_keys[start_key:7]:

                # fields that get more than one parameter
                if m == 'hw_out' or m == 'hw_in':
                    c[m] = self.master.xtrct_nums(but_defs[t])
                elif m == 'dimension':
                    if not but_defs[t] == '':
                        if not self.master.xtrct_nums(but_defs[t])[1] == []:
                            c['height'] = self.master.xtrct_nums(but_defs[t])[1]
                        else:
                            c['height'] = ''
                        if not self.master.xtrct_nums(but_defs[t])[0] == []:
                            c['width'] = self.master.xtrct_nums(but_defs[t])[0]
                        else:
                            c['width'] = ''
                    else:
                        pass
                else:
                    # All other keys which are not "special":
                    c[m] = but_defs[t]
                t += 1

            del c['type']
            self.args.append(c)

    def get_sched_defs(self):
        self.device_list_sched, self.sched_vector = [], []

        dev_names, off_list = [], []  # Alias of device # items that are OFF in TimeTable GUI
        for i, current_task in enumerate(self.master.sched_file):
            if current_task[1] == "0" or not all(current_task[0:6]):
                off_list.append(i)
                self.sched_vector.append([])
            else:
                self.sched_vector.append(current_task[3:6])
                self.sched_vector[i][0] = self.master.xtrct_nums(current_task[3])
            dev_names.append(current_task[2])

        # Create a list- including buttons and ALL sched in sched_vector ( multilpe values)
        # this list contain index of buttons in sched list
        for x, dev in enumerate(list(set(dev_names))):
            self.device_list_sched.append([dev])  # name of device
            self.device_list_sched[x].append([])  # index
            self.device_list_sched[x].append([])  # sched_vector

            for i, u in enumerate(self.master.sched_file):
                if dev in u and i not in off_list:
                    self.device_list_sched[x][1].append(i)
                    self.device_list_sched[x][2].append(self.sched_vector[i])

        # Update sched_vector into self.args
        for i, args in enumerate(self.args):
            for t, sched in enumerate(self.device_list_sched):
                if args['nickname'] == sched[0] or args['nickname'] in sched[0] and '[DOWN]' in sched[0].upper():
                    self.args[i]['sched_vector'] = self.device_list_sched[t][2]
                elif args['nickname'] in sched[0] and '[UP]' in sched[0].upper():  # Valid to Window UP sched
                    self.args[i]['sched_vector2'] = self.device_list_sched[t][2]

    def build_gui(self):

        x = 0
        row_index,col_index = 0, 0
        for l, current_button in enumerate(self.master.buts_defs):
            try:
                # load button if it in allowed ip list, and checked
                # [ 'ID','ENABLED','Type','nick','ip_out','hw_out','hw_in']
                print(l, self.args[l])
                if current_button[4] in self.reachable_ips and current_button[1] == '1':
                    self.buts.append(getattr(ButtonLib2, current_button[2])
                                     (self.mainframe, **self.args[l]))
                    self.loaded_buts.append([x, self.args[l]['nickname']])
                    if col_index >self.max_buts_in_row-1 :
                        row_index +=1
                        col_index = 0
                    self.buts[x].grid(row=row_index, column=col_index)
                    col_index +=1
                    x += 1
            except ValueError:
                self.master.write2log("Error loading Button" + str(l))
        self.master.write2log("Buttons loaded successfully: " + str([x[1] for x in self.loaded_buts]))

    def close_for_reload(self, nick=''):
        if nick != '':
            for but in self.buts:
                but.close_all()
            self.mainframe.destroy()

        self.master.write2log("Shutting all buttons...Done!")

    def close_but(self):
        for but in self.buts:
            but.close_all()


class MainGUI(ttk.Frame):
    """ This MainGui Class"""

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.log_stack = []
        self.write2log('init time')
        self.but_filename = 'ButtonsDef2.csv'
        self.sched_filename = 'Schedule.csv'
        self.app_name = 'Pi Scheduler'
        master.title(self.app_name)

        self.detectOS()
        self.reload_all()

    def detectOS(self):
        os_type = platform
        if os_type == 'darwin':
            self.path = '/Users/guyd/Documents/github/Rpi/SmartHome/'
        elif os_type == 'win32':
            self.path = 'd:/users/guydvir/Documents/git/Rpi/SmartHome/'
        elif os_type == 'linux':
            self.path = '/home/guy/Documents/github/Rpi/SmartHome/'
        self.write2log('OS detected:' + str(os_type))

    def reload_all(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid()
        self.connected_devices, self.sched_vector = [], []
        self.read_data_from_files()
        self.build_notebook()

    def read_data_from_files(self):
        # Read data from file to code
        self.FileManButs = readfile_ssh.LoadFile(filename=self.but_filename, path=self.path)
        self.buts_defs = self.FileManButs.data_from_file

        self.FileManSched = readfile_ssh.LoadFile(filename=self.sched_filename, path=self.path)
        self.sched_file = self.FileManSched.data_from_file

    # def save_data_to_file(self):
    #     self.FileManButs.save_to_file(mat=self.ButConfigTable.extract_data_from_gui())
    #     self.FileManSched.save_to_file(mat=self.WeekSched_TimeTable.extract_data_from_gui())
    #
    # def close_for_reload(self):
    #     self.ButtonNote.close_for_reload()
    #     self.main_frame.destroy()
    #     self.reload_all()

    def build_notebook(self):
        notebook = ttk.Notebook(self.main_frame)

        self.sched_tab = ttk.Frame(notebook)
        self.config_but_tab = ttk.Frame(notebook)
        self.buttons_tab = ttk.Frame(notebook)
        self.activity_log_tab = ttk.Frame(notebook)
        self.about_tab = ttk.Frame(notebook)
        
        notebook.add(self.sched_tab, text="Weekly Schedule", compound=tk.TOP)
        notebook.add(self.buttons_tab, text="Buttons", compound=tk.TOP)
        notebook.add(self.config_but_tab, text="Hardware Config", compound=tk.TOP)
        notebook.add(self.activity_log_tab, text="Activity Log", compound=tk.TOP)
        notebook.add(self.about_tab, text="About", compound=tk.TOP)
        notebook.grid()

        self.log_window()
        self.write2log("Notebooks built")
        self.butt_config_gui(2, 0)
        self.buttons_gui(1, 0)
        self.weekly_sched_gui(0, 0)

    def weekly_sched_gui(self, r=0, c=0):
        devices_names = []
        # import configured devices names into timetable
        for dev in self.buts_defs:
            if dev[2] == 'UpDownButton':
                devices_names.append(dev[3] + '[Up]')
                devices_names.append(dev[3] + '[Down]')
            else:
                devices_names.append(dev[3])

        self.WeekSched_TimeTable = tablegui.TimeTableConfigGUI(self.sched_tab,
                                data_file_name=self.path + self.sched_filename,
                                list=devices_names)
        self.WeekSched_TimeTable.grid(row=r, column=c)
        self.write2log("Weekly schedule GUI started")

        ttk.Button(self.sched_tab, text='reload schedule', command=self.update_schedule).grid()
        ttk.Button(self.config_but_tab, text='reload schedule', command=self.ButtonNote.close_but).grid()

    def update_schedule(self):
        self.WeekSched_TimeTable.save2()
        self.read_data_from_files()
        self.ButtonNote.get_sched_defs()
        self.WeekSched_TimeTable.create_relations_vector()

        keys = ['sched_vector', 'sched_vector2']
        for i, current_but in enumerate(self.ButtonNote.buts):
            for x, current_schedtask in enumerate(self.ButtonNote.args):
                if current_schedtask['nickname'] == current_but.nick:
                    new_sched = []
                    for key in keys:
                        if key in list(current_schedtask.keys()):
                            new_sched.append(current_schedtask[key])
                        else:
                            new_sched.append([])
                    current_but.schedule_update(new_sched)

    def butt_config_gui(self, r=0, c=0):
        buttons_type = getattr(ButtonLib2, 'button_list')  # Get Button type from ButtonLib
        self.ButConfigTable = tablegui.DeviceConfigGUI(self.config_but_tab,
                                                       data_file_name=self.path + self.but_filename,
                                                       list=buttons_type)
        self.ButConfigTable.grid(row=r, column=c)
        self.write2log("Buttons config GUI loaded")

    def buttons_gui(self, r=0, c=0):
        self.ButtonNote = ButtonsGUI(self, self.buttons_tab)
        self.ButtonNote.grid(row=0, column=0)
        self.write2log("Buttons GUI loaded")

    def log_window(self):
        # Create log Tab
        self.text_tab = tk.Text(self.activity_log_tab, bg='white', wrap=tk.NONE, width=110)
        self.text_tab.grid(row=0, column=0)#, sticky=tk.E + tk.W+tk.N+tk.S)
        scrollbar_y = ttk.Scrollbar(self.activity_log_tab, orient=tk.VERTICAL)
        scrollbar_y.grid(row=0, column=1, sticky=tk.N + tk.S)
        scrollbar_y.config(command=self.text_tab.yview)
        scrollbar_x = ttk.Scrollbar(self.activity_log_tab,orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=0, column=0, sticky=tk.E + tk.W+tk.S)
        scrollbar_x.config(command=self.text_tab.xview)
        
        self.text_tab.config(yscrollcommand=scrollbar_y.set)
        self.text_tab.config(xscrollcommand=scrollbar_x.set)
        self.text_tab.config(state=tk.DISABLED)

        #log_button = ttk.Button(self.activity_log_tab, text="Save log")  # , command=self.save_log)
        #log_button.grid(row=1, column=0, sticky=tk.E, pady=10)

    def write2log(self, text_in):
        try:
            self.text_tab.config(state=tk.NORMAL)
            time2log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
            start = tk.END
            if self.log_stack != []:
                for msg in self.log_stack:
                    self.text_tab.insert(start, msg)
                    start = tk.END
                self.log_stack = []
            self.text_tab.insert(start, "[" + str(time2log) + "] " + text_in + "\n")
            self.text_tab.config(state=tk.DISABLED)
        except AttributeError:
            # Stack log prior to boot of log
            time2log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.log_stack.append('[' + str(time2log) + '] ' + text_in + '\n')

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

    def findtasknum(self, m):
        sch_num = None
        ar = np.array(self.sched_file)
        on_index = ar[:m + 1, 1]
        name_index = ar[:m + 1, 2]
        seek_value = ar[m, 2]
        list1 = on_index[name_index == seek_value]

        if '[UP]' in seek_value.upper():
            sch_num = 1
        else:
            sch_num = 0
        if '[' in seek_value:
            i = seek_value.index('[')
            name = seek_value[:i]
        else:
            name = seek_value
        task_num = list(list1).count('1')

        if list1[-1] != '0':
            return [task_num - 1, sch_num, name]
        else:
            return [- 1, sch_num, name]


root = tk.Tk()

app = MainGUI(root)
app.grid()

root.mainloop()
