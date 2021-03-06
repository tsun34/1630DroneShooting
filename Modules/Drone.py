"""
    Drone.py
    Marcus Abate | 16.30
    12/1/18

    This class encapsulates many of the standard methods and objects used to
    run tests and scripts on the Parrot Mambo drone with vision.
"""

from pyparrot.Minidrone import Mambo
from pyparrot.DroneVisionGUI import DroneVisionGUI

class Drone:
    def __init__(self, test_flying, mambo_addr, use_wifi=True, use_vision=True):
        """
        Constructor for the Drone Superclass.
        When writing your code, you may redefine __init__() to have additional
        attributes for use in processing elsewhere. If you do this, be sure to
        call super().__init__() with relevant args in order properly
        initialize all mambo-related things.

        test_flying:    bool : run flight code if True
        mambo_addr:     str  : BLE address of drone
        use_wifi:       bool : connect with WiFi instead of BLE if True
        use_vision:     bool : turn on DroneVisionGUI module if True
        """
        self.test_flying = test_flying
        self.use_wifi = use_wifi
        self.use_vision = use_vision
        self.mamboAddr = mambo_addr
        self.mambo = Mambo(self.mamboAddr, use_wifi=self.use_wifi)

        self.mambo.set_user_sensor_callback(self.sensor_cb, args=None)
        if self.use_vision:
            self.mamboVision = DroneVisionGUI(self.mambo, is_bebop=False,
                                                buffer_size=200,
                                                user_code_to_run=self.flight_func,
                                                user_args=None)
            self.mamboVision.set_user_callback_function(self.vision_cb,
                                                user_callback_args=None)

    def execute(self):
        """
        Connects to drone and executes flight_func as well as any vision
        handling when needed.
        Run this after initializing your subclass in your main method to
        start the test/script.
        """
        print("trying to connect to self.mambo now")
        success = self.mambo.connect(num_retries=3)
        print("connected: %s" % success)

        if (success):
            self.mambo.smart_sleep(1)
            self.mambo.ask_for_state_update()
            self.mambo.smart_sleep(1)

            if self.use_vision:
                print("starting vision")
                self.mamboVision.open_video()
            else:
                print("starting flight without vision")
                self.flight_func(None, None)

            if self.use_vision:
                print("ending vision")
                self.mamboVision.close_video()
            self.mambo.smart_sleep(3)
            self.mambo.disconnect()

    def flight_func(self, mamboVision, args):
        """
        Method to me run for flight. This is defined by the user outside of this
        class.
        When writing your code, define a new class for each test that inherits
        this class. Redefine your flight_func in your subclass to match
        your flight plan.
        your redefinition of flight_func must include the mamboVision and args
        arguments to properly work.
        NOTE: after takeoff it is smart to do the following:
            print("sensor calib")
            while self.mambo.sensors.speed_ts == 0:
                continue
        This gives the sensors time to fully initialize and send back proper
        readings for use in your sensor callback method.
        Cannot be done before takeoff; sensors send nothing at this time.
        """
        pass

    def vision_cb(self, args):
        """
        Callback function for every vision-handle update Again, defined by the
        user outside of the class in a specific subclass for every test script.
        Your vision_cb must include the self and args arguments to work.
        """
        pass

    def sensor_cb(self, args):
        """
        Callback function for every sensor update. Again, defined by the
        user outside of the class in a specific subclass for every test script.
        Your sensor_cb must include the self and args arguments to work.
        """
        pass
