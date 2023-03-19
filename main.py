import argparse
from agent import *


class GO:
    def __init__(self, players_color, difficulty):
        self.players_color = players_color
        if self.players_color == 1:
            self.agents_color = 2
        elif self.players_color == 2:
            self.agents_color = 1
        self.difficulty = difficulty
        self.total_moves = 0
        self.previous_game_board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        self.current_game_board = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]

    def agent_move(self):
        next_x, next_y = next_optimal_move(previous_game_board=self.previous_game_board,
                                           current_game_board=self.current_game_board,
                                           players_color=self.players_color,
                                           agents_color=self.agents_color,
                                           depth=self.difficulty,
                                           total_moves=self.total_moves)

        self.current_game_board[next_x][next_y] = self.agents_color
        self.total_moves += 1

    def player_move(self):
        print('It is your turn')

        x = input('Please enter the row from the options - 0,1,2,3,4: ')
        y = input('Please enter the column from the options - 0,1,2,3,4: ')

        if x not in ('0', '1', '2', '3', '4') or y not in ('0', '1', '2', '3', '4'):
            print('Please enter valid row and column values!!!')
            return False
        else:
            x = int(x)
            y = int(y)
            self.current_game_board[x][y] = self.players_color
            # check if this is a valid move

            self.total_moves += 1
            return True


    def calculate_winner(self):
        pass


if __name__ == '__main__':

    print('===================================')
    print('Welcome to GO game')

    # Ask the user to select a stone color and difficulty. Then initialize the game.
    while True:
        try:
            chosen_color = int(input('Please enter a stone color. Enter 1 for black and 2 for white: '))
            if chosen_color == 1 or chosen_color == 2:
                break
            else:
                raise Exception
        except Exception as e:
            print('Please enter either 1 or 2!!!')
    chosen_difficulty = 1
    new_GO_game = GO(players_color=chosen_color, difficulty=chosen_difficulty)

    if new_GO_game.players_color == 1:
        turn = 'player'
    elif new_GO_game.players_color == 2:
        turn = 'agent'

    # Show the initial board state
    print('Current game board -->')
    for row in new_GO_game.current_game_board:
        print(row)
    print()

    # Run the game till we hit the maximum number of possible moves which is 24.
    while new_GO_game.total_moves <= 24:

        if turn == 'agent':
            print('Agent is making a move...')
            new_GO_game.agent_move()

            # pass the turn
            turn = 'player'

        elif turn == 'player':
            while True:
                valid_move = new_GO_game.player_move()
                if valid_move is True:
                    break

            # pass the turn
            turn = 'agent'

        # print the board state after making a move
        print('Current game board -->')
        for row in new_GO_game.current_game_board:
            print(row)
        print()



