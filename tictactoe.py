#!/usr/bin/python
import math

class Game:
  '''
  A Game is the primary component of this application. It is the facilitator of
  user and computer interactions, movements. A Game maintains a state which is
  one of STATE_IN_PROGRESS, STATE_DRAW, or STATE_COMPLETE
  '''
  STATE_IN_PROGRESS = 0
  STATE_COMPLETE = 1
  STATE_DRAW = 2

  def __init__(self,size):
    self.board = Board(size)
    self.state = Game.STATE_IN_PROGRESS
    self.winner = None

  def play(self, computer_first = True):
    '''Initiate the game'''
    if computer_first:
      self.computer = Player('X')
      self.player = Player('O')
      self.computer.move(self,self.board,self.player)
    else:
      self.computer = Player('O')
      self.player = Player('X')

  def complete(self, outcome, winner = None):
    '''Completes a game with the specified outcome and optional winner'''
    self.state = outcome
    self.winner = winner
    


class Board:
  '''
  A Board is the main component of a Game. It can be thought of as a bookkeeper
  of sorts for managing game operations. The board will keep track of all squares
  and those that have been played
  '''  
  def __init__(self, size):
    self.size = size
    self.squares = []
    self.played = []

    for i in range(size):
      self.squares.append([])
      for j in range(size):
        self.squares[i].append( Square(i,j) )

  def is_corner(self, x, y):
    '''
    Checks to see if an x,y position is a board corner or not. There are four corners to check
    for: (0,0), (0,size-1), (size-1,0), (size-1,size-1)
    '''
    return (x == 0 and (y == 0 or y == self.size - 1)) or (y == 0 and (x == 0 or x == self.size - 1))

  def occupy(self, x, y, marker):
    '''Marks a square at an x,y coordinate with a marker and sets it as having been played'''
    self.squares[x][y].placemark = marker
    self.played.append( self.squares[x][y] )

  def is_played(self, x, y):
    '''Shorthand for checking if an x,y coordinate has been played or not'''
    return self.squares[x][y] in self.played

  def __str__(self):
    rows = []
    glue = '\n   ' + ('+'.join(['---' for i in range(self.size)])) + '\n'
    header = '    ' + '   '.join([ str(x) for x in range(self.size) ]) + ' '

    for row in self.squares:
      rows.append(' ' + str(self.squares.index(row)) + '  ' + (' | '.join([ str(cell) for cell in row ])) + ' ')

    return '\n' + header + '\n' + glue.join(rows) + '\n'
    


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


class Path:
  '''
  A Path represents a collection of moves/squares that ultimately results in a win
  for the player that owns it. Paths are also direction-oriented as in this
  scenario, there are four distinct directions: horizontal, vertical, 
  diagonal and inverse diagonal. Paths also maintain a rank which is analagous to
  the number of moves need to complete the path
  '''
  PATH_HORIZONTAL = 0
  PATH_VERTICAL = 1
  PATH_DIAGONAL = 2
  PATH_DIAGONAL_INVERSE = 3

  def __init__(self, moves, direction):
    self.direction = direction
    self.moves = moves

  def rank(self):
    return len(self.moves)

  def last(self):
    return self.moves[-1]

  def __repr__(self):
    return 'Path(%s): %s' % (self.rank(),str(self.moves))


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

  def check_win_block(self,square):
    '''
    Checks a square being played lies within a single move path we are keeping track
    of. In otherwords, we check only rank-1 paths, otherwise return false
    '''
    for path in self.paths:
      if path.rank() > 1:
        return False
      elif square in path.moves:
        return True

  def move(self,game,board,opponent,x = None,y = None):
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
        if self.marker == 'X':
          # First Move, Choose 0,0
          board.occupy(0,0,self.marker)
          self.occupations.append( board.squares[0][0] )
          self.strategize(board,opponent,0,0)
        else:
          # What is the optimal 1st move for O?
          player_move = opponent.occupations[-1]
          if board.is_corner(first_move):
            next_x = player_move.x + (1 if player_move.x == 0 else -1)
            next_y = player_move.y + (1 if player_move.y == 0 else -1)

            board.occupy(next_x,next_y,self.marker)
            self.occupations.append( board.squares[next_x][next_y] )
            self.strategize(board,opponent,next_x,next_y)
          else:
            board.occupy(0,0,self.marker)
            self.occupations.append( board.squares[0][0] )
            self.strategize(board,opponent,0,0)
      else:
        if self.paths:
          # If the computer has available paths that could result in a win, we attempt to evaluate them
          winning_move = False
          next_move = None

          # First thing's first, check for a 1-move win for this player. Then check if we need to block.
          # If all else fails, grab the next move from the win path set
          if self.paths[0].rank() == 1:
            next_move = self.paths[0].last()
            winning_move = True
          elif opponent.paths and opponent.paths[0].rank() == 1:
            next_move = opponent.paths[0].last()
            winning_move = self.check_win_block(next_move)
          else:
            next_move = self.paths[0].last()
            winning_move = False # We won't win...we have already checked if this is a winning move

          board.occupy(next_move.x,next_move.y,self.marker)
          self.occupations.append( next_move )
          self.strategize(board,opponent,next_move.x,next_move.y)

          if winning_move:
            game.complete(Game.STATE_COMPLETE,self.marker)
        else:
          if opponent.paths:
            # The case where we don't have any more paths to look at but our opponent does
            next_move = opponent.paths[0].last()
            winning_move = False

            if next_move:
              winning_move = self.check_win_block(next_move)
              board.occupy(next_move.x,next_move.y,self.marker)
              self.occupations.append( next_move )
              self.strategize(board,opponent,next_move.x,next_move.y)

              if winning_move:
                game.complete(Game.STATE_COMPLETE,self.marker)
            else:
              # If for some reason the player has an empty path and we have no paths, then 
              # the game is a draw
              game.complete(Game.STATE_DRAW)
          else:
            # If this is not the first move and neither player has paths to win on, the game
            # is deemed a draw
            game.complete(Game.STATE_DRAW)
    else:
      # A User Move
      board.occupy(x,y,self.marker)
      self.occupations.append( board.squares[x][y] )
      self.strategize(board,opponent,x,y)
      opponent.move(game,board,self)

      # TODO: Check if the move resulted in a win

  def sort_paths(self):
    '''Ranks and orders win paths by the number of moves until completion'''
    self.paths.sort(key=lambda path: path.rank())

  def destrategize(self, board, opponent, x, y):
    '''
    Negatively impacts an opponents win paths with a move placed in the specified coordinate
    x,y. By doing so, we eliminate any winnable paths that contain this point and that have a 
    line of sight through this point.
    '''
    for path in opponent.paths:
      if board.squares[x][y] in path.moves:
        opponent.paths.remove(path)
    opponent.sort_paths()

  def strategize(self, board, opponent, x, y):
    '''
    The core logic of maintaining player strategies. The general logic is to first check if our
    move is already within a win path. If it is, remove the point from the path and mark the path
    to be ignored from further path calculations. Once this is done, we check the Squares that are
    within the line of sight of the specified coordinate x,y. If we encounter an opponent marker,
    we ignore the path. If we encounter our own marker, we ignore it. If we encounter an open space
    we add it to the direction-path.
    '''
    self.destrategize(board,opponent,x,y)
    ignore = [] # Array of ignoring path directions

    # Remove this point from any existing path
    square = board.squares[x][y]
    for path in self.paths:
      if square in path.moves:
        path.moves.remove(square)
        ignore.append(path.direction)

    # Dictionary of Direction:Moves that are winnable
    members = { Path.PATH_HORIZONTAL:[], Path.PATH_VERTICAL:[], Path.PATH_DIAGONAL:[], Path.PATH_DIAGONAL_INVERSE:[] }

    for i in range(board.size):
      # Check the row containing this particular point
      if Path.PATH_HORIZONTAL not in ignore:
        if board.is_played(x,i):
          if board.squares[x][i] in opponent.occupations:
            ignore.append(Path.PATH_HORIZONTAL)            
        else:
            members[Path.PATH_HORIZONTAL].append( board.squares[x][i] )

      # Check the column containing this particular point
      if Path.PATH_VERTICAL not in ignore:
        if board.is_played(i,y):
          if board.squares[i][y] in opponent.occupations:
            ignore.append(Path.PATH_VERTICAL)
        else:
            members[Path.PATH_VERTICAL].append( board.squares[i][y] )

      if x == y:
        # Only check the diagonal path if the point lies on the x=y diagonal (top-left to bottom-right)
        if Path.PATH_DIAGONAL not in ignore:
          if board.is_played(i,i):
            if board.squares[i][i] in opponent.occupations:
              ignore.append(Path.PATH_DIAGONAL)
          else:
              members[Path.PATH_DIAGONAL].append( board.squares[i][i] )

      if y == board.size - x - 1:
        # Only check the inverse diagonal path if the point lies on the y=size-x-1 diagonal (bottom-left to top-right)
        inverse = board.size - i - 1
        if Path.PATH_DIAGONAL_INVERSE not in ignore:
          if board.is_played(i,inverse):
            if board.squares[i][inverse] in opponent.occupations:
              ignore.append(Path.PATH_DIAGONAL_INVERSE)
          else:
              members[Path.PATH_DIAGONAL_INVERSE].append( board.squares[i][inverse] )

    for direction,path in members.items():
      if path and len(path) > 0 and direction not in ignore:
        self.paths.append( Path(path,direction) )

    self.sort_paths()


if __name__ == '__main__':
  def input_coordinate(row_col, max_val):
    coord = raw_input("Enter a %s number (0-%s): " % (row_col, max_val))
    while type(coord) == str:
      try:
        coord = int(coord)
        if coord not in range(max_val+1):
          raise ValueError
      except ValueError:
        print "I'm sorry, %s is not a valid input" % coord
        coord = raw_input("Enter a %s number (0-%s): " % (row_col, max_val))
    return coord  

  try:
    print '''
+------------------------------------------------------------------------------+
|                         Welcome to Tic-Tac-Toe!                              |
+------------------------------------------------------------------------------+
'''
    size = raw_input('What size board would you like to play? (Minimum 3, Default 3) ')

    while type(size) == str:
      if size.strip() == '':
        size = 3
      else:
        try:
          size = int(size)
          if size < 3:
            raise ValueError 
        except ValueError:
          print "I'm sorry, %s is not a valid board size" % size
          size = raw_input('What size board would you like to play? (Minimum 3, Default 3) ')

    print "Great, I'll set up a %(n)sx%(n)s playing board\n" % { 'n' : size }
    game = Game(size)

    first = raw_input('Would you like to move first? (Enter 1 or 2): ')
    while first.upper().strip() not in ['1','2']:
      print "I'm sorry, %s is an invalid choice" % first
      first = raw_input("Would you like to move first or second? (Enter 1 or 2): ")
    first = first.upper().strip() == '2'

    if first:
      print "Ok, I'll go first"
    else:
      print "That confident, eh? Ok, you'll go first"
    
    print '\nGOOD LUCK!\n'
    game.play(first)
    while game.state == Game.STATE_IN_PROGRESS:
      print game.board
      last_computer_move = game.computer.occupations[-1]
      if last_computer_move:
        print "My last move was at (%s,%s)" % (last_computer_move.x, last_computer_move.y)
      print "Now it's your move"

      move = [ None, None ]
      while not move[0] and not move[1]:
        move[0] = input_coordinate('row',game.board.size-1)
        move[1] = input_coordinate('column',game.board.size-1)
        if game.board.is_played(move[0],move[1]):
          print "Oops. The position (%s,%s) is unavailable" % tuple(move)
          move = [ None, None ]
        else:
          print "Making move at (%s,%s)" % tuple(move)
          game.player.move(game,game.board,game.computer,move[0],move[1])
          print "[ END TURN ]"
    print game.board
    if game.state == Game.STATE_DRAW:
      print 'The game is a draw!'
    elif game.state == Game.STATE_COMPLETE:
      print 'Game Over! %s has won!' % game.winner
  except KeyboardInterrupt:
    # Just so we have a way to exit cleanly
    print '\nGoodbye!'
