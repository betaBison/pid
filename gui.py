'''
Author: Derek Knowles
Date: 7.2019
Description: Simple PID control GUI
'''

"""
todo:
- add setpoint variable: noise
"""

import sys
sys.path.append('..')

if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk
from ttkthemes import ThemedStyle

from lib.tab import Tab

class Gui(tk.Frame):
    '''
    GUI Class
    '''
    def __init__(self, master = None):
        tk.Frame.__init__(self,master=None)
        self.master = master # gui master handle
        try:
            self.master.attributes('-zoomed', True) # maximizes screen for linux
        except (Exception) as e:
            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
            self.master.geometry("%dx%d+0+0" % (w, h)) # maximizes screen for mac

        self.master.title("PID Control")

        # set up tab notebook
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH,expand=1)

        # ------------------ KEY BINDINGS ---------------------#
        self.master.bind("<Escape>",self.close_window)
        self.master.bind("<<NotebookTabChanged>>",self.tab_change)


        # -----------------_- STEP INPUT  _--------------------#
        self.tab0 = Tab(self.master,self.notebook,"STEP")

        # -----------------_- STEP INPUT  _--------------------#
        self.tab1 = Tab(self.master,self.notebook,"RAMP")

        # -----------------_- STEP INPUT  _--------------------#
        self.tab2 = Tab(self.master,self.notebook,"QUADRATIC")

    def tab_change(self, event):
        """
        runs whenever the tab is changed in the gui
        """
        active_tab = self.notebook.index(self.notebook.select())

        if active_tab == 0:
            self.tab0.run()
        elif active_tab == 1:
            self.tab1.run()
        elif active_tab == 2:
            self.tab2.run()

    def close_window(self,event):
        """
        closes GUI safely
        """
        self.master.destroy()
        sys.exit()

def main():
    root = tk.Tk()
    # change ttk style to something that looks decent
    style = ThemedStyle(root)
    style.set_theme("arc")
    gui = Gui(root)
    try:
        #gui.master.after(200, gui.draw)
        gui.mainloop()
    except KeyboardInterrupt:
        root.destroy()
        sys.exit()

if __name__ == "__main__":
    main()
