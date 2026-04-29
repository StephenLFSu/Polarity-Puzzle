import sys
import time
sys.setrecursionlimit(100000)

def solve(board, specs):
	left = specs[0]  			#row
	right = specs[1]			#row
	top = specs[2]				#col
	bottom = specs[3]			#col
	board = [list(row) for row in board]
	numRows = len(board)
	numColumns = len(board[0])
	board = preZeroConstraintCheck(board, specs)
	startTime = time.time()
	lastPrint = [startTime]
	result = dfs(board, specs, 0, 0, numRows, numColumns, startTime, lastPrint)
	return result

def dfs(board, specs, currentRow, currentCol, numRows, numColumns, startTime, lastPrint):
	#print(f"Visiting: row={currentRow}, col={currentCol}")
	"""
	currentTime = time.time()
	if (currentTime - lastPrint[0] >= 30):
		elapsed = currentTime - startTime
		print(f"row={currentRow}, col={currentCol}, elapsed={elapsed:.0f}s")
		print_board(board, "Board state:")
		lastPrint[0] = currentTime"""
	if (currentRow == numRows and currentCol == numColumns):
		#print("Reached end of board:")
		#for row in board:
		#	print(row)
		#print("---")
		if (validateConfiguration(board, specs)):
			print("SOLUTION FOUND!")
			return  [row[:] for row in board]
		else:
			return None

	# Validate columns after all rows are filled
	if (currentRow == numRows):
		#print(f"Validating column {currentCol}")
		if (validateCol(board, currentRow, currentCol, specs)):
			#print(f"Col {currentCol} is VALID, moving to next column")
			result = dfs(board, specs, numRows, currentCol + 1, numRows, numColumns, startTime, lastPrint)
			return result
		else:
			#print(f"Col {currentCol} is INVALID, backtracking")
			#print_board(board, "Current board state:")
			return None

	# Move to next row if column finished
	if (currentCol == numColumns):
		#print(f"Validating row {currentRow}")
		if (validateRow(board, currentRow, currentCol, specs)):
			#print(f"Row {currentRow} is VALID, moving to next row")
			result = dfs(board, specs, currentRow + 1, 0, numRows, numColumns, startTime, lastPrint)
			return result
		else:
			#print(f"Row {currentRow} is INVALID, backtracking")
			#print_board(board, "Current board state:")
			return None

	currentTile = board[currentRow][currentCol]

	# if the current tile is "R" or "B" it signals were at the end of the magnet, if "X" skip those tiles
	if currentTile in ("R", "B", "X", "+", "-"):
		result = dfs(board, specs, currentRow, currentCol + 1, numRows, numColumns, startTime, lastPrint)
		return result

	# See if horizontal magnet can exist
	if (horizontalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numColumns)):
		# Try horizontal magnet in (+, -) orientation
		if (placeable(board, currentRow, currentCol, "+", specs) and placeable(board, currentRow, currentCol + 1, "-", specs)):
			board[currentRow][currentCol] = "+"
			board[currentRow][currentCol + 1] = "-"
			result = dfs(board, specs, currentRow, currentCol + 2, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "L"
			board[currentRow][currentCol + 1] = "R"

		# Try horizontal magnet in (-, +) orientation
		if (placeable(board, currentRow, currentCol, "-", specs) and placeable(board, currentRow, currentCol + 1, "+", specs)):
			board[currentRow][currentCol] = "-"
			board[currentRow][currentCol + 1] = "+"
			result = dfs(board, specs, currentRow, currentCol + 2, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "L"
			board[currentRow][currentCol + 1] = "R"

		# Try skipping this magnet slot
		board[currentRow][currentCol] = "X"
		board[currentRow][currentCol + 1] = "X"
		result = dfs(board, specs, currentRow, currentCol + 2, numRows, numColumns, startTime, lastPrint)
		if (result):
			return result

		# Backtrack
		board[currentRow][currentCol] = "L"
		board[currentRow][currentCol + 1] = "R"

		return None

	# See if vertical magnet can exist
	if (verticalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numColumns)):
		# Try vertical magnet in (+, -) orientation
		if (placeable(board, currentRow, currentCol, "+", specs) and placeable(board, currentRow + 1, currentCol, "-", specs)):
			board[currentRow][currentCol] = "+"
			board[currentRow + 1][currentCol] = "-"
			result = dfs(board, specs, currentRow, currentCol + 1, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "T"
			board[currentRow + 1][currentCol] = "B"

		# Try vertical magnet in (-, +) orientation
		if (placeable(board, currentRow, currentCol, "-", specs) and placeable(board, currentRow + 1, currentCol, "+", specs)):
			board[currentRow][currentCol] = "-"
			board[currentRow + 1][currentCol] = "+"
			result = dfs(board, specs, currentRow, currentCol + 1, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "T"
			board[currentRow + 1][currentCol] = "B"

		# Try skipping this magnet slot
		board[currentRow][currentCol] = "X"
		board[currentRow + 1][currentCol] = "X"
		result = dfs(board, specs, currentRow, currentCol + 1, numRows, numColumns, startTime, lastPrint)
		if (result):
			return result

		# Backtrack
		board[currentRow][currentCol] = "T"
		board[currentRow + 1][currentCol] = "B"

		return None

	# No valid placement found
	return None


def placeable(board, currentRow, currentCol, ch, specs): #ch is either + or - 
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])

	#Zero Constraint Check
	if (ch == "+" and left[currentRow] == 0):
		return False
	if (ch == "-" and right[currentRow] == 0):
		return False
	if (ch == "+" and top[currentCol] == 0):
		return False
	if (ch == "-" and bottom[currentCol] == 0):
		return False
	
	# Checks if for same charges around the tile
	if (((currentRow - 1 >= 0) and board[currentRow - 1][currentCol] == ch) or 				# checks if the tile above has same charge 
		((currentCol - 1 >= 0) and board[currentRow][currentCol - 1] == ch) or 				# checks if the tile behind has same charge
		((currentCol + 1 < numColumns) and board[currentRow][currentCol + 1] == ch) or			# checks if the tile on the right has same charge
		((currentRow + 1 < numRows) and board[currentRow + 1][currentCol] == ch)):			# checks if the tile below has same charge
		return False
	
	numChargeInRow = 0	
	numChargeInCol = 0

	# counts the number of times the tile to be placed appears in that row, it will iterate through that string's characters
	for currentTile in board[currentRow]:
		if (currentTile == ch):
			numChargeInRow += 1

	# counts the number of times the tile to be placed appears in that column, it will iterate all tiles in that column by going down the row and staying at the same column
	for tempRow in range(numRows):
		if (board[tempRow][currentCol] == ch):
			numChargeInCol += 1
	
	#When a constraint exits and were over the limit don't place
	if (ch == "+"):
		if(left[currentRow] != -1 and numChargeInRow >= left[currentRow]): 
			return False
		if(top[currentCol] != -1 and numChargeInCol >= top[currentCol]):
			return False
	
	#When a constraint exits and were over the limit don't place
	if (ch == "-"):
		if(right[currentRow] != -1 and numChargeInRow >= right[currentRow]): 
			return False
		if(bottom[currentCol] != -1 and numChargeInCol >= bottom[currentCol]):
			return False
		
	#Constraint can still be fulfilled in the row
	return True 

def forwardCheck(board, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])
	
	#Row Constraints Left & Right 
	for row in range(numRows):
		numPlacedPositiveInRow = 0
		numPlacedNegativeInRow = 0
		numPossiblePositiveInRow = 0
		numPossibleNegativeInRow = 0 
		column = 0
		while (column < numColumns):
			tile = board[row][column]
			if (tile == "+"):
				numPlacedPositiveInRow += 1
				column += 1
			elif (tile == '-'):
				numPlacedNegativeInRow += 1
				column += 1
			elif (tile == "L" and column + 1 < numColumns and board[row][column+1] == "R"):
				numPossiblePositiveInRow += 1
				numPossibleNegativeInRow += 1
				column += 2
			elif (tile == "T" and row + 1 < numRows and board[row+1][column] == "B"):
				numPossiblePositiveInRow += 1
				numPossibleNegativeInRow += 1
				column += 1
			elif (tile == "B" and row - 1 >= 0 and board[row-1][column] == "T"):
				numPossiblePositiveInRow += 1
				numPossibleNegativeInRow += 1
				column += 1
			else:
				column += 1
		#If the constraint exists & can't be statisfed (total < constraint limit)
		if (left[row] != -1 and (numPlacedPositiveInRow + numPossiblePositiveInRow) < left[row]): 
			#print(f"Row {row} failed left: placed={numPlacedPositiveInRow} possible={numPossiblePositiveInRow} constraint={left[row]}")
			return False
		#If the constraint exists & can't be statisfed (total < constraint limit)
		if (right[row] != -1 and (numPlacedNegativeInRow + numPossibleNegativeInRow) < right[row]):
			#print(f"Row {row} failed right: placed={numPlacedNegativeInRow} possible={numPossibleNegativeInRow} constraint={right[row]}")
			return False
		
	#Column Constraints Top & Bottom
	for column in range(numColumns):
		numPlacedPositiveInColumn = 0
		numPlacedNegativeInColumn = 0
		numPossiblePositiveInColumn = 0
		numPossibleNegativeInColumn = 0 
		row = 0
		while (row < numRows):
			tile = board[row][column]
			if (tile == "+"):
				numPlacedPositiveInColumn += 1
				row += 1
			elif (tile == '-'):
				numPlacedNegativeInColumn += 1
				row += 1
			elif (tile == "T" and row + 1 < numRows and board[row+1][column] == "B"):
				numPossiblePositiveInColumn += 1
				numPossibleNegativeInColumn += 1
				row += 2
			elif (tile == "L" and column + 1 < numColumns and board[row][column+1] == "R"):
				numPossiblePositiveInColumn += 1
				numPossibleNegativeInColumn += 1
				row += 1
			elif (tile == "R" and column > 0 and board[row][column-1] == "L"):
				numPossiblePositiveInColumn += 1
				numPossibleNegativeInColumn += 1
				row += 1
			else:
				row += 1
		#If the constraint exists & can't be statisfed (total < constraint limit) explore using > 0 instead of -1 if trouble still exist later
		if (top[column] != -1 and (numPlacedPositiveInColumn + numPossiblePositiveInColumn) < top[column]):
			#print(f"Column {column} failed top: placed={numPlacedNegativeInColumn} possible={numPossiblePositiveInColumn} constraint={bottom[column]}")
			return False
		#If the constraint exists & can't be statisfed (total < constraint limit)
		if (bottom[column] != -1 and (numPlacedNegativeInColumn + numPossibleNegativeInColumn) < bottom[column]):
			#print(f"Column {column} failed bottom: placed={numPlacedNegativeInColumn} possible={numPossiblePositiveInColumn} constraint={bottom[column]}")
			return False
		
	return True


def validateRow(board, currentRow, currentCol, specs):
	left, right, top, bottom = specs
	positiveRowCount = 0
	negativeRowCount = 0

	#Count # of times + or - in row
	for currentTile in board[currentRow]:
		if (currentTile == "+"):
			positiveRowCount += 1
		if (currentTile == "-"):
			negativeRowCount += 1

	#No constraint limits = -1 and constraints are met when the counts are the same, constraints can either exist in a realm of numbers either -1 or >= 0
	positiveMet = (positiveRowCount == left[currentRow] or left[currentRow] == -1)
	negativeMet = (negativeRowCount == right[currentRow] or right[currentRow] == -1)
		
	return (positiveMet and negativeMet)


def validateCol(board, currentRow, currentCol, specs):
	left, right, top, bottom = specs
	positiveRowCount = 0
	negativeRowCount = 0
	numRows = len(board)
	numColumns = len(board[0])

	#Count # of times + or - in column
	for currentRowIndex in range(numRows):
		if (board[currentRowIndex][currentCol] ==  "+"):
			positiveRowCount += 1
		if (board[currentRowIndex][currentCol] ==  "-"):
			negativeRowCount += 1	

	#No constraint limits = -1 and constraints are met when the counts are the same, constraints can either exist in a realm of numbers either -1 or >= 0
	positiveMet = (positiveRowCount == top[currentCol] or top[currentCol] == -1)
	negativeMet = (negativeRowCount == bottom[currentCol] or bottom[currentCol] == -1)

	return (positiveMet and negativeMet)


def horizontalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numColumns):
	if ((currentCol + 1 < numColumns) and currentTile == "L" and board[currentRow][currentCol+1] == "R"):
		return True
	else:
		return False
	
def verticalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numColumns):
	if ((currentRow + 1 < numRows) and currentTile == "T" and board[currentRow + 1][currentCol] == "B"):
		return True
	else:
		return False
	

def preZeroConstraintCheck(board, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])

	for currentRow in range(numRows):
		if (left[currentRow] == 0 and right[currentRow] == 0):
			board[currentRow] = ["X"] * numColumns

	for currentCol in range(numColumns):
		if (top[currentCol] == 0 and bottom[currentCol] == 0):
			for currentRow in range(numRows):
				board[currentRow][currentCol] = "X"
		
	return board


def validateConfiguration(board, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])

	# Row Constraint Check
	for rowIndex in range(numRows):  
		positiveCount = 0
		negativeCount = 0
		# Both Left & Right constraint
		if ((left[rowIndex] != -1) and (right[rowIndex] != -1)): 
			#Count the instances
			for currentTile in board[rowIndex]:
				if(currentTile == "+"):
					positiveCount += 1
				if (currentTile == "-"):
					negativeCount += 1
			#Positive constraints don't match up
			if (left[rowIndex] != positiveCount):
				#print(f"FAIL: Row {rowIndex} has {positiveCount} '+' but expected {left[rowIndex]} & {negativeCount} '-' expected {right[rowIndex]}")
				return False
			if (right[rowIndex] != negativeCount):
				#print(f"FAIL: Row {rowIndex} has {negativeCount} '-' but expected {right[rowIndex]} & {positiveCount} '+' expected {left[rowIndex]}")
				return False
		# Left constraint & no Right constraint
		elif (left[rowIndex] != -1):  
			#Count the instances
			for currentTile in board[rowIndex]:
				if(currentTile == "+"):
					positiveCount += 1
			if(left[rowIndex] != positiveCount):
				#print(f"FAIL: Row {rowIndex} has {positiveCount} '+' but expected {left[rowIndex]}")
				return False
		# Right constraint & no Left constraint
		elif (right[rowIndex] != -1):  
			#Count the instances
			for currentTile in board[rowIndex]:
				if(currentTile == "-"):
					negativeCount += 1
			if(right[rowIndex] != negativeCount):
				#print(f"FAIL: Row {rowIndex} has {negativeCount} '-' but expected {right[rowIndex]}")
				return False 
			
	#Column Constraint
	for columnIndex in range(numColumns):
		positiveCount = 0
		negativeCount = 0
		# Both Top & Bottom constraint 
		if (top[columnIndex] != -1) and (bottom[columnIndex] != -1):
			#Count the instances
			for rowIndex in range(numRows):
				if (board[rowIndex][columnIndex] == "+"):
					positiveCount += 1
				if (board[rowIndex][columnIndex] == "-"):
					negativeCount += 1
			#Checking if constraints match up
			if (top[columnIndex] != positiveCount):
				return False
			if (bottom[columnIndex] != negativeCount):
				#print(f"FAIL: Col {columnIndex} has {positiveCount} '+' but expected {top[columnIndex]}")
				return False
		# Top constraint & no Bottom constraint
		elif (top[columnIndex] != -1):
			#Count the instances
			for rowIndex in range(numRows):
				if (board[rowIndex][columnIndex] == "+"):
					positiveCount += 1
			if (top[columnIndex] != positiveCount):
				#print(f"FAIL: Col {i} has {positiveCount} '+' but expected {top[i]}")
				return False
		# Bottom constraint & no Top constraint
		elif (bottom[columnIndex] != -1):
			#Count the instances
			for rowIndex in range(numRows):
				if (board[rowIndex][columnIndex] == "-"):
					negativeCount += 1
			if (bottom[columnIndex] != negativeCount):
				#print(f"FAIL: Col {i} has {negativeCount} '-' but expected {bottom[i]}")
				return False

	#print("VALIDATION PASSED!")
	return True         


def print_board(board, title="Board:"):
    """Helper function to print the board nicely."""
    print(f"\n{title}")
    if board:
        for row in board:
            print(''.join(row))
    else:
        print("No solution found")		  

def main():

	# Simple test case - 2x2 board
	print("="*60)
	print("SIMPLE TEST: 2x2 Board")
	print("="*60)
	specs1 = [
		[1, 1],      # left: + per row (row 0 needs 1 +, row 1 needs 1 +)
		[1, 1],      # right: - per row (row 0 needs 1 -, row 1 needs 1 -)
		[1, 1],      # top: + per column (col 0 needs 1 +, col 1 needs 1 +)
		[1, 1]       # bottom: - per column (col 0 needs 1 -, col 1 needs 1 -)
	]
	board1 = ["LR", "LR"]  # Two horizontal magnets

	result1 = solve(board1, specs1)
	print_board(result1, "Solution:")

	# Test case 2 - 2x2 Board (vertical magnet)
	print("\n" + "="*60)
	print("TEST CASE 2: 2x2 Board (Vertical)")
	print("="*60)
	specs2 = [
		[1, 1],      # left: + per row
		[1, 1],      # right: - per row
		[1, 1],      # top: + per column
		[1, 1]       # bottom: - per column
	]
	board2 = ["TT", "BB"]

	result2 = solve(board2, specs2)
	print_board(result2, "Solution:")

	# Test case 3 - 2x2 Board (horizontal, variant)
	print("\n" + "="*60)
	print("TEST CASE 3: 2x2 Board (Horizontal Variant)")
	print("="*60)
	specs3 = [
		[1, -1],     # left: + per row
		[1, -1],     # right: - per row
		[1, -1],     # top: + per column
		[-1, 1]      # bottom: - per column
	]
	board3 = ["LR", "LR"]

	result3 = solve(board3, specs3)
	print_board(result3, "Solution:")

	# Test case 4 - 4x4 Board (with 0 constraints)
	print("\n" + "="*60)
	print("TEST CASE 4: 4x4 Board (with 0 constraints)")
	print("="*60)
	specs4 = [
		[0, 1, 2, -1],   # left: + per row
		[0, -1, 1, 2],   # right: - per row
		[1, 1, -1, 1],   # top: + per column
		[1, 1, 0, 2]     # bottom: - per column
	]
	board4 = ["TTLR", "BBLR", "LRTT", "LRBB"]

	result4 = solve(board4, specs4)
	print_board(result4, "Solution:")

	# Test case 5 - 4x4 Board (variant)
	print("\n" + "="*60)
	print("TEST CASE 5: 4x4 Board (Variant)")
	print("="*60)
	specs5 = [
		[1, 2, -1, -1],  # left: + per row
		[-1, 2, -1, 2],  # right: - per row
		[2, -1, 0, 2],   # top: + per column
		[2, -1, 2, 2]    # bottom: - per column
	]
	board5 = ["TLRT", "BLRB", "TLRT", "BLRB"]

	result5= solve(board5, specs5)
	print_board(result5, "Solution:")

	# Test case 6 - 5x6 Board
	print("\n" + "="*60)
	print("TEST CASE 6: 5x6 Board")
	print("="*60)
	specs6 = [
		[2, 3, -1, -1, -1],
		[-1, -1, -1, 1, -1],
		[1, -1, -1, 2, 1, -1],
		[2, -1, -1, 2, -1, 3]
	]
	board6 = ["LRLRTT", "LRLRBB", "TTTTLR", "BBBBTT", "LRLRBB"]

	result6 = solve(board6, specs6)
	print_board(result6, "Solution:")
	
	# Test case 7 - 8x8 Board
	print("\n" + "="*60)
	print("TEST CASE 7: 8x8 Board")
	print("="*60)
	specs7 = [
		[-1, -1, 2, 2, 4, -1, 3, 2],
		[-1, 1, -1, 3, 3, -1, -1, 4],
		[0, 4, 3, 3, -1, 3, -1, 1],
		[2, 2, 3, 3, 2, -1, 1, 3]
	]
	board7 = [
		'LRTTLRTT',
		'LRBBLRBB',
		'TTLRTTLR',
		'BBLRBBLR',
		'LRTTLRTT',
		'LRBBLRBB',
		'TTLRTTLR',
		'BBLRBBLR'
	]

	result7 = solve(board7, specs7)
	print_board(result7, "Solution:")
	
	# Test case 8 - 8x8 Board
	print("\n" + "="*60)
	print("TEST CASE 8: 8x8 Board")
	print("="*60)
	specs8 = [
		[-1, 2, 2, 2, 2, 2, 2, 0],
		[1, 1, 1, -1, 3, 3, -1, -1],
		[1, 0, 2, 3, 2, -1, 2, 2],
		[0, 2, 1, 3, 2, 2, 1, -1]
	]
	board8 = [
		'LRLRLRLR',
		'LRLRTLRT',
		'TTTTBTTB',
		'BBBBTBBT',
		'LRLRBTTB',
		'TLRTTBBT',
		'BLRBBLRB',
		'LRLRLRLR'
	]

	result8 = solve(board8, specs8)
	print_board(result8, "Solution:")

	
	# Test case 9 - 16x16 Board
	print("\n" + "="*60)
	print("TEST CASE 9: 16x16 Board")
	print("="*60)
	specs9 = [
		[-1, -1, -1, 2, 1, 4, 1, 2, 0, 2, -1, 3, 2, -1, -1, 1], #Row
		[0, 0, 3, 2, 1, 2, 3, 2, 0, 1, -1, -1, 2, 1, 1, 1],		#Row
		[1, 0, 0, 1, -1, 3, 2, 2, 1, -1, 3, 1, 2, -1, 2, -1],	#Col
		[1, -1, -1, 1, 3, 1, 3, 1, 0, 2, -1, 3, 2, 3, 2, 0]		#Col
	]
	board9 = [
		'LRLRTTTTTTTTLRLR',
		'LRLRBBBBBBBBLRLR',
		'LRTTTTLRTTLRLRTT',
		'LRBBBBLRBBLRLRBB',
		'LRLRLRLRLRLRLRLR',
		'TLRTTLRTTLRTTLRT',
		'BLRBBLRBBLRBBLRB',
		'TTLRLRLRTTLRTTLR',
		'BBLRLRLRBBLRBBLR',
		'TTLRTLRTLRTTTTLR',
		'BBLRBLRBLRBBBBLR',
		'LRLRLRLRLRLRLRLR',
		'LRLRTTLRLRLRTTTT',
		'LRLRBBLRLRLRBBBB',
		'TLRTTTTTTLRTTTTT',
		'BLRBBBBBBLRBBBBB'
	]

	#left, right, top, bottom = specs9
	#board9 = [list(row) for row in board9]
	#numRows = len(board9)
	#numColumns = len(board9[0])
	#for currentRow in range(numRows):
		#board9[currentRow] = ["X" if left[currentRow] == 0 or right[currentRow] == 0 else i for i in board9[currentRow]]

	#for currentCol in range(numColumns):
		#if(top[currentCol] == 0 or bottom[currentCol] == 0):
			#for currentRow in range(numRows):
				#board9[currentRow][currentCol] = "X"

	#print_board(board9, "chickenwong")
	result9 = solve(board9, specs9)
	print_board(result9, "Solution:")


if __name__ == "__main__":
    main()


"""
	# Checks if charges around first charge is the same
	if (((firstRow - 1 >= 0) and board[firstRow - 1][firstColumn] == firstCharge) or 					# checks if the tile above has same charge
		((firstColumn - 1 >= 0 ) and board[firstRow][firstColumn - 1 ] == firstCharge) or				# checks if the tile behind has same charge
		((firstColumn + 1 < numColumns) and board[firstRow][firstColumn + 1] == firstCharge) or			# checks if the tile on the right has same charge
		((firstRow + 1 < numRows) and board[firstRow + 1][firstColumn] == firstCharge)):				# checks if the tile below has same charge
		return False

	# Checks if charges around second charge is the same
	if (((secondRow - 1 >= 0) and board[secondRow - 1][secondColumn] == secondCharge) or 				# checks if the tile above has same charge
		((secondColumn - 1 >= 0 ) and board[secondRow][secondColumn - 1 ] == secondCharge) or			# checks if the tile behind has same charge
		((secondColumn + 1 < numColumns) and board[secondRow][secondColumn + 1] == secondCharge) or		# checks if the tile on the right has same charge
		((secondRow + 1 < numRows) and board[secondRow + 1][secondColumn] == secondCharge)):			# checks if the tile below has same charge
		return False
"""
