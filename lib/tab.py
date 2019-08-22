'''
Author: Derek Knowles
Date: 7.2019
Description: Tab widgets and functions for PID control GUI
'''

import sys

if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
else:
    import tkinter as tk
    from tkinter import ttk
from ttkthemes import ThemedStyle

from .pid import PID

import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from PyQt5.QtWidgets import QApplication
import random


class Tab():
    '''
    Tab Class
    '''
    def __init__(self, master, notebook, type):
        self.master = master # gui master handle
        self.notebook = notebook
        self.type = type
        self.initialized = False


        self.tab = ttk.Frame(self.notebook)
        tab_name = type + " INPUT"
        self.notebook.add(self.tab, text=tab_name)

        # makes resizing possible
        for x in range(10):
            tk.Grid.columnconfigure(self.tab,x,weight=1)
        for y in range(25):
            tk.Grid.rowconfigure(self.tab,y,weight=1)

        self.figure_setup()

    def run(self):
        if not(self.initialized):
            self.initialize()
            self.initialized = True

    def initialize(self):
        if self.type == "STEP":
            self.setpoint_setup_step()
        elif self.type == "RAMP":
            self.setpoint_setup_ramp()
        elif self.type == "QUADRATIC":
            self.setpoint_setup_quadratic()
        else:
            sys.exit('need valid input type (STEP, RAMP, etc.)')

        self.controller_setup()

        self.scrollbar_setup()

        self.random_initialization()

        self.draw()



    def figure_setup(self):
        app = QApplication(sys.argv)
        screen = app.screens()[0]
        my_dpi = screen.physicalDotsPerInch()
        my_size = screen.size()
        screen_width = my_size.width()
        screen_height = my_size.height()
        fig_width = self.tab.winfo_width()*screen_width/my_dpi
        fig_height = 0.5*self.tab.winfo_height()*screen_height/my_dpi
        self.fig = Figure(figsize=(fig_width,fig_height),dpi=my_dpi)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2,rowspan=10,
            column=0,columnspan=10)
        self.my_plot = self.fig.add_subplot(111)
        self.my_plot.set_ylim([-5,5])

    def setpoint_setup_step(self):
        self.hz = 100.0         # time frequency
        self.time_start = 0.0   # start time
        self.time_end = 10.0    # end time
        self.dt = 1.0/self.hz   # timestep
        self.time_length = int((self.time_end-self.time_start)/self.dt)

        # time array
        self.time = np.arange(self.time_start, self.time_end, self.dt)

        self.steady_state_low = -1.5
        self.steady_state_high = 1.5
        self.steady_state_error = 0.0

        self.noise_sigma_low = 0.0
        self.noise_sigma_high = 1.0
        self.noise_sigma = 0.0

        # create setpoint list
        self.setpoint = np.ones((self.time_length,1))
        self.setpoint_with_noise = np.ones((self.time_length,1))
        #  0% - 10% =  0.0
        self.setpoint[0:int(0.1*self.time_length)] *= 0.0
        # 10% - 20% =  1.0
        self.setpoint[int(0.1*self.time_length):int(0.2*self.time_length)] *=  1.0
        # 20% - 30% =  0.0
        self.setpoint[int(0.2*self.time_length):int(0.3*self.time_length)] *=  0.0
        # 30% - 40% = -1.0
        self.setpoint[int(0.3*self.time_length):int(0.4*self.time_length)] *= -1.0
        # 40% - 50% =  0.0
        self.setpoint[int(0.4*self.time_length):int(0.5*self.time_length)] *=  0.0
        # 50% - 60% =  1.0
        self.setpoint[int(0.5*self.time_length):int(0.6*self.time_length)] *=  1.0
        # 60% - 70% = -1.0
        self.setpoint[int(0.6*self.time_length):int(0.7*self.time_length)] *= -1.0
        # 70% - 80% =  2.0
        self.setpoint[int(0.7*self.time_length):int(0.8*self.time_length)] *=  2.0
        # 80% - 90% = -3.0
        self.setpoint[int(0.8*self.time_length):int(0.9*self.time_length)] *= -3.0
        # 90% -100% =  0.0
        self.setpoint[int(0.9*self.time_length):] *= -0.0

        self.setpoint_noise_update()

    def setpoint_setup_ramp(self):
        self.hz = 100.0         # time frequency
        self.time_start = 0.0   # start time
        self.time_end = 10.0    # end time
        self.dt = 1.0/self.hz   # timestep
        self.time_length = int((self.time_end-self.time_start)/self.dt)

        # time array
        self.time = np.arange(self.time_start, self.time_end, self.dt)

        self.steady_state_low = -1.5
        self.steady_state_high = 1.5
        self.steady_state_error = 0.0

        self.noise_sigma_low = 0.0
        self.noise_sigma_high = 1.0
        self.noise_sigma = 0.0

        # create setpoint list
        self.setpoint = np.ones((self.time_length,1))
        self.setpoint_with_noise = np.ones((self.time_length,1))
        #  0% - 10% =  0.0
        self.setpoint[0:int(0.1*self.time_length)] *= 0.0
        # 10% - 20% =  1.0 ramp
        for ii in range(int(0.1*self.time_length),int(0.15*self.time_length)):
            self.setpoint[ii] = 2.0 * self.time[ii] - 2.0
        for ii in range(int(0.15*self.time_length),int(0.2*self.time_length)):
            self.setpoint[ii] = -2.0 * self.time[ii] + 4.0
        # 20% - 30% =  0.0
        self.setpoint[int(0.2*self.time_length):int(0.3*self.time_length)] *=  0.0
        # 30% - 40% = -1.0 ramp
        for ii in range(int(0.3*self.time_length),int(0.35*self.time_length)):
            self.setpoint[ii] = -2.0 * self.time[ii] + 6.0
        for ii in range(int(0.35*self.time_length),int(0.4*self.time_length)):
            self.setpoint[ii] = 2.0 * self.time[ii] - 8.0
        # 40% - 50% =  0.0
        self.setpoint[int(0.4*self.time_length):int(0.5*self.time_length)] *=  0.0
        # 50% - 60% =  1.0 ramp
        for ii in range(int(0.5*self.time_length),int(0.55*self.time_length)):
            self.setpoint[ii] = 2.0 * self.time[ii] - 10.0
        for ii in range(int(0.55*self.time_length),int(0.6*self.time_length)):
            self.setpoint[ii] = -2.0 * self.time[ii] + 12.0
        # 60% - 70% = -1.0 ramp
        for ii in range(int(0.6*self.time_length),int(0.65*self.time_length)):
            self.setpoint[ii] = -2.0 * self.time[ii] + 12.0
        for ii in range(int(0.65*self.time_length),int(0.7*self.time_length)):
            self.setpoint[ii] = 2.0 * self.time[ii] - 14.0
        # 70% - 80% =  2.0 ramp
        for ii in range(int(0.7*self.time_length),int(0.75*self.time_length)):
            self.setpoint[ii] = 4.0 * (self.time[ii] - 7.0)
        for ii in range(int(0.75*self.time_length),int(0.8*self.time_length)):
            self.setpoint[ii] = -4.0 * (self.time[ii] - 7.5) + 2.0
        # 80% - 90% = -3.0 ramp
        for ii in range(int(0.8*self.time_length),int(0.85*self.time_length)):
            self.setpoint[ii] = -6.0 * (self.time[ii] - 8.0)
        for ii in range(int(0.85*self.time_length),int(0.9*self.time_length)):
            self.setpoint[ii] = 6.0 * (self.time[ii] - 8.5) - 3.0
        # 90% -100% =  0.0
        self.setpoint[int(0.9*self.time_length):] *= -0.0

        self.setpoint_noise_update()

    def setpoint_setup_quadratic(self):
        self.hz = 100.0         # time frequency
        self.time_start = 0.0   # start time
        self.time_end = 10.0    # end time
        self.dt = 1.0/self.hz   # timestep
        self.time_length = int((self.time_end-self.time_start)/self.dt)

        # time array
        self.time = np.arange(self.time_start, self.time_end, self.dt)

        self.steady_state_low = -1.5
        self.steady_state_high = 1.5
        self.steady_state_error = 0.0

        self.noise_sigma_low = 0.0
        self.noise_sigma_high = 1.0
        self.noise_sigma = 0.0

        # create setpoint list
        self.setpoint = np.ones((self.time_length,1))
        self.setpoint_with_noise = np.ones((self.time_length,1))
        #  0% - 10% =  0.0
        self.setpoint[0:int(0.1*self.time_length)] *= 0.0
        # 10% - 20% =  1.0 parabola
        for ii in range(int(0.1*self.time_length),int(0.2*self.time_length)):
            self.setpoint[ii] = -4.0 * (self.time[ii] - 1.5)**2 + 1.0
        # 20% - 30% =  0.0
        self.setpoint[int(0.2*self.time_length):int(0.3*self.time_length)] *=  0.0
        # 30% - 40% = -1.0 parabola
        for ii in range(int(0.3*self.time_length),int(0.4*self.time_length)):
            self.setpoint[ii] = 4.0 * (self.time[ii] - 3.5)**2 - 1.0
        # 40% - 50% =  0.0
        self.setpoint[int(0.4*self.time_length):int(0.5*self.time_length)] *=  0.0
        # 50% - 60% =  1.0 parabola
        for ii in range(int(0.5*self.time_length),int(0.6*self.time_length)):
            self.setpoint[ii] = -4.0 * (self.time[ii] - 5.5)**2 + 1.0
        # 60% - 70% = -1.0 parabola
        for ii in range(int(0.6*self.time_length),int(0.7*self.time_length)):
            self.setpoint[ii] = 4.0 * (self.time[ii] - 6.5)**2 - 1.0
        # 70% - 80% =  2.0 parabola
        for ii in range(int(0.7*self.time_length),int(0.8*self.time_length)):
            self.setpoint[ii] = -8.0 * (self.time[ii] - 7.5)**2 + 2.0
        # 80% - 90% = -3.0 parabola
        for ii in range(int(0.8*self.time_length),int(0.9*self.time_length)):
            self.setpoint[ii] = 12.0 * (self.time[ii] - 8.5)**2 - 3.0
        # 90% -100% =  0.0
        self.setpoint[int(0.9*self.time_length):] *= -0.0

        self.setpoint_noise_update()

    def setpoint_noise_update(self):
        for ii in range(self.time_length):
            self.setpoint_with_noise[ii] = self.setpoint[ii] \
                + self.noise_sigma*np.random.randn()

    def controller_setup(self):

        # setup results lists
        self.controller_1_result = np.zeros((self.time_length,1))
        self.controller_2_result = np.zeros((self.time_length,1))
        self.controller_3_result = np.zeros((self.time_length,1))
        self.controller_4_result = np.zeros((self.time_length,1))

        # setup gains
        self.kp_low = 0.0
        self.kp_high = 2.0
        self.kps = [tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab)]

        self.ki_low = 0.0
        self.ki_high = 20.0
        self.kis = [tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab)]

        self.kd_low = 0.0
        self.kd_high = 0.25
        self.kds = [tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab),
                    tk.DoubleVar(self.tab)]

        self.feed_forward_low = -5.0
        self.feed_forward_high = 5.0
        self.feed_forwards = [tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab)]

        self.noise_sigma_low    # defined in setpoint_setup_*()
        self.noise_sigma_high   # defined in setpoint_setup_*()
        self.noise_sigmas = [tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab),
                              tk.DoubleVar(self.tab)]

        #setup controllers
        self.controller_1 = PID(self.kps[0].get(),self.kis[0].get(),self.kds[0].get())
        self.controller_2 = PID(self.kps[1].get(),self.kis[1].get(),self.kds[1].get())
        self.controller_3 = PID(self.kps[2].get(),self.kis[2].get(),self.kds[2].get())
        self.controller_4 = PID(self.kps[3].get(),self.kis[3].get(),self.kds[3].get())

        # update results with initialized gains
        self.controller_update(self.controller_1,self.controller_1_result)
        self.controller_update(self.controller_2,self.controller_2_result)
        self.controller_update(self.controller_3,self.controller_3_result)
        self.controller_update(self.controller_4,self.controller_4_result)

    def random_number(self,low,high):
        number = random.random()*(high-low)+low
        return number

    def random_initialization(self):
        for ii in range(4):
            random_kp = self.random_number(self.kp_low + 0.2*(self.kp_high - self.kp_low)
                ,self.kp_low + 0.8*(self.kp_high - self.kp_low))
            self.kps[ii].set(random_kp)
            self.kp_scrollbars[ii].set(random_kp)
            random_ki = self.random_number(self.ki_low,self.ki_high)
            self.kis[ii].set(random_ki)
            self.ki_scrollbars[ii].set(random_ki)
        random_steady_state = self.random_number(self.steady_state_low,self.steady_state_high)
        self.steady_state.set(random_steady_state)
        self.steady_state_scrollbar.set(random_steady_state)

    def controller_update(self,controller,result):
        controller.reset()
        for ii in range(1,self.time_length):
            result[ii] = controller.update(result[ii-1],
                self.setpoint_with_noise[ii],self.dt) \
                + self.steady_state_error

    def draw(self):

        self.my_plot.clear() # clear the graph

        # plot the setpoint
        self.my_plot.plot(self.time,self.setpoint_with_noise
            ,color='xkcd:indigo')

        # plot the controllers
        if self.controller_1_enabled.get():
            self.my_plot.plot(self.time,self.controller_1_result,
                color='xkcd:orangered')
        if self.controller_2_enabled.get():
            self.my_plot.plot(self.time,self.controller_2_result,
                color='xkcd:goldenrod')
        if self.controller_3_enabled.get():
            self.my_plot.plot(self.time,self.controller_3_result,
                color='xkcd:azure')
        if self.controller_4_enabled.get():
            self.my_plot.plot(self.time,self.controller_4_result,
                color='xkcd:teal')

        self.my_plot.set_ylim([-3.2,3.2])

        self.canvas.draw()

    def steady_state_scrollbar_update(self,value):
        self.steady_state.set(value)
        self.steady_state_error = float(value)
        self.controller_update(self.controller_1,self.controller_1_result)
        self.controller_update(self.controller_2,self.controller_2_result)
        self.controller_update(self.controller_3,self.controller_3_result)
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def steady_state_entry_update(self,event):
        try:
            entry = float(self.steady_state_entry.get())
            value = np.clip(entry,self.steady_state_low,self.steady_state_high)
            self.steady_state_scrollbar.set(float(value))
        except ValueError:
            self.steady_state.set(self.steady_state_error)

    def noise_sigma_scrollbar_update(self,value):
        self.noise_sigma_var.set(value)
        self.noise_sigma = float(value)
        self.setpoint_noise_update()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.controller_update(self.controller_2,self.controller_2_result)
        self.controller_update(self.controller_3,self.controller_3_result)
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def noise_sigma_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entry.get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbar.set(float(value))
        except ValueError:
            self.noise_sigma_var.set(self.noise_sigma)

    def kp_1_scrollbar_update(self,value):
        self.kps[0].set(value)
        self.controller_1.kp = float(value)
        self.controller_1.ki = self.ki_scrollbars[0].get()
        self.controller_1.kd = self.kd_scrollbars[0].get()
        self.controller_1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller_1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def kp_1_entry_update(self,event):
        try:
            entry = float(self.kp_entries[0].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[0].set(float(value))
        except ValueError:
            self.kps[0].set(self.controller_1.kp)

    def kp_2_scrollbar_update(self,value):
        self.kps[1].set(value)
        self.controller_2.kp = float(value)
        self.controller_2.ki = self.ki_scrollbars[1].get()
        self.controller_2.kd = self.kd_scrollbars[1].get()
        self.controller_2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller_2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def kp_2_entry_update(self,event):
        try:
            entry = float(self.kp_entries[1].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[1].set(float(value))
        except ValueError:
            self.kps[1].set(self.controller_2.kp)

    def kp_3_scrollbar_update(self,value):
        self.kps[2].set(value)
        self.controller_3.kp = float(value)
        self.controller_3.ki = self.ki_scrollbars[2].get()
        self.controller_3.kd = self.kd_scrollbars[2].get()
        self.controller_3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller_3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def kp_3_entry_update(self,event):
        try:
            entry = float(self.kp_entries[2].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[2].set(float(value))
        except ValueError:
            self.kps[2].set(self.controller_3.kp)

    def kp_4_scrollbar_update(self,value):
        self.kps[3].set(value)
        self.controller_4.kp = float(value)
        self.controller_4.ki = self.ki_scrollbars[3].get()
        self.controller_4.kd = self.kd_scrollbars[3].get()
        self.controller_4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller_4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def kp_4_entry_update(self,event):
        try:
            entry = float(self.kp_entries[3].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[3].set(float(value))
        except ValueError:
            self.kps[3].set(self.controller_4.kp)

    def ki_1_scrollbar_update(self,value):
        self.kis[0].set(value)
        self.controller_1.kp = self.kp_scrollbars[0].get()
        self.controller_1.ki = float(value)
        self.controller_1.kd = self.kd_scrollbars[0].get()
        self.controller_1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller_1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def ki_1_entry_update(self,event):
        try:
            entry = float(self.ki_entries[0].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[0].set(float(value))
        except ValueError:
            self.kis[0].set(self.controller_1.ki)

    def ki_2_scrollbar_update(self,value):
        self.kis[1].set(value)
        self.controller_2.kp = self.kp_scrollbars[1].get()
        self.controller_2.ki = float(value)
        self.controller_2.kd = self.kd_scrollbars[1].get()
        self.controller_2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller_2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def ki_2_entry_update(self,event):
        try:
            entry = float(self.ki_entries[1].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[1].set(float(value))
        except ValueError:
            self.kis[1].set(self.controller_2.ki)

    def ki_3_scrollbar_update(self,value):
        self.kis[2].set(value)
        self.controller_3.kp = self.kp_scrollbars[2].get()
        self.controller_3.ki = float(value)
        self.controller_3.kd = self.kd_scrollbars[2].get()
        self.controller_3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller_3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def ki_3_entry_update(self,event):
        try:
            entry = float(self.ki_entries[2].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[2].set(float(value))
        except ValueError:
            self.kis[2].set(self.controller_3.ki)

    def ki_4_scrollbar_update(self,value):
        self.kis[3].set(value)
        self.controller_4.kp = self.kp_scrollbars[3].get()
        self.controller_4.ki = float(value)
        self.controller_4.kd = self.kd_scrollbars[3].get()
        self.controller_4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller_4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def ki_4_entry_update(self,event):
        try:
            entry = float(self.ki_entries[3].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[3].set(float(value))
        except ValueError:
            self.kis[3].set(self.controller_4.ki)

    def kd_1_scrollbar_update(self,value):
        self.kds[0].set(value)
        self.controller_1.kp = self.kp_scrollbars[0].get()
        self.controller_1.ki = self.ki_scrollbars[0].get()
        self.controller_1.kd = float(value)
        self.controller_1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller_1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def kd_1_entry_update(self,event):
        try:
            entry = float(self.kd_entries[0].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[0].set(float(value))
        except ValueError:
            self.kds[0].set(self.controller_1.kd)

    def kd_2_scrollbar_update(self,value):
        self.kds[1].set(value)
        self.controller_2.kp = self.kp_scrollbars[1].get()
        self.controller_2.ki = self.ki_scrollbars[1].get()
        self.controller_2.kd = float(value)
        self.controller_2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller_2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def kd_2_entry_update(self,event):
        try:
            entry = float(self.kd_entries[1].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[1].set(float(value))
        except ValueError:
            self.kds[1].set(self.controller_2.kd)

    def kd_3_scrollbar_update(self,value):
        self.kds[2].set(value)
        self.controller_3.kp = self.kp_scrollbars[2].get()
        self.controller_3.ki = self.ki_scrollbars[2].get()
        self.controller_3.kd = float(value)
        self.controller_3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller_3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def kd_3_entry_update(self,event):
        try:
            entry = float(self.kd_entries[2].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[2].set(float(value))
        except ValueError:
            self.kds[2].set(self.controller_3.kd)

    def kd_4_scrollbar_update(self,value):
        self.kds[3].set(value)
        self.controller_4.kp = self.kp_scrollbars[3].get()
        self.controller_4.ki = self.ki_scrollbars[3].get()
        self.controller_4.kd = float(value)
        self.controller_4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller_4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def kd_4_entry_update(self,event):
        try:
            entry = float(self.kd_entries[3].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[3].set(float(value))
        except ValueError:
            self.kds[3].set(self.controller_4.kd)

    def kd_1_type_update(self):
        self.controller_1.kd_error = self.kd_1_type.get()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def kd_2_type_update(self):
        self.controller_2.kd_error = self.kd_2_type.get()
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def kd_3_type_update(self):
        self.controller_3.kd_error = self.kd_3_type.get()
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def kd_4_type_update(self):
        self.controller_4.kd_error = self.kd_4_type.get()
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def feed_forward_1_scrollbar_update(self,value):
        self.feed_forwards[0].set(value)
        self.controller_1.kp = self.kp_scrollbars[0].get()
        self.controller_1.ki = self.ki_scrollbars[0].get()
        self.controller_1.kd = self.kd_scrollbars[0].get()
        self.controller_1.feed_forward = float(value)
        self.controller_1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def feed_forward_1_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[0].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[0].set(float(value))
        except ValueError:
            self.feed_forwards[0].set(self.controller_1.feed_forward)

    def feed_forward_2_scrollbar_update(self,value):
        self.feed_forwards[1].set(value)
        self.controller_2.kp = self.kp_scrollbars[1].get()
        self.controller_2.ki = self.ki_scrollbars[1].get()
        self.controller_2.kd = self.kd_scrollbars[1].get()
        self.controller_2.feed_forward = float(value)
        self.controller_2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def feed_forward_2_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[1].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[1].set(float(value))
        except ValueError:
            self.feed_forwards[1].set(self.controller_2.feed_forward)

    def feed_forward_3_scrollbar_update(self,value):
        self.feed_forwards[2].set(value)
        self.controller_3.kp = self.kp_scrollbars[2].get()
        self.controller_3.ki = self.ki_scrollbars[2].get()
        self.controller_3.kd = self.kd_scrollbars[2].get()
        self.controller_3.feed_forward = float(value)
        self.controller_3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def feed_forward_3_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[2].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[2].set(float(value))
        except ValueError:
            self.feed_forwards[2].set(self.controller_3.feed_forward)

    def feed_forward_4_scrollbar_update(self,value):
        self.feed_forwards[3].set(value)
        self.controller_4.kp = self.kp_scrollbars[3].get()
        self.controller_4.ki = self.ki_scrollbars[3].get()
        self.controller_4.kd = self.kd_scrollbars[3].get()
        self.controller_4.feed_forward = float(value)
        self.controller_4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def feed_forward_4_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[3].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[3].set(float(value))
        except ValueError:
            self.feed_forwards[3].set(self.controller_4.feed_forward)

    def noise_sigma_1_scrollbar_update(self,value):
        self.noise_sigmas[0].set(value)
        self.controller_1.kp = self.kp_scrollbars[0].get()
        self.controller_1.ki = self.ki_scrollbars[0].get()
        self.controller_1.kd = self.kd_scrollbars[0].get()
        self.controller_1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller_1.noise_sigma = float(value)
        self.controller_update(self.controller_1,self.controller_1_result)
        self.draw()

    def noise_sigma_1_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[0].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[0].set(float(value))
        except ValueError:
            self.noise_sigmas[0].set(self.controller_1.noise_sigma)

    def noise_sigma_2_scrollbar_update(self,value):
        self.noise_sigmas[1].set(value)
        self.controller_2.kp = self.kp_scrollbars[1].get()
        self.controller_2.ki = self.ki_scrollbars[1].get()
        self.controller_2.kd = self.kd_scrollbars[1].get()
        self.controller_2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller_2.noise_sigma = float(value)
        self.controller_update(self.controller_2,self.controller_2_result)
        self.draw()

    def noise_sigma_2_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[1].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[1].set(float(value))
        except ValueError:
            self.noise_sigmas[1].set(self.controller_2.noise_sigma)

    def noise_sigma_3_scrollbar_update(self,value):
        self.noise_sigmas[2].set(value)
        self.controller_3.kp = self.kp_scrollbars[2].get()
        self.controller_3.ki = self.ki_scrollbars[2].get()
        self.controller_3.kd = self.kd_scrollbars[2].get()
        self.controller_3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller_3.noise_sigma = float(value)
        self.controller_update(self.controller_3,self.controller_3_result)
        self.draw()

    def noise_sigma_3_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[2].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[2].set(float(value))
        except ValueError:
            self.noise_sigmas[2].set(self.controller_3.noise_sigma)

    def noise_sigma_4_scrollbar_update(self,value):
        self.noise_sigmas[3].set(value)
        self.controller_4.kp = self.kp_scrollbars[3].get()
        self.controller_4.ki = self.ki_scrollbars[3].get()
        self.controller_4.kd = self.kd_scrollbars[3].get()
        self.controller_4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller_4.noise_sigma = float(value)
        self.controller_update(self.controller_4,self.controller_4_result)
        self.draw()

    def noise_sigma_4_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[3].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[3].set(float(value))
        except ValueError:
            self.noise_sigmas[3].set(self.controller_4.noise_sigma)

    def enable_controller_1(self):
        if self.controller_1_enabled.get():
            self.kp_scrollbars[0].state(["!disabled"])
            self.kp_entries[0].configure(state=tk.NORMAL)
            self.ki_scrollbars[0].state(["!disabled"])
            self.ki_entries[0].configure(state=tk.NORMAL)
            self.kd_scrollbars[0].state(["!disabled"])
            self.kd_entries[0].configure(state=tk.NORMAL)
            self.kd_1_type_state.configure(state=tk.NORMAL)
            self.kd_1_type_error.configure(state=tk.NORMAL)
            self.feed_forward_scrollbars[0].state(["!disabled"])
            self.feed_forward_entries[0].configure(state=tk.NORMAL)
            self.noise_sigma_scrollbars[0].state(["!disabled"])
            self.noise_sigma_entries[0].configure(state=tk.NORMAL)
        else:
            self.kp_scrollbars[0].state(["disabled"])
            self.kp_entries[0].configure(state=tk.DISABLED)
            self.ki_scrollbars[0].state(["disabled"])
            self.ki_entries[0].configure(state=tk.DISABLED)
            self.kd_scrollbars[0].state(["disabled"])
            self.kd_entries[0].configure(state=tk.DISABLED)
            self.kd_1_type_state.configure(state=tk.DISABLED)
            self.kd_1_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[0].state(["disabled"])
            self.feed_forward_entries[0].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[0].state(["disabled"])
            self.noise_sigma_entries[0].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller_2(self):
        if self.controller_2_enabled.get():
            self.kp_scrollbars[1].state(["!disabled"])
            self.kp_entries[1].configure(state=tk.NORMAL)
            self.ki_scrollbars[1].state(["!disabled"])
            self.ki_entries[1].configure(state=tk.NORMAL)
            self.kd_scrollbars[1].state(["!disabled"])
            self.kd_entries[1].configure(state=tk.NORMAL)
            self.kd_2_type_state.configure(state=tk.NORMAL)
            self.kd_2_type_error.configure(state=tk.NORMAL)
            self.feed_forward_scrollbars[1].state(["!disabled"])
            self.feed_forward_entries[1].configure(state=tk.NORMAL)
            self.noise_sigma_scrollbars[1].state(["!disabled"])
            self.noise_sigma_entries[1].configure(state=tk.NORMAL)
        else:
            self.kp_scrollbars[1].state(["disabled"])
            self.kp_entries[1].configure(state=tk.DISABLED)
            self.ki_scrollbars[1].state(["disabled"])
            self.ki_entries[1].configure(state=tk.DISABLED)
            self.kd_scrollbars[1].state(["disabled"])
            self.kd_entries[1].configure(state=tk.DISABLED)
            self.kd_2_type_state.configure(state=tk.DISABLED)
            self.kd_2_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[1].state(["disabled"])
            self.feed_forward_entries[1].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[1].state(["disabled"])
            self.noise_sigma_entries[1].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller_3(self):
        if self.controller_3_enabled.get():
            self.kp_scrollbars[2].state(["!disabled"])
            self.kp_entries[2].configure(state=tk.NORMAL)
            self.ki_scrollbars[2].state(["!disabled"])
            self.ki_entries[2].configure(state=tk.NORMAL)
            self.kd_scrollbars[2].state(["!disabled"])
            self.kd_entries[2].configure(state=tk.NORMAL)
            self.kd_3_type_state.configure(state=tk.NORMAL)
            self.kd_3_type_error.configure(state=tk.NORMAL)
            self.feed_forward_scrollbars[2].state(["!disabled"])
            self.feed_forward_entries[2].configure(state=tk.NORMAL)
            self.noise_sigma_scrollbars[2].state(["!disabled"])
            self.noise_sigma_entries[2].configure(state=tk.NORMAL)
        else:
            self.kp_scrollbars[2].state(["disabled"])
            self.kp_entries[2].configure(state=tk.DISABLED)
            self.ki_scrollbars[2].state(["disabled"])
            self.ki_entries[2].configure(state=tk.DISABLED)
            self.kd_scrollbars[2].state(["disabled"])
            self.kd_entries[2].configure(state=tk.DISABLED)
            self.kd_3_type_state.configure(state=tk.DISABLED)
            self.kd_3_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[2].state(["disabled"])
            self.feed_forward_entries[2].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[2].state(["disabled"])
            self.noise_sigma_entries[2].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller_4(self):
        if self.controller_4_enabled.get():
            self.kp_scrollbars[3].state(["!disabled"])
            self.kp_entries[3].configure(state=tk.NORMAL)
            self.ki_scrollbars[3].state(["!disabled"])
            self.ki_entries[3].configure(state=tk.NORMAL)
            self.kd_scrollbars[3].state(["!disabled"])
            self.kd_entries[3].configure(state=tk.NORMAL)
            self.kd_4_type_state.configure(state=tk.NORMAL)
            self.kd_4_type_error.configure(state=tk.NORMAL)
            self.feed_forward_scrollbars[3].state(["!disabled"])
            self.feed_forward_entries[3].configure(state=tk.NORMAL)
            self.noise_sigma_scrollbars[3].state(["!disabled"])
            self.noise_sigma_entries[3].configure(state=tk.NORMAL)
        else:
            self.kp_scrollbars[3].state(["disabled"])
            self.kp_entries[3].configure(state=tk.DISABLED)
            self.ki_scrollbars[3].state(["disabled"])
            self.ki_entries[3].configure(state=tk.DISABLED)
            self.kd_scrollbars[3].state(["disabled"])
            self.kd_entries[3].configure(state=tk.DISABLED)
            self.kd_4_type_state.configure(state=tk.DISABLED)
            self.kd_4_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[3].state(["disabled"])
            self.feed_forward_entries[3].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[3].state(["disabled"])
            self.noise_sigma_entries[3].configure(state=tk.DISABLED)
        self.draw()

    def scrollbar_setup(self):

        # Setpoint
        setpoint_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Setpoint Variables', foreground='midnight blue')
        setpoint_label.grid(row=12,rowspan=2,column=0, columnspan=2)
        steady_state_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Steady State Error',foreground='midnight blue')
        steady_state_label.grid(row=14,rowspan=1,column=0,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.steady_state_scrollbar = ttk.Scale(self.tab,
            from_=self.steady_state_low, to=self.steady_state_high,
            command=self.steady_state_scrollbar_update)
        self.steady_state_scrollbar.grid(row=15,column=0,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        self.steady_state = tk.DoubleVar(self.tab)
        self.steady_state_entry = ttk.Entry(self.tab,textvariable=self.steady_state)
        self.steady_state_entry.bind("<Return>",self.steady_state_entry_update)
        self.steady_state_entry.grid(row=15,column=1,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Noise Sigma',foreground='midnight blue')
        noise_sigma_label.grid(row=16,rowspan=1,column=0,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.noise_sigma_scrollbar = ttk.Scale(self.tab,
            from_=self.noise_sigma_low, to=self.noise_sigma_high,
            command=self.noise_sigma_scrollbar_update)
        self.noise_sigma_scrollbar.grid(row=17,column=0,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        self.noise_sigma_var = tk.DoubleVar(self.tab)
        self.noise_sigma_entry = ttk.Entry(self.tab,textvariable=self.noise_sigma_var)
        self.noise_sigma_entry.bind("<Return>",self.noise_sigma_entry_update)
        self.noise_sigma_entry.grid(row=17,column=1,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)

        # PID # 1
        pid_1_label = ttk.Label(self.tab, anchor=tk.W,
            text='PID Controller #1',foreground='orange red')
        pid_1_label.grid(row=12,rowspan=2,column=3,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.controller_1_enabled = tk.BooleanVar()
        self.controller_1_enabled.set(True)
        controller_1_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller_1_enabled, command=self.enable_controller_1)
        controller_1_checkbox.grid(row=12,rowspan=2,column=2,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='orange red')
        kp_1_label.grid(row=14,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp_1_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp_1_scrollbar_update)
        kp_1_scrollbar.grid(row=15,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp_1_entry = ttk.Entry(self.tab,textvariable=self.kps[0])
        kp_1_entry.bind("<Return>",self.kp_1_entry_update)
        kp_1_entry.grid(row=15,column=3,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='orange red')
        ki_1_label.grid(row=16,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki_1_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki_1_scrollbar_update)
        ki_1_scrollbar.grid(row=17,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_1_entry = ttk.Entry(self.tab,textvariable=self.kis[0])
        ki_1_entry.bind("<Return>",self.ki_1_entry_update)
        ki_1_entry.grid(row=17,column=3,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='orange red')
        kd_1_label.grid(row=18,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_1_type = tk.BooleanVar()
        self.kd_1_type.set(True)
        self.kd_1_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd_1_type,
            command=self.kd_1_type_update)
        self.kd_1_type_error.grid(row=19,rowspan=1,column=2,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_1_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd_1_type,
            command=self.kd_1_type_update)
        self.kd_1_type_state.grid(row=19,rowspan=1,column=3,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd_1_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd_1_scrollbar_update)
        kd_1_scrollbar.grid(row=20,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_1_entry = ttk.Entry(self.tab,textvariable=self.kds[0])
        kd_1_entry.bind("<Return>",self.kd_1_entry_update)
        kd_1_entry.grid(row=20,column=3,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Feed Forward',foreground='orange red')
        feed_forward_1_label.grid(row=21,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        feed_forward_1_scrollbar = ttk.Scale(self.tab,
            from_=self.feed_forward_low, to=self.feed_forward_high,
            command=self.feed_forward_1_scrollbar_update)
        feed_forward_1_scrollbar.grid(row=23,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_1_entry = ttk.Entry(self.tab,
            textvariable=self.feed_forwards[0])
        feed_forward_1_entry.bind("<Return>",self.feed_forward_1_entry_update)
        feed_forward_1_entry.grid(row=23,column=3,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Noise Sigma',foreground='orange red')
        noise_sigma_1_label.grid(row=24,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        noise_sigma_1_scrollbar = ttk.Scale(self.tab,
            from_=self.noise_sigma_low, to=self.noise_sigma_high,
            command=self.noise_sigma_1_scrollbar_update)
        noise_sigma_1_scrollbar.grid(row=25,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_1_entry = ttk.Entry(self.tab,
            textvariable=self.noise_sigmas[0])
        noise_sigma_1_entry.bind("<Return>",self.noise_sigma_1_entry_update)
        noise_sigma_1_entry.grid(row=25,column=3,
            sticky=tk.E+tk.W,padx=5,pady=5)

        # PID #2
        pid_2_label = ttk.Label(self.tab, anchor=tk.W,
            text='PID Controller #2',foreground='goldenrod')
        pid_2_label.grid(row=12,rowspan=2,column=5,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.controller_2_enabled = tk.BooleanVar()
        self.controller_2_enabled.set(True)
        controller_2_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller_2_enabled, command=self.enable_controller_2)
        controller_2_checkbox.grid(row=12,rowspan=2,column=4,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='goldenrod')
        kp_2_label.grid(row=14,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp_2_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp_2_scrollbar_update)
        kp_2_scrollbar.grid(row=15,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp_2_entry = ttk.Entry(self.tab,textvariable=self.kps[1])
        kp_2_entry.bind("<Return>",self.kp_2_entry_update)
        kp_2_entry.grid(row=15,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='goldenrod')
        ki_2_label.grid(row=16,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki_2_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki_2_scrollbar_update)
        ki_2_scrollbar.grid(row=17,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_2_entry = ttk.Entry(self.tab,textvariable=self.kis[1])
        ki_2_entry.bind("<Return>",self.ki_2_entry_update)
        ki_2_entry.grid(row=17,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='goldenrod')
        kd_2_label.grid(row=18,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_2_type = tk.BooleanVar()
        self.kd_2_type.set(True)
        self.kd_2_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd_2_type,
            command=self.kd_2_type_update)
        self.kd_2_type_error.grid(row=19,rowspan=1,column=4,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_2_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd_2_type,
            command=self.kd_2_type_update)
        self.kd_2_type_state.grid(row=19,rowspan=1,column=5,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd_2_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd_2_scrollbar_update)
        kd_2_scrollbar.grid(row=20,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_2_entry = ttk.Entry(self.tab,textvariable=self.kds[1])
        kd_2_entry.bind("<Return>",self.kd_2_entry_update)
        kd_2_entry.grid(row=20,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Feed Forward',foreground='goldenrod')
        feed_forward_2_label.grid(row=21,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        feed_forward_2_scrollbar = ttk.Scale(self.tab,
            from_=self.feed_forward_low, to=self.feed_forward_high,
            command=self.feed_forward_2_scrollbar_update)
        feed_forward_2_scrollbar.grid(row=23,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_2_entry = ttk.Entry(self.tab,
            textvariable=self.feed_forwards[1])
        feed_forward_2_entry.bind("<Return>",self.feed_forward_2_entry_update)
        feed_forward_2_entry.grid(row=23,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Noise Sigma',foreground='goldenrod')
        noise_sigma_2_label.grid(row=24,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        noise_sigma_2_scrollbar = ttk.Scale(self.tab,
            from_=self.noise_sigma_low, to=self.noise_sigma_high,
            command=self.noise_sigma_2_scrollbar_update)
        noise_sigma_2_scrollbar.grid(row=25,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_2_entry = ttk.Entry(self.tab,
            textvariable=self.noise_sigmas[1])
        noise_sigma_2_entry.bind("<Return>",self.noise_sigma_2_entry_update)
        noise_sigma_2_entry.grid(row=25,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)


        # PID #3
        pid_3_label = ttk.Label(self.tab, anchor=tk.W,
            text='PID Controller #3',foreground='DodgerBlue2')
        pid_3_label.grid(row=12,rowspan=2,column=7,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.controller_3_enabled = tk.BooleanVar()
        self.controller_3_enabled.set(True)
        controller_3_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller_3_enabled, command=self.enable_controller_3)
        controller_3_checkbox.grid(row=12,rowspan=2,column=6,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='DodgerBlue2')
        kp_3_label.grid(row=14,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp_3_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp_3_scrollbar_update)
        kp_3_scrollbar.grid(row=15,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp_3_entry = ttk.Entry(self.tab,textvariable=self.kps[2])
        kp_3_entry.bind("<Return>",self.kp_3_entry_update)
        kp_3_entry.grid(row=15,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='DodgerBlue2')
        ki_3_label.grid(row=16,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki_3_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki_3_scrollbar_update)
        ki_3_scrollbar.grid(row=17,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_3_entry = ttk.Entry(self.tab,textvariable=self.kis[2])
        ki_3_entry.bind("<Return>",self.ki_3_entry_update)
        ki_3_entry.grid(row=17,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='DodgerBlue2')
        kd_3_label.grid(row=18,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_3_type = tk.BooleanVar()
        self.kd_3_type.set(True)
        self.kd_3_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd_3_type,
            command=self.kd_3_type_update)
        self.kd_3_type_error.grid(row=19,rowspan=1,column=6,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_3_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd_3_type,
            command=self.kd_3_type_update)
        self.kd_3_type_state.grid(row=19,rowspan=1,column=7,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd_3_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd_3_scrollbar_update)
        kd_3_scrollbar.grid(row=20,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_3_entry = ttk.Entry(self.tab,textvariable=self.kds[2])
        kd_3_entry.bind("<Return>",self.kd_3_entry_update)
        kd_3_entry.grid(row=20,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Feed Forward',foreground='DodgerBlue2')
        feed_forward_3_label.grid(row=21,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        feed_forward_3_scrollbar = ttk.Scale(self.tab,
            from_=self.feed_forward_low, to=self.feed_forward_high,
            command=self.feed_forward_3_scrollbar_update)
        feed_forward_3_scrollbar.grid(row=23,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_3_entry = ttk.Entry(self.tab,
            textvariable=self.feed_forwards[2])
        feed_forward_3_entry.bind("<Return>",self.feed_forward_3_entry_update)
        feed_forward_3_entry.grid(row=23,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Noise Sigma',foreground='DodgerBlue2')
        noise_sigma_3_label.grid(row=24,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        noise_sigma_3_scrollbar = ttk.Scale(self.tab,
            from_=self.noise_sigma_low, to=self.noise_sigma_high,
            command=self.noise_sigma_3_scrollbar_update)
        noise_sigma_3_scrollbar.grid(row=25,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_3_entry = ttk.Entry(self.tab,
            textvariable=self.noise_sigmas[2])
        noise_sigma_3_entry.bind("<Return>",self.noise_sigma_3_entry_update)
        noise_sigma_3_entry.grid(row=25,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)

        # PID #4
        pid_4_label = ttk.Label(self.tab, anchor=tk.W,
            text='PID Controller #4',foreground='cyan4')
        pid_4_label.grid(row=12,rowspan=2,column=9,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.controller_4_enabled = tk.BooleanVar()
        self.controller_4_enabled.set(True)
        controller_4_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller_4_enabled, command=self.enable_controller_4)
        controller_4_checkbox.grid(row=12,rowspan=2,column=8,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='cyan4')
        kp_4_label.grid(row=14,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp_4_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp_4_scrollbar_update)
        kp_4_scrollbar.grid(row=15,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp_4_entry = ttk.Entry(self.tab,textvariable=self.kps[3])
        kp_4_entry.bind("<Return>",self.kp_4_entry_update)
        kp_4_entry.grid(row=15,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='cyan4')
        ki_4_label.grid(row=16,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki_4_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki_4_scrollbar_update)
        ki_4_scrollbar.grid(row=17,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_4_entry = ttk.Entry(self.tab,textvariable=self.kis[3])
        ki_4_entry.bind("<Return>",self.ki_4_entry_update)
        ki_4_entry.grid(row=17,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='cyan4')
        kd_4_label.grid(row=18,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_4_type = tk.BooleanVar()
        self.kd_4_type.set(True)
        self.kd_4_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd_4_type,
            command=self.kd_4_type_update)
        self.kd_4_type_error.grid(row=19,rowspan=1,column=8,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd_4_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd_4_type,
            command=self.kd_4_type_update)
        self.kd_4_type_state.grid(row=19,rowspan=1,column=9,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd_4_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd_4_scrollbar_update)
        kd_4_scrollbar.grid(row=20,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_4_entry = ttk.Entry(self.tab,textvariable=self.kds[3])
        kd_4_entry.bind("<Return>",self.kd_4_entry_update)
        kd_4_entry.grid(row=20,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Feed Forward',foreground='cyan4')
        feed_forward_4_label.grid(row=21,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        feed_forward_4_scrollbar = ttk.Scale(self.tab,
            from_=self.feed_forward_low, to=self.feed_forward_high,
            command=self.feed_forward_4_scrollbar_update)
        feed_forward_4_scrollbar.grid(row=23,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        feed_forward_4_entry = ttk.Entry(self.tab,
            textvariable=self.feed_forwards[3])
        feed_forward_4_entry.bind("<Return>",self.feed_forward_4_entry_update)
        feed_forward_4_entry.grid(row=23,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Noise Sigma',foreground='cyan4')
        noise_sigma_4_label.grid(row=24,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        noise_sigma_4_scrollbar = ttk.Scale(self.tab,
            from_=self.noise_sigma_low, to=self.noise_sigma_high,
            command=self.noise_sigma_4_scrollbar_update)
        noise_sigma_4_scrollbar.grid(row=25,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        noise_sigma_4_entry = ttk.Entry(self.tab,
            textvariable=self.noise_sigmas[3])
        noise_sigma_4_entry.bind("<Return>",self.noise_sigma_4_entry_update)
        noise_sigma_4_entry.grid(row=25,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)

        self.kp_scrollbars = [kp_1_scrollbar,kp_2_scrollbar,kp_3_scrollbar,kp_4_scrollbar]
        self.kp_entries = [kp_1_entry,kp_2_entry,kp_3_entry,kp_4_entry]

        self.ki_scrollbars = [ki_1_scrollbar,ki_2_scrollbar,ki_3_scrollbar,ki_4_scrollbar]
        self.ki_entries = [ki_1_entry,ki_2_entry,ki_3_entry,ki_4_entry]

        self.kd_scrollbars = [kd_1_scrollbar,kd_2_scrollbar,kd_3_scrollbar,kd_4_scrollbar]
        self.kd_entries = [kd_1_entry,kd_2_entry,kd_3_entry,kd_4_entry]

        self.feed_forward_scrollbars = [feed_forward_1_scrollbar,feed_forward_2_scrollbar,feed_forward_3_scrollbar,feed_forward_4_scrollbar]
        self.feed_forward_entries = [feed_forward_1_entry,feed_forward_2_entry,feed_forward_3_entry,feed_forward_4_entry]

        self.noise_sigma_scrollbars = [noise_sigma_1_scrollbar,noise_sigma_2_scrollbar,noise_sigma_3_scrollbar,noise_sigma_4_scrollbar]
        self.noise_sigma_entries = [noise_sigma_1_entry,noise_sigma_2_entry,noise_sigma_3_entry,noise_sigma_4_entry]
