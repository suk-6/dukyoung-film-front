import win32print
import win32api
import os

def printer(file):
    printerName = win32print.GetDefaultPrinter()
    printerInfo = win32print.GetPrinter(printerName, 2)

    if not os.path.isfile(file):
        return False
    else:
        # 프린트 작업 설정
        printerInfo['pPortName'] = printerName
        printerInfo['pDatatype'] = 'RAW'
        
        hprinter = win32print.OpenPrinter(printerName)
        win32print.StartDocPrinter(hprinter, 1, ('Print Job', None, 'RAW'))
        win32print.StartPagePrinter(hprinter)
        with open(file, 'rb') as f:
            win32api.ShellExecute(0, 'print', file, None, '.', 0)
        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
        win32print.ClosePrinter(hprinter)
