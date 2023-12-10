import tkinter as tk
import customtkinter as ctk
from CTkListbox import *
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import sys
import os
import multiprocessing
import threading

import subprocess

from client import Client

REPO_PATH = 'repository/'

class App():
  def __init__(self):
    self.app = ctk.CTk()

    self.fontS = ctk.CTkFont('Montserrat', 12)
    self.fontM = ctk.CTkFont('Montserrat', 16)
    self.fontL = ctk.CTkFont('Montserrat', 18, 'bold')
    self.fontXL = ctk.CTkFont('Montserrat', 24, 'bold')

    self.deleteLocalBtnState = 'disabled'
    # self.isFetchFileSelected = False

    self.init_app()

    # Starting client logic
    # Hardcoded params first...
    
    self.show_login_screen()

  def init_app(self):
    self.app.title("Client App")

    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720

    SCREEN_WIDTH = self.app.winfo_screenwidth()
    SCREEN_HEIGHT = self.app.winfo_screenheight()

    X_OFFSET = (SCREEN_WIDTH/2) - (WINDOW_WIDTH/2)
    Y_OFFSET = (SCREEN_HEIGHT/2) - (WINDOW_HEIGHT/2)

    self.app.geometry('%dx%d+%d+%d' % (WINDOW_WIDTH, WINDOW_HEIGHT, X_OFFSET, Y_OFFSET))
    # self.app.resizable(False, True)
    self.app.config(bg = "#474040")

    self.setup_frames()

    self.app.frame = tk.Frame(self.app, bg = '#474040')
    self.app.frame.pack(side = tk.TOP, fill = tk.BOTH)

    self.app.protocol("WM_DELETE_WINDOW", self.on_closing)

  def setup_frames(self):
    self.signInFrame = ctk.CTkFrame(self.app, 1024, 720, fg_color='#b3cccc', corner_radius=0)
    self.mainFrame = ctk.CTkFrame(self.app, 1024, 720, fg_color='#67729D', corner_radius=0)

  def show_login_screen(self):
    self.signInFrame.place(relwidth=1, relheight=1, relx=0.5, rely=0.5, anchor=ctk.CENTER)

    self.EntryFrame = ctk.CTkFrame(self.signInFrame, 350, 200, fg_color='#b3cccc', corner_radius=15, border_width=2, border_color='white')
    self.AppTitleLogin = ctk.CTkLabel(self.signInFrame, text='File-Sharing Application', font=self.fontXL,
                                  text_color='black', corner_radius=15)
    self.AppIcon = ctk.CTkLabel(self.signInFrame, 70, 70, fg_color='#75a3a3', text='', corner_radius=15)
    self.ServerIPLabel = ctk.CTkLabel(self.signInFrame, 100, 30, text='SERVER IP', font=self.fontL, 
                                      text_color='black')
    self.ServerIPEntry = ctk.CTkEntry(self.signInFrame, 200, 30,
                                corner_radius=10, placeholder_text='Server IP', text_color='white')
    self.HostnameLabel = ctk.CTkLabel(self.signInFrame, 100, 30, text='HOSTNAME', font=self.fontL,
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
    self.mainFrame.place(relwidth=1, relheight=1, relx=0.5, rely=0.5, anchor=ctk.CENTER)

    self.PublishLabel = ctk.CTkLabel(self.mainFrame, text='Publish a file to server', fg_color='#FED9ED', text_color='#860A35', font=self.fontXL, corner_radius=8)
    self.PublishLabel.place(relwidth = 0.4, relheight=0.06, relx=0.25, rely=0.07, anchor=ctk.CENTER)

    self.FetchLabel = ctk.CTkLabel(self.mainFrame, text='Fetch a file from another peer', fg_color='#FED9ED', text_color='#860A35', font=self.fontXL, corner_radius=8)
    self.FetchLabel.place(relwidth = 0.4, relheight=0.06, relx=0.75, rely=0.07, anchor=ctk.CENTER)

    self.PeerLabel = ctk.CTkLabel(self.mainFrame, text='Select a peer to fetch', fg_color='#FED9ED', text_color='#860A35', font=self.fontXL, corner_radius=8)
    self.PeerLabel.place(relwidth = 0.4, relheight=0.06, relx=0.75, rely=0.585, anchor=ctk.CENTER)

    # self.PublishFrame = ctk.CTkFrame(self.mainFrame, 350, 120, fg_color='#FED9ED', corner_radius=8)
    # self.PublishFrame.place(relwidth=0.4, relheight=0.65, relx=0.25, rely=0.55, anchor=ctk.CENTER)
    
    # self.FetchFrame = ctk.CTkFrame(self.mainFrame, 350, 120, fg_color='#FED9ED', corner_radius=8)
    # self.FetchFrame.place(relwidth=0.4, relheight=0.65, relx=0.75, rely=0.55, anchor=ctk.CENTER)

    self.PublishButton = ctk.CTkButton(self.mainFrame, text='Choose a file to publish', command=self.publish_file, fg_color='#CC5C70')
    self.PublishButton.place(relwidth=0.34, relheight=0.05, relx=0.05, rely=0.14, anchor=ctk.W)
    
    self.RepoRefreshButton = ctk.CTkButton(self.mainFrame, text='Refresh', command=self.update_LocalList, fg_color='#29ADB2')
    self.RepoRefreshButton.place(relwidth=0.05, relheight=0.05, relx=0.45, rely=0.14, anchor=ctk.E)
    
    self.renderFetchBtn()
    
    self.FetchRefreshButton = ctk.CTkButton(self.mainFrame, text='Refresh', command=self.get_available_files, fg_color='#29ADB2')
    self.FetchRefreshButton.place(relwidth=0.05, relheight=0.05, relx=0.95, rely=0.14, anchor=ctk.E)

    self.disconnect_Button = ctk.CTkButton(self.mainFrame, text='Disonnect', command=self.disconnect_server, fg_color='#CC5C70')
    self.disconnect_Button.place(relwidth=0.35, relheight=0.06, relx=0.5, rely=0.94, anchor=ctk.CENTER)

    self.renderDeleteLocalBtn()

    self.LocalList = CTkListbox(self.mainFrame, fg_color='#FED9ED', corner_radius=8, border_width=3, border_color='#CC5C70', text_color='#860A35',
                                   hover_color='#FFC0D9', font=self.fontM, select_color='#29ADB2', command=self.toggleLocalFileSelection)
    self.LocalList.place(relwidth=0.4, relheight=0.7, relx=0.25, rely=0.18, anchor=ctk.N)                               
    
    self.FetchList = CTkListbox(self.mainFrame, fg_color='#FED9ED', corner_radius=8, border_width=3, border_color='#CC5C70', text_color='#860A35',
                                   hover_color='#FFC0D9', font=self.fontM, select_color='#29ADB2', command=self.fetch_peers)
    self.FetchList.place(relwidth=0.4, relheight=0.36, relx=0.75, rely=0.18, anchor=ctk.N)                               

    self.PeerList = CTkListbox(self.mainFrame, fg_color='#FED9ED', corner_radius=8, border_width=3, border_color='#CC5C70', text_color='#860A35',
                                   hover_color='#FFC0D9', font=self.fontM, select_color='#29ADB2')
    self.PeerList.place(relwidth=0.4, relheight=0.25, relx=0.75, rely=0.63, anchor=ctk.N)                               

    

  def connect_server(self):
    serverIP = self.ServerIPEntry.get()
    hostname = self.HostnameEntry.get()
    print('got inputs', serverIP, hostname)

    if not serverIP or not hostname:
      # Handle empty fields
      self.WarningLabel = ctk.CTkLabel(self.signInFrame, text='Please enter both Server IP and Hostname.', font=self.fontM,
                                        text_color='red')
      self.WarningLabel.place(relx=0.5, rely=0.75, anchor=ctk.CENTER)
      self.WarningLabel.after(2000, lambda: self.WarningLabel.place_forget())
      return

    self.client = Client(controller=self, hostname=hostname, server_host=serverIP)
    self.client_thread = threading.Thread(target=self.client.start,daemon=True)
    self.client_thread.start()

    self.hide_login_screen()
    self.show_main_screen()
    # self.client.get_all_available_files()
    self.update_Lists()
    self.get_available_files()
    # self.update_LocalList()
    # self.update_FetchList()

  def disconnect_server(self):
    restart()
    
    self.hide_main_screen()
    self.show_login_screen()

  def get_available_files(self):
    self.client.get_available_files()

  def publish_file(self):
    print('publishing file')
    self.upload_file()
    self.update_Lists()
    # self.update_LocalList()
    # self.get_available_files()
    
  def fetch_file(self):
    file_name = self.FetchList.get()
    hostname = self.PeerList.get()

    if not file_name or not hostname:
      self.pop_error_dialog("You have to select the file and the peer to fetch!")
      return
      
    print('fetching file...')
    peer = self.find_peer_by_hostname(hostname)

    if not peer:
      self.pop_error_dialog()
      return

    hostname, host, port, file_path = peer.split()
    self.client.make_download_request((hostname, host, port, file_path, file_name))

  def find_peer_by_hostname(self, hostname):
    print('current peer list', self.client.peerList)
    for peer in self.client.peerList:
      if hostname == peer.split()[0]:
        print('Hehe found peer', peer)
        return peer
    print('Huhu no peer')
    return None

  def fetch_peers(self, val):
    print('Fetching peers for ', val)
    self.client.get_peers(val)

  def upload_file(self):
    filePath = filedialog.askopenfilename()
    lname, fname = os.path.split(filePath)
    print('Got file path:', lname, '-', fname)
    self.client.store_file_into_repo(lname, fname)
    self.client.publish_file_info(('./repository', fname))

  def update_Lists(self):
    self.update_LocalList()
    self.update_FetchList()
    self.update_PeerList()

  def update_LocalList(self):
    print('[UI] updating local list')
    if self.LocalList.size():
        self.LocalList.delete(0,'END')
    filePath = os.path.join(os.getcwd(), REPO_PATH)
    for fileName in os.listdir(filePath):
        self.LocalList.insert('END',fileName)
    
    self.deleteLocalBtnState = 'disabled'
    self.renderDeleteLocalBtn()

  def update_FetchList(self):
    print('[UI] updating fetch list - ', self.client.remoteFiles)
    print('checking len:', len(self.client.remoteFiles))
    if self.FetchList.size() > 0:
      self.FetchList.delete(0, 'END')

    # if len(self.client.remoteFiles) == 0:
    #   self.client.get_available_files()
    #   return

    for file in self.client.remoteFiles:
      print('adding ', file)
      self.FetchList.insert('END', file)
    
  def update_PeerList(self):
    print('[UI] updating peer list', self.client.peerList)
    if self.PeerList.size():
      self.PeerList.delete(0, 'END')
    for peer in self.client.peerList:
      hostname = peer.split()[0]
      print('adding ', peer)
      self.PeerList.insert('END', hostname)

  def remove_local_file(self):
    fname = self.LocalList.get()
    print('removing local file', fname)
    self.client.remove_local_file(('./repository', fname))
    self.LocalList.delete(self.LocalList.curselection())

  def renderDeleteLocalBtn(self):
    self.DeleteLocalFileButton = ctk.CTkButton(self.mainFrame, text='Delete Local', command=self.remove_local_file, fg_color='#D80032', state=self.deleteLocalBtnState)
    self.DeleteLocalFileButton.place(relwidth=0.15, relheight=0.06, relx=0.05, rely=0.94, anchor=ctk.W)

  # Placeholder for future button logic
  def renderFetchBtn(self):
    self.FetchButton = ctk.CTkButton(self.mainFrame, text='Fetch file', command=self.fetch_file, fg_color='#CC5C70')
    self.FetchButton.place(relwidth=0.34, relheight=0.05, relx=0.55, rely=0.14, anchor=ctk.W)

  def toggleLocalFileSelection(self, val):
    fname = self.LocalList.get()
    if fname == None:
      self.deleteLocalBtnState = 'disabled'
    else:
      self.deleteLocalBtnState = 'normal'
    self.renderDeleteLocalBtn()
  
  def toggleFetchFileSelection(self, val):
    fname = self.FetchList.get()
    if fname == None:
      self.isFetchFileSelected = False
    else:
      self.isFetchFileSelected = True
    self.renderFetchBtn()

  def pop_error_dialog(self, msg):
    CTkMessagebox(title="Error", message=msg if msg else 'Something went wrong, please try again.', icon="cancel")
    return

  def on_closing(self):
    print("Closing!")
    # self.sender.close()

    # self.listen_thread.terminate()

    # self.terminate_flag.set()

    # self.client_thread.join()
    if hasattr(self, 'client'):
      self.client.disconnect()
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
