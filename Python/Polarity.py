def solve(board, specs):
	left = specs[0]  			#cols
	right = specs[1]			#cols
	top = specs[2]				#rows
	bottom = specs[3]			#rows
	board = [list(row) for row in board]
	numRows = len(board)
	numCols = len(board[0])
	
	result = dfs(board, specs, 0, 0, numRows, numCols)
	return result

def dfs(board, specs, currentRow, currentCol, numRows, numCols):
	left, right, top, bottom = specs
	
	#print(f"Visiting: row={currentRow}, col={currentCol}")
	if currentRow == numRows:
		#print("Reached end of board:")
		#for row in board:
		#	print(row)
		#print("---")
		if(validateConfiguration(board, specs)):
			print("SOLUTION FOUND!")
			return  [row[:] for row in board]
		else:
			return None
		
	# Move to next row if column finished
	if currentCol == numCols:
		result = dfs(board, specs, currentRow + 1, 0, numRows, numCols)
		return result

	currentTile = board[currentRow][currentCol]

	# if the current tile is "R" or "B" it signals were at the end of the magnet, if "X" skip those tiles
	if currentTile in ("R", "B", "X", "+", "-"):
		result = dfs(board, specs, currentRow, currentCol + 1, numRows, numCols)
		return result

	# See if horizontal magnet can exist
	if horizontalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numCols):
		# Try horizontal magnet in (+, -) orientation
		if(placeable(board, currentRow, currentCol, "+", specs) and placeable(board, currentRow, currentCol + 1, "-", specs)):
			board[currentRow][currentCol] = "+"
			board[currentRow][currentCol + 1] = "-"

			result = dfs(board, specs, currentRow, currentCol + 2, numRows, numCols)
			if(result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "L"
			board[currentRow][currentCol + 1] = "R"

		# Try horizontal magnet in (-, +) orientation
		if(placeable(board, currentRow, currentCol, "-", specs) and placeable(board, currentRow, currentCol + 1, "+", specs)):
			board[currentRow][currentCol] = "-"
			board[currentRow][currentCol + 1] = "+"

			result = dfs(board, specs, currentRow, currentCol + 2, numRows, numCols)
			if(result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "L"
			board[currentRow][currentCol + 1] = "R"

		# Try skipping this magnet slot
		board[currentRow][currentCol] = "X"
		board[currentRow][currentCol + 1] = "X"

		result = dfs(board, specs, currentRow, currentCol + 2, numRows, numCols)
		if(result):
			return result

		# Backtrack
		board[currentRow][currentCol] = "L"
		board[currentRow][currentCol + 1] = "R"

		return None

	# See if vertical magnet can exist
	if verticalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numCols):
		# Try vertical magnet in (+, -) orientation
		if(placeable(board, currentRow, currentCol, "+", specs) and placeable(board, currentRow + 1, currentCol, "-", specs)):
			board[currentRow][currentCol] = "+"
			board[currentRow + 1][currentCol] = "-"

			result = dfs(board, specs, currentRow, currentCol + 1, numRows, numCols)
			if(result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "T"
			board[currentRow + 1][currentCol] = "B"

		# Try vertical magnet in (-, +) orientation
		if(placeable(board, currentRow, currentCol, "-", specs) and placeable(board, currentRow + 1, currentCol, "+", specs)):
			board[currentRow][currentCol] = "-"
			board[currentRow + 1][currentCol] = "+"

			result = dfs(board, specs, currentRow, currentCol + 1, numRows, numCols)
			if(result):
				return result

			# Backtrack
			board[currentRow][currentCol] = "T"
			board[currentRow + 1][currentCol] = "B"

		# Try skipping this magnet slot
		board[currentRow][currentCol] = "X"
		board[currentRow + 1][currentCol] = "X"

		result = dfs(board, specs, currentRow, currentCol + 1, numRows, numCols)
		if(result):
			return result

		# Backtrack
		board[currentRow][currentCol] = "T"
		board[currentRow + 1][currentCol] = "B"

		return None

	# No valid placement found
	return None


def placeable(board, currentRow, currentCol, ch, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numCols = len(board[0])
	
	# Checks if for same charges around the tile
	if(((currentRow - 1 >= 0) and board[currentRow - 1][currentCol] == ch) or 				# checks if the tile above has same charge 
		((currentCol - 1 >= 0) and board[currentRow][currentCol - 1] == ch) or 				# checks if the tile behind has same charge
		((currentCol + 1 < numCols) and board[currentRow][currentCol + 1] == ch) or			# checks if the tile on the right has same charge
		((currentRow + 1 < numRows) and board[currentRow + 1][currentCol] == ch)):			# checks if the tile below has same charge
		return False
	
	numTileInRow = 0	
	numTileInCol = 0

	# counts the number of times the tile to be placed appears in that row, it will iterate through that string's characters
	for currentTile in board[currentRow]:
		if(currentTile == ch):
			numTileInRow += 1

	# counts the number of times the tile to be placed appears in that column, it will iterate all tiles in that column by going down the row and staying at the same column
	for tempRow in range(numRows):
		if(board[tempRow][currentCol] == ch):
			numTileInCol += 1
	
	if(ch == "+"):
		if(left[currentRow] != -1 and numTileInRow >= left[currentRow] ): #if constraint doesn't exist don't place, if number of placed charges exceeds limit don't place
			return False
		if(top[currentCol] != -1 and numTileInCol >= top[currentCol]):
			return False
		
	if(ch == "-"):
		if(right[currentRow] != -1 and numTileInRow >= right[currentRow]): #if constraint doesn't exist don't place, if number of placed charges exceeds limit don't place
			return False
		if(bottom[currentCol] != -1 and numTileInCol >= bottom[currentCol]):
			return False
		
	return True 

def validateConfiguration(board, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numCols = len(board[0])

	# Check left constraints (+ signs in each row)
	for i in range(numRows):
		if left[i] != -1:  # Only check if constraint exists
			positiveCount = 0
			for currentTile in board[i]:
				if(currentTile == "+"):
					positiveCount += 1
			if(left[i] != positiveCount):
				#print(f"FAIL: Row {i} has {positiveCount} '+' but expected {left[i]}")
				return False
			
	# Check right constraints (- signs in each row)
	for i in range(numRows):
		if (right[i] != -1):  # Only check if constraint exists
			negativeCount = 0
			for currentTile in board[i]:
				if(currentTile == "-"):
					negativeCount += 1
			if(right[i] != negativeCount):
				#print(f"FAIL: Row {i} has {negativeCount} '-' but expected {right[i]}")
				return False
			
	for i in range(numCols):
		if (top[i] != -1):
			positiveCount = 0
			for j in range(numRows):
				if (board[j][i] == "+"):
					positiveCount += 1
			if(top[i] != positiveCount):
				#print(f"FAIL: Col {i} has {positiveCount} '+' but expected {top[i]}")
				return False
			
	for i in range(numCols):
		if (bottom[i] != -1):
			negativeCount = 0
			for j in range(numRows):
				if (board[j][i] == "-"):
					negativeCount += 1
			if(bottom[i] != negativeCount):
				#print(f"FAIL: Col {i} has {negativeCount} '-' but expected {bottom[i]}")
				return False

	print("VALIDATION PASSED!")
	return True
	
def horizontalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numCols):
	if((currentCol + 1 < numCols) and currentTile == "L" and board[currentRow][currentCol+1] == "R"):
		return True
	else:
		return False
	
def verticalPlacementExists(currentTile, board, currentRow, currentCol, numRows, numCols):
	if((currentRow + 1 < numRows) and currentTile == "T" and board[currentRow + 1][currentCol] == "B"):
		return True
	else:
		return False
          

def print_board(board, title="Board:"):
    """Helper function to print the board nicely."""
    print(f"\n{title}")
    if board:
        for row in board:
            print(row)
    else:
        print("No solution found")		  

def main():
	"""
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
	print_board(result8, "Solution:")"""

	
	# Test case 9 - 16x16 Board
	print("\n" + "="*60)
	print("TEST CASE 9: 16x16 Board")
	print("="*60)
	specs9 = [
		[-1, -1, -1, 2, 1, 4, 1, 2, 0, 2, -1, 3, 2, -1, -1, 1],
		[0, 0, 3, 2, 1, 2, 3, 2, 0, 1, -1, -1, 2, 1, 1, 1],
		[1, 0, 0, 1, -1, 3, 2, 2, 1, -1, 3, 1, 2, -1, 2, -1],
		[1, -1, -1, 1, 3, 1, 3, 1, 0, 2, -1, 3, 2, 3, 2, 0]
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

	result9 = solve(board9, specs9)
	print_board(result9, "Solution:")
	


if __name__ == "__main__":
    main()




