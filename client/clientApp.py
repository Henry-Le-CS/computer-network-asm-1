import tkinter as tk
import sys
import multiprocessing
import threading

from client import Client

class App(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self)

    self.title("Client App")
    self.geometry("500x500+300+100")
    self.resizable(False, True)
    self.config(bg = "#474040")
    
    self.frame = tk.Frame(self, bg = '#474040')
    self.frame.pack(side = tk.TOP, fill = tk.BOTH)

    # Hardcoded params first...
    self.client = Client(hostname='hihihehe', server_host='192.168.254.144')
    self.client_thread = threading.Thread(target=self.client.start)
    self.client_thread.start()

    self.protocol("WM_DELETE_WINDOW", self.on_closing)

  def on_closing(self):
    print("Closing!")
    # self.sender.close()

    # self.listen_thread.terminate()
    sys.exit()

if __name__ == "__main__":
  # if not os.path.exists(downloads_folder):
  #   print("Download dir is not correct")
  #   tkinter.messagebox.showerror(title="Error", message="Download directory do not exist !\n Please check Client.py 'download_folder'")
  #   sys.exit(-1)
  # if not os.path.exists(share_folder):
  #   print("Sharing Folder is not correct")
  #   tkinter.messagebox.showerror(title="Error", message="Sharing directory do not exist !\n Please check Client.py 'share_folder'")
  #   sys.exit(-1)

  app = App()
  app.mainloop()
