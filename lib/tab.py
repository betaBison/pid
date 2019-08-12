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
        self.controller1_result = np.zeros((self.time_length,1))
        self.controller2_result = np.zeros((self.time_length,1))
        self.controller3_result = np.zeros((self.time_length,1))
        self.controller4_result = np.zeros((self.time_length,1))

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
        self.controller1 = PID(self.kps[0].get(),self.kis[0].get(),self.kds[0].get())
        self.controller2 = PID(self.kps[1].get(),self.kis[1].get(),self.kds[1].get())
        self.controller3 = PID(self.kps[2].get(),self.kis[2].get(),self.kds[2].get())
        self.controller4 = PID(self.kps[3].get(),self.kis[3].get(),self.kds[3].get())

        # update results with initialized gains
        self.controller_update(self.controller1,self.controller1_result)
        self.controller_update(self.controller2,self.controller2_result)
        self.controller_update(self.controller3,self.controller3_result)
        self.controller_update(self.controller4,self.controller4_result)

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
        if self.controller1_enabled.get():
            self.my_plot.plot(self.time,self.controller1_result,
                color='xkcd:orangered')
        if self.controller2_enabled.get():
            self.my_plot.plot(self.time,self.controller2_result,
                color='xkcd:goldenrod')
        if self.controller3_enabled.get():
            self.my_plot.plot(self.time,self.controller3_result,
                color='xkcd:azure')
        if self.controller4_enabled.get():
            self.my_plot.plot(self.time,self.controller4_result,
                color='xkcd:teal')

        self.my_plot.set_ylim([-3.2,3.2])

        self.canvas.draw()

    def steady_state_scrollbar_update(self,value):
        self.steady_state.set(value)
        self.steady_state_error = float(value)
        self.controller_update(self.controller1,self.controller1_result)
        self.controller_update(self.controller2,self.controller2_result)
        self.controller_update(self.controller3,self.controller3_result)
        self.controller_update(self.controller4,self.controller4_result)
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
        self.controller_update(self.controller1,self.controller1_result)
        self.controller_update(self.controller2,self.controller2_result)
        self.controller_update(self.controller3,self.controller3_result)
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def noise_sigma_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entry.get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbar.set(float(value))
        except ValueError:
            self.noise_sigma_var.set(self.noise_sigma)

    def kp1_scrollbar_update(self,value):
        self.kps[0].set(value)
        self.controller1.kp = float(value)
        self.controller1.ki = self.ki_scrollbars[0].get()
        self.controller1.kd = self.kd_scrollbars[0].get()
        self.controller1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def kp1_entry_update(self,event):
        try:
            entry = float(self.kp_entries[0].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[0].set(float(value))
        except ValueError:
            self.kps[0].set(self.controller1.kp)

    def kp2_scrollbar_update(self,value):
        self.kps[1].set(value)
        self.controller2.kp = float(value)
        self.controller2.ki = self.ki_scrollbars[1].get()
        self.controller2.kd = self.kd_scrollbars[1].get()
        self.controller2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def kp2_entry_update(self,event):
        try:
            entry = float(self.kp_entries[1].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[1].set(float(value))
        except ValueError:
            self.kps[1].set(self.controller2.kp)

    def kp3_scrollbar_update(self,value):
        self.kps[2].set(value)
        self.controller3.kp = float(value)
        self.controller3.ki = self.ki_scrollbars[2].get()
        self.controller3.kd = self.kd_scrollbars[2].get()
        self.controller3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def kp3_entry_update(self,event):
        try:
            entry = float(self.kp_entries[2].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[2].set(float(value))
        except ValueError:
            self.kps[2].set(self.controller3.kp)

    def kp4_scrollbar_update(self,value):
        self.kps[3].set(value)
        self.controller4.kp = float(value)
        self.controller4.ki = self.ki_scrollbars[3].get()
        self.controller4.kd = self.kd_scrollbars[3].get()
        self.controller4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def kp4_entry_update(self,event):
        try:
            entry = float(self.kp_entries[3].get())
            value = np.clip(entry,self.kp_low,self.kp_high)
            self.kp_scrollbars[3].set(float(value))
        except ValueError:
            self.kps[3].set(self.controller4.kp)

    def ki1_scrollbar_update(self,value):
        self.kis[0].set(value)
        self.controller1.kp = self.kp_scrollbars[0].get()
        self.controller1.ki = float(value)
        self.controller1.kd = self.kd_scrollbars[0].get()
        self.controller1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def ki1_entry_update(self,event):
        try:
            entry = float(self.ki_entries[0].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[0].set(float(value))
        except ValueError:
            self.kis[0].set(self.controller1.ki)

    def ki2_scrollbar_update(self,value):
        self.kis[1].set(value)
        self.controller2.kp = self.kp_scrollbars[1].get()
        self.controller2.ki = float(value)
        self.controller2.kd = self.kd_scrollbars[1].get()
        self.controller2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def ki2_entry_update(self,event):
        try:
            entry = float(self.ki_entries[1].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[1].set(float(value))
        except ValueError:
            self.kis[1].set(self.controller2.ki)

    def ki3_scrollbar_update(self,value):
        self.kis[2].set(value)
        self.controller3.kp = self.kp_scrollbars[2].get()
        self.controller3.ki = float(value)
        self.controller3.kd = self.kd_scrollbars[2].get()
        self.controller3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def ki3_entry_update(self,event):
        try:
            entry = float(self.ki_entries[2].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[2].set(float(value))
        except ValueError:
            self.kis[2].set(self.controller3.ki)

    def ki4_scrollbar_update(self,value):
        self.kis[3].set(value)
        self.controller4.kp = self.kp_scrollbars[3].get()
        self.controller4.ki = float(value)
        self.controller4.kd = self.kd_scrollbars[3].get()
        self.controller4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def ki4_entry_update(self,event):
        try:
            entry = float(self.ki_entries[3].get())
            value = np.clip(entry,self.ki_low,self.ki_high)
            self.ki_scrollbars[3].set(float(value))
        except ValueError:
            self.kis[3].set(self.controller4.ki)

    def kd1_scrollbar_update(self,value):
        self.kds[0].set(value)
        self.controller1.kp = self.kp_scrollbars[0].get()
        self.controller1.ki = self.ki_scrollbars[0].get()
        self.controller1.kd = float(value)
        self.controller1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def kd1_entry_update(self,event):
        try:
            entry = float(self.kd_entries[0].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[0].set(float(value))
        except ValueError:
            self.kds[0].set(self.controller1.kd)

    def kd2_scrollbar_update(self,value):
        self.kds[1].set(value)
        self.controller2.kp = self.kp_scrollbars[1].get()
        self.controller2.ki = self.ki_scrollbars[1].get()
        self.controller2.kd = float(value)
        self.controller2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def kd2_entry_update(self,event):
        try:
            entry = float(self.kd_entries[1].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[1].set(float(value))
        except ValueError:
            self.kds[1].set(self.controller2.kd)

    def kd3_scrollbar_update(self,value):
        self.kds[2].set(value)
        self.controller3.kp = self.kp_scrollbars[2].get()
        self.controller3.ki = self.ki_scrollbars[2].get()
        self.controller3.kd = float(value)
        self.controller3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def kd3_entry_update(self,event):
        try:
            entry = float(self.kd_entries[2].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[2].set(float(value))
        except ValueError:
            self.kds[2].set(self.controller3.kd)

    def kd4_scrollbar_update(self,value):
        self.kds[3].set(value)
        self.controller4.kp = self.kp_scrollbars[3].get()
        self.controller4.ki = self.ki_scrollbars[3].get()
        self.controller4.kd = float(value)
        self.controller4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def kd4_entry_update(self,event):
        try:
            entry = float(self.kd_entries[3].get())
            value = np.clip(entry,self.kd_low,self.kd_high)
            self.kd_scrollbars[3].set(float(value))
        except ValueError:
            self.kds[3].set(self.controller4.kd)

    def kd1_type_update(self):
        self.controller1.kd_error = self.kd1_type.get()
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def kd2_type_update(self):
        self.controller2.kd_error = self.kd2_type.get()
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def kd3_type_update(self):
        self.controller3.kd_error = self.kd3_type.get()
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def kd4_type_update(self):
        self.controller4.kd_error = self.kd4_type.get()
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def feed_forward_1_scrollbar_update(self,value):
        self.feed_forwards[0].set(value)
        self.controller1.kp = self.kp_scrollbars[0].get()
        self.controller1.ki = self.ki_scrollbars[0].get()
        self.controller1.kd = self.kd_scrollbars[0].get()
        self.controller1.feed_forward = float(value)
        self.controller1.noise_sigma = self.noise_sigma_scrollbars[0].get()
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def feed_forward_1_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[0].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[0].set(float(value))
        except ValueError:
            self.feed_forwards[0].set(self.controller1.feed_forward)

    def feed_forward_2_scrollbar_update(self,value):
        self.feed_forwards[1].set(value)
        self.controller2.kp = self.kp_scrollbars[1].get()
        self.controller2.ki = self.ki_scrollbars[1].get()
        self.controller2.kd = self.kd_scrollbars[1].get()
        self.controller2.feed_forward = float(value)
        self.controller2.noise_sigma = self.noise_sigma_scrollbars[1].get()
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def feed_forward_2_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[1].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[1].set(float(value))
        except ValueError:
            self.feed_forwards[1].set(self.controller2.feed_forward)

    def feed_forward_3_scrollbar_update(self,value):
        self.feed_forwards[2].set(value)
        self.controller3.kp = self.kp_scrollbars[2].get()
        self.controller3.ki = self.ki_scrollbars[2].get()
        self.controller3.kd = self.kd_scrollbars[2].get()
        self.controller3.feed_forward = float(value)
        self.controller3.noise_sigma = self.noise_sigma_scrollbars[2].get()
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def feed_forward_3_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[2].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[2].set(float(value))
        except ValueError:
            self.feed_forwards[2].set(self.controller3.feed_forward)

    def feed_forward_4_scrollbar_update(self,value):
        self.feed_forwards[3].set(value)
        self.controller4.kp = self.kp_scrollbars[3].get()
        self.controller4.ki = self.ki_scrollbars[3].get()
        self.controller4.kd = self.kd_scrollbars[3].get()
        self.controller4.feed_forward = float(value)
        self.controller4.noise_sigma = self.noise_sigma_scrollbars[3].get()
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def feed_forward_4_entry_update(self,event):
        try:
            entry = float(self.feed_forward_entries[3].get())
            value = np.clip(entry,self.feed_forward_low,self.feed_forward_high)
            self.feed_forward_scrollbars[3].set(float(value))
        except ValueError:
            self.feed_forwards[3].set(self.controller4.feed_forward)

    def noise_sigma_1_scrollbar_update(self,value):
        self.noise_sigmas[0].set(value)
        self.controller1.kp = self.kp_scrollbars[0].get()
        self.controller1.ki = self.ki_scrollbars[0].get()
        self.controller1.kd = self.kd_scrollbars[0].get()
        self.controller1.feed_forward = self.feed_forward_scrollbars[0].get()
        self.controller1.noise_sigma = float(value)
        self.controller_update(self.controller1,self.controller1_result)
        self.draw()

    def noise_sigma_1_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[0].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[0].set(float(value))
        except ValueError:
            self.noise_sigmas[0].set(self.controller1.noise_sigma)

    def noise_sigma_2_scrollbar_update(self,value):
        self.noise_sigmas[1].set(value)
        self.controller2.kp = self.kp_scrollbars[1].get()
        self.controller2.ki = self.ki_scrollbars[1].get()
        self.controller2.kd = self.kd_scrollbars[1].get()
        self.controller2.feed_forward = self.feed_forward_scrollbars[1].get()
        self.controller2.noise_sigma = float(value)
        self.controller_update(self.controller2,self.controller2_result)
        self.draw()

    def noise_sigma_2_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[1].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[1].set(float(value))
        except ValueError:
            self.noise_sigmas[1].set(self.controller2.noise_sigma)

    def noise_sigma_3_scrollbar_update(self,value):
        self.noise_sigmas[2].set(value)
        self.controller3.kp = self.kp_scrollbars[2].get()
        self.controller3.ki = self.ki_scrollbars[2].get()
        self.controller3.kd = self.kd_scrollbars[2].get()
        self.controller3.feed_forward = self.feed_forward_scrollbars[2].get()
        self.controller3.noise_sigma = float(value)
        self.controller_update(self.controller3,self.controller3_result)
        self.draw()

    def noise_sigma_3_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[2].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[2].set(float(value))
        except ValueError:
            self.noise_sigmas[2].set(self.controller3.noise_sigma)

    def noise_sigma_4_scrollbar_update(self,value):
        self.noise_sigmas[3].set(value)
        self.controller4.kp = self.kp_scrollbars[3].get()
        self.controller4.ki = self.ki_scrollbars[3].get()
        self.controller4.kd = self.kd_scrollbars[3].get()
        self.controller4.feed_forward = self.feed_forward_scrollbars[3].get()
        self.controller4.noise_sigma = float(value)
        self.controller_update(self.controller4,self.controller4_result)
        self.draw()

    def noise_sigma_4_entry_update(self,event):
        try:
            entry = float(self.noise_sigma_entries[3].get())
            value = np.clip(entry,self.noise_sigma_low,self.noise_sigma_high)
            self.noise_sigma_scrollbars[3].set(float(value))
        except ValueError:
            self.noise_sigmas[3].set(self.controller4.noise_sigma)

    def enable_controller1(self):
        if self.controller1_enabled.get():
            self.kp_scrollbars[0].state(["!disabled"])
            self.kp_entries[0].configure(state=tk.NORMAL)
            self.ki_scrollbars[0].state(["!disabled"])
            self.ki_entries[0].configure(state=tk.NORMAL)
            self.kd_scrollbars[0].state(["!disabled"])
            self.kd_entries[0].configure(state=tk.NORMAL)
            self.kd1_type_state.configure(state=tk.NORMAL)
            self.kd1_type_error.configure(state=tk.NORMAL)
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
            self.kd1_type_state.configure(state=tk.DISABLED)
            self.kd1_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[0].state(["disabled"])
            self.feed_forward_entries[0].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[0].state(["disabled"])
            self.noise_sigma_entries[0].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller2(self):
        if self.controller2_enabled.get():
            self.kp_scrollbars[1].state(["!disabled"])
            self.kp_entries[1].configure(state=tk.NORMAL)
            self.ki_scrollbars[1].state(["!disabled"])
            self.ki_entries[1].configure(state=tk.NORMAL)
            self.kd_scrollbars[1].state(["!disabled"])
            self.kd_entries[1].configure(state=tk.NORMAL)
            self.kd2_type_state.configure(state=tk.NORMAL)
            self.kd2_type_error.configure(state=tk.NORMAL)
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
            self.kd2_type_state.configure(state=tk.DISABLED)
            self.kd2_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[1].state(["disabled"])
            self.feed_forward_entries[1].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[1].state(["disabled"])
            self.noise_sigma_entries[1].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller3(self):
        if self.controller3_enabled.get():
            self.kp_scrollbars[2].state(["!disabled"])
            self.kp_entries[2].configure(state=tk.NORMAL)
            self.ki_scrollbars[2].state(["!disabled"])
            self.ki_entries[2].configure(state=tk.NORMAL)
            self.kd_scrollbars[2].state(["!disabled"])
            self.kd_entries[2].configure(state=tk.NORMAL)
            self.kd3_type_state.configure(state=tk.NORMAL)
            self.kd3_type_error.configure(state=tk.NORMAL)
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
            self.kd3_type_state.configure(state=tk.DISABLED)
            self.kd3_type_error.configure(state=tk.DISABLED)
            self.feed_forward_scrollbars[2].state(["disabled"])
            self.feed_forward_entries[2].configure(state=tk.DISABLED)
            self.noise_sigma_scrollbars[2].state(["disabled"])
            self.noise_sigma_entries[2].configure(state=tk.DISABLED)
        self.draw()

    def enable_controller4(self):
        if self.controller4_enabled.get():
            self.kp_scrollbars[3].state(["!disabled"])
            self.kp_entries[3].configure(state=tk.NORMAL)
            self.ki_scrollbars[3].state(["!disabled"])
            self.ki_entries[3].configure(state=tk.NORMAL)
            self.kd_scrollbars[3].state(["!disabled"])
            self.kd_entries[3].configure(state=tk.NORMAL)
            self.kd4_type_state.configure(state=tk.NORMAL)
            self.kd4_type_error.configure(state=tk.NORMAL)
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
            self.kd4_type_state.configure(state=tk.DISABLED)
            self.kd4_type_error.configure(state=tk.DISABLED)
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
        self.controller1_enabled = tk.BooleanVar()
        self.controller1_enabled.set(True)
        controller1_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller1_enabled, command=self.enable_controller1)
        controller1_checkbox.grid(row=12,rowspan=2,column=2,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='orange red')
        kp_1_label.grid(row=14,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp1_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp1_scrollbar_update)
        kp1_scrollbar.grid(row=15,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp1_entry = ttk.Entry(self.tab,textvariable=self.kps[0])
        kp1_entry.bind("<Return>",self.kp1_entry_update)
        kp1_entry.grid(row=15,column=3,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='orange red')
        ki_1_label.grid(row=16,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki1_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki1_scrollbar_update)
        ki1_scrollbar.grid(row=17,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki1_entry = ttk.Entry(self.tab,textvariable=self.kis[0])
        ki1_entry.bind("<Return>",self.ki1_entry_update)
        ki1_entry.grid(row=17,column=3,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_1_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='orange red')
        kd_1_label.grid(row=18,rowspan=1,column=2,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd1_type = tk.BooleanVar()
        self.kd1_type.set(True)
        self.kd1_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd1_type,
            command=self.kd1_type_update)
        self.kd1_type_error.grid(row=19,rowspan=1,column=2,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd1_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd1_type,
            command=self.kd1_type_update)
        self.kd1_type_state.grid(row=19,rowspan=1,column=3,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd1_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd1_scrollbar_update)
        kd1_scrollbar.grid(row=20,column=2,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd1_entry = ttk.Entry(self.tab,textvariable=self.kds[0])
        kd1_entry.bind("<Return>",self.kd1_entry_update)
        kd1_entry.grid(row=20,column=3,
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
        self.controller2_enabled = tk.BooleanVar()
        self.controller2_enabled.set(True)
        controller2_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller2_enabled, command=self.enable_controller2)
        controller2_checkbox.grid(row=12,rowspan=2,column=4,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='goldenrod')
        kp_2_label.grid(row=14,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp2_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp2_scrollbar_update)
        kp2_scrollbar.grid(row=15,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp2_entry = ttk.Entry(self.tab,textvariable=self.kps[1])
        kp2_entry.bind("<Return>",self.kp2_entry_update)
        kp2_entry.grid(row=15,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='goldenrod')
        ki_2_label.grid(row=16,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki2_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki2_scrollbar_update)
        ki2_scrollbar.grid(row=17,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki2_entry = ttk.Entry(self.tab,textvariable=self.kis[1])
        ki2_entry.bind("<Return>",self.ki2_entry_update)
        ki2_entry.grid(row=17,column=5,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_2_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='goldenrod')
        kd_2_label.grid(row=18,rowspan=1,column=4,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd2_type = tk.BooleanVar()
        self.kd2_type.set(True)
        self.kd2_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd2_type,
            command=self.kd2_type_update)
        self.kd2_type_error.grid(row=19,rowspan=1,column=4,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd2_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd2_type,
            command=self.kd2_type_update)
        self.kd2_type_state.grid(row=19,rowspan=1,column=5,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd2_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd2_scrollbar_update)
        kd2_scrollbar.grid(row=20,column=4,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd2_entry = ttk.Entry(self.tab,textvariable=self.kds[1])
        kd2_entry.bind("<Return>",self.kd2_entry_update)
        kd2_entry.grid(row=20,column=5,
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
        self.controller3_enabled = tk.BooleanVar()
        self.controller3_enabled.set(True)
        controller3_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller3_enabled, command=self.enable_controller3)
        controller3_checkbox.grid(row=12,rowspan=2,column=6,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='DodgerBlue2')
        kp_3_label.grid(row=14,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp3_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp3_scrollbar_update)
        kp3_scrollbar.grid(row=15,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp3_entry = ttk.Entry(self.tab,textvariable=self.kps[2])
        kp3_entry.bind("<Return>",self.kp3_entry_update)
        kp3_entry.grid(row=15,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='DodgerBlue2')
        ki_3_label.grid(row=16,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki3_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki3_scrollbar_update)
        ki3_scrollbar.grid(row=17,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki3_entry = ttk.Entry(self.tab,textvariable=self.kis[2])
        ki3_entry.bind("<Return>",self.ki3_entry_update)
        ki3_entry.grid(row=17,column=7,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_3_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='DodgerBlue2')
        kd_3_label.grid(row=18,rowspan=1,column=6,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd3_type = tk.BooleanVar()
        self.kd3_type.set(True)
        self.kd3_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd3_type,
            command=self.kd3_type_update)
        self.kd3_type_error.grid(row=19,rowspan=1,column=6,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd3_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd3_type,
            command=self.kd3_type_update)
        self.kd3_type_state.grid(row=19,rowspan=1,column=7,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd3_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd3_scrollbar_update)
        kd3_scrollbar.grid(row=20,column=6,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd3_entry = ttk.Entry(self.tab,textvariable=self.kds[2])
        kd3_entry.bind("<Return>",self.kd3_entry_update)
        kd3_entry.grid(row=20,column=7,
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
        self.controller4_enabled = tk.BooleanVar()
        self.controller4_enabled.set(True)
        controller4_checkbox = ttk.Checkbutton(self.tab,
            var=self.controller4_enabled, command=self.enable_controller4)
        controller4_checkbox.grid(row=12,rowspan=2,column=8,columnspan=1,
            stick=tk.E, padx=5,pady=5,ipadx=5,ipady=5)
        kp_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Proportional Gain',foreground='cyan4')
        kp_4_label.grid(row=14,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kp4_scrollbar = ttk.Scale(self.tab,from_=self.kp_low, to=self.kp_high,
            command=self.kp4_scrollbar_update)
        kp4_scrollbar.grid(row=15,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kp4_entry = ttk.Entry(self.tab,textvariable=self.kps[3])
        kp4_entry.bind("<Return>",self.kp4_entry_update)
        kp4_entry.grid(row=15,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Integral Gain',foreground='cyan4')
        ki_4_label.grid(row=16,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        ki4_scrollbar = ttk.Scale(self.tab,from_=self.ki_low, to=self.ki_high,
            command=self.ki4_scrollbar_update)
        ki4_scrollbar.grid(row=17,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        ki4_entry = ttk.Entry(self.tab,textvariable=self.kis[3])
        ki4_entry.bind("<Return>",self.ki4_entry_update)
        ki4_entry.grid(row=17,column=9,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd_4_label = ttk.Label(self.tab, anchor=tk.CENTER,
            text='Derivative Gain',foreground='cyan4')
        kd_4_label.grid(row=18,rowspan=1,column=8,columnspan=2,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd4_type = tk.BooleanVar()
        self.kd4_type.set(True)
        self.kd4_type_error = ttk.Radiobutton(self.tab, text="error derivative",
            value=True, variable=self.kd4_type,
            command=self.kd4_type_update)
        self.kd4_type_error.grid(row=19,rowspan=1,column=8,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        self.kd4_type_state = ttk.Radiobutton(self.tab, text="state derivative",
            value = False, variable=self.kd4_type,
            command=self.kd4_type_update)
        self.kd4_type_state.grid(row=19,rowspan=1,column=9,columnspan=1,
            sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5,ipadx=5,ipady=5)
        kd4_scrollbar = ttk.Scale(self.tab,from_=self.kd_low, to=self.kd_high,
            command=self.kd4_scrollbar_update)
        kd4_scrollbar.grid(row=20,column=8,columnspan=1,
            sticky=tk.E+tk.W,padx=5,pady=5)
        kd4_entry = ttk.Entry(self.tab,textvariable=self.kds[3])
        kd4_entry.bind("<Return>",self.kd4_entry_update)
        kd4_entry.grid(row=20,column=9,
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

        self.kp_scrollbars = [kp1_scrollbar,kp2_scrollbar,kp3_scrollbar,kp4_scrollbar]
        self.kp_entries = [kp1_entry,kp2_entry,kp3_entry,kp4_entry]

        self.ki_scrollbars = [ki1_scrollbar,ki2_scrollbar,ki3_scrollbar,ki4_scrollbar]
        self.ki_entries = [ki1_entry,ki2_entry,ki3_entry,ki4_entry]

        self.kd_scrollbars = [kd1_scrollbar,kd2_scrollbar,kd3_scrollbar,kd4_scrollbar]
        self.kd_entries = [kd1_entry,kd2_entry,kd3_entry,kd4_entry]

        self.feed_forward_scrollbars = [feed_forward_1_scrollbar,feed_forward_2_scrollbar,feed_forward_3_scrollbar,feed_forward_4_scrollbar]
        self.feed_forward_entries = [feed_forward_1_entry,feed_forward_2_entry,feed_forward_3_entry,feed_forward_4_entry]

        self.noise_sigma_scrollbars = [noise_sigma_1_scrollbar,noise_sigma_2_scrollbar,noise_sigma_3_scrollbar,noise_sigma_4_scrollbar]
        self.noise_sigma_entries = [noise_sigma_1_entry,noise_sigma_2_entry,noise_sigma_3_entry,noise_sigma_4_entry]
