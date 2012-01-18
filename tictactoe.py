#!/usr/bin/python -tt
from random import shuffle

class Game:
    '''
    A Game is the primary component of this application. It is the facilitator of
    user and computer interactions, movements. A Game maintains a state which is
    one of STATE_IN_PROGRESS, STATE_DRAW, or STATE_COMPLETE. A Game maintains a 
    board (i.e. a list of playable squares). One should note that a Square is considered
    "not played" if it's placemark is None.
    '''
    STATE_IN_PROGRESS = 0
    STATE_COMPLETE = 1
    STATE_DRAW = 2

    def __init__(self,size):
        self.board = self.__make_board(size)
        self.state = Game.STATE_IN_PROGRESS
        self.size = size
        self.winner = None
        self.squares_played = 0

        # Setup players. By default, computer is first and is X
        self.computer = Player('X')
        self.player = Player('O')

    def __make_board(self,size):
        '''
        Creates a list of Squares for coordinates x,y within an nxn range. The result
        is a single list where the index of a particular x,y is (size * x) + 1
        '''
        board = []
        for i in range(size):
            for j in range(size):
                board.append(Square(i,j))
        return board

    def play(self, computer_first = True):
        '''Initiate the game'''
        if computer_first:
            self.computer.move(self,self.player)
        else:
            # Update the markers to be the other way around from the default
            self.computer.marker = 'O'
            self.player.marker = 'X'

    def complete(self, outcome, winner = None):
        '''Completes a game with the specified outcome and optional winner'''
        self.state = outcome
        self.winner = winner

    def is_corner(self, square):
        '''
        Checks to see if a square is a board corner or not. There are four corners to check
        for: (0,0), (0,size-1), (size-1,0), (size-1,size-1)
        '''
        x,y = square.x, square.y
        return ( (x == 0 and (y == 0 or y == self.size - 1)) or 
                 (y == 0 and (x == 0 or x == self.size - 1)) or 
                 (x == self.size - 1 and y == self.size - 1) )

    def is_edge(self, square):
        '''
        Checks to see if a square is a non-corner edge. In other words, a square is on the 
        edge if x is the first or last row and y is between (0,size) - OR - y is the first 
        or last column and x is between (0,size)
        '''
        x,y = square.x, square.y
        return ((x in [0,self.size-1] and y in range(1,self.size-1)) or 
                (y in [0,self.size-1] and x in range(1,self.size-1)))

    def is_any_edge(self, square):
        '''Checks to see if a square is along the edge of the board (corners and edges)'''
        return self.is_edge(square) or self.is_corner(square)

    def coordinate_key(self, x, y):
        '''Utility to transform an x,y into a 1D list offset'''
        return (self.size * x) + y

    def square(self,x,y=None):
        '''Returns the square at x,y or if y is not provided, treat x as a key'''
        if y == None:
            return self.board[x]
        else:
            return self.board[ self.coordinate_key(x,y) ]

    def occupy(self, x, y, marker):
        '''Marks a square at an x,y coordinate with a marker and sets it as having been played'''
        self.square(x,y).mark(marker)
        self.squares_played += 1

    def is_played(self, x, y):
        '''Shorthand for checking if an x,y coordinate has been played or not'''
        return self.square(x,y).marked()

    def squares_available(self):
        '''Squares are available if the squares_played counter < size^2'''
        return self.squares_played < pow(self.size,2)

    def __permute_and_choose_point(self,digit_range):
        '''Permutes a chooses a random available point (x,y) or (None,None)'''
        coords = [(x,y) for x in digit_range for y in digit_range]
        shuffle(coords)
        for coord in coords:
            x,y = coord
            if not self.is_played(x,y):
                return (x,y)
        return (None,None)

    def available_square(self):
        '''Gets any available square'''
        return self.__permute_and_choose_point(range(self.size))

    def available_corner(self):
        '''Picks an unplayed corner at random'''
        return self.__permute_and_choose_point([0,self.size-1])

    def available_edge(self):
        '''Picks an unplayed edge at random'''
        for square in self.board:
            if self.is_edge(square) and not self.is_played(square.x,square.y):
                return (square.x,square.y)
        return (None,None)

    def available_center(self):
        '''Picks an unplayed "center" or non-edge square available'''
        return self.__permute_and_choose_point(range(1,self.size-1))

    def print_board(self):
        rows = []
        glue = '\n   ' + ('+'.join(['---' for i in range(self.size)])) + '\n'
        header = '    ' + '   '.join([ str(x) for x in range(self.size) ]) + ' '

        for row_num in range(self.size):
            row = self.board[ self.coordinate_key(row_num,0) : self.coordinate_key(row_num,self.size) ]
            rows.append(' ' + str(row_num) + '  ' + (' | '.join([ str(cell) for cell in row])) + ' ')

        print '\n' + header + '\n' + glue.join(rows) + '\n'
        


class Square:
    '''
    A Square is a basic component of a Board. It maintains an x,y coordinate
    position and a placemarker which is by default empty.
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.placemark = None

    def __repr__(self):
        return "(%s,%s)" % (self.x,self.y)

    def __str__(self):
        return ' ' if self.placemark == None else self.placemark

    def __eq__(self,item):
        return isinstance(item,Square) and item.x == self.x and item.y == self.y

    def mark(self,marker):
        self.placemark = marker

    def marked(self):
        return self.placemark != None


class Path:
    '''
    A Path represents a collection of moves/squares that ultimately results in a win
    for the player that owns it. Paths are also direction-oriented as in this
    scenario, there are four distinct directions: horizontal, vertical, 
    diagonal and inverse diagonal. Paths also maintain a rank which is analagous to
    the number of moves need to complete the path
    '''
    HORIZONTAL = 0
    VERTICAL = 1
    DIAGONAL = 2
    DIAGONAL_INVERSE = 3

    def __init__(self, squares, direction):
        self.direction = direction
        self.squares = squares

    def rank(self):
        return len(self.squares)

    def __contains__(self, item):
        return item in self.squares

    def __getitem__(self, key):
        return self.squares[key]

    def remove(self, square):
        return self.squares.remove(square)

    def __repr__(self):
        return 'Path(%s): %s' % (self.rank(),str(self.squares))

    def line_slope_intersect(self):
        '''
        Gets the slope and y-intercept of this path-line if there are more than two points.
        Because paths are more visually represented rather than by an equation, horizontal
        lines are analagous to x = <val>, vertical to y = <val>, diagonal to y = x, and
        diagonal inverse to y = b - x
        '''
        if len(self.squares) > 1:
            pt = self.squares[0]

            if self.direction == Path.DIAGONAL:
                m = 1
            elif self.direction == Path.DIAGONAL_INVERSE:
                m = -1
            elif self.direction == Path.VERTICAL:
                m = 0
            else:
                m = None

            b = pt.y - (m * pt.x) if m != None else None

            return (m,b)
        else:
            return (None,None)

    def intersection(self, path):
        '''Gets the intersection of self and another path'''
        if self.direction != path.direction:
            if Path.HORIZONTAL in [self.direction,path.direction]:
                # This is a unique case in which one path will have an undefined slope
                m1,b1 = path.line_slope_intersect() if self.direction == Path.HORIZONTAL else self.line_slope_intersect()
                x = self.squares[0].x if self.direction == Path.HORIZONTAL else path.squares[0].x
                y = (m1 * x) + b1
                return (x,y)
            else:
                m0,b0 = self.line_slope_intersect()
                m1,b1 = path.line_slope_intersect()
                x = (b0 - b1) / (m1 - m0)
                y = (m0 * x) + b0
                return (x,y)
        else:
            # These paths are either parallel or equivalent
            return (None,None)
        

class Player:
    '''
    Should be self-explanatory. One should note that Player objects will also 
    maintain a collection of occupations (Squares) and their optimal paths 
    which are strategized at each move.
    '''
    def __init__(self,marker):
        self.marker = marker
        self.paths = []
        self.occupations = []

    def check_winning_move(self,square):
        '''
        Checks a square being played lies within a single move path we are keeping track
        of. In otherwords, we check only rank-1 paths, otherwise return false
        '''
        for path in self.paths:
            if path.rank() > 1:
                return False
            elif square in path:
                return True

    def move(self,game,opponent,x = None,y = None):
        '''
        Performs a move on a specified board for a specified game against a specified opponent.
        User moves are treated without any extra consideration. Computer moves, however, have more
        logic behind them.

        Special care is taken on each move the computer makes, especially the first move. Above
        all else, the computer prefers corner placement. If the computer moves second and the 
        human player has chosen a corner, the computer places a mark at an available "center"
        square within the line of sight of the human move. This should open an opportunity to 
        force the human player into a block instead of a split or two-way possible win.
        '''
        
        if x == None and y == None:
            # A Computer Move
            if not self.occupations:
                if self.marker == 'O' and game.is_any_edge(opponent.occupations[-1]):
                    # Choose a nearby "center" square from the opponent's first move
                    x,y = game.available_center()
                else:
                    # Prefer a corner on the first move
                    x,y = game.available_corner()

                game.occupy(x,y,self.marker)
                self.occupations.append( game.square(x,y) )
                self.strategize(game,opponent,x,y)
            elif self.paths or opponent.paths:
                winning_move = False
                next_move = None

                # Set these variables as we may or may not need them in the move strategy
                try:
                    o_first = opponent.occupations[-2]
                except:
                    o_first = opponent.occupations[0]
                o_last = opponent.occupations[-1]

                '''
                In summary, the move procedure for a computer player is the following:
                    1) Is a computer win available? WIN
                    2) Is a player one move from a win? BLOCK
                    3) Is this our second move as 'O' and has the player taken two corners?
                       Attempt to draw the player into playing defense
                    4) Use heuristics to determine an optimal move within computer paths and player paths
                    5) Choose an available move from either the computer paths or player paths
                '''
                if self.paths and self.paths[0].rank() == 1:
                    next_move = self.paths[0][0]
                    winning_move = True
                elif opponent.paths and opponent.paths[0].rank() == 1:
                    next_move = opponent.paths[0][0]
                    winning_move = self.check_winning_move(next_move)
                elif ( self.marker == 'O' and game.is_corner(o_first) and game.is_corner(o_last) and 
                        len(self.occupations) == 1 ):
                    x,y = game.available_edge()
                    next_move = game.square(x,y)
                elif self.paths and opponent.paths:
                    '''
                    If both the computer and human player have win-paths that are defined, apply some
                    heuristics to determine what would be the best choice for the computer. What we are 
                    really looking for here is if there is a move that is both in one of the computer's
                    win paths and the player's win paths. This would both advance the computer's strategy
                    and provide a block against the player. Moreover, for performance, we need only concern
                    ourselves with intersections between opposing paths. If two paths intersect, we increase
                    the "weight" of the intersection by a value inversely proportional to the minimum rank
                    of the two intersecting paths. This ensures that intersections in "better" paths will
                    ultimately result in a win or a block.
                    '''
                    weights = {}
                    for my_path in self.paths:
                        for opp_path in opponent.paths:
                            # Get the intersection point
                            x,y = my_path.intersection(opp_path)
                            if x != None and y != None and not game.is_played(x,y):
                                # Only evaluate "legal" moves, i.e. non-occupied squares
                                key = game.coordinate_key(x,y)
                                if not weights.has_key(key):
                                    weights[key] = 0.0
                                weights[key] += 1.0 / min(my_path.rank(),opp_path.rank())

                    if len(weights.values()) > 0:
                        # If intersection points were found, locate one with a maximum weight
                        # It's OK to break after we find one, we have already guaranteed that these are ALL legal moves
                        max_weight = max(weights.values())
                        for key,weight in weights.items():
                            if weight == max_weight:
                                next_move = game.square(key)
                                break

                    if next_move == None:
                        # If no move was found, use a backup of one of the computer's win-path moves
                        last_move = self.occupations[-1]
                        next_path = self.paths[0]
                        half = game.size / 2
                        preferred_choice = -1
            
                        if ( (next_path.direction in [Path.HORIZONTAL,Path.DIAGONAL_INVERSE] and last_move.y > half) or
                             (next_path.direction in [Path.VERTICAL,Path.DIAGONAL] and last_move.x > half) ):
                             preferred_choice = 0
                        next_move = next_path[preferred_choice]
                    winning_move = self.check_winning_move(next_move)
                else:
                    # If all else fails, choose either a move along our next win-path or choose one to block the opponent
                    # if there are not more suitable paths to follow
                    last_move = self.occupations[-1] if self.paths else o_last
                    next_path = self.paths[0] if self.paths else opponent.paths[0]
                    half = game.size / 2
                    preferred_choice = -1
            
                    if ( (next_path.direction in [Path.HORIZONTAL,Path.DIAGONAL_INVERSE] and last_move.y > half) or
                         (next_path.direction in [Path.VERTICAL,Path.DIAGONAL] and last_move.x > half) ):
                         preferred_choice = 0
                    next_move = next_path[preferred_choice]

                if next_move:
                    game.occupy(next_move.x,next_move.y,self.marker)
                    self.occupations.append( next_move )
                    self.strategize(game,opponent,next_move.x,next_move.y)

                    if winning_move:
                        game.complete(Game.STATE_COMPLETE,self.marker)
                else:
                    # If we didn't find any reasonable move to make, the game is a draw
                    game.complete(Game.STATE_DRAW)
            else:
                # If this is not the first move and neither player has paths to win on, the game is a draw
                game.complete(Game.STATE_DRAW)
        else:
            # A User Move
            game.occupy(x,y,self.marker)
            self.occupations.append( game.square(x,y) )

            if self.check_winning_move(game.square(x,y)):
                game.complete(Game.STATE_COMPLETE,self.marker)
            elif not game.squares_available():
                # No more moves available, game is a draw
                game.complete(Game.STATE_DRAW)
            else:
                self.strategize(game,opponent,x,y)
                opponent.move(game,self)

    def sort_paths(self):
        '''Ranks and orders win paths by the number of moves until completion'''
        self.paths.sort(key=lambda path: path.rank())

    def destrategize(self, game, x, y):
        '''
        Negatively impacts an player's win paths with an opponent move placed in the specified coordinate
        x,y. By doing so, we eliminate any winnable paths that contain this point and that have a 
        line of sight through this point.
        '''
        valid_paths = []
        for path in self.paths:
            if game.square(x,y) not in path:
                valid_paths.append(path)
        self.paths = valid_paths
        self.sort_paths()

    def strategize(self, game, opponent, x, y):
        '''
        The core logic of maintaining player strategies. The general logic is to first check if our
        move is already within a win path. If it is, remove the point from the path and mark the path
        to be ignored from further path calculations. Once this is done, we check the Squares that are
        within the line of sight of the specified coordinate x,y. If we encounter an opponent marker,
        we ignore the path. If we encounter our own marker, we ignore it. If we encounter an open space
        we add it to the direction-path.
        '''
        def __check_square(x,y,direction):
            '''A utility function for strategize() that prevents repetition and simplifies the code'''
            if direction not in ignore:
                if game.is_played(x,y):
                    if game.square(x,y) in opponent.occupations:
                        ignore.append(direction)
                else:
                    members[direction].append(game.square(x,y))

        opponent.destrategize(game,x,y)
        ignore = [] # Array of ignoring path directions

        # Mark any existing path containing this point to be ignored to prevent double paths
        square = game.square(x,y)
        for path in self.paths:
            if path.direction not in ignore and square in path:
                path.remove(square)
                ignore.append(path.direction)

        # Dictionary of Direction:Moves that are winnable
        members = { Path.HORIZONTAL:[], Path.VERTICAL:[], Path.DIAGONAL:[], Path.DIAGONAL_INVERSE:[] }
        is_diagonal = (y == x)
        is_diagonal_inverse = (y == game.size - x - 1)

        for i in range(game.size):
            # Check the row, column and diagonals containing this particular point
            __check_square(x,i,Path.HORIZONTAL)
            __check_square(i,y,Path.VERTICAL)
            if is_diagonal:
                __check_square(i,i,Path.DIAGONAL)
            if is_diagonal_inverse:
                __check_square(i,game.size - i - 1,Path.DIAGONAL_INVERSE)

        for direction,path in members.items():
            if path and direction not in ignore:
                self.paths.append( Path(path,direction) )

        self.sort_paths()


if __name__ == '__main__':
    def input_coordinate(row_col, max_val):
        coord = raw_input(">>> Enter a %s number (0-%s): " % (row_col, max_val))
        while type(coord) == str:
            try:
                coord = int(coord)
                if coord not in range(max_val+1):
                    raise ValueError
            except ValueError:
                print "I'm sorry, %s is not a valid input" % coord
                coord = raw_input(">>> Enter a %s number (0-%s): " % (row_col, max_val))
        return coord

    try:
        print '[ TIC TAC TOE ]'
        while True:
            size = None
            while size is None or type(size) == str:
                size = raw_input('>>> Enter a board size (Minimum 3): ')
                try:
                    size = int(size)
                    if size < 3:
                        raise ValueError 
                except ValueError:
                    print "'%s' is not a valid board size" % size
                    size = None

            print "Setting up a %sx%s playing board" % (size,size)
            game = Game(size)

            first = None
            while first is None:
                 first = raw_input('>>> Would you like to move first or second? (1 or 2): ')
                 if first.upper().strip() not in ['1','2']:
                     print "'%s' is an invalid choice" % first
                     first = None
            first = first.upper().strip() == '2' # Should the computer go first?

            game.play(first)
            while game.state == Game.STATE_IN_PROGRESS:
                game.print_board()
                if game.computer.occupations:
                    print "Last computer move at %s" % game.computer.occupations[-1].__repr__()

                move = []
                while not move:
                    move = [ input_coordinate('row',game.size-1), input_coordinate('column',game.size-1) ]
                    if game.is_played(move[0],move[1]):
                        print "The position (%s,%s) is unavailable" % tuple(move)
                        move = []
                    else:
                        game.player.move(game,game.computer,move[0],move[1])
            game.print_board()
            if game.state == Game.STATE_DRAW:
                print 'The game is a draw!'
            else:
                print 'Game Over! %s has won! YOU HAVE %s' % ( game.winner, ('WON' if game.winner == game.player.marker else 'LOST'))

            again = raw_input('Would you like to play again? (Enter y or n): ')
            while again.upper().strip() not in ['Y','N']:
                print "I'm sorry, but %s is an invalid option" % again
                again = raw_input('Would you like to play again? (Enter y or n): ')

            if again.upper().strip() == 'N':
                break
    except KeyboardInterrupt:
        pass

    print 'Goodbye!'
