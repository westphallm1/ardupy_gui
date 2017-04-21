# Hello world example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v55.3+.

from cefpython3 import cefpython as cef
import platform
import sys
import os
import glob
import time
import serial
from echo import SerialEcho


class External(object):
    KEY_CODES = {
        'SUM': ',s',
        'PROD':',p',
        'MEAN':',m',
        'CLEAR':',c',
        'EMPTY_BUFFSTR':SerialEcho.EMPTY_BUFFSTR
    }
    noop = lambda:None
    def __init__(self,tty='/dev/ttyACM0'):
        self.ser = None
        self.err_callback = None

    def parse_coords(self,coord_string):
        return sum([[item for item in pair.split(',')]
            for pair in coord_string.split()],[])

    def send(self,string,use_end=True):
        """send a character string to the arduino via serial,
        then read all characters off the arduino's buffer
        """
        if self.ser is None:
            if len(string) > 1:
                self.raise_serial_err("Not currently connected to an Arduino")
            return

        int_strings = self.parse_coords(string)
        try:
            for substr in int_strings:
                self.ser.send_chars(substr,use_end)
        except serial.serialutil.SerialException as e:
            if(len(string) > 1):
                self.raise_serial_err(e)
    
    def echo(self,js_callback):
        try:
            js_callback.Call(self.ser.recieve_chars(),External.noop)
        except serial.serialutil.SerialException as e:
            self.raise_serial_err(e)
        except AttributeError as e:
            pass

    def set_serial_err(self,js_callback):
        self.err_callback = js_callback

    def raise_serial_err(self,msg=''):
        print(msg)
        self.good_to_read = False
        if self.err_callback:
            self.err_callback.Call(str(msg),External.noop)

    def set_serial_port(self,tty):
        try:
            self.ser = SerialEcho(tty)
            self.good_to_read = True
            print("Connected to arduino at %s"%tty)
        except serial.serialutil.SerialException:
            self.raise_serial_err("Couldn't connect to Arduino at %s"%tty)

    def get_tty_options(self,js_callback):
        js_callback.Call(glob.glob('/dev/ttyACM*'),External.noop)


def main():
    url= 'file://%s/index.html'%os.getcwd()
    print(url)
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

    
    cef.Initialize()
    #set up a browser
    browser = cef.CreateBrowserSync(window_title="Hello World!", url=url)
    frame = browser.GetMainFrame()
    #set up the browser's javascript bindings
    external = External()
    bindings = cef.JavascriptBindings()
    bindings.SetFunction("echo", external.echo)
    bindings.SetObject("external",external)
    bindings.SetProperty("KEY_CODES",External.KEY_CODES)
    browser.SetJavascriptBindings(bindings)
    cef.MessageLoop()
    cef.Shutdown()


def check_versions():
    print("[hello_world.py] CEF Python {ver}".format(ver=cef.__version__))
    print("[hello_world.py] Python {ver} {arch}".format(
          ver=platform.python_version(), arch=platform.architecture()[0]))
    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"


if __name__ == '__main__':
    main()
