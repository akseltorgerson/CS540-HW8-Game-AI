import random
import copy

class Teeko2Player:
    """ An object representation for an AI game player for the game Teeko2.
    """
    board = [[' ' for j in range(5)] for i in range(5)]
    pieces = ['b', 'r']
    placed = 0

    def __init__(self):
        """ Initializes a Teeko2Player object by randomly selecting red or black as its
        piece color.
        """
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def succ(self, state, drop_phase, piece):
        succs = []
        # drop phase means a piece can be placed at any open spot on the board
        if drop_phase:
            for row in range(len(state)):
                for col in range(len(state[row])):
                    if state[row][col] == ' ':
                        stateCopy = copy.deepcopy(state)
                        stateCopy[row][col] = piece
                        succs.append(stateCopy)
        # if not the drop phase      
        else:
            for row in range(len(state)):
                for col in range(len(state[row])):
                    if (state[row][col] == piece):
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                # long conditional, but we just check the spaces around the piece and see if they are not out of bounds and a free space
                                if (row+i >= 0 and row+i < len(state) and col+j >= 0 and col+j < len(state[row]) and state[row+i][col+j] == ' '):
                                    stateCopy = copy.deepcopy(state)
                                    stateCopy[row][col] = ' '
                                    stateCopy[row+i][col+j] = piece
                                    succs.append(stateCopy)
        # return the list
        return succs

    def make_move(self, state):
        """ 
        Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this Teeko2Player object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """
        drop_phase = True
        move = []
        best_state = []
        best_value = -1
        solvable = False

        if self.placed >= 4:
            drop_phase = False
        else:
            self.placed += 1

        # Random spot for the AI to start with
        if self.placed == 1:
            row = random.randint(0, 4)
            col = random.randint(0, 4)
            move.insert(0, (row, col))
            return move
        
        # Check for a solution
        for possible_state in self.succ(state, drop_phase, self.my_piece):
            if self.game_value(possible_state):
                best_state = possible_state
                solvable = True
                break

        # Check all states to find the best one
        if not solvable:
            for possible_state in self.succ(state, drop_phase, self.my_piece):
                possible_state_val = self.max_val(possible_state, 0, drop_phase)
                if possible_state_val > best_value:
                    best_value = possible_state_val
                    best_state = possible_state

        # Find the differences in state and best_state, and insert the moves accordingly
        for row in range(len(state)):
            for col in range(len(state[row])):
                if best_state[row][col] != state[row][col]:
                    if best_state[row][col] == self.my_piece:
                        move.insert(0, (row, col))
                    elif (not drop_phase) and state[row][col] == self.my_piece:
                        move.insert(1, (row, col))

        return move

    def heuristic_game_value(self, state, depth, piece):
        h = self.game_value(state)
        if (h == 0):
            loc = []
            # some numbers
            heur = [[1,1,1,1,1],
                    [1,2,2,2,1],
                    [1,2,3,2,1],
                    [1,2,2,2,1],
                    [1,1,1,1,1]]
            for row in range(len(state)):
                for col in range (len(state)):
                    if(state[row][col] == piece):
                        h += heur[row][col] / 20
        return h if piece == self.my_piece else -h

    def max_val(self, state, depth, drop_phase):
        # artificial negative infinity
        value = -999
        game_value = self.game_value(state)
        if game_value == 1:
            return 1
        elif game_value == -1:
            return -1
        elif depth >= 2:
            return self.heuristic_game_value(state, depth, self.my_piece)
        else:
            for possible_state in self.succ(state, drop_phase, self.my_piece):
                value = max(value, self.min_val(state, depth + 1, drop_phase))
        return value

    def min_val(self, state, depth, drop_phase):
        # artificial infinity
        value = 999
        game_value = self.game_value(state)
        if game_value == 1:
            return 1
        elif game_value == -1:
            return -1
        elif depth >= 2:
            return self.heuristic_game_value(state, depth, self.opp)
        else:
            for possible_state in self.succ(state, drop_phase, self.opp):
                value = min(value, self.max_val(state, depth + 1, drop_phase))
        return value

    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    def game_value(self, state):
        """ Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this Teeko2Player object, or a generated successor state.

        Returns:
            int: 1 if this Teeko2Player wins, -1 if the opponent wins, 0 if no winner
        """
        # check - horizontal wins
        for row in range(5):
            for col in range(2):
                if (state[row][col] != ' ') and (state[row][col] == state[row][col + 1] == state[row][col + 2] == state[row][col + 3]):
                    return 1 if state[row][col] == self.my_piece else -1

        # check | vertical wins
        for row in range(2):
            for col in range(5):
                if state[row][col] != ' ' and state[row][col] == state[row + 1][col] == state[row + 2][col] == state[row + 3][col]:
                    return 1 if state[row][col] == self.my_piece else -1

        # check \ diagonal wins
        for row in range(2):
            for col in range(2):
                if state[row][col] != ' ' and state[row][col] == state[row + 1][col + 1] == state[row + 2][col + 2] == state[row + 3][col + 3]:
                    return 1 if state[row][col] == self.my_piece else -1
        
        # check / diagonal wins
        for row in range(2):
            for col in range(2):
                if state[row][col + 3] != ' ' and state[row][col + 3] == state[row + 1][col + 2] == state[row + 2][col + 1] == state[row + 3][col]:
                    return 1 if state[row][col + 3] == self.my_piece else -1
        
        # check 3x3 square corners wins
        for row in range(3):
            for col in range(3):
                if state[row][col] != ' ' and state[row + 2][col] == state[row + 2][col + 2] == state[row][col + 2] == state[row][col]:
                    return 1 if state[row][col] == self.my_piece else -1

        return 0 # no winner yet

############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = Teeko2Player()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            #print(move)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()
