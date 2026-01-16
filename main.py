import wx
from controller import AppControler

def main():

    app = wx.App()
    controller = AppControler()
    app.MainLoop()
if __name__ == "__main__":
    main()
