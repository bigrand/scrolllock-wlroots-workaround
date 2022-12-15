#!/usr/bin/python3

import libevdev
import sys
import re
import os


def toggle(path, keystr, ledstr, forceLed, startLed):

    ledmap = {
        'numlock': (libevdev.EV_LED.LED_NUML, libevdev.EV_KEY.KEY_NUMLOCK),
        'capslock': (libevdev.EV_LED.LED_CAPSL, libevdev.EV_KEY.KEY_CAPSLOCK),
        'scrolllock': (libevdev.EV_LED.LED_SCROLLL, libevdev.EV_KEY.KEY_SCROLLLOCK),
    }

    if keystr not in ledmap:
        print('Unknown key: "{}". Use one of "{}".'.format(
            keystr, '", "'.join(ledmap.keys())))
        sys.exit(1)

    if ledstr not in ledmap:
        print('Unknown LED: "{}". Use one of "{}".'.format(
            ledstr, '", "'.join(ledmap.keys())))
        sys.exit(1)

    otherKeys = [ledmap[key] for key in ledmap if key != keystr]
    (_, ledKey1), (_, ledKey2) = otherKeys

    _, toggleKey = ledmap[keystr]
    led, _ = ledmap[ledstr]

    ledsInput = os.listdir('/sys/class/leds/')

    for inputFile in ledsInput:
        if re.search(keystr, inputFile):
            inputName = inputFile

    brightnessPath = '/sys/class/leds/{}/brightness'.format(inputName)

    with (
        open(path, "r+b", buffering=0) as fd,
        open(brightnessPath, 'r') as f
    ):

        dev = libevdev.Device(fd)
        keyState = int(f.read().strip())

        if keystr == 'scrolllock':
            keyState = True

        if not dev.has(led):
            print('Device does not have a {} LED'.format(ledstr))
            sys.exit(0)

        if not dev.has(toggleKey):
            print('Device does not have a {} toggleKey'.format(keystr))
            sys.exit(0)

        if startLed:
            ledState = True
            dev.set_leds([(led, ledState)])

        elif not startLed:
            ledState = False
            dev.set_leds([(led, ledState)])

        if forceLed:
            while True:
                for e in dev.events():
                    if e.value:
                        continue
                    
                    dev.set_leds([(led, ledState)])

                    if e.matches(ledKey1) or e.matches(ledKey2):
                        continue

                    if e.matches(toggleKey):
                        keyState = not keyState
                        if not (ledState == keyState):
                            ledState = not ledState
                        else:
                            continue
        elif not forceLed:
            while True:
                for e in dev.events():
                    if not e.matches(toggleKey):
                        continue

                    if not e.value:
                        continue

                    keyState = not keyState
                    dev.set_leds([(led, keyState)])
        else:
            print(
                "Usage: {} /dev/input/eventX {{numlock|capslock|scrolllock}} {{numlock|capslock|scrolllock}} {{0|1}} {{0|1}}".format(sys.argv[0]))
            print(" <path> <keystr> <ledstr> <forceLed> <startLed>".format(
                sys.argv[0]))
            sys.exit(1)


if __name__ == "__main__":

    if len(sys.argv) < 6:
        print(
            "Usage: {} /dev/input/eventX {{numlock|capslock|scrolllock}} {{numlock|capslock|scrolllock}} {{0|1}} {{0|1}}".format(sys.argv[0]))
        print(" <path> <keystr> <ledstr> <forceLed> <startLed>".format(
            sys.argv[0]))
        sys.exit(1)

    path = sys.argv[1]  # /dev/input/eventX | event path
    keystr = sys.argv[2]  # {numlock|capslock|scrolllock} | led toggle key
    ledstr = sys.argv[3]  # {numlock|capslock|scrolllock} | led to toggle
    forceLed = sys.argv[4] # {0|1} | forces led to stay ON unless the toggle key is pressed
    startLed = sys.argv[5] # {0|1} | upong executing sets the led ON or OFF

    if not (forceLed in {'0','1'}):
        print('Invalid argument: "{}" is not a <forceLed> boolean value . Use 0 or 1.'.format(
            str(forceLed)))
        sys.exit(1)

    forceLed = int(forceLed)

    if not (startLed in {'0','1'}):
        print('Invalid argument: "{}" is not a <startLEd> boolean value . Use 0 or 1.'.format(
            str(startLed)))
        sys.exit(1)

    startLed = int(startLed)

    try:
        toggle(path, keystr, ledstr, forceLed, startLed)
    except KeyboardInterrupt:
        pass
    except IOError as e:
        import errno
        if e.errno == errno.EACCES:
            print("Error: Insufficient permissions to access {}".format(path))
        elif e.errno == errno.ENOENT:
            print("Error: Device {} does not exist".format(path))
        else:
            raise e