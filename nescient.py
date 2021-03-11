"""
local network falcon chat server and tkinter client side chat UI

litepresence2020

to serve to www, go to http://192.168.0.1 ROUTER settings page in browswer, then:

IPV6 Firewall ALLOW:

    HTTP IN
    HTTPS IN

"Port Forwarding", bind your LAN to your WAN:

your machine's LAN address is something like 192.168.0.2; 0.3 0.4 etc.; you can do:

    hostname -I

Router Port Forwarding setting Should be something like:

Network     IP              MINPORT MAXPORT

LAN IP      192.168.0.2     8000 8000

WAN IP      0.0.0.0         26016 27019 

When client attaches from WWW update their IP and PORT to your external IP
you can get that at www.myip.com

When serving to WWW

IP = WAN_IP
PORT = 27016

When serving locally

IP = LAN_IP #192.168.0.2; 0.3 0.4 etc. your LAN IP
PORT = 8000 #8001, etc.
"""


# STANDARD PYTHON MODULES
import os
import sys
import time
import json
import tkinter as tk
from multiprocessing import Process
from subprocess import call, check_output
from wsgiref.simple_server import make_server as wsgi

# THIRD PARTY MODULES
from requests import get
import falcon

PORT = "8000"
ENDPOINT = "/server"
PATH = str(os.path.dirname(os.path.abspath(__file__))) + "/"
LAN = str(check_output(["hostname", "-I"]), "utf-8").split(" ")[0]
WAN = str(check_output(["curl", "ifconfig.me"]), "utf-8").split(" ")[0]


class ChatServer:
    """
    respond to server requests; on_get
    """

    def on_get(self, req, resp):
        """
        update the message to pong, add server_time and update the response body
        """
        print("\033c\n")
        # extract the incoming parameters to a dictionary
        data = dict(req.params)
        # update json json_ipc with the server's response
        chat = json_ipc()
        if data["msg"]:
            chat.append([str(time.time()), data["user"], data["msg"]])
        if data["msg"] == "/clear":
            chat = []
        json_chat = json.dumps(chat)
        json_ipc(text=json_chat)
        # build the response body with a jsonified data dictionary
        resp.body = json_chat


class MessageBox(tk.Frame):
    """
    live update scrolling text box
    """

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.text = tk.Text(self, bg="#272727", fg="white")
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.v_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.previous_data = []
        self.update_dialog()

    def update_dialog(self):
        """
        check the chat server for new data once per second
        """
        data = None
        try:
            data = get(url=URL, params={"msg": "", "user": ""}).json()[-10:]
        except Exception:
            pass
        if data == []:
            self.text.delete("1.0", "end")
        if data and self.previous_data != data:
            new_items = [i for i in data if i not in self.previous_data]
            self.previous_data = data
            for item in new_items:
                msg = item[2]
                if ("\n" in msg) or len(msg) > 60:
                    msg = "\n\n" + msg + "\n"
                self.text.insert(
                    "end",
                    str(time.ctime(int(float(item[0]))))[11:19]  # time
                    + " "
                    + item[1].ljust(16)  # user
                    + " "
                    + msg  # msg
                    + "\n",
                )
            self.text.see("end")
        self.after(1000, self.update_dialog)


def on_enter(_):
    """
    when the user presses <Enter> send user input to the chat server
    """
    entry = input_box.get()
    if entry == "/quit":
        sys.exit()
    if entry == "/help":
        entry = "options: /quit /clear"
    if entry:
        input_box.delete(first=0, last=100000)
        print(URL, entry, user)
        get(url=URL, params={"msg": entry, "user": user}).json()


def server_process():
    """
    create a falcon api and add endpoints
    """

    create_database()
    app = falcon.App()
    app.add_route(ENDPOINT, ChatServer())
    print("\033c\n")
    with wsgi("", int(PORT), app) as httpd:
        httpd.serve_forever()


def json_ipc(text=""):
    """
    Concurrent Interprocess Communication via Read and Write JSON File Operation
    """
    doc = PATH + "pipe/" + "database.json"
    i = 0
    while True:
        try:
            time.sleep(0.05 * i ** 2)
            i += 1
            if text:
                # write to file operation
                try:
                    # ensure it is legit json
                    text = json.dumps(json.loads(str(text)))
                except Exception as error:
                    msg = str(type(error).__name__) + str(error.args)
                    break
                with open(doc, "w+") as handle:
                    handle.write(text)
                    handle.close()
                    break
            else:
                # read from file operation
                with open(doc, "r") as handle:
                    data = json.loads(handle.read())
                    handle.close()
                    return data
        except Exception as error:
            msg = str(type(error).__name__) + str(error.args)
            msg += " json_ipc race condition"
            print(msg)
            continue
        finally:
            try:
                handle.close()
            except Exception:
                pass


def create_database(data="[]"):
    """
    initialize an empty text pipe IPC json_ipc
    """
    os.makedirs(PATH + "pipe", exist_ok=True)
    json_ipc(text=data)


if __name__ == "__main__":


    print("\033c")
    print(
        f"""
            LAN ADDRESS {LAN}
            WAN ADDRESS {WAN}
        """
    )

    print(
        """
            1: LAN server
            2: LAN client
            3: WAN server
            4: WAN client
        """
    )
    selection = int(input("Enter choice number: \n"))
    if selection == 1:
        ip = LAN
    elif selection == 2:
        ip = "192.168.0." + input("Which x in format 192.168.0.x is the host?\n\n")
    elif selection == 3:
        ip = WAN
    elif selection == 4:
        ip = input("Enter WAN HOST IP in format x.x.x.x\n\n")
    URL = "http://" + ip + ":" + PORT + ENDPOINT  
    # update the terminal title bar
    title = "Nescient Chat at " + str(ip).strip() + " on port " + str(PORT)
    sys.stdout.write("\x1b]2;" + title + "\x07")
    # initial username input
    user = input("\033cInput user name: ")
    print("\033c")
    # spawn the server process
    if selection in [1, 3]:
        main_process = Process(target=server_process)
        main_process.start()
    # create the tkinter gui
    root = tk.Tk()
    root.config(bg="#272727")
    root.title(title)
    w, h = int(root.winfo_screenwidth() / 4), int(root.winfo_screenheight() / 2)
    root.geometry(f"{w}x{h}")
    # attach qwerty and numeric keypad <ENTER> button to on_enter definition
    root.bind("<Return>", on_enter)
    root.bind("<KP_Enter>", on_enter)
    # add scrolling dialog and message input
    dialog = MessageBox(root)
    dialog.pack(fill="both", expand=True)
    input_box = tk.Entry(root, bd=5, fg="white", bg="#272727")
    input_box.pack(fill="both", expand=False)
    # begin the tkinter event
    root.mainloop()

