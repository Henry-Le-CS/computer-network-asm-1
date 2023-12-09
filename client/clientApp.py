import tkinter as tk
import customtkinter as ctk
import sys
import os
import multiprocessing
import threading

from client import Client

class App():
  def __init__(self):
    self.app = ctk.CTk()
    self.init_app()

    # Starting client logic
    # Hardcoded params first...
    

    self.show_login_screen()

    

  def init_app(self):
    self.app.title("Client App")
    self.app.geometry("500x500+300+100")
    self.app.resizable(False, True)
    self.app.config(bg = "#474040")

    self.setup_frames()

    self.app.frame = tk.Frame(self.app, bg = '#474040')
    self.app.frame.pack(side = tk.TOP, fill = tk.BOTH)

    self.app.protocol("WM_DELETE_WINDOW", self.on_closing)

  def setup_frames(self):
    self.signInFrame = ctk.CTkFrame(self.app, 700, 400, fg_color='#b3cccc', corner_radius=0)
    self.mainFrame = ctk.CTkFrame(self.app, 700, 400, fg_color='#f4cccc', corner_radius=0)

  def show_login_screen(self):
    self.signInFrame.place(relwidth=0.96, relheight=0.96, relx=0.5, rely=0.5, anchor=ctk.CENTER)

    self.EntryFrame = ctk.CTkFrame(self.signInFrame, 350, 200, fg_color='#b3cccc', corner_radius=15, border_width=2, border_color='white')
    self.AppTitleLogin = ctk.CTkLabel(self.signInFrame, text='File-Sharing Application',
                                  text_color='black', corner_radius=15)
    self.AppIcon = ctk.CTkLabel(self.signInFrame, 70, 70, fg_color='#75a3a3', text='', corner_radius=15)
    self.ServerIPLabel = ctk.CTkLabel(self.signInFrame, 100, 30, text='SERVER IP', 
                                      text_color='black')
    self.ServerIPEntry = ctk.CTkEntry(self.signInFrame, 200, 30,
                                corner_radius=10, placeholder_text='Server IP', text_color='white')
    self.HostnameLabel = ctk.CTkLabel(self.signInFrame, 100, 30, text='HOSTNAME',
                                      text_color='black')
    self.HostnameEntry = ctk.CTkEntry(self.signInFrame, 200, 30,
                                corner_radius=10, placeholder_text='Hostname', text_color='white')
    self.connect_Button = ctk.CTkButton(self.signInFrame, text='Connect', command=self.connect_server, fg_color='#3d5c5c')

    self.EntryFrame.place(relwidth=0.55, relheight=0.5, relx=0.5, rely=0.7, anchor=ctk.CENTER)
    self.AppTitleLogin.place(relwidth = 0.8, relheight=0.2, relx=0.5, rely=0.13, anchor=ctk.CENTER)
    #self.AppIcon.configure(image=ctk.CTkImage(Image.open('FileSharingIcon.png'), size=(70,70)))
    self.AppIcon.place(relwidth=0.15, relheight=0.2, relx=0.5, rely=0.3, anchor=ctk.CENTER)
    self.ServerIPLabel.place(relwidth=0.2, relheight=0.08, relx=0.35, rely=0.55, anchor=ctk.CENTER)
    self.ServerIPEntry.configure(state='normal')
    self.ServerIPEntry.place(relwidth=0.25, relheight=0.08, relx=0.55, rely=0.55, anchor=ctk.CENTER)
    self.HostnameLabel.place(relwidth=0.2, relheight=0.08, relx=0.35, rely=0.68, anchor=ctk.CENTER)
    self.HostnameEntry.configure(state='normal')
    self.HostnameEntry.place(relwidth=0.25, relheight=0.08, relx=0.55, rely=0.68, anchor=ctk.CENTER)
    self.connect_Button.place(relwidth=0.15, relheight=0.06, relx=0.5, rely=0.85, anchor=ctk.CENTER)
  
  def hide_login_screen(self):
    self.signInFrame.place_forget()

  def hide_main_screen(self):
    self.mainFrame.place_forget()
  
  def show_main_screen(self):
    self.mainFrame.place(relwidth=0.96, relheight=0.96, relx=0.5, rely=0.5, anchor=ctk.CENTER)
    self.disconnect_Button = ctk.CTkButton(self.mainFrame, text='Disonnect', command=self.disconnect_server, fg_color='#3d5c5c')
    self.disconnect_Button.place(relwidth=0.15, relheight=0.06, relx=0.5, rely=0.85, anchor=ctk.CENTER)

  def connect_server(self):
    serverIP = self.ServerIPEntry.get()
    hostname = self.HostnameEntry.get()
    print('got inputs', serverIP, hostname)

    if not serverIP or not hostname:
      # Handle empty fields
      self.WarningLabel = ctk.CTkLabel(self.signInFrame, text='Please enter both Server IP and Hostname.',
                                        text_color='red')
      self.WarningLabel.place(relx=0.5, rely=0.75, anchor=ctk.CENTER)
      self.WarningLabel.after(2000, lambda: self.WarningLabel.place_forget())
      return

    self.client = Client(hostname=hostname, server_host=serverIP)
    self.client_thread = threading.Thread(target=self.client.start,daemon=True)
    self.client_thread.start()

    
    self.hide_login_screen()
    self.show_main_screen()

  def disconnect_server(self):
    restart()
    
    self.hide_main_screen()
    self.show_login_screen()

  def on_closing(self):
    print("Closing!")
    # self.sender.close()

    # self.listen_thread.terminate()

    # self.terminate_flag.set()

    # self.client_thread.join()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    # self.client.shutdown()

def restart():
  print('Restarting process')

  os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
  # if not os.path.exists(downloads_folder):
  #   print("Download dir is not correct")
  #   tkinter.messagebox.showerror(title="Error", message="Download directory do not exist !\n Please check Client.py 'download_folder'")
  #   sys.exit(-1)
  # if not os.path.exists(share_folder):
  #   print("Sharing Folder is not correct")
  #   tkinter.messagebox.showerror(title="Error", message="Sharing directory do not exist !\n Please check Client.py 'share_folder'")
  #   sys.exit(-1)

  client = App()
  client.app.mainloop()
