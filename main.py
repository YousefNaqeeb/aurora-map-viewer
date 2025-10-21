import wx
from controller import AppControler

def main():
    """Main function"""
    # Initialise all components
    app = wx.App()
    controller = AppControler()
    app.MainLoop()
if __name__ == "__main__":
    main()
