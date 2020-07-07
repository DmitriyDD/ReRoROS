"""
Motor() class intialises the serve-client then manages all movement comms
direct to the Hitatchi
Methods are:
cmd() = sends a movement instruction
set() = sets parameters such as vel speed
wheel_left/_right() = addresses an individual wheel
checksum() = calculates the end checksum
write_cmd() = sends command to server
"""

from time import sleep
from rerobot.comms import Comms

class Motor():
    global ready_flag

    def __init__(self):

        self.bytecount = 6 # this may change but so far all basic commands are 6 bytes long
        self.positive = 59
        self.negative = 27
        self.comms = Comms()

    # def start_up(self):
        print ('1.....Sending three start-up codes COM0, COM1 and COM2')

        # send the 3 codes to initialise connection
        # b"\xFA\xFB\x03\x00\x00\x00", b"\xFA\xFB\x03\x01\x00\x01", b"\xFA\xFB\x03\x02\x00\x02"
        init_string = [250, 251, 3, 0, 0, 0], [250, 251, 3, 1, 0, 1], [250, 251, 3, 2, 0, 2]

        for i in range (3):
            msg_match = False
            self.comms.flush()

            # send the data
            data = init_string[i] # iterates the 3 positions of datastring
            print(f'sending SYNC{i}: {init_string[i]} to robot')
            self.comms.write(data)
            #sleep(1)

            while msg_match == False:
                rtn_msg = self.comms.read()  # read server info packets as incoming messages
                print('listening')
                decode = list(rtn_msg)
                if rtn_msg == decode or i == 2:
                    print(f'return message is  ... {rtn_msg}')
                    msg_match = True
                sleep(0.1)  # wait for a bit

        """# 2. Initialise sequence
        sets up server connection on pg37
        and send motors ON cmd
        1. #' Open ArRobot Connection #code 40, +, 1 (IOconfig request = once)
        2. #code 18, + (request config SIP
        3. #code 50, + (set baud rate to setting 2 )  #pulse"""

        print('2.....Sending open server-client connection and initialising conditions')
        # opening_codes = b"\xFA\xFB\x06\x01\x3B\x01\x00\x02\x3B\xFA\xFB\x06\x28\x3B\x02\x00\x2a\x3B",
        #                      b"\xFA\xFB\x06\x12\x3B\x01\x00\x13\x3B",
        #                      b"\xFA\xFB\x06\x32\x3B\x02\x00\x34\x3B\xFA\xFB\x03\x00\x00\x00"
        opening_codes = [250, 251, 6, 1, 59, 1, 0, 2, 59, 250, 251, 6, 40, 59, 1, 0, 41, 59],  \
                        [250, 251, 6, 18, 59, 1, 0, 19, 59], \
                        [250, 251, 6, 50, 59, 2, 0, 52, 59, 250, 251, 3, 0, 0, 0]

        for i, codes in enumerate(opening_codes):
            self.comms.write(opening_codes[i])

            sleep(0.5)
            self.sip_read()
            self.comms.pulse()

        """3. initialises all the motor params
        A: #code 62, +, 1 (????not in manual … pulse off? No further pulses) 
        #code 4 = Enable robot's motors

        B: #code 06, +, && (set max vel to 500mm/sec)
        #code 05, +, 2c 01 (set trans accelerator to 300mm/s/s)
        #code 05, -, 2c 01 (set trans decelerations to 300mm/s/s
        #code 11, +, 0 (translate vel to mm/sec fwd
        #code 10, +, 64 (set rotate vel to 64mm/s
        #code 23, + 64 (rotational accel to 100
        #code 23, -, 64 (ditto anti-clockwise"""

        print('3.......Sending motor setup and params')
        # motor_codes = b"\xFA\xFB\x06\x3E\x3B\x01\x00\x3F\x3B\xFA\xFB\x06\x04\x3B\x01\x00\x05\x3B",
        # b"\xFA\xFB\x06\x06\x3B\xF4\x01\xFA\x3C\xFA\xFB\x06\x05\x3B\x2C\x01\x31\x3C
        # \xFA\xFB\x06\x05\x1B\x2C\x01\x31\x1C\xFA\xFB\x06\x0B\x3B\x00\x00\x0B\x3B
        # \xFA\xFB\x06\x0A\x3B\x64\x00\x6E\x3B\xFA\xFB\x06\x17\x3B\x64\x00\x7B\x3B\xFA\xFB\x06\x17\x1B\x64\x00\x7B\x1B"
        motor_codes = [250, 251, 6, 62, 59, 1, 0, 63, 59, 250, 251, 6, 4, 59, 1, 0, 5, 59], \
                      [250, 251, 6, 6, 59, 244, 1, 250, 60, 250, 251, 6, 5, 59, 44, 1, 49, 60,
                       250, 251, 6, 5, 27, 44, 1, 49, 28, 250, 251, 6, 11, 59, 0, 0, 11, 59,
                       250, 251, 6, 10, 59, 100, 0, 110, 59, 250, 251, 6, 23, 59, 100, 0, 123, 59,
                       250, 251, 6, 23, 27, 100, 0, 123, 27]

        for i, codes in enumerate(motor_codes):
            self.comms.write(motor_codes[i])
            sleep(1)
            self.sip_read()
            self.comms.pulse()

        for i in range (5):
            print(f'REROBOT READY ... {5 - i}\n\n\t\t')
            sleep(0.5)

        self.ready_flag = True

    def cmd(self, cmd, value):
        """builds and sends a movement instruction
        1st creates checksum from bytes after byte-count"""
        command_array = [cmd] # adds command code
        if value > 0: # + or - integer to follow
            command_array.append(self.positive)
        else:
            command_array.append(self.negative)
            value *= -1
        command_array.append(value) # 2 byte integer Least 1st
        command_array.append(0) # 2 byte integer Least 1st
        # calculate checksum
        checksum = self.checksum(command_array)
        command_array += checksum # add it to end of arra
        command_array[:0] = [250, 251, 6] # finally adds header x2 & bytecount (which is always 6) to the front
        self.send_cmd(command_array)

    def set(self):
        """sets parameters such as max vel speed
        SETRV limit (cmd 10)= heading turn
        SETV speed (cmd 6)= Move speed
        """
        pass

    def stop(self):
        # self.send_cmd(b'\xFA\xFB\x03\x1D\x00\x1D')   # all stop command
        self.send_cmd([250, 251, 3, 29, 00, 29])   # all stop command

    def checksum(self, code):
        # TODO will need to amend when large number come through e.g. set vel speed as these will use both bytes for the value
        ls_a = code[::2]
        ls_b = code[1::2]
        cs_a = sum(ls_a)
        cs_b = sum(ls_b)
        return [cs_a, cs_b]

    def send_cmd(self, send_message):
        """header (2 bytes = \xFA\xFB),
        byte count (1 byte),
        command_num (1 byte 0-255),
        arg_type (\x3B, \x1B or \x2B),
        arg (n bytes - always 2-byte or string conatinig lgth prefix),
        checksum (2 bytes))"""
        self.comms.write(send_message)

    def sip_read(self):
        read_data = self.comms.read()
        print(f'return message is {read_data}')
        self.comms.decode(read_data)
        self.comms.flush()

    def left(self, speed):
        """Set independent wheel velocities;
        bits 0-7 for right wheel,
        bits 8-15 for left wheel; in 20mm/sec"""
        command_array = [32, self.positive]  # adds command code
        command_array.append(speed)  # 2 byte integer Least 1st = left
        command_array.append(0)  # 2 byte integer Least 1st
        # calculate checksum
        checksum = self.checksum(command_array)
        command_array += checksum  # add it to end of arra
        command_array[:0] = [250, 251, 6]  # finally adds header x2 & bytecount (which is always 6) to the front
        self.send_cmd(command_array)

    def right(self, speed):
        """Set independent wheel velocities;
                bits 0-7 for right wheel,
                bits 8-15 for left wheel; in 20mm/sec"""
        command_array = [32, self.positive]  # adds command code
        command_array.append(0)  # 2 byte integer Least 1st
        command_array.append(speed)  # 2 byte integer Least 1st = right
        # calculate checksum
        checksum = self.checksum(command_array)
        command_array += checksum  # add it to end of arra
        command_array[:0] = [250, 251, 6]  # finally adds header x2 & bytecount (which is always 6) to the front
        self.send_cmd(command_array)

    def terminate(self):
        print ('Closing down all connections')
        # close_down_code = b"\xFA\xFB\x03\x02\x00\x02"
        close_down_code = [250, 251, 3, 2, 0, 2]
        self.comms.close_sequence(close_down_code)
