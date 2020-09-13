import tkinter as tk
import threading
import socket

class SERVER:

    def __init__(self):
        self.HOST_ADDR = "127.0.0.1"
        self.HOST_PORT = 1234
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.dimension = 0

    def start_server(self):
        self.server_socket.bind((self.HOST_ADDR, self.HOST_PORT))
        self.server_socket.listen(4)

        threading._start_new_thread(self.accept_clients, ())

        # now some changes in GUI
        start.config(state=tk.DISABLED)
        stop.config(state=tk.NORMAL)
        host["text"] = "Address: " + self.HOST_ADDR
        port["text"] = "Port: " + str(self.HOST_PORT)
    def stop_server(self):
        if len(self.clients) != 0:
            for i in self.clients:
                i[0].send((bytes("Oh Oh! Server Stopped!", "utf-8")))
                window.destroy()
        else:
            window.destroy()

    def accept_clients(self):
        while True:
            client_connected, address = self.server_socket.accept()

            client_name = client_connected.recv(1024)
            if client_name.startswith(bytes("username", "utf-8")):
                client_name = client_name.decode("utf-8")
                client_name = client_name.replace('username', '')

            self.clients.append((client_connected, address, client_name))
            print("Client With Username (", client_name, ") and address", {address}, "Connected!")

            welcome = "Welcome to Server!"
            client_connected.send(welcome.encode())

            threading._start_new_thread(self.recieve_message_from_client, (client_connected, client_name))

            if len(self.clients) >= 2:
                threading._start_new_thread(self.show_online_users, ())
    def client_exit(self, c, c_name):
        print("Client (", c_name, ") Left!")
        for i in self.clients:
            if i[0] == c:
                self.clients.remove(i)
        if len(self.clients) != 0:
            for j in self.clients:
                msg = "exit_user" + str(c_name)
                j[0].send((bytes(msg, "utf-8")))
            self.show_online_users()
    def show_online_users(self):
        msg = 'is_online'
        for i in self.clients:  # showing other online players to current user
            for j in self.clients:
                if i[2] != j[2]:
                    msg += str(j[2]) + " "
            i[0].send(bytes(msg, "utf-8"))
            msg = 'is_online'
        return

    def recieve_message_from_client(self, c, c_name):
        while True:
            message = c.recv(4096)
            message = message.decode("utf-8")
            print("message received from", c_name, ": ", message)
            if message.startswith("exit"):  # client wants to exit
                # OK
                self.client_exit(c, c_name)
                return
            if message.startswith("game_req"):
                # OK
                self.recieve_game_request(c, c_name, message)
            if message.startswith("accepted_offer"):
                # OK
                self.game_offer_accepted(c, c_name, message)
            if message.startswith("declined_offer"):
                # OK
                self.game_offer_declined(c, c_name, message)
            if message.startswith("coor"):
                # OK
                self.forward_coor(c, c_name, message)
            if message.startswith("timeout"):
                # OK
                self.time_out(c, c_name, message)
            if message.startswith("result"):
                # OK
                self.game_result(message)

    def recieve_game_request(self, c, c_name, msg):
        msg = msg.replace('game_req', '')
        msg = msg.split('#')
        user_name = msg[0]
        self.dimension = int(msg[1])
        for i in self.clients:
            if i[2] == user_name:  # i[2] is the destination user
                message = 'offer_from' + str(c_name) + '#' + str(self.dimension)
                i[0].send((bytes(message, "utf-8")))
        return

    def game_offer_accepted(self, c, c_name, msg):
        user_name = msg.replace('accepted_offer', '')
        for i in self.clients:
            if i[2] == user_name:
                message = "offer_acceptance_from" + str(c_name)
                i[0].send((bytes(message, "utf-8")))
        return
    def game_offer_declined(self, c, c_name, msg):
        user_name = msg.replace('declined_offer', '')
        for i in self.clients:
            if i[2] == user_name:
                message = "offer_declined_from" + str(c_name)
                i[0].send((bytes(message, "utf-8")))
        return

    def forward_coor(self, c, c_name, msg):
        msg = msg.replace('coor', '')
        msg = msg.split('#')
        user_name = msg[2]
        for i in self.clients:
            if i[2] == user_name:
                message = 'coorfrom' + str(msg[0]) + '#' + str(msg[1]) + '#' + str(c_name)
                i[0].send((bytes(message, "utf-8")))
        return

    def time_out(self, c, c_name, msg):
        user_name = msg.replace('timeout', '')
        for i in self.clients:
            if i[2] == user_name:
                message = 'timeout' + str(c_name)
                i[0].send((bytes(message, "utf-8")))

    def game_result(self, msg):
        msg = msg.replace('result', '')
        msg = msg.split('#')

        if msg[0] == 'draw':
            result1 = tk.Tk()
            result1.title("Draw")
            user1 = msg[1]
            user2 = msg[2]
            for i in self.clients:
                if i[2] == user1:
                    message = 'resultdraw#'
                    i[0].send((bytes(message, "utf-8")))
                if i[2] == user2:
                    message = 'resultdraw#'
                    i[0].send((bytes(message, "utf-8")))
            firstFrame = tk.Frame(result1)
            label_draw = tk.Label(firstFrame, text="No one Won! The Game is a Draw!")
            label_draw.pack(side=tk.LEFT)
            firstFrame.pack(side=tk.TOP, pady=(5, 0))
            result1.mainloop()

        else:
            result2 = tk.Tk()
            result2.title("Win & Lose")

            winner = msg[0]
            loser = msg[1]

            for i in self.clients:
                if i[2] == winner:
                    message = 'resultwin#'
                    i[0].send((bytes(message, "utf-8")))
                if i[2] == loser:
                    message = 'resultlose#'
                    i[0].send((bytes(message, "utf-8")))

            firstFrame = tk.Frame(result2)
            label_c_name = tk.Label(firstFrame, text=winner)
            label_c_name.pack(side=tk.LEFT)
            label_c_result = tk.Label(firstFrame, text="Won!")
            label_c_result.pack(side=tk.LEFT)
            firstFrame.pack(side=tk.TOP, pady=(5, 0))

            secondFrame = tk.Frame(result2)
            label_o_name = tk.Label(secondFrame, text=loser)
            label_o_name.pack(side=tk.LEFT)
            label_o_result = tk.Label(secondFrame, text="Lost!")
            label_o_result.pack(side=tk.LEFT)
            secondFrame.pack(side=tk.TOP, pady=(5, 0))
            result2.mainloop()

def main():
    game_server = SERVER()

    global window
    window = tk.Tk()
    window.title("Server")

    screen_position = '+' + str(330) + '+' + str(40)
    window.geometry(screen_position)

    # first frame consisting of two buttons widgets
    global start, stop
    firstFrame = tk.Frame(window)
    start = tk.Button(firstFrame, text="Start", command=lambda: game_server.start_server())
    start.pack(side=tk.LEFT)
    stop = tk.Button(firstFrame, text="Stop", command=lambda: game_server.stop_server(), state=tk.DISABLED)
    stop.pack(side=tk.LEFT)
    firstFrame.pack(side=tk.TOP, pady=(5, 0))

    # second frame consisting of two labels for displaying the host address and port info
    global host, port
    secondFrame = tk.Frame(window)
    host = tk.Label(secondFrame, text="Address: X.X.X.X")
    host.pack(side=tk.LEFT)
    port = tk.Label(secondFrame, text="Port:XXXX")
    port.pack(side=tk.LEFT)
    secondFrame.pack(side=tk.TOP, pady=(5, 0))

    window.mainloop()

main()
