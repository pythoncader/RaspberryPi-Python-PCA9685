import time
import sys
import random
# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 120
servo_max = 650
servo_frequency = 60
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(servo_frequency)


def translate(value, left_min, left_max, right_min, right_max):
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)


class Servo:
    # frequency is the number of pulses per second
    # each pulse has 4096 clock sections
    # on: The tick (between 0 and 4095) when the signal should transition from low to high
    # off:the tick (between 0 and 4095) when the signal should transition from high to low

    def __init__(self, channel, servo_min_bound=0, servo_max_bound=180, current_angle="unknown", info_print=False):
        self.channel = channel
        self.currentAngle = current_angle
        self.info_print = info_print
        self.servo_min_bound = servo_min_bound
        self.servo_max_bound = servo_max_bound
        if self.info_print:
            print(
                f'Initializing Servo on channel {self.channel} with range {self.servo_min_bound} '
                f'to {self.servo_max_bound} degrees.')

    def __str__(self):
        return f"Servo on channel {self.channel} at {self.currentAngle} degrees"

    def set_info_print(self, info_print):
        self.info_print = info_print

    def set_angle(self, angle=90, delay_amount=0.3, clock_start=0):
        self.currentAngle = angle
        if self.servo_min_bound != 0 or self.servo_max_bound != 180:
            angle = translate(angle, 0, 180, self.servo_min_bound, self.servo_max_bound)
            self.currentAngle = angle

        duty_cycle = angle / 180
        pulse_width = 548 * duty_cycle + 120
        pulse_width = int(pulse_width)

        if 0 <= clock_start <= 4095:
            pwm.set_pwm(self.channel, clock_start, pulse_width + clock_start)
            # pwm.set_pwm(channel, on , off) #on and off are 12-bit values so they are in between 0 and 4095
            # pwm.set_pwm_freq(freq) in hz
        else:
            print("Invalid clock start time, resetting to zero...")
            pwm.set_pwm(self.channel, 0, pulse_width)

        if self.info_print:
            print(
                f"Setting Servo on channel {self.channel} to {self.currentAngle} "
                f"on clock starting time {clock_start} and waiting {delay_amount} seconds")
        time.sleep(delay_amount)

    def glide_angle(self, starting_angle, ending_angle, time_to_take):
        if self.info_print:
            print(
                f"Servo on channel {self.channel} gliding from angle {starting_angle} to {ending_angle} "
                f"in {time_to_take} seconds")
            self.info_print = False
            gliding_info_print = True
        else:
            gliding_info_print = False

        time_interval = time_to_take / abs((starting_angle - ending_angle))
        self.set_angle(starting_angle, 0.5)
        if starting_angle < ending_angle:
            for angle_i in range(starting_angle + 1, ending_angle + 1):
                self.set_angle(angle_i, time_interval)
        else:
            neg_angle = starting_angle - 1
            while neg_angle != ending_angle:
                neg_angle -= 1
                self.set_angle(neg_angle, time_interval)
        if gliding_info_print:
            self.info_print = True

    def random_angle(self, random_time=200):
        random_time = (random.randint(0, random_time)) / 1000.0
        self.set_angle(random.randint(0, 180), random_time)

    def vibrate(self, start_at=0, interval=15, delay_amount=3, duration=100):
        print("vibrate starting...")
        start_time = time.time() * 1000
        end_time = start_time
        duration_millis = duration * 1000
        for i in range(start_at, 180):
            self.set_angle(0, 0)
            time.sleep(delay_amount)
            self.set_angle(i, 0)
            time.sleep(delay_amount)
            i += interval
            if (end_time - start_time) <= duration_millis:
                end_time = time.time() * 1000
            else:
                break

        self.set_angle(0, 0)
        print("vibrate ending...")


class ServoGroup:
    # frequency is the number of pulses per second
    # each pulse has 4096 clock sections
    # on: The tick (between 0 and 4095) when the signal should transition from low to high
    # off:the tick (between 0 and 4095) when the signal should transition from high to low

    def __init__(self, num_of_servos, *channels, current_angle="unknown", info_print=False):
        self.currentAngle = current_angle
        self.info_print = info_print
        self.num_of_servos = num_of_servos
        self.channels = channels  # tuple of channels
        if len(self.channels) != num_of_servos:
            sys.exit("\n\nDid not give enough channels for servos!\n")

    def __str__(self):
        return f":self.num_of_servos servos on channels :self.channels at :self.currentAngle degrees"

    def set_info_print(self, info_print):
        self.info_print = info_print

    def set_angle(self, angle=90, delay_amount=1, clock_start=0):
        self.currentAngle = angle
        duty_cycle = angle / 180
        pulse_width = 548 * duty_cycle + 120
        pulse_width = int(pulse_width)

        if 0 <= clock_start <= 4095:
            for channel in self.channels:
                pwm.set_pwm(channel, clock_start, pulse_width + clock_start)
                # pwm.set_pwm(channel, on , off) #on and off are 12-bit values so they are in between 0 and 4095
                # pwm.set_pwm_freq(freq) in hz
        else:
            for channel in self.channels:
                print("Invalid clock start time, resetting to zero...")
                pwm.set_pwm(channel, 0, pulse_width)

        if self.info_print:
            print(
                f"Setting servos on channels {self.channels} to {self.currentAngle} "
                f"on clock starting time {clock_start}")
        time.sleep(delay_amount)


class ServoGroup2:
    def __init__(self, list_of_servos, info_print=False):
        self.info_print = info_print
        self.list_of_servos = list_of_servos
        if self.info_print:
            print(f"Initiating Servo Group with {len(list_of_servos)} members")

    def set_angle(self, angle=90, delay_amount=1.0, clock_start=0):
        info_print_list = []
        if self.info_print:
            print(f"Setting Servo Group to {angle} and waiting {delay_amount} seconds")

        for i in range(0, len(self.list_of_servos)):
            if self.list_of_servos[i].info_print:
                self.list_of_servos[i].set_info_print(False)
                info_print_list.append(i)
            else:
                info_print_list.append(-1)
            self.list_of_servos[i].set_angle(angle, 0, clock_start)
        if self.info_print:
            for i in range(0, len(self.list_of_servos)):
                if i == info_print_list[i]:
                    self.list_of_servos[i].set_info_print(True)

        time.sleep(delay_amount)

    def glide_angle(self, starting_angle, ending_angle, time_to_take):
        if self.info_print:
            print(
                f"ServoGroup gliding from angle {starting_angle} to {ending_angle} in {time_to_take} seconds")
            self.info_print = False
            gliding_info_print = True
        else:
            gliding_info_print = False

        time_interval = time_to_take / abs((starting_angle - ending_angle))
        self.set_angle(starting_angle, 0.5)
        if starting_angle < ending_angle:
            for angle_i in range(starting_angle + 1, ending_angle + 1):
                self.set_angle(angle_i, time_interval)
        else:
            neg_angle = starting_angle - 1
            while neg_angle != ending_angle:
                neg_angle -= 1
                self.set_angle(neg_angle, time_interval)
        if gliding_info_print:
            self.info_print = True


class ServoPumpkin:
    def __init__(self, eye0, eye1, eye2, eye3, eye4, eye5, eye6, eye7):
        self.eye1 = eye1
        self.eye0 = eye0
        self.eye2 = eye2
        self.eye3 = eye3
        self.eye4 = eye4
        self.eye5 = eye5
        self.eye6 = eye6
        self.eye7 = eye7

    def reset_out(self, delay_amount=2):
        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye2.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        time.sleep(delay_amount)

    def random_eyes(self, duration, random_time=200):  # give duration of running in seconds
        print("pumpkin random starting...")
        start_time = time.time() * 1000
        end_time = start_time
        duration_millis = duration * 1000
        while (end_time - start_time) <= duration_millis:
            self.eye0.random_angle(random_time)
            self.eye1.random_angle(random_time)
            self.eye2.random_angle(random_time)
            self.eye3.random_angle(random_time)
            self.eye4.random_angle(random_time)
            self.eye5.random_angle(random_time)
            self.eye6.random_angle(random_time)
            self.eye7.random_angle(random_time)

            end_time = time.time() * 1000

        print("pumpkin random ending...")

    def min_max(self, duration, delay_amount=1):  # give duration of running in seconds
        print("pumpkin min_max starting...")
        start_time = time.time() * 1000
        end_time = start_time
        duration_millis = duration * 1000
        while (end_time - start_time) <= duration_millis:
            time.sleep(delay_amount)
            self.eye0.set_angle(0, 0)
            self.eye1.set_angle(0, 0)
            self.eye2.set_angle(0, 0)
            self.eye3.set_angle(180, 0)
            self.eye4.set_angle(0, 0)
            self.eye5.set_angle(180, 0)
            self.eye6.set_angle(180, 0)
            self.eye7.set_angle(180, 0)

            time.sleep(delay_amount)

            self.eye0.set_angle(180, 0)
            self.eye1.set_angle(180, 0)
            self.eye2.set_angle(180, 0)
            self.eye3.set_angle(0, 0)
            self.eye4.set_angle(180, 0)
            self.eye5.set_angle(0, 0)
            self.eye6.set_angle(0, 0)
            self.eye7.set_angle(0, 0)

            end_time = time.time() * 1000

        print("pumpkin min_max ending...")

    def min_max_glide(self, eye_speed, delay_amount=1):
        self.reset_out(4)
        print("pumpkin min_max_glide starting...")
        print(f"eye speed {eye_speed}")
        self.eye0.glide_angle(180, 0, eye_speed)
        self.eye1.glide_angle(180, 0, eye_speed)
        self.eye2.glide_angle(180, 0, eye_speed)
        self.eye3.glide_angle(0, 180, eye_speed)
        self.eye7.glide_angle(0, 180, eye_speed)
        self.eye6.glide_angle(0, 180, eye_speed)
        self.eye5.glide_angle(0, 180, eye_speed)
        self.eye4.glide_angle(180, 0, eye_speed)

        time.sleep(delay_amount)

        self.eye4.glide_angle(0, 180, eye_speed)
        self.eye5.glide_angle(180, 0, eye_speed)
        self.eye6.glide_angle(180, 0, eye_speed)
        self.eye7.glide_angle(180, 0, eye_speed)
        self.eye3.glide_angle(180, 0, eye_speed)
        self.eye2.glide_angle(0, 180, eye_speed)
        self.eye1.glide_angle(0, 180, eye_speed)
        self.eye0.glide_angle(0, 180, eye_speed)

        print("pumpkin min_max_glide ending...")

    def half_half(self, delay_amount=1):
        self.reset_out()
        print("Half_Half starting...")

        # start half half
        self.eye0.set_angle(0, 0)
        self.eye1.set_angle(0, 0)
        self.eye4.set_angle(0, 0)
        self.eye5.set_angle(180, 0)

        time.sleep(delay_amount)

        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)

        time.sleep(delay_amount)
        self.eye2.set_angle(0, 0)
        self.eye3.set_angle(180, 0)
        self.eye6.set_angle(180, 0)
        self.eye7.set_angle(180, 0)

        time.sleep(delay_amount)

        self.eye2.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)

        print("Half_Half ending...")

    def columns(self, delay_amount=1):
        self.reset_out()
        print("columns starting...")
        # start each column is a group

        # column 1:
        self.eye0.set_angle(0, 0)
        self.eye4.set_angle(0, 0)
        time.sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        time.sleep(delay_amount)

        # column 2:
        self.eye1.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye1.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        time.sleep(delay_amount)

        # column 3:
        self.eye2.set_angle(0, 0)
        self.eye6.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye2.set_angle(180, 0)
        self.eye6.set_angle(0, 0)
        time.sleep(delay_amount)

        # column 4:
        self.eye3.set_angle(180, 0)
        self.eye7.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye3.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        time.sleep(delay_amount)

        print("columns ending...")

    def columns_converging(self, delay_amount=1):
        self.reset_out()
        print("columns converging starting...")
        # start each column is a group

        # column 1:
        self.eye0.set_angle(0, 0)
        self.eye4.set_angle(0, 0)
        # column 4:
        self.eye3.set_angle(180, 0)
        self.eye7.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        time.sleep(delay_amount)

        # column 2:
        self.eye1.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        # column 3:
        self.eye2.set_angle(0, 0)
        self.eye6.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye1.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye2.set_angle(180, 0)
        self.eye6.set_angle(0, 0)
        time.sleep(delay_amount)

        print("columns converging ending...")

    def rows(self, delay_amount=1):
        self.reset_out()
        print("rows starting...")
        # start each row is a group

        # top row:
        self.eye0.set_angle(0, 0)
        self.eye1.set_angle(0, 0)
        self.eye2.set_angle(0, 0)
        self.eye3.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye2.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        time.sleep(delay_amount)

        # bottom row:
        self.eye4.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        self.eye6.set_angle(180, 0)
        self.eye7.set_angle(180, 0)
        time.sleep(delay_amount)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        time.sleep(delay_amount)
        print("rows ending...")

    def look_directions(self, delay_amount=1):
        self.reset_out()
        print("look_directions starting...")
        # start bottom halves at same time
        self.eye4.set_angle(0, 0)  # inward
        self.eye5.set_angle(0, 0)  # inward
        self.eye6.set_angle(0, 0)  # outward
        self.eye7.set_angle(0, 0)  # outward
        time.sleep(delay_amount)
        self.eye4.set_angle(180, 0)  # outward
        self.eye5.set_angle(180, 0)  # outward
        self.eye6.set_angle(180, 0)  # inward
        self.eye7.set_angle(180, 0)  # inward
        time.sleep(delay_amount)

        # start top halves at same time
        self.eye0.set_angle(0, 0)  # inward
        self.eye1.set_angle(0, 0)  # inward
        self.eye2.set_angle(180, 0)  # outward
        self.eye3.set_angle(180, 0)  # outward
        time.sleep(delay_amount)
        self.eye0.set_angle(180, 0)  # outward
        self.eye1.set_angle(180, 0)  # outward
        self.eye2.set_angle(0, 0)  # inward
        self.eye3.set_angle(0, 0)  # inward
        time.sleep(delay_amount)
        print("look_directions ending...")

    def ladders(self, start_at, interval=15, delay_amount=3.0, duration=100):
        print("ladders starting...")
        start_time = time.time() * 1000
        end_time = start_time
        duration_millis = duration * 1000
        i = start_at
        while i <= 180:
            self.eye0.set_angle(0, 0)
            self.eye1.set_angle(0, 0)
            self.eye2.set_angle(0, 0)
            self.eye3.set_angle(180, 0)
            self.eye4.set_angle(0, 0)
            self.eye5.set_angle(0, 0)
            self.eye6.set_angle(0, 0)
            self.eye7.set_angle(0, 0)
            time.sleep(delay_amount)
            self.eye0.set_angle(i, 0)
            self.eye1.set_angle(i, 0)
            self.eye2.set_angle(i, 0)
            self.eye3.set_angle(abs(i - 180), 0)
            self.eye4.set_angle(i, 0)
            self.eye5.set_angle(i, 0)
            self.eye6.set_angle(i, 0)
            self.eye7.set_angle(i, 0)
            time.sleep(delay_amount)
            print(f"delay_amount = {delay_amount}")
            i += interval
            print(f"i = {i}")
            if (end_time - start_time) <= duration_millis:
                end_time = time.time() * 1000
            else:
                break

        self.eye0.set_angle(0, 0)
        self.eye1.set_angle(0, 0)
        self.eye2.set_angle(0, 0)
        self.eye3.set_angle(180, 0)
        self.eye4.set_angle(0, 0)
        self.eye5.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        print("ladders ending...")

    def vibrate_rounds(self):
        self.eye0.vibrate(50, 1, 0.05, 1)
        self.eye1.vibrate(50, 1, 0.05, 1)
        self.eye2.vibrate(50, 1, 0.05, 1)
        self.eye3.vibrate(50, 1, 0.05, 1)
        self.eye4.vibrate(50, 1, 0.05, 1)
        self.eye5.vibrate(50, 1, 0.05, 1)
        self.eye6.vibrate(50, 1, 0.05, 1)
        self.eye7.vibrate(50, 1, 0.05, 1)


if __name__ == "__main__":
    top_left = Servo(0, 35, 82)
    top_mid_left = Servo(1, 137, 180)
    top_mid_right = Servo(2, 35, 84)
    top_right = Servo(3, 80, 130)
    bottom_left = Servo(4, 30, 70)
    bottom_mid_left = Servo(5, 90, 140)
    bottom_mid_right = Servo(6, 80, 150)
    bottom_right = Servo(7, 38, 83)
    pumpkin = ServoPumpkin(top_left, top_mid_left, top_mid_right, top_right,
                           bottom_left, bottom_mid_left, bottom_mid_right, bottom_right)

    eyes = ServoGroup2(
        [top_left, top_mid_left, top_mid_right, top_right, bottom_left, bottom_mid_left, bottom_mid_right,
         bottom_right])
    while True:
        pumpkin.vibrate_rounds()
        # pumpkin.random_eyes(15)
        pumpkin.ladders(30, 1, 0.05, 1)
        pumpkin.min_max(6, 1)
        pumpkin.min_max_glide(0.0003)
        pumpkin.rows()
        pumpkin.half_half()
        pumpkin.min_max_glide(0.0000009)
        pumpkin.look_directions()
        pumpkin.ladders(0, 10, 0.1)
        pumpkin.columns()
        eyes.set_angle(180)
        eyes.glide_angle(0, 180, 4)
        pumpkin.ladders(0, 2, 0.05)
