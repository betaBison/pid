'''
Author: Derek Knowles
Date: 7.2019
Description: PID control template
'''

import warnings
warnings.filterwarnings("error")
import numpy as np

class PID():
    '''
    PID control class template
    '''
    def __init__(self,kp=0.0,ki=0.0,kd=0.0,kd_error=True):
        # inputs
        self.kp = kp                # proportional gain
        self.ki = ki                # integral gain
        self.kd = kd                # derivative gain
        self.kd_error = kd_error    # use error or state derivative

        # intermediaries
        self.integrator = 0.0
        self.previous_state = 0.0
        self.previous_state_error = 0.0
        self.state_derivative = 0.0
        self.error_derivative = 0.0
        self.feed_forward = 0.0
        self.noise_sigma = 0.0

    def update(self,current_state,desired_state,dt):
        # calculate current error
        state_error = desired_state - current_state

        # update integrator
        self.integrator += (dt/2.0) * (state_error + self.previous_state_error);

        # update derivative
        if self.kd_error:
            self.error_derivative = self.calculate_derivative(state_error, dt)
        else:
            self.state_derivative = self.calculate_state_derivative(current_state, dt)

        # calculate  command
        try:
            if self.kd_error:
                command = current_state + self.kp * state_error \
                    + self.ki * self.integrator \
                    + self.kd * self.error_derivative \
                    + self.feed_forward \
                    + self.noise_sigma*np.random.randn()
            else:
                command = current_state + self.kp * state_error \
                    + self.ki * self.integrator \
                    - self.kd * self.state_derivative \
                    + self.feed_forward \
                    + self.noise_sigma*np.random.randn()

        except RuntimeWarning as warn:
            self.reset()
            self.kp = 0.0
            self.ki = 0.0
            self.kd = 0.0
            self.feed_forward = 0.0
            command = 0.0


        # update current to previous
        self.previous_state = current_state
        self.previous_state_error = state_error

        return command

    def calculate_derivative(self, state_error, dt):
        # dirty derivative calculation
        sigma = 10.0 * dt                               # cutoff frequency for dirty derivative
        beta = (2.0 * sigma - dt) / (2.0 * sigma + dt)  # dirty derivative gain
        try:
            error_derivative_updated = beta * self.error_derivative \
                + (1.0 - beta) * (state_error - self.previous_state_error) / dt
        except RuntimeWarning as warn:
            self.reset()
            self.kp = 0.0
            self.ki = 0.0
            self.kd = 0.0
            self.feed_forward = 0.0
            error_derivative_updated = 0.0
        return error_derivative_updated

    def calculate_state_derivative(self, current_state, dt):
        # dirty derivative calculation
        sigma = 10.0 * dt                               # cutoff frequency for dirty derivative
        beta = (2.0 * sigma - dt) / (2.0 * sigma + dt)  # dirty derivative gain
        try:
            state_derivative_updated = beta * self.state_derivative \
                + (1.0 - beta) * (current_state - self.previous_state) / dt
        except RuntimeWarning as warn:
            self.reset()
            self.kp = 0.0
            self.ki = 0.0
            self.kd = 0.0
            self.feed_forward = 0.0
            state_derivative_updated = 0.0
        return state_derivative_updated



    def reset(self):
        self.integrator = 0.0
        self.previous_state = 0.0
        self.previous_state_error = 0.0
        self.state_derivative = 0.0
        self.error_derivative = 0.0
