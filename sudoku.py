
import math
import time
import timeit

debug = True


''' 
CHANGES TO MAKE/TRY:
    Naked Subset - set of cells with the exact same notes of ONLY the possible numbers (as many as there are cells) that can be there
    in the same row, column or box. This indicates those cells can only be those numbers and the notes for all other 
    connected cells should be updated.
    Hidden Subset - set of cells in same row, column, or box that are the only place that a set of numbers appear 
    (equal amount of candidates to the # of cells).
    * Note: Neither of these cases require that all candidates be in all cells, only that the # of candidate only appear in the same # of cells
    Didn't take this into account below...
    
    Add function to identify naked pairs in rows columns and boxes
        * Notes:
        Naked pairs aren't needed for updating notes in the box they're in because this code begins with all
        notes being possible and removes notes, as opposed to filling in notes from scratch. This means a naked pair found
        in a box won't change any of the notes in that box because, by definition, those numbers' notes are only in that
        box. This also means that the notes in the same row or column of a naked pair need to be updated according to the
        numbers that make up that naked pair when they are on the same row or column (regardless of if they're in the same block).
        But, since we are only removing notes and not adding them, we don't have to worry about naked pairs becoming hidden as well.
        
        Idea to compare all sets in the same box with length two to see if same? Then uses indices of notes to identify
        position.
            0. Check for cell with notes of length 2 for its set
            1. Identify two #s contained
            2. Check row/column/box to see if both numbers only appear twice
            3. Check row/column/box to see if another cell contains both numbers
            3. If two cells in same row/column/box contain the only two instances of the same two numbers, remove the 
                notes for all other numbers from both cells
                
    Add function for hidden pairs in rows columns and boxes
        *Notes:
        Plan
            1. Check each row/column/box for # of occurrences of each # in their cells' notes
            2. Determine all combinations of #s that appear twice (or any # of times [2-8] for most comprehensive method)
            3. check all cells in row/column/box to see if they contain both of each combination 
            (or the same amount of cells as # of occurrences of #s involved if comprehensive)
            4. If two cells contain two numbers that both only appear twice, remove all other notes in those cells and 
            remove those numbers from the notes of all other connected cells
            
        Idea for both of these is a 4-D list: outer list for each number, next layer for each box in grid, next layer 
        for each row of each box, final layer for index of column in each row. Then we compare each number's grid to 
        each other one and look for overlap that would indicate hidden pairs, trios...others?
    
    Scanning Technique 4: Eliminating notes from rows columns and boxes based on notes in other boxes
    
    https://www.conceptispuzzles.com/index.aspx?uri=puzzle/sudoku/techniques
    http://hodoku.sourceforge.net/en/tech_intersections.php

    Replace recursive entry function with global variable that stores positions (and values?) to update
    
'''


class Sudoku:

    def __init__(self, grid):
        # initiate attributes
        self.grid = grid
        self.od = len(self.grid)
        self.id = math.sqrt(self.od)
        self.beginNote = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        # completion count: measures # of cells with determined values
        self.cmpltnct = 0
        self.evalct = 0
        self.updated = True
        # list of sets to contain values in each rows and another for each column
        self.rows = [set() for i in range(self.od)]
        self.cols = [set() for j in range(self.od)]
        self.boxs = [set() for k in range(self.od)]
        # replace empty spots (0s) with sets of all possible #s that could be in the cell, 1-9
        for i in range(self.od):
            for j in range(self.od):
                temp = self.grid[i][j]
                if temp == 0:
                    self.grid[i][j] = self.beginNote
                else:
                    self.cmpltnct+=1
                    self.rows[i].add(temp)
                    self.cols[j].add(temp)
                    boxNum = self.boxVals(i, j)[0]
                    self.boxs[boxNum].add(temp)

    # run logical checks in order of difficulty from easiest to hardest repeatedly to solve sudoku puzzle
    def solve(self):
        # only while puzzle is not completed and changes continue to be discovered (will stop if analytical methods stop
        # determining new values
        while self.cmpltnct < self.od**2 and self.updated:
            # update notes in all cells based on row, column, and box notes and identify naked singles.
            # Call function to fill them in
            self.rowcolboxNotes()
            # Identify hidden singles and make them naked and call function to fill them in.
            self.discoverSingles()

        # bifurcate if incomplete. no longer updating notes (not sure how to track through recursion)
        # if self.cmpltnct < self.od**2:
        #     self.bifurcate()

        print(self.evalct)
        print("\nFinal", end=" ")
        self.printGrid()

    # print the values in the main grid, and the nested sets for all rows and columns and boxes
    def printGrid(self):
        print('Grid:')
        for i in range(self.od):
            for j in range(self.od):
                temp = self.grid[i][j]
                if type(temp) == int:
                    print(str(temp), end=' ')
                else:
                    print(' ', end=' ')
            print('')
        '''
        print('Rows:')
        for i in range(self.od):
            print(str(self.rows[i]))

        print('Columns:')
        for j in range(self.od):
            print(str(self.cols[j]))

        print('Boxes:')
        for k in range(self.od):
            print(str(self.boxs[k]))
        '''

    # return the box number, 1-9 (Left to right and top to bottom), and indices of the box bounds for the given position
    # in a 9x9 sudoku grid
    def boxVals(self, i, j):
        imin = 0
        imax = 0
        jmin = 0
        jmax = 0
        if i < 3:
            imax = 3
            if j < 3:
                jmax = 3
                bnum = 0
            elif j < 6:
                jmin = 3
                jmax = 6
                bnum = 1
            else:
                jmin = 6
                jmax = 9
                bnum = 2
        elif i < 6:
            imin = 3
            imax = 6
            if j < 3:
                jmax = 3
                bnum = 3
            elif j < 6:
                jmin = 3
                jmax = 6
                bnum = 4
            else:
                jmin = 6
                jmax = 9
                bnum = 5
        else:
            imin = 6
            imax = 9
            if j < 3:
                jmax = 3
                bnum = 6
            elif j < 6:
                jmin = 3
                jmax = 6
                bnum = 7
            else:
                jmin = 6
                jmax = 9
                bnum = 8

        return [bnum, [imin, imax], [jmin,jmax]]

    # update set of notes in each undetermined cell - only undetermined cells have notes - based on contents of the
    # determined cells it is connected to, those in the same row, column, and box.
    def rowcolboxNotes(self):
        self.updated = False
        for i in range(self.od):
            for j in range(self.od):
                if type(self.grid[i][j]) == set:
                    supSet = self.rows[i].union(self.cols[j], self.boxs[self.boxVals(i, j)[0]])
                    self.grid[i][j] = self.grid[i][j].difference(supSet)
                    # use evalct (evaluation count) to prevent running updateNakedSingle function
                    # until all notes are accurate
                    if self.evalct >= 1:
                        if len(self.grid[i][j]) == 1:
                            self.updateNakedSingle(i, j)
        self.evalct += 1
        # calls itself again when notes have been filled in fully for first time to evaluate for nakedSingles
        if self.evalct == 1:
            self.rowcolboxNotes()

    # fill in a cell that has only 1 number remaining in its notes with that number
    # and update all attributes accordingly
    def updateNakedSingle(self, i, j):
        if self.cmpltnct == self.od**2:
            return
        # print("{} {}".format(i,j))
        if type(self.grid[i][j]) == set and len(self.grid[i][j]) == 1:
            self.cmpltnct += 1
            val = self.grid[i][j].pop()
            self.grid[i][j] = val
            otherNakedSingles = set()
            print('Row: ' + str(i) + ', Col: ' + str(j) + '\nNew Value: ' + str(self.grid[i][j]))
            for x in range(self.od):
                if type(self.grid[x][j]) == set:
                    self.grid[x][j].discard(val)
                    if len(self.grid[x][j]) == 1:
                        otherNakedSingles.add((x,j))
                    # print('Row: ' + str(x) + ', Col: ' + str(j) + '\nNew Notes' + str(self.grid[x][j]))
            for y in range(self.od):
                if type(self.grid[i][y]) == set:
                    self.grid[i][y].discard(val)
                    if len(self.grid[i][y]) == 1:
                        otherNakedSingles.add((i, y))
                    # print('Row: ' + str(i) + ', Col: ' + str(y) + '\nNew Notes' + str(self.grid[i][y]))
            bvals = self.boxVals(i, j)
            for x in range(bvals[1][0], bvals[1][1]):
                for y in range(bvals[2][0], bvals[2][1]):
                    if type(self.grid[x][y]) == set:
                        self.grid[x][y].discard(val)
                        if len(self.grid[x][y]) == 1:
                            otherNakedSingles.add((x, y))
                        # print('Row: ' + str(x) + ', Col: ' + str(y) + '\nNew Notes' + str(self.grid[x][y]))
            self.rows[i].add(val)
            self.cols[j].add(val)
            self.boxs[bvals[0]].add(val)
            self.updated = True
            self.printGrid()
            for NS in otherNakedSingles:
                self.updateNakedSingle(NS[0], NS[1])
            # print("{}\n{}\n{}".format(self.rows[i], self.cols[j], self.boxs[bvals[0]]))
        else:
            return

    # Identify hidden singles and "reveal" them by finding the difference between each cell's notes and the superset of
    # all other cells' notes in its row, column, and box, and seeing if it's exactly 1
    def discoverSingles(self):
        for i in range(self.od):
            for j in range(self.od):
                temp = self.grid[i][j]
                if type(temp) == set:
                    # row difference check
                    rsupSet = set()
                    for x in range(self.od):
                        if x != i and type(self.grid[x][j]) == set:
                            rsupSet.update(self.grid[x][j])
                    diff = temp - rsupSet
                    if len(diff) == 1:
                        self.grid[i][j] = diff
                        print("Single Found: {} in Row: {}, Col: {} from row diff = {} - {}".format(diff, i, j, temp, rsupSet))
                        self.updateNakedSingle(i, j)
                        break

                    # column difference check
                    csupSet = set()
                    for y in range(self.od):
                        if y != j and type(self.grid[i][y]) == set:
                            csupSet.update(self.grid[i][y])
                    diff = temp - csupSet
                    if len(diff) == 1:
                        self.grid[i][j] = diff
                        print("Single Found: {} in Row: {}, Col: {} from column diff = {} - {}".format(diff, i, j, temp, csupSet))
                        self.updateNakedSingle(i, j)
                        break

                    # box difference check
                    bsupSet = set()
                    bvals = self.boxVals(i,j)
                    for x in range(bvals[1][0], bvals[1][1]):
                        for y in range(bvals[2][0], bvals[2][1]):
                            if (x != i or y != j) and type(self.grid[x][y]) == set:
                                bsupSet.update(self.grid[x][y])
                    diff = temp - bsupSet
                    if len(diff) == 1:
                        self.grid[i][j] = diff
                        print("Single Found: {} in Row: {}, Col: {} from box diff = {} - {}".format(diff, i, j, temp, bsupSet))
                        self.updateNakedSingle(i, j)

    # verify grid is valid
    def check(self, cur_idx, temp):


    # solve with recursive guess and check from self.grid with notes
        # idea to use unpacking to pass all grid variables between recursive calls without having to create new grid.
        # This way notes can be passed between grids, updated, and used for checking the validity of the grid. Not currently used.
    def bifurcate(self, prev_idx=False, prev_notes=False, cur_idx=False, next_idx=False):
        # starting from scratch
        if not cur_idx:
            # identify starting empty cell and rerun
            count = 0
            for i in range(self.od):
                for j in range(self.od):
                    if type(self.grid[i][j]) == set:
                        if count == 0:
                            cur_idx = [i, j]
                            count += 1
                        elif count == 1:
                            next_idx = [i, j]
                            break
        # starting from first empty cell
        if not prev_idx:
            # check values in notes until valid
            temp = self.grid[cur_idx[0]][cur_idx[1]].pop()
            while not self.check(cur_idx, temp):
                temp = self.grid[cur_idx[0]][cur_idx[1]].pop()





        self.bifurcate(prev_idx, prev_notes, cur_idx, next_idx)


def main():
    tic = time.perf_counter()

    '''
    # test class and methods without external file
    easyPuz1 = [
        [5, 0, 3, 0, 0, 4, 6, 7, 0],
        [0, 9, 0, 2, 5, 0, 8, 3, 1],
        [0, 0, 2, 6, 0, 3, 0, 0, 9],
        [0, 2, 0, 3, 7, 0, 0, 1, 5],
        [0, 0, 8, 0, 2, 0, 7, 6, 0],
        [3, 0, 0, 5, 6, 0, 0, 0, 0],
        [4, 6, 0, 0, 0, 0, 1, 0, 7],
        [2, 8, 1, 0, 4, 0, 0, 0, 0],
        [0, 0, 5, 0, 9, 0, 0, 8, 0]
    ]
    for i in range(100):
        eP1 = sudoku(easyPuz1)
        #eP1.printGrid()
        #eP1.rowcolboxNotes()
        #eP1.updateNakedSingle(8,0)
        eP1.solve()
    '''

    file = open('sudoku_puzzles.txt', 'r')
    # print(file.readlines())
    grids = []
    lines = []
    for line in file.readlines():
        if line == '\n':
            # SHOULD CHECK IF LIST IS EMPTY FIRST TO HANDLE CASE WHERE MORE THAN ONE EMPTY LINE BETWEEN GRIDS
            grids.append(lines)
            lines=[]
        else:
            line = line.strip('\n').split(' ')
            line = [int(line[i]) for i in range(len(line))]
            lines.append(line)
    grids.append(lines)

    if debug:
        # test file reading
        print('All grids retrieved from text file:\n')
        for grid in grids:
            for row in grid:
                print(row)
            print('')

    for grid in grids:
        Sudoku(grid).solve()

    toc = time.perf_counter()
    elapsed = toc-tic

    print('Time taken: ' + str(elapsed))
    file.close()


main()


'''
emeryEzP2 for second puzzle in sudoku solver
'''