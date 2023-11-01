import win32print
import win32api
import os
import pyautogui
import time

printerName = win32print.GetDefaultPrinter()
hprinter = win32print.OpenPrinter(printerName)
printerInfo = win32print.GetPrinter(hprinter, 2)
printerInfo['pPortName'] = printerName
printerInfo['pDatatype'] = 'RAW'

def printer(file):

    if not os.path.isfile(file):
        return False
    else:
        win32print.StartDocPrinter(hprinter, 1, ('Print Job', None, 'RAW'))
        win32print.StartPagePrinter(hprinter)
        with open(file, 'rb') as f:
            win32api.ShellExecute(0, 'print', file, None, '.', 0)
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)
        time.sleep(1)
        pyautogui.press('enter')

if __name__ == "__main__":
    print(printerInfo)