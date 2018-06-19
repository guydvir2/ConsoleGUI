import tkinter as tk
from tkinter import ttk

import readfile_ssh


class CoreTable(ttk.Frame):
    def __init__(self, master, data_filename=''):
        ttk.Frame.__init__(self, master)
        try:
            self.com = self.master.master,master.master.master.master.write2log
        except:
            print("DUSH")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("warning.TButton", foreground='red')
        self.style.configure("bg_title.TLabel", foreground='grey')
        #self.com("GUY!!!")

        # bg_color = 'slate gray'
        # bg_color = 'gray31'
        # self.style.configure("bg.TFrame", background=bg_color)
        # self.style.configure("bg.TButton", background=bg_color)
        # self.style.configure("bg.TEntry", background=bg_color)
        # self.style.configure("bg.TLabel", background=bg_color)
        # self.style.configure("bg.TCheckbutton", background=bg_color)

        self.main_frame = ttk.Frame(self, style='bg.TFrame')
        self.main_frame.grid()

        self.button_frame = ttk.Labelframe(self.main_frame, padding=(3, 1, 3, 1))
        self.button_frame.grid(row=2, column=0, pady=(0, 10))

        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=1, column=0)

        self.data_mat, self.add_row_flag = [], 0
        self.filename = data_filename

        self.load_data_from_file()
        self.button_gui()
        self.restart_table()
        self.status_bar()

    def load_data_from_file(self):
        self.data_from_file = readfile_ssh.LoadFile(filename=self.filename).data_from_file
        if not any(self.data_from_file):
            self.data_from_file = self.default_data

    def button_gui(self):
        px = 5
        self.new_row = ttk.Button(self.button_frame, text='Add Row', width=8,
                                  command=self.add_row_cb, style='bg.TButton')
        self.new_row.grid(row=0, column=0, padx=px)

        self.del_row = ttk.Button(self.button_frame, text='Delete Row', width=8,
                                  command=self.del_row, takefocus=False, style="warning.TButton")
        self.del_row.grid(row=0, column=1, padx=px)

        self.save_table = ttk.Button(self.button_frame, text='Save', width=8,
                                     command=self.save_table, style='bg.TButton')
        self.save_table.grid(row=0, column=2, padx=px)

    def add_row_cb(self):
        self.add_row_flag = 1
        self.crash_table()
        self.extract_data()
        self.restart_table(self.data_mat)

    def extract_data(self):
        self.data_mat = []

        for i, row in enumerate(self.vars_vector):
            self.data_mat.append([])
            for n, cell in enumerate(row):

                # if cell is empty - igonre entire line
                if n > 1 and cell.get() == '':
                    del self.data_mat[-1]
                    break
                else:
                    self.data_mat[-1].append(cell.get())

        print(self.data_mat)

        return self.data_mat

    def fill_table(self, m=[]):
        if m == []:
            self.data_mat = self.data_from_file
        else:
            self.data_mat = m
        if self.add_row_flag == 1:
            self.data_mat.append(self.default_data[0])
        rows = len(self.data_mat)
        self.table_structure(rows)

        for i, row in enumerate(self.data_mat):
            for x, cell in enumerate(row):
                try:
                    if x == 0:
                        self.vars_vector[i][x].set(self.counter + '#%02d' % i)
                    else:
                        self.vars_vector[i][x].set(cell)
                except IndexError:
                    print('error in updating table')

        self.add_row_flag = 0

    def crash_table(self):
        self.table_frame.destroy()

    def build_header(self):
        for i, header in enumerate(self.headers):
            ttk.Label(self.table_frame, text=header).grid(row=0, column=i)

    def restart_table(self, m=[]):
        self.table_frame = ttk.Frame(self.main_frame, padding=(20, 0, 20, 0))
        self.table_frame.grid(row=0, column=0)

        self.vars_vector = []
        self.build_header()
        self.fill_table(m=m)

    def del_row(self):
        del self.data_mat[int(self.table_frame.focus_get().grid_info().get('row')) - 1]
        self.crash_table()
        self.restart_table(m=self.data_mat)

    def save_table(self):
        self.extract_data()
        print(self.data_mat)
        readfile_ssh.LoadFile(filename=self.filename).save_to_file(mat=self.data_mat)

    def save2(self):
        self.extract_data()
        readfile_ssh.LoadFile(filename=self.filename).save_to_file(mat=self.data_mat)

    def status_bar(self):
        ttk.Label(self.status_frame, text='filename: ' + str(self.filename),
                  style='bg_title.TLabel').grid()


class DeviceConfigGUI(CoreTable):
    def __init__(self, master, data_file_name='', list=[]):
        self.headers = ['ID#', 'Enabled', 'Type', 'Name', 'IP Address', 'I/O In', 'I/O Out']
        self.counter = 'SW'
        self.default_data = [[0, 0, 'ERR', 'Load', 'DATA', 'FILE', '!!!!']]
        self.dropbox_values = list
        CoreTable.__init__(self, master, data_filename=data_file_name)

    def table_structure(self, rows):
        for i in range(1, rows + 1):
            self.v, c = [], 0

            # DeviceNumber
            self.v.append(tk.StringVar())
            a1 = ttk.Label(self.table_frame, textvariable=self.v[c], style='bg.TLabel')
            a1.grid(row=i, column=c)
            c += 1

            # Enabled
            self.v.append(tk.IntVar())
            a2 = ttk.Checkbutton(self.table_frame, variable=self.v[c], style='bg.TCheckbutton')
            a2.grid(row=i, column=c)
            c += 1

            # Type
            self.v.append(tk.StringVar())
            a3 = ttk.Combobox(self.table_frame, textvariable=self.v[c], width=20,
                              values=list(self.dropbox_values), state='readonly', justify=tk.CENTER)
            a3.grid(row=i, column=c)
            c += 1

            # Name
            self.v.append(tk.StringVar())
            a4 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=18, justify=tk.CENTER, style='bg.TEntry')
            a4.grid(row=i, column=c)
            c += 1

            # IP
            self.v.append(tk.StringVar())
            a5 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=18, justify=tk.CENTER, style='bg.TEntry')
            a5.grid(row=i, column=c)
            c += 1

            # GPIO IN
            self.v.append(tk.StringVar())
            a6 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=7, justify=tk.CENTER, style='bg.TEntry')
            a6.grid(row=i, column=c)
            c += 1

            # GPIO OUT
            self.v.append(tk.StringVar())
            a7 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=7, justify=tk.CENTER, style='bg.TEntry')
            a7.grid(row=i, column=c)
            c += 1

            self.vars_vector.append(self.v)


class TimeTableConfigGUI(CoreTable):
    def __init__(self, master, data_file_name='', list=[]):
        self.master = master
        self.headers = ['Task #', 'On/Off', 'Device', 'Day', 'Start Time', 'Stop Time', 'Time Left']
        self.counter = 'TSK'
        self.dropbox_values = list
        self.default_data = [[0, 0, 'empty', [3, 4, 5, 6], "12:00:00", "13:08:00", 'empty', ]]
        CoreTable.__init__(self, master, data_filename=data_file_name)
        self.additional_buttons()

        self.update_time_table()

    def table_structure(self, rows):
        self.time_left_vector = []

        for i in range(1, rows + 1):
            self.v, c = [], 0

            # TaskNumber
            self.v.append(tk.StringVar())
            a1 = ttk.Label(self.table_frame, textvariable=self.v[c], style='bg.TLabel')
            a1.grid(row=i, column=c)
            c += 1

            # on/off
            self.v.append(tk.IntVar())
            a2 = ttk.Checkbutton(self.table_frame, variable=self.v[c], style='bg.TCheckbutton')
            a2.grid(row=i, column=c)
            c += 1

            # Device
            self.v.append(tk.StringVar())
            a3 = ttk.Combobox(self.table_frame, textvariable=self.v[c], width=20, values=list(self.dropbox_values),
                              state='readonly', justify=tk.CENTER)
            a3.grid(row=i, column=c)
            c += 1

            # Day
            self.v.append(tk.StringVar())
            a4 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=14, justify=tk.CENTER, style='bg.TEntry')
            a4.grid(row=i, column=c)
            c += 1

            # Start Time
            self.v.append(tk.StringVar())
            a5 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=14, justify=tk.CENTER, style='bg.TEntry')
            a5.grid(row=i, column=c)
            c += 1

            # Stop Time
            self.v.append(tk.StringVar())
            a6 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=14, justify=tk.CENTER, style='bg.TEntry')
            a6.grid(row=i, column=c)
            c += 1

            # Time Left
            self.v.append(tk.StringVar())
            a7 = ttk.Entry(self.table_frame, textvariable=self.v[c], width=20, justify=tk.CENTER, style='bg.TEntry')
            a7.grid(row=i, column=c)
            c += 1

            self.time_left_vector.append(a7)
            self.vars_vector.append(self.v)

    def additional_buttons(self):
        self.skip_button = ttk.Button(self.button_frame, text='Skip Run', width=8, takefocus=False,
                                      command=self.skip_button_cb, style='bg.TButton')
        self.skip_button.grid(row=0, column=3, padx=5)

    def skip_button_cb(self):
        MainGUI = self.master.master.master.master
        try:
            line_num = int(self.table_frame.focus_get().grid_info().get('row')) - 1
            if MainGUI.sched_file[line_num][1] == '1':
                tsk_properties = MainGUI.findtasknum(line_num)
                # tsk_properties= [ tsk#, sw#,device_name]
                for i, dev_name in enumerate(MainGUI.ButtonNote.buts):
                    if dev_name.nick == tsk_properties[2]:
                        if dev_name.task_state[tsk_properties[1]][tsk_properties[0]] == 0:
                            dev_name.task_state[tsk_properties[1]][tsk_properties[0]] = 1
                        elif dev_name.task_state[tsk_properties[1]][tsk_properties[0]] == 1:
                            dev_name.task_state[tsk_properties[1]][tsk_properties[0]] = 0
            else:
                print("Disabled task")
        except AttributeError:
            print("Line not selected")

    def update_time_table(self):
        # Shortcut to Main GUI
        MainGUI = self.master.master.master.master

        def update_run():
            def text_to_entry(text, color):
                self.vars_vector[a][6].set(text)
                self.time_left_vector[a]['foreground'] = color

            for a, current_task in enumerate(MainGUI.sched_file):
                try:
                    # shortcuts
                    but_index = self.relations_vector[a][1]
                    actv_tsk = self.relations_vector[a][2]
                    sch_index = self.relations_vector[a][3]
                    but = MainGUI.ButtonNote.buts[but_index]
                    # print(a, but.nick, but.task_state, actv_tsk)
                    # case of checkedout schedule at GUI
                    if actv_tsk != -1:  # any(but.task_state):
                        task_state = but.task_state[sch_index][actv_tsk]
                    else:
                        text_to_entry('Inactive task', 'orange')

                    but_sched_active = but.SchRun[sch_index].get_state()[0][0]
                    but_sced_tsk_num = but.SchRun[sch_index].get_state()[0][1]
                    time_remain = str(but.SchRun[sch_index].get_state()[1][actv_tsk])

                    # case of checked out schedule (with multiple entries)
                    if actv_tsk == -1:
                        text_to_entry('Inactive task', 'orange')
                        continue
                    # task state can be [ 1 - on, 0 - off/skip, -1 cancel task permanently]
                    if but_sched_active == 1 and task_state == 1 and actv_tsk == but_sced_tsk_num:
                        text_to_entry('on: ' + time_remain, 'green')
                    elif but_sched_active == 1 and task_state == 0 and actv_tsk == but_sced_tsk_num:
                        text_to_entry('aborted: ' + time_remain, 'red')
                    elif task_state == -1 and actv_tsk == but_sced_tsk_num:
                        text_to_entry('cancelled: ' + time_remain, 'red')
                    elif but_sched_active == -1 and task_state == 1 or \
                            but_sched_active == 1 and task_state == 1 and actv_tsk != but_sced_tsk_num:
                        text_to_entry('wait: ' + time_remain, 'red')
                    elif but_sched_active == -1 and task_state == 0:
                        text_to_entry('skip: ' + time_remain, 'orange')

                except IndexError:
                    # In case of error - device not loaded
                    text_to_entry('Device not loaded ', 'orange')

            self.run_id = self.after(1000, update_run)

        self.create_relations_vector()
        update_run()

    def create_relations_vector(self):
        MainGUI = self.master.master.master.master
        self.relations_vector = []
        for i, current_timetable_row in enumerate(MainGUI.sched_file):
            tasknum = MainGUI.findtasknum(i)
            v = []
            for m, current_button in enumerate(MainGUI.ButtonNote.buts):
                if current_button.nick in current_timetable_row[2]:
                    v = [i, m, tasknum[0], tasknum[1]]
                    # v = [index, but#, tsk#, SchRun#]
            self.relations_vector.append(v)


if __name__ == "__main__":
    root = tk.Tk()

    filename = '/Users/guy/Documents/gitHub/Rpi/SmartHome/ButtonsDef2.csv'
    # filename = 'd:/users/guydvir/Documents/git/Rpi/SmartHome/ButtonsDef2.csv'
    b = DeviceConfigGUI(root, data_file_name=filename, list=['hi', 'there', 'little', 'princess'])
    b.grid()
    #
    # filename = 'd:/users/guydvir/Documents/git/Rpi/SmartHome/Schedule.csv'
    # b = TimeTableConfigGUI(root, data_file_name=filename, list=['hi', 'there', 'little', 'princess'])
    b.grid()

    root.mainloop()
