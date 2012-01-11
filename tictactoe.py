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

  def __init__(self,size,computer_first = True):
    self.board = Board(size)
    self.state = Game.STATE_IN_PROGRESS
    self.winner = None

    if computer_first:
      self.computer = Player('X')
      self.player = Player('O')
      self.computer.move(self,self.player)
    else:
      self.computer = Player('O')
      self.player = Player('X')

  def complete(self, outcome, winner = None):
    self.state = outcome
    self.winner = winner
    


class Board:
  '''
  A Board is the main component of a Game. It can be thought of as a bookkeeper
  of sorts for managing game operations.
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
    return (x == 0 and y == 0) or \
      (x == self.size - 1 and y == self.size - 1) or \
      (x == 0 and y == self.size - 1) or \
      (x == self.size - 1 and y == 0)

  def occupy(self, x, y, marker):
    square = self.squares[x][y]
    square.placemark = marker
    self.played.append( square.key )
    return square

  def is_played(self, x, y):
    return self.squares[x][y] in self.played

  def __str__(self):
    rows = []
    glue = '\n' + ('+'.join(['---' for i in range(self.size)])) + '\n'

    for row in self.squares:
      rows.append(' ' + (' | '.join([ str(cell) for cell in row ])) + ' ')

    return glue.join(rows)    
    


class Square:
  '''
  A Square is a basic component of a Board. It maintains an x,y coordinate
  position and a placemarker which is by default empty.
  '''
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.placemark = None

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

  def __init__(self, members, direction):
    self.direction = direction
    self.members = members

  def contains(self, square):
    return square in self.members

  def remove(self, square):
    if self.contains(square):
      self.members.remove(square)
      return True
    else:
      return False

  def add(self, square):
    self.members.append(square)

  def rank(self):
    return len(self.members)

  def last(self):
    return self.members[-1]


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

  def check_win_block(square):
    for path in self.paths:
      if path.rank() > 1:
        return False
      elif path.contains(square):
        return True

  def move(game,opponent,x = None,y = None):
    board = game.board
    
    if x == None and y == None:
      # A Computer Move
      if not self.occupations:
        if self.marker == 'X':
          # First Move, Choose 1,1
          self.occupations.append( board.occupy(1,1,self.marker) )
          self.strategize(board,opponent,1,1)
        else:
          # What is the optimal 1st move for O?
          first_move = opponent.occupations[-1]
          if board.is_corner(first_move):
            next_x = first_move.x + (1 if first_move.x == 0 else -1)
            next_y = first_move.y + (1 if first_move.y == 0 else -1)

            self.occupations.append( board.occupy(next_x,next_y,self.marker) )
            self.strategize(board,opponent,next_x,next_y)
          else:
            self.occupations.append( board.occupy(1,1,self.marker) )
            self.strategize(board,opponent,1,1)
      else:
        if self.paths:
          winning_move = False
          next_move = None

          # First thing's first, check for a 1-move opponent win
          if opponent.paths and opponent.paths[1].rank() == 1:
            next_move = opponent.paths[1].last()
            winning_move = self.check_win_block(next_move)
          else:
            next_move = self.paths[1].last()
            winning_move = self.paths[1].rank() == 1

          self.occupations.append( board.occupy(next_move.x,next_move.y,self.marker) )
          self.strategize(board,opponent,next_move.x,next_move.y)

          if winning_move:
            game.complete(Game.STATE_COMPLETE,self.marker)
        else:
          if opponent.paths:
            # The case where we don't have any more paths to look at
            # but our opponent does
            next_move = opponent.paths[1].last()
            winning_move = False

            if next_move:
              winning_move = self.check_win_block(next_move)
              self.occupations.append( board.occupy(next_move.x,next_move.y,self.marker) )
              self.strategize(board,opponent,next_move.x,next_move.y)

              if winning_move:
                game.complete(Game.STATE_COMPLETE,self.marker)
            else:
              game.complete(Game.STATE_DRAW)
          else:
            game.complete(Game.STATE_DRAW)
    else:
      # A User Move
      self.occupations.append( board.occupy(x,y,self.marker) )
      self.strategize(board,opponent,x,y)
      opponent.move(game,self)

      # TODO: Check if the move resulted in a win

  def sort_paths(self):
    self.paths.sort(key=lambda path: path.rank())

  def destrategize(self, board, opponent, x, y):
    for path in opponent.paths:
      if path.contains( board.squares[x][y] ):
        opponent.paths.remove(path)
    opponent.sort_paths()

  def strategize(self, board, opponent, x, y):
    self.destrategize(board,opponent,x,y)
    ignore = { \
      Path.PATH_HORIZONTAL:False, \
      Path.PATH_VERTICAL:False, \
      Path.PATH_DIAGONAL:False, \
      Path.PATH_DIAGONAL_INVERSE:False }

    square = board.squares[x][y]
    for path in self.paths:
      if path.contains(square):
        path.remove(square)
        ignore[path.direction] = True

    members = { \
      Path.PATH_HORIZONTAL:[], \
      Path.PATH_VERTICAL:[], \
      Path.PATH_DIAGONAL:[], \
      Path.PATH_DIAGONAL_INVERSE:[] }

    for i in range(board.size):
      if not ignore[Path.PATH_HORIZONTAL] and members[Path.PATH_HORIZONTAL] != None:
        if board.is_played(x,i):
          if board.squares[x][i] in opponent.occupations:
            members[Path.PATH_HORIZONTAL] = None
        else:
            members[Path.PATH_HORIZONTAL].append( board.squares[x][i] )

      if not ignore[Path.PATH_VERTICAL] and members[Path.PATH_VERTICAL] != None:
        if board.is_played(i,y):
          if board.squares[i][y] in opponent.occupations:
            members[Path.PATH_VERTICAL] = None
        else:
            members[Path.PATH_VERTICAL].append( board.squares[i][y] )

      if x == y:
        if not ignore[Path.PATH_DIAGONAL] and members[Path.PATH_DIAGONAL] != None:
          if board.is_played(i,i):
            if board.squares[i][i] in opponent.occupations:
              members[Path.PATH_DIAGONAL] = None
          else:
              members[Path.PATH_DIAGONAL].append( board.squares[i][i] )

      if y == board.size - x - 1:
        inverse = board.size - x - 1
        if not ignore[Path.PATH_DIAGONAL_INVERSE] and members[Path.PATH_DIAGONAL_INVERSE] != None:
          if board.is_played(i,inverse):
            if board.squares[i][inverse] in opponent.occupations:
              members[Path.PATH_DIAGONAL_INVERSE] = None
          else:
              members[Path.PATH_DIAGONAL_INVERSE].append( board.squares[i][inverse] )

    for direction,path in members:
      if path and len(path) > 0:
        self.paths.append( Path(path,direction) )

    self.sort_paths()
