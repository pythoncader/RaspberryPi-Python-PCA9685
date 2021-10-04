from time import sleep, time

import sys
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


class Servo:
    # frequency is the number of pulses per second
    # each pulse has 4096 clock sections
    # on: The tick (between 0 and 4095) when the signal should transition from low to high
    # off:the tick (between 0 and 4095) when the signal should transition from high to low

    def __init__(self, channel, servo_min_bound=0, servo_max_bound=180, current_angle="unknown", info_print=True):
        self.channel = channel
        self.currentAngle = current_angle
        self.info_print = info_print
        self.servo_min_bound = servo_min_bound
        self.servo_max_bound = servo_max_bound
        if self.info_print:
            print(
                f'Initializing Servo on channel :self.channel with range :self.servo_min_bound '
                f'to :self.servo_max_bound degrees.')

    def __str__(self):
        return f"Servo on channel :self.channel at :self.currentAngle degrees"

    def set_info_print(self, info_print):
        self.info_print = info_print

    def set_angle(self, angle=90, delay_amount=0.3, clock_start=0):
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
                f"Setting Servo on channel :self.channel to :self.currentAngle "
                f"on clock starting time :clock_start and waiting :time seconds")
        sleep(delay_amount)

    def glide_angle(self, starting_angle, ending_angle, time_to_take):
        if self.info_print:
            print(
                f"Servo on channel :self.channel gliding from angle :starting_angle to :ending_angle "
                f"in :time_to_take seconds")
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


class ServoGroup:
    # frequency is the number of pulses per second
    # each pulse has 4096 clock sections
    # on: The tick (between 0 and 4095) when the signal should transition from low to high
    # off:the tick (between 0 and 4095) when the signal should transition from high to low

    def __init__(self, num_of_servos, *channels, current_angle="unknown", info_print=True):
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
                f"Setting servos on channels :self.channels to :self.currentAngle "
                f"on clock starting time :clock_start")
        sleep(delay_amount)


class ServoGroup2:
    def __init__(self, *Servos, info_print=True):
        self.info_print = info_print
        self.Servos = Servos

    def set_angle(self, angle=90, delay_amount=1.0, clock_start=0):
        for servo_i in self.Servos:
            servo_i.set_angle(angle, 0, clock_start)
        sleep(delay_amount)

    def glide_angle(self, starting_angle, ending_angle, time_to_take):
        if self.info_print:
            print(
                f"ServoGroup gliding from angle :starting_angle to :ending_angle in :time_to_take seconds")
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

    def reset_out(self, amount_time=2):
        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye2.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        sleep(amount_time * 1000)

    def random_eyes(self, duration, random_time=200):  # give duration of running in seconds
        print("pumpkin random starting...")
        start_time = time()
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

            end_time = time()

        print("pumpkin random ending...")

    def min_max(self, duration, delay_amount=1):  # give duration of running in seconds
        print("pumpkin min_max starting...")
        start_time = time()
        end_time = start_time
        duration_millis = duration * 1000
        while (end_time - start_time) <= duration_millis:
            sleep(delay_amount)
            self.eye0.set_angle(0, 0)
            self.eye1.set_angle(0, 0)
            self.eye2.set_angle(0, 0)
            self.eye3.set_angle(180, 0)
            self.eye4.set_angle(0, 0)
            self.eye5.set_angle(180, 0)
            self.eye6.set_angle(180, 0)
            self.eye7.set_angle(180, 0)

            sleep(delay_amount)

            self.eye0.set_angle(180, 0)
            self.eye1.set_angle(180, 0)
            self.eye2.set_angle(180, 0)
            self.eye3.set_angle(0, 0)
            self.eye4.set_angle(180, 0)
            self.eye5.set_angle(0, 0)
            self.eye6.set_angle(0, 0)
            self.eye7.set_angle(0, 0)

            end_time = time()

        print("pumpkin min_max ending...")

    def min_max_glide(self, eye_speed, delay_amount=1):
        self.reset_out(4)
        print("pumpkin min_max_glide starting...")

        self.eye0.glide_angle(180, 0, eye_speed)
        self.eye1.glide_angle(180, 0, eye_speed)
        self.eye2.glide_angle(180, 0, eye_speed)
        self.eye3.glide_angle(0, 180, eye_speed)
        self.eye7.glide_angle(0, 180, eye_speed)
        self.eye6.glide_angle(0, 180, eye_speed)
        self.eye5.glide_angle(0, 180, eye_speed)
        self.eye4.glide_angle(180, 0, eye_speed)

        sleep(delay_amount)
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

        sleep(delay_amount)

        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)

        sleep(delay_amount)
        self.eye2.set_angle(0, 0)
        self.eye3.set_angle(180, 0)
        self.eye6.set_angle(180, 0)
        self.eye7.set_angle(180, 0)

        sleep(delay_amount)

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
        sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        sleep(delay_amount)

        # column 2:
        self.eye1.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        sleep(delay_amount)
        self.eye1.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        sleep(delay_amount)

        # column 3:
        self.eye2.set_angle(0, 0)
        self.eye6.set_angle(180, 0)
        sleep(delay_amount)
        self.eye2.set_angle(180, 0)
        self.eye6.set_angle(0, 0)
        sleep(delay_amount)

        # column 4:
        self.eye3.set_angle(180, 0)
        self.eye7.set_angle(180, 0)
        sleep(delay_amount)
        self.eye3.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        sleep(delay_amount)

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
        sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye4.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        sleep(delay_amount)

        # column 2:
        self.eye1.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        # column 3:
        self.eye2.set_angle(0, 0)
        self.eye6.set_angle(180, 0)
        sleep(delay_amount)
        self.eye1.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye2.set_angle(180, 0)
        self.eye6.set_angle(0, 0)
        sleep(delay_amount)

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
        sleep(delay_amount)
        self.eye0.set_angle(180, 0)
        self.eye1.set_angle(180, 0)
        self.eye2.set_angle(180, 0)
        self.eye3.set_angle(0, 0)
        sleep(delay_amount)

        # bottom row:
        self.eye4.set_angle(0, 0)
        self.eye5.set_angle(180, 0)
        self.eye6.set_angle(180, 0)
        self.eye7.set_angle(180, 0)
        sleep(delay_amount)
        self.eye4.set_angle(180, 0)
        self.eye5.set_angle(0, 0)
        self.eye6.set_angle(0, 0)
        self.eye7.set_angle(0, 0)
        sleep(delay_amount)
        print("rows ending...")

    def look_directions(self, delay_amount=1):
        self.reset_out()
        print("look_directions starting...")
        # start bottom halves at same time
        self.eye4.set_angle(0, 0)  # inward
        self.eye5.set_angle(0, 0)  # inward
        self.eye6.set_angle(0, 0)  # outward
        self.eye7.set_angle(0, 0)  # outward
        sleep(delay_amount)
        self.eye4.set_angle(180, 0)  # outward
        self.eye5.set_angle(180, 0)  # outward
        self.eye6.set_angle(180, 0)  # inward
        self.eye7.set_angle(180, 0)  # inward
        sleep(delay_amount)

        # start top halves at same time
        self.eye0.set_angle(0, 0)  # inward
        self.eye1.set_angle(0, 0)  # inward
        self.eye2.set_angle(180, 0)  # outward
        self.eye3.set_angle(180, 0)  # outward
        sleep(delay_amount)
        self.eye0.set_angle(180, 0)  # outward
        self.eye1.set_angle(180, 0)  # outward
        self.eye2.set_angle(0, 0)  # inward
        self.eye3.set_angle(0, 0)  # inward
        sleep(delay_amount)
        print("look_directions ending...")

    def ladders(self, interval=15, delay_amount=3, duration=100):
        print("ladders starting...")
        start_time = time()
        end_time = start_time
        duration_millis = duration * 1000
        for i in range(0, 181):
            self.eye0.set_angle(0, 0)
            self.eye1.set_angle(0, 0)
            self.eye2.set_angle(0, 0)
            self.eye3.set_angle(180, 0)
            self.eye4.set_angle(0, 0)
            self.eye5.set_angle(0, 0)
            self.eye6.set_angle(0, 0)
            self.eye7.set_angle(0, 0)
            sleep(delay_amount * 1000)
            self.eye0.set_angle(i, 0)
            self.eye1.set_angle(i, 0)
            self.eye2.set_angle(i, 0)
            self.eye3.set_angle(abs(i - 180), 0)
            self.eye4.set_angle(i, 0)
            self.eye5.set_angle(i, 0)
            self.eye6.set_angle(i, 0)
            self.eye7.set_angle(i, 0)
            sleep(delay_amount * 1000)
            i += interval
            if (end_time - start_time) <= duration_millis:
                end_time = time()
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
        self.eye0.vibrate(1, 0.05, 1)
        self.eye1.vibrate(1, 0.05, 1)
        self.eye2.vibrate(1, 0.05, 1)
        self.eye3.vibrate(1, 0.05, 1)
        self.eye4.vibrate(1, 0.05, 1)
        self.eye5.vibrate(1, 0.05, 1)
        self.eye6.vibrate(1, 0.05, 1)
        self.eye7.vibrate(1, 0.05, 1)


if __name__ == "__main__":
    servo_1 = Servo(0, 90, 135)
    servo_2 = Servo(1)
    servo_3 = Servo(2)
    servo_4 = Servo(3, 0, 180)
    four_servos = ServoGroup2((servo_1, servo_2, servo_3, servo_4))
