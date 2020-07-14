import time

from consts import *
from interception import  *
import mido
from mido import Message

# Change these settings for your own setup
# this is the MIDI channel this script will transmit on
MIDI_CHANNEL = 'pedalboard 1'
CHANNEL = 0

# edit the notemap yourself, it is formatted as key_Stroke:note
# remember that 35 will be added to each note
NOTE_MAP = {
    0: {9:1, 3:2, 4:3, 5:4, 8:5,
        26:6, 65:7, 27:8, 21:9, 20:10, 61:11, 58:12, 126:13,
        81:14, 79:15, 39:16, 38:17, 36:18, 37:19, 33:20, 32:21,
        63:22, 40:23, 121:24, 64:25, 35:26, 34:27},
}
# DO NOT CHANGE unless you understand the code
ACTIVE_DEVICES = []
ACTIVE_NOTES = []
INTERCEPTION = None

def get_note(device, scan_code):
    device = ACTIVE_DEVICES.index(device)
    
    if scan_code not in NOTE_MAP[device]:
        print('unknown scan code {}'.format(scan_code))
        return
    
    return NOTE_MAP[device][scan_code] + 35

def press_note(device, code, port):
    if int(code) in ACTIVE_NOTES:
        return

    note = get_note(device, code)
    if not note:
        return
    
    msg = Message('note_on', note=note, channel=CHANNEL, velocity=127)
    port.send(msg)
    ACTIVE_NOTES.append(int(code))
    print(msg)

def release_note(device, code, port):
    note = get_note(device, code)
    if not note:
        return

    ACTIVE_NOTES.remove(int(code))
    msg = Message('note_on', note=note, channel=CHANNEL, velocity=0)
    print(msg)
    port.send(msg)

def on_note(device, code, state, port):
    if state == 0: # TODO change
        press_note(device, code, port)
    elif state == 1:
        release_note(device, code, port)
    else:
        print('unknown state')

def register_device():
    print('Press a key on the device to register')
    device = capture_keyboard_device()
    ACTIVE_DEVICES.append(device)
    print('Listening to device {}'.format(device))

def setup_interception():
    global INTERCEPTION
    INTERCEPTION = interception()
    INTERCEPTION.set_filter(interception.is_keyboard,
                 interception_filter_key_state.INTERCEPTION_FILTER_KEY_ALL.value)

def capture_keyboard_device():
    global INTERCEPTION
    device = INTERCEPTION.wait()
    return device

def active_devices_to_midi():
    global INTERCEPTION
    print('Using active devices {}'.format(ACTIVE_DEVICES))

    # open up the midi port
    with mido.open_output(MIDI_CHANNEL) as port:
        print('Opened MIDI port {}'.format(MIDI_CHANNEL))
        while True:
            device = INTERCEPTION.wait()
            # check if device is a keyboard
            if interception.is_keyboard(device):
                stroke = INTERCEPTION.receive(device)

                # required to let your main keyboard function
                if device not in ACTIVE_DEVICES:
                    INTERCEPTION.send(device, stroke)
                else:
                    if type(stroke) is key_stroke:
                        on_note(device, stroke.code, stroke.state, port)

if __name__ == "__main__":
    setup_interception()
    register_device()
    active_devices_to_midi()
