#!/usr/bin/python -tt
import unittest
from tictactoe import *

class TestSquare(unittest.TestCase):
    def setUp(self):
        self.marked_square = Square(0,0)
        self.marked_square.mark('X')
        self.unmarked_square = Square(1,1)

    def test_marked(self):
        '''Ensures the marked() method returns the proper boolean'''
        self.assertFalse(self.unmarked_square.marked())
        self.assertTrue(self.marked_square.marked())

    def test_equals(self):
        '''Ensure that the __eq__() method correctly compares x,y values of a square to determine equality'''
        self.assertEquals(self.unmarked_square,self.unmarked_square)
        self.assertEquals(self.unmarked_square,Square( self.unmarked_square.x, self.unmarked_square.y ))
        self.assertNotEquals(self.unmarked_square,self.marked_square)


class TestPath(unittest.TestCase):
    def setUp(self):
        self.diagonal_path = Path([ Square(0,0), Square(1,1), Square(2,2)],Path.DIAGONAL)
        self.diagonal_inverse_path = Path([ Square(2,0), Square(1,1), Square(0,2) ], Path.DIAGONAL_INVERSE)
        self.horizontal_path = Path([ Square(0,0), Square(0,1), Square(0,2)],Path.HORIZONTAL)
        self.vertical_path = Path([ Square(0,0), Square(1,0), Square(2,0) ], Path.VERTICAL)

    def test_contains(self):
        '''Ensures proper working condition of __contains__'''
        self.assertTrue( Square(0,0) in self.diagonal_path )
        self.assertTrue( Square(1,0) not in self.horizontal_path )

    def test_getitem(self):
        '''Ensures working order of __getitem__'''
        self.assertEquals( Square(0,0), self.horizontal_path[0] )
        self.assertEquals( Square(2,2), self.diagonal_path[-1] )
        self.assertNotEquals( Square(1,1), self.diagonal_path[0] )

    def test_remove(self):
        '''Ensures that the remove() utility removes a particular square from a path'''
        self.assertEquals( self.horizontal_path.rank(), 3 )
        self.horizontal_path.remove( Square(0,0) )
        self.assertEquals( self.horizontal_path.rank(), 2 )
        self.assertTrue( Square(0,0) not in self.horizontal_path )
        self.setUp()

    def test_line_slope_intersect(self):
        '''
        Ensures the correct m and b values for slope-intersect calculations is correct.
        Correct functionality would yield the following:
            Horizontal Path: m = None, b = None
            Vertical Path: m = 0, b = <y-value of square in path>
            Diagonal Path: m = 1, b = 0
            Diagonal Inverse Path: m = -1, b = <size of game board> - 1
        '''
        self.assertEquals( self.diagonal_path.line_slope_intersect(), (1,0) )
        self.assertEquals( self.diagonal_inverse_path.line_slope_intersect(), (-1,2) )
        self.assertEquals( self.horizontal_path.line_slope_intersect(), (None,None) )
        self.assertEquals( self.vertical_path.line_slope_intersect(), (0,self.vertical_path[0].y) )

    def test_intersection(self):
        '''
        All paths should yield some intersection that solves the system of linear equations representing
        each line. This is NOT the case if the lines are equivalent or parallel and the expectation is (None,None).
        This property should be reflexive.
        '''
        parallel_horizontal_path = Path([ Square(2,0), Square(2,1), Square(2,2)],Path.HORIZONTAL) 
        self.assertEquals( self.horizontal_path.intersection(parallel_horizontal_path), (None,None) )
        self.assertEquals( self.horizontal_path.intersection(self.horizontal_path), (None,None) )

        # Diagonal and Diagonal Inverse should intersect at grid's midpoint...(1,1) in our case
        self.assertEquals( self.diagonal_path.intersection(self.diagonal_inverse_path), (1,1) )
        self.assertEquals( self.diagonal_inverse_path.intersection(self.diagonal_path), (1,1) )

        # Horizontal and vertical lines intersect at the combination of their x and y values
        self.assertEquals( self.horizontal_path.intersection(self.vertical_path), (self.horizontal_path[0].x,self.vertical_path[0].y))

        # Diagonal and horizontal/vertical intersections solve the system of linear equations
        # Case 1:
        #   y = x       Diagonal
        #   x = 0       Horizontal
        #   y = 0       Vertical
        #   Intersect at (0,0)
        self.assertEquals( self.horizontal_path.intersection(self.diagonal_path), (0,0) )
        self.assertEquals( self.vertical_path.intersection(self.diagonal_path), (0,0) )

        # Case 2:
        #   y = 2 - x   Diagonal Inverse
        #   x = 0       Horizontal
        #   y = 0       Vertical
        #   Intersect at (0,2) for horizontal, (2,0) for vertical
        self.assertEquals( self.horizontal_path.intersection(self.diagonal_inverse_path), (0,2) )
        self.assertEquals( self.vertical_path.intersection(self.diagonal_inverse_path), (2,0) )


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(3)

    def test_board_creation(self):
        '''Ensures the utility method __make_board() is working as it should to create a 1-D list of squares'''
        self.assertEquals( len(self.game.board), 9 )
        self.assertTrue( Square(0,0) in self.game.board )
        self.assertTrue( Square(10,10) not in self.game.board )

        # The offsets of the list should be (size * x) + y
        self.assertEquals( self.game.coordinate_key(1,2), 5)
        self.assertNotEquals( self.game.coordinate_key(1,1), 1)
        self.assertEquals( self.game.board.index(Square(1,2)), 5 )
        self.assertNotEquals( self.game.board.index(Square(1,1)), 1)

    def test_get_square(self):
        '''Ensures that proper squares are retrieved by the square() method'''
        self.assertEquals( self.game.square(0,0), Square(0,0) )
        self.assertEquals( self.game.square(1,2), Square(1,2) )
        self.assertNotEquals( self.game.square(2,2), Square(1,1) )
        self.assertRaises( IndexError, self.game.square, 5, 5)

    def test_occupy(self):
        '''Ensures that a square is marked appropriately, it is not available and the play count increases'''
        self.assertFalse( self.game.square(0,0).marked() )
        self.assertFalse( self.game.is_played(0,0) )
        self.game.occupy(0,0,'X')
        self.assertTrue( self.game.square(0,0).marked(), 'X')
        self.assertTrue( self.game.is_played(0,0) )
        self.setUp()


    def test_is_played(self):
        '''A square should be "played" if it has been marked'''
        self.assertFalse( self.game.is_played(0,0) )
        self.game.occupy(0,0,'X')
        self.assertTrue( self.game.is_played(0,0) )
        self.setUp()

    def test_is_corner(self):
        '''The corners are (0,0), (0,size-1), (size-1,0), and (size-1,size-1)'''
        self.assertTrue( self.game.is_corner(Square(0,0)) )
        self.assertTrue( self.game.is_corner(Square(2,2)) )
        self.assertTrue( self.game.is_corner(Square(0,2)) )
        self.assertTrue( self.game.is_corner(Square(2,0)) )
        self.assertFalse( self.game.is_corner(Square(1,1)) )
        self.assertFalse( self.game.is_corner(Square(1,0)) )

    def test_is_edge(self):
        '''
        The edges are when x = 0 and y is between [1,size-1) - OR - y = 0 and x is between [1,size-1)
        +-------+-------+-------+
        |       | (0,1) |       |
        +-------+-------+-------+
        | (1,0) |       | (1,2) |
        +-------+-------+-------+
        |       | (2,1) |       |
        +-------+-------+-------+
        '''
        self.assertTrue( self.game.is_edge(Square(0,1)) )
        self.assertTrue( self.game.is_edge(Square(2,1)) )
        self.assertTrue( self.game.is_edge(Square(1,0)) )
        self.assertTrue( self.game.is_edge(Square(1,2)) )
        self.assertFalse( self.game.is_edge(Square(0,0)) )
        self.assertFalse( self.game.is_edge(Square(1,1)) )

    def test_is_any_edge(self):
        '''
        Ensures that any edge or corner returns a True
        +-------+-------+-------+
        | (0,0) | (0,1) | (0,2) |
        +-------+-------+-------+
        | (1,0) |       | (1,2) |
        +-------+-------+-------+
        | (2,0) | (2,1) | (2,2) |
        +-------+-------+-------+
        '''
        self.assertTrue( self.game.is_any_edge(Square(0,1)) )
        self.assertTrue( self.game.is_any_edge(Square(2,1)) )
        self.assertTrue( self.game.is_any_edge(Square(1,0)) )
        self.assertTrue( self.game.is_any_edge(Square(1,2)) )
        self.assertTrue( self.game.is_any_edge(Square(0,0)) )
        self.assertTrue( self.game.is_any_edge(Square(2,2)) )
        self.assertFalse( self.game.is_any_edge(Square(1,1)) )

    def test_available_center(self):
        '''Ensures that an available center is generated or None'''
        self.assertEquals( self.game.available_center(), (1,1) )
        self.assertNotEquals( self.game.available_center(), (0,0) )
    
        # Occupy the center so we get nothing back
        self.game.occupy(1,1,'X')
        self.assertEquals( self.game.available_center(), (None,None) )

        self.setUp()

    def test_avialable_corner(self):
        '''Ensures that an available corner is generated or None'''
        x,y = self.game.available_corner()
        self.assertTrue( self.game.is_corner( self.game.square(x,y) ))
        self.assertTrue( self.game.is_any_edge( self.game.square(x,y) ))
        self.assertFalse( self.game.is_edge( self.game.square(x,y) ))

        # Occupy the chosen square
        self.game.occupy(x,y,'X')
        self.assertNotEquals( self.game.available_corner(), self.game.square(x,y) )
        
        # Occupy the remianing three corners
        for i in range(3):
            x,y = self.game.available_corner()
            self.game.occupy(x,y,'X')

        # Make sure (None,None) is returned
        self.assertEquals( self.game.available_corner(), (None,None) )
        self.setUp()

    def test_play(self):
        '''
        To ensure the computer AI mechanisms are "smart" enough to play and not
        lose in any case, simulate fully automated games for 3x3, 4x4 and 5x5. The
        AI should be smart enough to know not to lose and simply wait for a "dumb" 
        move by the player. This test should PASS if a "dumb" player will make random
        moves and the game either results in a win for the computer or a draw
        '''
        num_games = 500
        sizes = range(3,10)

        for size in sizes:
            for i in range(num_games):
                self.game = Game(size)

                if i % 2 == 1:
                    # Simulate the first move by the "dumb" player
                    self.game.player.marker = 'X'
                    self.game.computer.marker = 'O'
                else:
                    # Computer is making the first move
                    self.game.computer.move(self.game,self.game.player)

                while self.game.state == Game.STATE_IN_PROGRESS:
                    x,y = self.game.available_square()
                    self.game.player.move(self.game,self.game.computer,x,y)

                self.assertTrue( self.game.state in [Game.STATE_DRAW,Game.STATE_COMPLETE] )
                if self.game.state == Game.STATE_COMPLETE:
                    self.assertEquals( self.game.winner, self.game.computer.marker )
                else:
                    self.assertEquals( self.game.state, Game.STATE_DRAW )


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.game = Game(3)

    def test_destrategize(self):
        '''
        Proper working order of destrategize() would eliminate a path containing a block.
        '''
        self.game.computer.occupations.append( Square(0,0) )
        self.game.computer.paths.append( Path([ Square(1,1), Square(2,2) ],Path.DIAGONAL) )
        self.game.computer.destrategize( self.game, 0, 1 )
        self.assertEquals( len(self.game.computer.paths), 1 )

        self.game.computer.destrategize( self.game, 1, 1 )
        self.assertEquals( len(self.game.computer.paths), 0 )
        self.setUp()

    def test_check_winning_move(self):
     '''A winning move is one that lies in a single element path'''
     self.game.computer.paths = [ Path([Square(1,1)],Path.DIAGONAL) ]
     self.assertTrue( self.game.computer.check_winning_move(Square(1,1)) )
     self.assertFalse( self.game.computer.check_winning_move(Square(2,2)) )

     self.game.computer.paths = [ Path([Square(1,1),Square(2,2)],Path.DIAGONAL) ]
     self.assertFalse( self.game.computer.check_winning_move(Square(1,1)) )
     self.assertFalse( self.game.computer.check_winning_move(Square(0,2)) )
     self.setUp()

    def test_strategize(self):
        '''
        Ensure the proper working order of the strategize() method. For this to work properly,
        we must see that paths are generated for a given square. We must also gurantee that any
        paths are ignored if an opponent lies within it.
        '''
        self.game.occupy(0,0,self.game.player.marker)
        self.game.player.strategize(self.game,self.game.computer,0,0)

        # There should be three paths of rank 2, and they should be vertical, horizontal and 
        # diagonal
        self.assertEquals( len(self.game.player.paths), 3 )
        for path in self.game.player.paths:
            self.assertEquals( path.rank(), 2 )
            self.assertTrue( path.direction in [Path.HORIZONTAL,Path.VERTICAL,Path.DIAGONAL] )
            self.assertNotEquals( path.direction, Path.DIAGONAL_INVERSE )            
            # Check each path and ensure the proper points appear in them
            if path.direction == Path.HORIZONTAL:
                self.assertTrue( Square(0,1) in path )
                self.assertTrue( Square(0,2) in path )
                self.assertTrue( Square(2,2) not in path )
                self.assertTrue( Square(0,0) not in path )
            elif path.direction == Path.VERTICAL:
                self.assertTrue( Square(1,0) in path )
                self.assertTrue( Square(2,0) in path )
                self.assertTrue( Square(2,2) not in path )
                self.assertTrue( Square(0,0) not in path )
            elif path.direction == Path.DIAGONAL:
                self.assertTrue( Square(1,1) in path )
                self.assertTrue( Square(2,2) in path )
                self.assertTrue( Square(1,0) not in path )
                self.assertTrue( Square(0,0) not in path )

        # Reset and check the center which will have paths that contain ALL the edge/corners
        self.setUp()
        self.game.occupy(1,1,self.game.player.marker)
        self.game.player.strategize(self.game,self.game.computer,1,1)
        self.assertEquals( len(self.game.player.paths), 4 )
        path_squares = []
        for path in self.game.player.paths:
            for square in path:
                path_squares.append(square)
                self.assertTrue( self.game.is_any_edge(square) )
        self.assertEquals( len(path_squares), 8 )
        self.assertTrue( Square(1,1) not in path_squares )
        self.setUp()

    def test_move(self):
        '''Testing all aspects of a "move"'''
        # Human Moves. The computer responds to this corner move with a center square.
        # We make the assumption that the human player is X and therefore is making the first move
        self.game.player.marker = 'X'
        self.game.computer.marker = 'O'
        self.game.player.move(self.game,self.game.computer,0,0)
        self.assertEquals( len(self.game.player.paths), 2 )
        self.assertEquals( len(self.game.player.occupations), 1 )
        self.assertTrue( Square(0,0) in self.game.player.occupations )
        self.assertTrue( self.game.is_played(0,0) )
        self.assertFalse( self.game.is_any_edge( self.game.computer.occupations[0] ) )
        self.setUp()

        # Human move on a non-corner edge
        self.game.player.marker = 'X'
        self.game.computer.marker = 'O'
        self.game.player.move(self.game,self.game.computer,0,1)
        self.assertEquals( len(self.game.player.paths), 1 )
        self.assertEquals( len(self.game.player.occupations), 1 )
        self.assertTrue( Square(0,1) in self.game.player.occupations )
        self.assertTrue( self.game.is_played(0,1) )
        self.assertFalse( self.game.is_any_edge( self.game.computer.occupations[0] ) )
        self.setUp()

        # Human move on a center. Four paths generated, computer blocks a corner and reduces paths by 1
        self.game.player.marker = 'X'
        self.game.computer.marker = 'O'
        self.game.player.move(self.game,self.game.computer,1,1)
        self.assertEquals( len(self.game.player.paths), 3 )
        self.assertEquals( len(self.game.player.occupations), 1 )
        self.assertTrue( Square(1,1) in self.game.player.occupations )
        self.assertTrue( self.game.is_played(1,1) )
        self.assertTrue( self.game.is_corner( self.game.computer.occupations[0] ) )
        self.assertFalse( self.game.is_edge( self.game.computer.occupations[0] ) )
        self.setUp()

        # Computer Initial Move. This should pick a random corner
        self.game.computer.move(self.game,self.game.player)
        self.assertEquals( len(self.game.computer.paths), 3 )
        self.assertEquals( len(self.game.computer.occupations), 1 )
        self.assertTrue( self.game.is_corner( self.game.computer.occupations[0] ) )
        self.assertTrue( self.game.is_played( self.game.computer.occupations[0].x, self.game.computer.occupations[0].y ) )

        # Have the player choose the opposite corner from the first move and make sure the diagonal path is eliminated
        computer_move = self.game.computer.occupations[0]
        x = 0 if computer_move.x == 2 else 2
        y = 0 if computer_move.y == 2 else 2
        self.game.player.move(self.game,self.game.computer,x,y)
        self.assertEquals( len(self.game.computer.occupations), 2 )
        for path in self.game.computer.paths:
            self.assertTrue( Square(x,y) not in path )

        # There should be a 1-move win within immediate grasp
        self.assertEquals( self.game.computer.paths[0].rank(), 1 )
        self.assertTrue( self.game.computer.check_winning_move(self.game.computer.paths[0][0]) )

        # Ensure that the next move made by the computer results in the game win
        self.assertEquals( self.game.state, Game.STATE_IN_PROGRESS )
        self.game.computer.move( self.game, self.game.player )
        self.assertEquals( self.game.state, Game.STATE_COMPLETE )
        self.assertEquals( self.game.winner, self.game.computer.marker )
        self.setUp()


if __name__ == '__main__':
    unittest.main()
