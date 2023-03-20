import copy
import math


def get_neighbors(x, y):
    """
    Return a list of all valid neighbors of a given stone.
    Neighbors are in the 4 directions top, down, left, right.
    Valid neighbors are within the boundary of the game board.
    """
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    neighbors = []
    for d in directions:
        neighbor = tuple(map(lambda a, b: a + b, d, (x, y)))

        r, c = neighbor
        if 0 <= r < 5 and 0 <= c < 5:
            neighbors.append(neighbor)

    return neighbors


def get_group(x, y, current_game_board, stone_color):
    """
    Given a stone, form a group.
    Return a list of all stones in that group. Use DFS.
    """
    group = []
    stack = [(x, y)]
    visited = set()
    visited.add((x, y))
    while stack:
        stone = stack.pop()
        group.append(stone)

        for neighbor in get_neighbors(x=stone[0], y=stone[1]):
            if neighbor not in visited and current_game_board[neighbor[0]][neighbor[1]] == stone_color:
                stack.append(neighbor)
                visited.add(neighbor)
    return group


def get_liberties(x, y, current_game_board, stone_color):
    """
    Get the liberties for a stone or a group of stones given a single input stone.
    First find the group and then get all liberties which are positions which are 0 (empty)
    """

    liberties = set()

    group = get_group(x=x, y=y, current_game_board=current_game_board, stone_color=stone_color)

    visited_neighbors = set()

    for stone in group:
        neighbors_of_curr_stone = get_neighbors(x=stone[0], y=stone[1])

        for neighbor in neighbors_of_curr_stone:
            if neighbor not in visited_neighbors:
                visited_neighbors.add(neighbor)

            if current_game_board[neighbor[0]][neighbor[1]] == 0:
                liberties.add(neighbor)

    return liberties


def find_dead_stones(board, stone_color):
    """
    Check for dead stones. Go through all points on the board.
    If a position is occupied by the agent's stone, then get the group.
    Find its liberties, if there are none, then this group is dead.
    """
    dead_stones = set()

    for i in range(5):
        for j in range(5):
            if board[i][j] == stone_color:
                group = get_group(x=i, y=j, current_game_board=board, stone_color=stone_color)
                liberties = get_liberties(x=i, y=j, current_game_board=board, stone_color=stone_color)

                if len(liberties) == 0:
                    for stone in group:
                        dead_stones.add(stone)

    return dead_stones


def try_a_move(next_move_x, next_move_y, board, players_color, agents_color):
    """
    Agent plays a valid move on a given game board and gets the output board.
    Get the number of dead stones of the player and the agent itself by making this move.
    """

    # create a copy of the board and play the next move by setting that position to the agent's color
    tmp_board = copy.deepcopy(board)
    tmp_board[next_move_x][next_move_y] = agents_color

    # after making this move, find and remove any stones of the player which were captured
    players_dead_stones = find_dead_stones(board=tmp_board, stone_color=players_color)
    for dead_stone in players_dead_stones:
        tmp_board[dead_stone[0]][dead_stone[1]] = 0

    # after making this move, find and remove any stones of the agent which were captured
    agents_dead_stones = find_dead_stones(board=tmp_board, stone_color=agents_color)
    for dead_stone in agents_dead_stones:
        tmp_board[dead_stone[0]][dead_stone[1]] = 0

    # this will lead to a higher heuristic value
    num_players_stones_removed = len(players_dead_stones)
    # this will lead to a lower heuristic value
    num_agents_stones_removed = len(agents_dead_stones)

    return tmp_board, num_players_stones_removed, num_agents_stones_removed


def get_valid_moves(players_color, agents_color, previous_game_board, current_game_board):
    """
    Get all the valid moves the agent can play.
    - First get all the positions where the agent can play, i.e. all positions on the board which are 0.
    - For each possible move we will get the output board. All possibles moves are not valid.
    - Get the partial utility for each move, which is the number of players stones removed - agents own stones removed.
    - If the output board is the same as current board, then this is an invalid 'suicide' move.
    - If the output board is the same as previous board, then this means we are violating the 'ko' rule.
    - Anything else is a valid move. Sort the valid moves with the highest partial utility.
    """

    possible_moves = set()
    for i in range(5):
        for j in range(5):
            if current_game_board[i][j] != 0:
                liberties_of_curr_position = get_liberties(x=i,
                                                           y=j,
                                                           current_game_board=current_game_board,
                                                           stone_color=agents_color)
                possible_moves = possible_moves.union(liberties_of_curr_position)

    valid_moves_with_partial_utility = []
    for move in possible_moves:
        output_board, num_players_stones_removed, num_agents_stones_removed = try_a_move(next_move_x=move[0],
                                                                                         next_move_y=move[1],
                                                                                         board=current_game_board,
                                                                                         players_color=players_color,
                                                                                         agents_color=agents_color)

        partial_utility = num_players_stones_removed - num_agents_stones_removed

        # check for suicide and ko
        if output_board != current_game_board and output_board != previous_game_board:
            valid_moves_with_partial_utility.append((move, partial_utility))

    # sort valid moves with the highest partial utility value
    valid_moves_with_partial_utility.sort(key=lambda x: x[1], reverse=True)

    valid_moves = []
    for move, partial_utility in valid_moves_with_partial_utility:
        valid_moves.append(move)

    if len(valid_moves) == 0:
        return None

    return valid_moves


def get_heuristic_value(board, agents_color):
    """
    Get the heuristic value of a give game board state.
    Find the number of black stones and white stones currently on the board.
    Find the number of black stones in danger and number of white stones in danger.
    A stone is in danger if it has only 1 liberty left.
    If the agent is black then number of black stones and white stones in danger will increase the value.
    And the number of white stones and black stones in danger will decrease the value.
    Vice versa for if the agent is white.
    """

    black_stones = 0
    white_stones = 0
    black_stones_in_danger = 0
    white_stones_in_danger = 0

    # go through the board and count number of black and white stones and also stones in danger.
    for i in range(5):
        for j in range(5):
            if board[i][j] == 1:
                black_stones += 1

                # determine if this stone is danger or not.
                num_liberties = len(get_liberties(x=i, y=j, current_game_board=board, stone_color=1))
                if num_liberties <= 1:
                    black_stones_in_danger += 1

            elif board[i][j] == 2:
                white_stones += 1

                # determine if this stone is danger or not.
                num_liberties = len(get_liberties(x=i, y=j, current_game_board=board, stone_color=2))
                if num_liberties <= 1:
                    white_stones_in_danger += 1

    # give white a handicap
    white_stones += 6

    # if the agent is black
    if agents_color == 1:
        heuristic_value = 10*black_stones - 10*white_stones + 2*white_stones_in_danger - 1.5*black_stones_in_danger
    elif agents_color == 2:
        heuristic_value = 10*white_stones - 10*black_stones + 2*black_stones_in_danger - 1.5*white_stones_in_danger

    return heuristic_value


def MAX(previous_game_board, current_game_board, agents_color, opponents_color, depth, total_moves, alpha, beta):
    if depth == 0 or total_moves > 24:
        heuristic_value = get_heuristic_value(board=current_game_board, agents_color=agents_color)
        max_value_action = []
        return heuristic_value, max_value_action

    valid_next_moves = get_valid_moves(players_color=opponents_color,
                                       agents_color=agents_color,
                                       previous_game_board=previous_game_board,
                                       current_game_board=current_game_board)

    maxv = -math.inf
    maxv_action = []

    for next_move in valid_next_moves:

        tmp_board = copy.deepcopy(current_game_board)

        output_board, num_players_stones_removed, num_agents_stones_removed = try_a_move(next_move_x=next_move[0],
                                                                                         next_move_y=next_move[1],
                                                                                         board=tmp_board,
                                                                                         players_color=opponents_color,
                                                                                         agents_color=agents_color)

        heuristic_value, next_moves = MIN(previous_game_board=current_game_board,
                                          current_game_board=output_board,
                                          agents_color=opponents_color,
                                          opponents_color=agents_color,
                                          depth=depth-1,
                                          total_moves=total_moves+1,
                                          alpha=alpha,
                                          beta=beta)

        heuristic_value = heuristic_value + num_players_stones_removed*5 - num_agents_stones_removed*8.5

        if heuristic_value > maxv:
            maxv = heuristic_value
            maxv_action = [next_move] + next_moves

        if maxv >= beta:
            return maxv, maxv_action

        if maxv > alpha:
            alpha = maxv

    return maxv, maxv_action


def MIN(previous_game_board, current_game_board, agents_color, opponents_color, depth, total_moves, alpha, beta):
    if depth == 0 or total_moves > 24:
        heuristic_value = get_heuristic_value(board=current_game_board, agents_color=agents_color)
        max_value_action = []
        return heuristic_value, max_value_action

    valid_next_moves = get_valid_moves(players_color=opponents_color,
                                       agents_color=agents_color,
                                       previous_game_board=previous_game_board,
                                       current_game_board=current_game_board)

    minv = math.inf
    minv_action = []

    for next_move in valid_next_moves:
        tmp_board = copy.deepcopy(current_game_board)

        output_board, num_players_stones_removed, num_agents_stones_removed = try_a_move(next_move_x=next_move[0],
                                                                                         next_move_y=next_move[1],
                                                                                         board=tmp_board,
                                                                                         players_color=opponents_color,
                                                                                         agents_color=agents_color)

        heuristic_value, next_moves = MAX(previous_game_board=current_game_board,
                                          current_game_board=output_board,
                                          agents_color=opponents_color,
                                          opponents_color=agents_color,
                                          depth=depth-1,
                                          total_moves=total_moves+1,
                                          alpha=alpha,
                                          beta=beta)

        heuristic_value = heuristic_value + num_players_stones_removed*5 - num_agents_stones_removed*8.5

        if heuristic_value < minv:
            minv = heuristic_value
            minv_action = [next_move] + next_moves

        if minv <= alpha:
            return minv, minv_action

        if minv < beta:
            beta = minv

    return minv, minv_action


def next_optimal_move(previous_game_board, current_game_board, players_color, agents_color, depth, total_moves):
    """
    If total_moves is 0, and this is the agent's turn, then the agent is black. Start the game at (2,2)
    If total_moves is 1, and this is the agent's turn, then the agent is white. Start the game at (2,2) if free or (2,1)
    If total_moves > 1 then run minimax with alpha beta pruning
    """
    if total_moves == 0:
        return 2, 2

    if total_moves == 1:
        if current_game_board[2][2] == 0:
            return 2, 2
        else:
            return 2, 1

    # run minimax with alpha beta pruning
    # initialize alpha and beta
    alpha = float(-math.inf)
    beta = float(math.inf)

    _, next_moves = MAX(previous_game_board=previous_game_board,
                        current_game_board=current_game_board,
                        agents_color=agents_color,
                        opponents_color=players_color,
                        depth=depth,
                        total_moves=total_moves,
                        alpha=alpha,
                        beta=beta)

    print(next_moves)
    return next_moves[0]
