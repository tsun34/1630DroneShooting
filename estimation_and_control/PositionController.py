"""
    PositionController.py
    Marcus Abate | 16.30
    12/1/18

    Calculates control input required to converge to a desired xyz position
    based on current state and drone dynamics. This is an LQR model.
    Control inputs are roll, pitch, yaw commands for the pyparrot interface.
    These commands are represented as xyz velocity commands. This is because
    at slow speeds, the quadrotor is roughly level to the ground and travels
    at a constant velocity when given these commands. They do not actually
    determine the angles around the three body axes of the drone.

    Because the system is modeling the input to the quadrotor as velocity
    commands, the commands must be normalized to a much smaller range than is
    actually possible so as to hold the "small velocities" assumption.
"""

import numpy as np
import scipy.linalg

class PositionController:
    def __init__(self, A, B, Q, R):
        """
        desired_state   : holds the current desired state of the drone in
                            the state format:
                            [x, y, z, dx/dt, dy/dt, dz/dt]
                            where dx/dt, dy/dt, dz/dt are velocities in the
                            x,y,z directions respectively.
        current_state   : holds the current state of the drone as estimated
                            by the KalmanFilter module.
        max_input_power : corresponds to the maximum power (normalized to 100
                            in the pyparrot module) that is permited in each
                            of the following commands:
                            [roll, pitch, yaw, vertical_movement]
        cmd_input       : [r, p, y, vm] list of commands in the
                            [roll, pitch, yaw, vertical_movement] formulation.

        Reference:
        https://github.com/ssloy/tutorials/blob/master/tutorials/pendulum/lqr.py

        Solve the discrete LQR problem for the instance system.
        Return the solution to the Ricatti equation and the K gains matrix.

        x[k+1] = A x[k] + B u[k]
        cost = sum x[k].T*Q*x[k] + u[k].T*R*u[k]
        """
        self.desired_state = []
        self.current_state = []
        self.cmd_input = []
        self.max_input_power = [20, 20, 20, 20]
        self.A = A
        self.B = B
        self.Q = Q
        self.R = R
        self.P = np.matrix(scipy.linalg.solve_discrete_are(self.A, self.B,
                                self.Q, self.R))
        self.K = np.matrix(scipy.linalg.inv(self.B.T*self.P*self.B+self.R)*(
                                self.B.T*self.P*self.A))

    def get_eig(self):
        """
        Return system eigenvalues and eigenvectors for checking stability and
        response character.
        """
        return scipy.linalg.eig(self.A-self.B*self.K)

    def set_current_state(self, current_state):
        """
        Called at every state update in a main loop.

            current_state: holds the current state of the drone.
                the state is x-y-z positions and x-y-z linear velocities.
        """
        self.current_state = current_state

    def set_desired_state(self, desired_state):
        """
        Called when the desired waypoint is updated in a main loop.

            desired_state: holds the desired x-y-z position of the drone as a
                3-element list.
        """
        self.desired_state = desired_state

    def calculate_cmd_input(self):
        """
        Determine x y z velocities required to converge to the desired state
        from the current state. These become roll, pitch, yaw "commands" in the
        pyparrot fly_direct() method.

            returns [r, p, y, vm] : r = roll power
                                    p = pitch power
                                    y = yaw power
                                    vm = vertical_movement power
        """
        raise NotImplementedError

        return self.get_current_cmd()

    def get_current_cmd(self):
        """
        Return the current command input to the quadrotor.
        This is stored as a member of the PositionController object and
        is recalculated after every desired/current state update.
        """
        return self.cmd_input

class MamboPositionController(PositionController):
    def __init__(self):
        """
        Initializes the PositionController with Mambo system and weight
        matrices.
        Change Q and R to change weights on the states and inputs.
        """
        A = np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, -9.81, 0.0, -.064, 0.0, 0.0, 0.0, .1382, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 9.81, 0.0, -0.64, 0.0, -.1382, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.1999, 0.0, -2.5898, 0.0, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9755, 0.0, 0.0, 0.0, -2.1056, 0.0],
                      [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.1715]])
        B = 10000 * np.array([[0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0],
                              [0.0015, 0.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 1.7157],
                              [0.0, 0.0, 1.3949, 0.0],
                              [0.0, 1.0, 0.0, 0.0]])
        Q =
        R =
        super().__init__(A, B, Q, R)
