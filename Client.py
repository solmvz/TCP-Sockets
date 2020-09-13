import tkinter as tk
import threading
import socket
import pygame

class CLIENT:

    def __init__(self):
        self.HOST_ADDR = "127.0.0.1"
        self.HOST_PORT = 1234
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_name = ''
        self.board_size = 0
        self.score = 0
        self.opon_score = 0

    def join_server(self):
        self.client_name = str(ent_name.get())

        c_name = "username" + self.client_name

        self.client_socket.connect((self.HOST_ADDR, self.HOST_PORT))
        self.client_socket.send((bytes(c_name, "utf-8")))

        btn_connect.config(state=tk.DISABLED)
        btn_leave.config(state=tk.NORMAL)

        threading._start_new_thread(self.recieve_message_from_server, ())
    def exit_server(self):
        exit_msg = "exit" + str(self.client_name)
        self.client_socket.send(exit_msg.encode())
        window.destroy()

    def recieve_message_from_server(self):
        while True:
            server_msg = self.client_socket.recv(1024)
            server_msg = server_msg.decode("utf-8")
            if not server_msg:
                break
            else:
                if server_msg.startswith("Welcome"):
                    # OK
                    print(server_msg)
                elif server_msg.startswith("Oh"):
                    print(server_msg)
                    btn_connect.config(state=tk.DISABLED)
                    btn_leave.config(state=tk.DISABLED)
                    window.destroy()
                elif server_msg.startswith("is_online"):
                    print("Online Users: ", end='')
                    msg = server_msg.split("is_online")
                    msg.pop(0)
                    print(msg)
                    btn_request.config(state=tk.NORMAL)
                elif server_msg.startswith("exit_user"):
                    server_msg = server_msg.replace('exit_user', '')
                    print("User (", server_msg, ") Left!")
                elif server_msg.startswith("offer_from"):
                    # OK
                    self.recieve_offer_from_other_client(server_msg)
                elif server_msg.startswith("offer_acceptance_from"):
                    user_name = server_msg.replace('offer_acceptance_from', '')
                    self.run_game(self.client_name, 1, user_name, True, self.board_size)
                elif server_msg.startswith("offer_declined_from"):
                    user_name = server_msg.replace('offer_declined_from', '')
                    print(user_name, "Declined Your Game Request")

    def send_game_request(self):
        oponent_name = ent_opname.get()
        self.board_size = int(ent_size.get())
        msg = 'game_req' + str(oponent_name) + '#' + str(self.board_size)
        self.client_socket.send(msg.encode())
    def recieve_offer_from_other_client(self, msg):
        msg = msg.replace('offer_from', '')
        msg = msg.split("#")
        user_name = msg[0]
        dimension = int(msg[1])
        print("User", user_name, "Has Invited You to Play Tic-Tac-Toe!")
        answer = str(input("Do You Accept? yes/no: "))
        if answer == 'yes':
            massage = "accepted_offer" + str(user_name)
            self.client_socket.send(bytes(massage, "utf-8"))
            self.run_game(self.client_name, 2, user_name, False, dimension)
        else:
            massage = "declined_offer" + str(user_name)
            self.client_socket.send(bytes(massage, "utf-8"))
        return

    def send_coordinates(self, row, col, oponent_name):
        msg = 'coor' + str(row) + '#' + str(col) + '#' + str(oponent_name)
        self.client_socket.send(msg.encode())
    def recv_coor_from(self, msg):
        msg = msg.replace('coorfrom', '')
        msg = msg.split('#')
        row = int(msg[0])
        col = int(msg[1])
        return row, col

    def send_time_out(self, oponent_name):
        msg = 'timeout' + str(oponent_name)
        self.client_socket.send(msg.encode())
    def send_result(self, oponent_name):
        game_result = ''
        if self.score == self.opon_score:
            game_result = 'resultdraw#' + str(self.client_name) + '#' + str(oponent_name)
        elif self.score > self.opon_score:  # first name is the winner
            game_result = 'result' + str(self.client_name) + '#' + str(oponent_name)
        elif self.opon_score > self.score:
            game_result = 'result' + str(oponent_name) + '#' + str(self.client_name)
        self.client_socket.send(game_result.encode())
        return

    def check_scores(self, board, player, score=0):
        global win
        for x in range(len(board)):
            win = True
            for y in range(len(board)):
                if board[x][y] != player:
                    win = False
                    continue
            if win:
                score += 1
        for x in range(len(board)):
            win = True
            for y in range(len(board)):
                if board[y][x] != player:
                    win = False
                    continue
            if win:
                score += 1

        win = True
        y = 0
        for x in range(len(board)):
            if board[x][x] != player:
                win = False
        if win:
            score += 1
        win = True
        if win:
            for x in range(len(board)):
                y = len(board) - 1 - x
                if board[x][y] != player:
                    win = False
        if win:
            score += 1

        return score
    def run_game(self, c_name, playernum, oponent_name, yourTurn, dim):
        print("You are Player Number", playernum)
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)

        pygame.init()

        n = int(dim)
        CELL_SIZE = 60

        HEIGHT = CELL_SIZE
        WIDTH = CELL_SIZE
        MARGIN = 5
        grid = []
        for row in range(n):
            grid.append([])
            for column in range(n):
                grid[row].append(0)

        w_size = n * CELL_SIZE + (n + 1) * MARGIN
        WINDOW_SIZE = [w_size, w_size + 128]
        screen = pygame.display.set_mode(WINDOW_SIZE)
        if playernum == 1:
            pygame.display.set_caption(str(c_name) + "'s Board! Color: Green")
        if playernum == 2:
            pygame.display.set_caption(str(c_name) + "'s Board! Color: Red")

        font = pygame.font.SysFont('arial', 30)
        clock = pygame.time.Clock()
        counter, text = 10, '10'.rjust(3)
        pygame.time.set_timer(pygame.USEREVENT, 1000)

        done = False

        while not done:
            ended = True
            for i in range(len(grid)):
                for j in range(len(grid)):
                    if grid[i][j] == 0:
                        ended = False
            if ended:
                self.send_result(oponent_name)
                done = True
            if yourTurn:
                clock = pygame.time.Clock()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                    if event.type == pygame.USEREVENT:
                        counter -= 1
                        if counter > 0:
                            text = str(counter).rjust(3)
                        else:
                            text = 'TIMEOUT!'
                            yourTurn = False
                            self.send_time_out(oponent_name)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        column = pos[0] // (WIDTH + MARGIN)
                        row = pos[1] // (HEIGHT + MARGIN)
                        # Set that location to one
                        if grid[row][column] == 0:
                            grid[row][column] = playernum
                            yourTurn = False
                            self.send_coordinates(row, column, oponent_name)
                            self.score = self.check_scores(grid, playernum)
                            self.update_turn_in_GUI(2)
                            self.update_score_in_GUI()
                            if self.score != 0:
                                self.send_result(oponent_name)
                                done = True

            else:
                pygame.event.set_blocked(pygame.MOUSEMOTION)
                self.update_turn_in_GUI(2)

            screen.fill(BLACK)

            txt = font.render(text, True, WHITE)
            text_rect = txt.get_rect(center=(w_size / 2, w_size + 128 / 2))
            screen.blit(txt, text_rect)

            for row in range(n):
                for column in range(n):
                    color = WHITE
                    if grid[row][column] == 1:
                        color = GREEN
                    if grid[row][column] == 2:
                        color = RED
                    pygame.draw.rect(screen, color, [(MARGIN + WIDTH) * column + MARGIN,
                                                     (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])

            pygame.display.flip()
            if not yourTurn:
                server_msg = self.client_socket.recv(1024)
                server_msg = server_msg.decode("utf-8")
                if server_msg.startswith('result'):
                    yourTurn = False
                    done = True
                    break
                elif server_msg.startswith('timeout'):
                    yourTurn = True
                    pygame.event.set_allowed(pygame.MOUSEMOTION)
                    counter, text = 10, '10'.rjust(3)
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                elif server_msg.startswith("coorfrom"):
                    row, col = self.recv_coor_from(server_msg)
                    if playernum == 1:
                        grid[row][col] = 2
                        self.opon_score = self.check_scores(grid, 2)
                    if playernum == 2:
                        grid[row][col] = 1
                        self.opon_score = self.check_scores(grid, 1)

                    yourTurn = True
                    pygame.event.set_allowed(pygame.MOUSEMOTION)
                    counter, text = 10, '10'.rjust(3)
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                    self.update_turn_in_GUI(1)

    def update_turn_in_GUI(self, temp):
        if temp == 1:
            label_turn.configure(text="Your Turn    -")
        else:
            label_turn.configure(text="Oponent's Turn    -")
    def update_score_in_GUI(self):
        label_score.configure(text="  Your Score = " + str(self.score))


def main():
    game_client = CLIENT()

    global window
    window = tk.Tk()
    window.title("Client")

    g1 = 630
    g2 = 40

    screen_position = '+' + str(g1) + '+' + str(g2)
    window.geometry(screen_position)

    # first frame cosisting of a button to connect to sever
    global ent_name, ent_opname, ent_size, btn_connect, btn_leave, btn_request, label_turn, label_score
    firstFrame = tk.Frame(window)
    label_name = tk.Label(firstFrame, text="Name:")
    label_name.pack(side=tk.LEFT)
    ent_name = tk.Entry(firstFrame)
    ent_name.pack(side=tk.LEFT)
    btn_connect = tk.Button(firstFrame, text="Join", command=lambda: game_client.join_server())
    btn_connect.pack(side=tk.LEFT)
    btn_leave = tk.Button(firstFrame, text="Leave", command=lambda: game_client.exit_server(), state=tk.DISABLED)
    btn_leave.pack(side=tk.LEFT)
    firstFrame.pack(side=tk.TOP)

    secondFrame = tk.Frame(window)
    label_opname = tk.Label(secondFrame, text="Oponent Name:")
    label_opname.pack(side=tk.LEFT)
    ent_opname = tk.Entry(secondFrame)
    ent_opname.pack(side=tk.LEFT)
    label_size = tk.Label(secondFrame, text="Board Size:")
    label_size.pack(side=tk.LEFT)
    ent_size = tk.Entry(secondFrame)
    ent_size.pack(side=tk.LEFT)
    btn_request = tk.Button(secondFrame, text="Send Request", command=lambda: game_client.send_game_request(), state=tk.DISABLED)
    btn_request.pack(side=tk.LEFT)
    secondFrame.pack(side=tk.TOP)

    thirdFrame = tk.Frame(window)
    label_turn = tk.Label(thirdFrame, text="Turn    -")
    label_turn.pack(side=tk.LEFT)
    label_score = tk.Label(thirdFrame, text="  Your Score = 0")
    label_score.pack(side=tk.LEFT)
    thirdFrame.pack(side=tk.TOP)

    window.mainloop()

main()
