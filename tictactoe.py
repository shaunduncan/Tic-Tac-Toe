#!/usr/bin/python

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
    return (x == 0 and (y == 0 or y == self.size - 1)) or (y == 0 and (x == 0 or x == self.size - 1))

  def coordinate_key(self, x, y):
    '''Utility to transform an x,y into a 1D list offset'''
    return (size * x) + y

  def square(self,x,y):
    '''Returns the square at x,y'''
    return self.board[ self.coordinate_key(x,y) ]

  def occupy(self, x, y, marker):
    '''Marks a square at an x,y coordinate with a marker and sets it as having been played'''
    self.square(x,y).placemark = marker
    self.squares_played += 1

  def is_played(self, x, y):
    '''Shorthand for checking if an x,y coordinate has been played or not'''
    return self.square(x,y).marked()

  def squares_available(self):
    '''Squares are available if the squares_played counter < size^2'''
    return self.squares_played < pow(self.size,2)

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

  def __setitem__(self, key, value):
    self.squares[key] = value

  def __delitem__(self, key):
    del self.squares[key]

  def remove(self, square):
    self.squares.remove(square)

  def __repr__(self):
    return 'Path(%s): %s' % (self.rank(),str(self.squares))


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
        if self.marker == 'X':
          # First Move, Choose 0,0
          game.occupy(0,0,self.marker)
          self.occupations.append( game.square(0,0) )
          self.strategize(game,opponent,0,0)
        else:
          # What is the optimal 1st move for O?
          player_move = opponent.occupations[-1]
          if game.is_corner(player_move):
            next_x = player_move.x + (1 if player_move.x == 0 else -1)
            next_y = player_move.y + (1 if player_move.y == 0 else -1)

            game.occupy(next_x,next_y,self.marker)
            self.occupations.append( game.square(next_x,next_y) )
            self.strategize(game,opponent,next_x,next_y)
          else:
            game.occupy(0,0,self.marker)
            self.occupations.append( game.square(0,0) )
            self.strategize(game,opponent,0,0)
      else:
        if self.paths:
          # If the computer has available paths that could result in a win, we attempt to evaluate them
          winning_move = False
          next_move = None

          # First thing's first, check for a 1-move win for this player. Then check if we need to block.
          # If all else fails, grab the next move from the win path set
          if self.paths[0].rank() == 1:
            next_move = self.paths[0][-1]
            winning_move = True
          elif opponent.paths and opponent.paths[0].rank() == 1:
            next_move = opponent.paths[0][-1]
            winning_move = self.check_winning_move(next_move)
          else:
            next_move = self.paths[0][-1]
            winning_move = False # We won't win...we have already checked if this is a winning move

          game.occupy(next_move.x,next_move.y,self.marker)
          self.occupations.append( next_move )
          self.strategize(game,opponent,next_move.x,next_move.y)

          if winning_move:
            game.complete(Game.STATE_COMPLETE,self.marker)
        else:
          if opponent.paths:
            # The case where we don't have any more paths to look at but our opponent does
            next_move = opponent.paths[0][-1]
            winning_move = False

            if next_move:
              winning_move = self.check_winning_move(next_move)
              game.occupy(next_move.x,next_move.y,self.marker)
              self.occupations.append( next_move )
              self.strategize(game,opponent,next_move.x,next_move.y)

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
    Negatively impacts an opponents win paths with a move placed in the specified coordinate
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

    # Remove this point from any existing path
    square = game.square(x,y)
    for path in self.paths:
      if square in path:
        path.remove(square)
        ignore.append(path.direction)

    # Dictionary of Direction:Moves that are winnable
    members = { Path.HORIZONTAL:[], Path.VERTICAL:[], Path.DIAGONAL:[], Path.DIAGONAL_INVERSE:[] }

    for i in range(game.size):
      # Check the row, column and diagonals containing this particular point
      __check_square(x,i,Path.HORIZONTAL)
      __check_square(i,y,Path.VERTICAL)
      if y == x:
        __check_square(i,i,Path.DIAGONAL)
      if y == game.size - x - 1:
        __check_square(i,game.size - i - 1,Path.DIAGONAL_INVERSE)

    for direction,path in members.items():
      if path and direction not in ignore:
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
    print '\n[ TIC TAC TOE]\n'
    while True:
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
        game.print_board()
        if game.computer.occupations:
          print "My last move was at (%s,%s)" % (game.computer.occupations[-1].x, game.computer.occupations[-1].y)
        print "Now it's your move"

        move = []
        while not move:
          move = [ input_coordinate('row',game.size-1), input_coordinate('column',game.size-1) ]
          if game.is_played(move[0],move[1]):
            print "Oops. The position (%s,%s) is unavailable" % tuple(move)
            move = []
          else:
            print "Making move at (%s,%s)" % tuple(move)
            game.player.move(game,game.computer,move[0],move[1])
            print "[ END TURN ]"
      game.print_board()
      if game.state == Game.STATE_DRAW:
        print 'The game is a draw!\n'
      else:
        print 'Game Over! %s has won!' % game.winner
        print 'YOU HAVE %s\n' % ('WON' if game.winner == game.player.marker else 'LOST')

      again = raw_input('Would you like to play again? (Enter y or n): ')
      while again.upper().strip() not in ['Y','N']:
        print "I'm sorry, but %s is an invalid option" % again
        again = raw_input('Would you like to play again? (Enter y or n): ')

      if again.upper().strip() == 'N':
        break
  except KeyboardInterrupt:
    pass

  print '\nGoodbye! Thanks for playing!'
  # EOF
