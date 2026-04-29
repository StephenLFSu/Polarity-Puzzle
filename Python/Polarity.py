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
	#Tile trackers
	rowPositives = [0] * numRows								#(+)
	rowNegatives = [0] * numRows								#(-)
	columnPositives = [0] * numColumns							#(+)
	columnNegatives = [0] * numColumns							#(-)
	rowRemainingHorizontalPositives = [0] * numRows				#(L, R)
	rowRemainingHorizontalNegatives = [0] * numRows				#(L, R)	
	rowRemainingVerticalPositives = [0] * numRows				#(T, B)
	rowRemainingVerticalNegatives = [0] * numRows				#(T, B)
	columnRemainingVerticalPositives = [0] * numColumns			#(T, B)
	columnRemainingVerticalNegatives = [0] * numColumns 		#(T, B)
	columnRemainingHorizontalPositives = [0] * numColumns 		#(L, R)	
	columnRemainingHorizontalNegatives = [0] * numColumns		#(L, R)	
	rowNumX = [0] * numRows										#(X, X)				
	columnNumX = [0] * numColumns								#(X. X)
	for currentRow in range(numRows):
		for currentColumn in range(numColumns):
			currentTile = board[currentRow][currentColumn]
			#Positive charge
			if(currentTile == "+"):
				rowPositives[currentRow] += 1
				columnPositives[currentColumn] += 1
			#Negative charge
			elif(currentTile == "-"):
				rowNegatives[currentRow] += 1
				columnNegatives[currentColumn] +=1
			#Horizontal placement, columns differ rows same
			elif((currentTile == "L") and (currentColumn + 1 < numColumns) and (board[currentRow][currentColumn + 1] == "R")):
				#Dealing with 2 tiles at once since merged 4 functions can't rely on doing 1 by 1
				rowRemainingHorizontalPositives[currentRow]	+= 1				#(L, R)
				rowRemainingHorizontalNegatives[currentRow]	+= 1				#(L, R)
				columnRemainingHorizontalPositives[currentColumn] += 1			#(L, R)	
				columnRemainingHorizontalNegatives[currentColumn] += 1			#(L, R)	
				columnRemainingHorizontalPositives[currentColumn + 1] += 1		#(L, R)	
				columnRemainingHorizontalNegatives[currentColumn + 1] += 1		#(L, R)	
			#Vertical placement, rows differ columns same
			elif((currentTile == "T") and (currentRow + 1 < numRows) and (board[currentRow + 1][currentColumn] == "B")):
				#Dealing with 2 tiles at once since merged 4 functions can't rely on doing 1 by 1
				columnRemainingVerticalPositives[currentColumn] += 1			#(T, B)
				columnRemainingVerticalNegatives[currentColumn] += 1			#(T, B)
				rowRemainingVerticalPositives[currentRow] += 1					#(T, B)
				rowRemainingVerticalNegatives[currentRow] += 1					#(T, B)
				rowRemainingVerticalPositives[currentRow + 1] += 1				#(T, B)
				rowRemainingVerticalNegatives[currentRow + 1] += 1				#(T, B)
			#X
			elif(currentTile == "X"):
				rowNumX[currentRow] += 1
				columnNumX[currentColumn] += 1

	result = dfs(board, specs, 0, 0, numRows, numColumns, startTime, lastPrint)
	return result

def dfs(board, specs, currentRow, currentColumn, numRows, numColumns, startTime, lastPrint):
	
	if (currentRow == numRows and currentColumn == numColumns):
		if (validateConfiguration(board, specs)):
			print("SOLUTION FOUND!")
			return  [row[:] for row in board]
		else:
			return None

	# Validate columns after all rows are filled
	if (currentRow == numRows):
		#print(f"Validating column {currentColumn}")
		if (validateColumn(board, currentRow, currentColumn, specs)):
			#print(f"Col {currentColumn} is VALID, moving to next column")
			result = dfs(board, specs, numRows, currentColumn + 1, numRows, numColumns, startTime, lastPrint)
			return result
		else:
			#print(f"Col {currentColumn} is INVALID, backtracking")
			#print_board(board, "Current board state:")
			return None

	# Move to next row if column finished
	if (currentColumn == numColumns):
		#print(f"Validating row {currentRow}")
		if (validateRow(board, currentRow, currentColumn, specs)):
			#print(f"Row {currentRow} is VALID, moving to next row")
			result = dfs(board, specs, currentRow + 1, 0, numRows, numColumns, startTime, lastPrint)
			return result
		else:
			#print(f"Row {currentRow} is INVALID, backtracking")
			#print_board(board, "Current board state:")
			return None

	currentTile = board[currentRow][currentColumn]

	# if the current tile is "R" or "B" it signals were at the end of the magnet, if "X" skip those tiles
	if currentTile in ("R", "B", "X", "+", "-"):
		result = dfs(board, specs, currentRow, currentColumn + 1, numRows, numColumns, startTime, lastPrint)
		return result

	# See if horizontal magnet can exist, columns differ rows are same
	if (horizontalPlacementExists(currentTile, board, currentRow, currentColumn, numRows, numColumns)):
		originalFirstCharge = board[currentRow][currentColumn]
		originalSecondCharge = board[currentRow][currentColumn + 1]
		numPositivesFirstRow, numNegativesFirstRow = rowChargeCount(board, currentRow)
		numPositivesFirstColumn, numNegativesFirstColumn = columnChargeCount(board, numRows, currentColumn)
		numPositivesSecondColumn, numNegativesSecondColumn = columnChargeCount(board, numRows, currentColumn + 1)
		firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives = remainingInRow(board, currentRow, numColumns)
		firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives = remainingInColumn(board, currentColumn, numRows)
		secondColumnRemainingVerticalPositives, secondColumnRemainingVerticalNegatives, secondColumnRemainingHorizontalPositives, secondColumnRemainingHorizontalNegatives = remainingInColumn(board, currentColumn + 1, numRows)
		# Try horizontal magnet in (+, -) orientation
		if placeable(board, currentRow, currentColumn, currentRow, currentColumn + 1, "+", "-", specs, numPositivesFirstRow, numNegativesFirstRow, 0, 0, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn):
			board[currentRow][currentColumn] = "+"
			board[currentRow][currentColumn + 1] = "-"
			numPositivesFirstRow += 1
			numNegativesFirstRow += 1
			numPositivesFirstColumn += 1
			numNegativesSecondColumn += 1
			firstRowRemainingHorizontalPositives -= 1
			firstRowRemainingHorizontalNegatives -= 1
			firstColumnRemainingHorizontalPositives -= 1
			firstColumnRemainingHorizontalNegatives -= 1
			secondColumnRemainingHorizontalPositives -= 1
			secondColumnRemainingHorizontalNegatives -= 1
			if(forwardCheck(currentRow, currentColumn, currentRow, currentColumn + 1, specs, numPositivesFirstRow, numNegativesFirstRow, 0, 0, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, 0, 0, 0, 0, secondColumnRemainingVerticalPositives, secondColumnRemainingVerticalNegatives, secondColumnRemainingHorizontalPositives, secondColumnRemainingHorizontalNegatives)):
				result = dfs(board, specs, currentRow, currentColumn + 2, numRows, numColumns, startTime, lastPrint)
				if (result):
					return result

			# Backtrack
			board[currentRow][currentColumn] = originalFirstCharge
			board[currentRow][currentColumn + 1] = originalSecondCharge
			numPositivesFirstRow -= 1
			numNegativesFirstRow -= 1
			numPositivesFirstColumn -= 1
			numNegativesSecondColumn -= 1
			firstRowRemainingHorizontalPositives += 1
			firstRowRemainingHorizontalNegatives += 1
			firstColumnRemainingHorizontalPositives += 1
			firstColumnRemainingHorizontalNegatives += 1
			secondColumnRemainingHorizontalPositives += 1
			secondColumnRemainingHorizontalNegatives += 1

		# Try horizontal magnet in (-, +) orientation
		if placeable(board, currentRow, currentColumn, currentRow, currentColumn + 1, "-", "+", specs, numPositivesFirstRow, numNegativesFirstRow, 0, 0, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn):
			board[currentRow][currentColumn] = "-"
			board[currentRow][currentColumn + 1] = "+"
			numPositivesFirstRow += 1
			numNegativesFirstRow += 1
			numNegativesFirstColumn += 1
			numPositivesSecondColumn += 1
			firstRowRemainingHorizontalPositives -= 1
			firstRowRemainingHorizontalNegatives -= 1
			firstColumnRemainingHorizontalPositives -= 1
			firstColumnRemainingHorizontalNegatives -= 1
			secondColumnRemainingHorizontalPositives -= 1
			secondColumnRemainingHorizontalNegatives -= 1
			if(forwardCheck(currentRow, currentColumn, currentRow, currentColumn + 1, specs, numPositivesFirstRow, numNegativesFirstRow, 0, 0, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, 0, 0, 0, 0, secondColumnRemainingVerticalPositives, secondColumnRemainingVerticalNegatives, secondColumnRemainingHorizontalPositives, secondColumnRemainingHorizontalNegatives)):
				result = dfs(board, specs, currentRow, currentColumn + 2, numRows, numColumns, startTime, lastPrint)
				if (result):
					return result

			# Backtrack
			board[currentRow][currentColumn] = originalFirstCharge
			board[currentRow][currentColumn + 1] = originalSecondCharge
			numPositivesFirstRow -= 1
			numNegativesFirstRow -= 1
			numNegativesFirstColumn -= 1
			numPositivesSecondColumn -= 1
			firstRowRemainingHorizontalPositives += 1
			firstRowRemainingHorizontalNegatives += 1
			firstColumnRemainingHorizontalPositives += 1
			firstColumnRemainingHorizontalNegatives += 1
			secondColumnRemainingHorizontalPositives += 1
			secondColumnRemainingHorizontalNegatives += 1

		# Try skipping this magnet slot
		board[currentRow][currentColumn] = "X"
		board[currentRow][currentColumn + 1] = "X"
		firstRowRemainingHorizontalPositives -= 1
		firstRowRemainingHorizontalNegatives -= 1
		firstColumnRemainingHorizontalPositives -= 1
		firstColumnRemainingHorizontalNegatives -= 1
		secondColumnRemainingHorizontalPositives -= 1
		secondColumnRemainingHorizontalNegatives -= 1
		if(forwardCheck(currentRow, currentColumn, currentRow, currentColumn + 1, specs, numPositivesFirstRow, numNegativesFirstRow, 0, 0, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, 0, 0, 0, 0, secondColumnRemainingVerticalPositives, secondColumnRemainingVerticalNegatives, secondColumnRemainingHorizontalPositives, secondColumnRemainingHorizontalNegatives)):
			result = dfs(board, specs, currentRow, currentColumn + 2, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

		# Backtrack
		board[currentRow][currentColumn] = originalFirstCharge
		board[currentRow][currentColumn + 1] = originalSecondCharge
		firstRowRemainingHorizontalPositives += 1
		firstRowRemainingHorizontalNegatives += 1
		firstColumnRemainingHorizontalPositives += 1
		firstColumnRemainingHorizontalNegatives += 1
		secondColumnRemainingHorizontalPositives += 1
		secondColumnRemainingHorizontalNegatives += 1

		return None

	# See if vertical magnet can exist, rows differ columns are same
	if (verticalPlacementExists(currentTile, board, currentRow, currentColumn, numRows, numColumns)):
		originalFirstCharge = board[currentRow][currentColumn]
		originalSecondCharge = board[currentRow + 1][currentColumn]
		numPositivesFirstRow, numNegativesFirstRow = rowChargeCount(board, currentRow)
		numPositivesSecondRow, numNegativesSecondRow = rowChargeCount(board, currentRow + 1)
		numPositivesFirstColumn, numNegativesFirstColumn = columnChargeCount(board, numRows, currentColumn)
		firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives = remainingInRow(board, currentRow, numColumns)
		secondRowRemainingHorizontalPositives, secondRowRemainingHorizontalNegatives, secondRowRemainingVerticalPositives, secondRowRemainingVerticalNegatives = remainingInRow(board, currentRow + 1, numColumns)
		firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives = remainingInColumn(board, currentColumn, numRows)
		# Try vertical magnet in (+, -) orientation
		if placeable(board, currentRow, currentColumn, currentRow + 1, currentColumn, "+", "-", specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, 0, 0):
			board[currentRow][currentColumn] = "+"
			board[currentRow + 1][currentColumn] = "-"
			numPositivesFirstRow += 1
			numNegativesSecondRow += 1
			numPositivesFirstColumn += 1
			numNegativesFirstColumn += 1
			firstRowRemainingVerticalPositives -= 1
			firstRowRemainingVerticalNegatives -= 1
			secondRowRemainingVerticalPositives -= 1
			secondRowRemainingVerticalNegatives -= 1
			firstColumnRemainingVerticalPositives -= 1
			firstColumnRemainingVerticalNegatives -= 1
			if(forwardCheck(currentRow, currentColumn, currentRow + 1, currentColumn, specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, 0, 0, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, secondRowRemainingHorizontalPositives, secondRowRemainingHorizontalNegatives, secondRowRemainingVerticalPositives, secondRowRemainingVerticalNegatives, 0, 0, 0, 0)):
				result = dfs(board, specs, currentRow, currentColumn + 1, numRows, numColumns, startTime, lastPrint)
				if (result):
					return result

			# Backtrack
			board[currentRow][currentColumn] = originalFirstCharge
			board[currentRow + 1][currentColumn] = originalSecondCharge
			numPositivesFirstRow -= 1
			numNegativesSecondRow -= 1
			numPositivesFirstColumn -= 1
			numNegativesFirstColumn -= 1
			firstRowRemainingVerticalPositives += 1
			firstRowRemainingVerticalNegatives += 1
			secondRowRemainingVerticalPositives += 1
			secondRowRemainingVerticalNegatives += 1
			firstColumnRemainingVerticalPositives += 1
			firstColumnRemainingVerticalNegatives += 1

		# Try vertical magnet in (-, +) orientation
		if placeable(board, currentRow, currentColumn, currentRow + 1, currentColumn, "-", "+", specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, 0, 0):
			board[currentRow][currentColumn] = "-"
			board[currentRow + 1][currentColumn] = "+"
			numNegativesFirstRow += 1
			numPositivesSecondRow += 1
			numPositivesFirstColumn += 1
			numNegativesFirstColumn += 1
			firstRowRemainingVerticalPositives -= 1
			firstRowRemainingVerticalNegatives -= 1
			secondRowRemainingVerticalPositives -= 1
			secondRowRemainingVerticalNegatives -= 1
			firstColumnRemainingVerticalPositives -= 1
			firstColumnRemainingVerticalNegatives -= 1
			if(forwardCheck(currentRow, currentColumn, currentRow + 1, currentColumn, specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, 0, 0, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, secondRowRemainingHorizontalPositives, secondRowRemainingHorizontalNegatives, secondRowRemainingVerticalPositives, secondRowRemainingVerticalNegatives, 0, 0, 0, 0)):
				result = dfs(board, specs, currentRow, currentColumn + 1, numRows, numColumns, startTime, lastPrint)
				if (result):
					return result

			# Backtrack
			board[currentRow][currentColumn] = originalFirstCharge
			board[currentRow + 1][currentColumn] = originalSecondCharge
			numNegativesFirstRow -= 1
			numPositivesSecondRow -= 1
			numPositivesFirstColumn -= 1
			numNegativesFirstColumn -= 1
			firstRowRemainingVerticalPositives += 1
			firstRowRemainingVerticalNegatives += 1
			secondRowRemainingVerticalPositives += 1
			secondRowRemainingVerticalNegatives += 1
			firstColumnRemainingVerticalPositives += 1
			firstColumnRemainingVerticalNegatives += 1

		# Try skipping this magnet slot
		board[currentRow][currentColumn] = "X"
		board[currentRow + 1][currentColumn] = "X"
		firstRowRemainingVerticalPositives -= 1
		firstRowRemainingVerticalNegatives -= 1
		secondRowRemainingVerticalPositives -= 1
		secondRowRemainingVerticalNegatives -= 1
		firstColumnRemainingVerticalPositives -= 1
		firstColumnRemainingVerticalNegatives -= 1
		if(forwardCheck(currentRow, currentColumn, currentRow + 1, currentColumn, specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, 0, 0, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, secondRowRemainingHorizontalPositives, secondRowRemainingHorizontalNegatives, secondRowRemainingVerticalPositives, secondRowRemainingVerticalNegatives, 0, 0, 0, 0)):
			result = dfs(board, specs, currentRow, currentColumn + 1, numRows, numColumns, startTime, lastPrint)
			if (result):
				return result

		# Backtrack
		board[currentRow][currentColumn] = originalFirstCharge
		board[currentRow + 1][currentColumn] = originalSecondCharge
		firstRowRemainingVerticalPositives += 1
		firstRowRemainingVerticalNegatives += 1
		secondRowRemainingVerticalPositives += 1
		secondRowRemainingVerticalNegatives += 1
		firstColumnRemainingVerticalPositives += 1
		firstColumnRemainingVerticalNegatives += 1

		return None

	# No valid placement found
	return None

#charge is either + or -
def placeable(board, firstRow, firstColumn, secondRow, secondColumn, firstCharge, secondCharge, specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn): 
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])
	#Zero Constraint Check
	if((firstCharge == "+" and left[firstRow] == 0) or (secondCharge == "+" and left[secondRow] == 0)):					#Row positive
		return False
	if((firstCharge == "-" and right[firstRow] == 0) or (secondCharge == "-" and right[secondRow] == 0)):				#Row negative
		return False
	if((firstCharge == "+" and top[firstColumn] == 0) or (secondCharge == "+" and top[secondColumn] == 0)):				#Column positive
		return False
	if((firstCharge == "-" and bottom[firstColumn] == 0) or (secondCharge == "-" and bottom[secondColumn] == 0)):		#Column negative
		return False

	#Horizontal placement
	if(firstRow == secondRow):
		#Checks if charges around first charge is the same, rows same their columns differ
		if (((firstRow - 1 >= 0) and board[firstRow - 1][firstColumn] == firstCharge) or 					#Checks if the tile above has same charge
			((firstRow + 1 < numRows) and board[firstRow + 1][firstColumn] == firstCharge) or 				#Checks if the tile below has same charge
			((firstColumn - 1 >= 0) and board[firstRow][firstColumn - 1 ] == firstCharge)):					#Checks if the tile left has same charge
			return False
		#Checks if charges around second charge is the same, rows same their columns differ
		if (((firstRow - 1 >= 0) and board[firstRow - 1][secondColumn] == secondCharge) or 					#Checks if the tile above has same charge
			((firstRow + 1 < numRows) and board[firstRow + 1][secondColumn] == secondCharge) or				#Checks if the tile below has same charge
			((secondColumn + 1 < numColumns) and board[firstRow][secondColumn + 1 ] == secondCharge)):		#Checks if the tile right has same charge
			return False
		#Overlimit constraint, when a constraint exits and were over the limit don't place, first and second charge share same rows
		if((firstCharge == "+" or secondCharge == "+") and left[firstRow] != -1 and numPositivesFirstRow >= left[firstRow]):					#Positive charge count over row constraint limit
			return False
		if((firstCharge == "-" or secondCharge == "-") and right[firstRow] != -1 and numNegativesFirstRow >= right[firstRow]):					#Negative charge count over row constraint limit
			return False	
		if(firstCharge == "+" and top[firstColumn] != -1 and numPositivesFirstColumn >= top[firstColumn]):										#Positive charge count over first column constraint limit
			return False	
		if(firstCharge == "-" and bottom[firstColumn] != -1 and numNegativesFirstColumn >= bottom[firstColumn]):								#Negative charge count over first column constraint limit
			return False
		if(secondCharge == "+" and top[secondColumn] != -1 and numPositivesSecondColumn >= top[secondColumn]):									#Positive charge count over second column constraint limit
			return False	
		if(secondCharge == "-" and bottom[secondColumn] != -1 and numNegativesSecondColumn >= bottom[secondColumn]):							#Negative charge count over second column constraint limit
			return False
	#Vertical placement
	else:
		#Checks if charges around first charge is the same, columns same their rows differ 
		if (((firstColumn - 1 >= 0 ) and board[firstRow][firstColumn - 1 ] == firstCharge) or				#Checks if the tile left has same charge
			((firstColumn + 1 < numColumns) and board[firstRow][firstColumn + 1] == firstCharge) or			#Checks if the tile right has same charge
			((firstRow - 1 >= 0) and board[firstRow - 1][firstColumn] == firstCharge)):						#Checks if the tile above has same charge
			return False
		#Checks if charges around second charge is the same, columns same their rows differ 
		if (((firstColumn - 1 >= 0 ) and board[secondRow][firstColumn - 1 ] == secondCharge) or				#Checks if the tile left has same charge
			((firstColumn + 1 < numColumns) and board[secondRow][firstColumn + 1] == secondCharge) or		#Checks if the tile right has same charge
			((secondRow + 1 < numRows) and board[secondRow + 1][firstColumn] == secondCharge)):				#Checks if the tile below has same charge
			return False
		#Overlimit constraint, when a constraint exits and were over the limit don't place, first and second charge share same columns
		if(firstCharge == "+" and left[firstRow] != -1 and numPositivesFirstRow >= left[firstRow]):												#Positive charge count over first row constraint limit
			return False
		if(firstCharge == "-" and right[firstRow] != -1 and numNegativesFirstRow >= right[firstRow]):											#Negative charge count over first row constraint limit
			return False	
		if(secondCharge == "+" and left[secondRow] != -1 and numPositivesSecondRow >= left[secondRow]):											#Positive charge count over second row constraint limit
			return False
		if(secondCharge == "-" and right[secondRow] != -1 and numNegativesSecondRow >= right[secondRow]):										#Negative charge count over second row constraint limit
			return False	
		if((firstCharge == "+" or secondCharge == "+") and top[firstColumn] != -1 and numPositivesFirstColumn >= top[firstColumn]):				#Positive charge count over column constraint limit
			return False	
		if((firstCharge == "-" or secondCharge == "-") and bottom[firstColumn] != -1 and numNegativesFirstColumn >= bottom[firstColumn]):		#Negative charge count over column constraint limit
			return False

	#Constraint can still be fulfilled in the row
	return True 

def forwardCheck(firstRow, firstColumn, secondRow, secondColumn, specs, numPositivesFirstRow, numNegativesFirstRow, numPositivesSecondRow, numNegativesSecondRow, numPositivesFirstColumn, numNegativesFirstColumn, numPositivesSecondColumn, numNegativesSecondColumn, firstRowRemainingHorizontalPositives, firstRowRemainingHorizontalNegatives, firstRowRemainingVerticalPositives, firstRowRemainingVerticalNegatives, firstColumnRemainingVerticalPositives, firstColumnRemainingVerticalNegatives, firstColumnRemainingHorizontalPositives, firstColumnRemainingHorizontalNegatives, secondRowRemainingHorizontalPositives, secondRowRemainingHorizontalNegatives, secondRowRemainingVerticalPositives, secondRowRemainingVerticalNegatives, secondColumnRemainingVerticalPositives, secondColumnRemainingVerticalNegatives, secondColumnRemainingHorizontalPositives, secondColumnRemainingHorizontalNegatives):
	left, right, top, bottom = specs
	#Horizontal placement, columns differ rows are same
	if(firstRow == secondRow):
		#Row 
		if(left[firstRow] > 0 and right[firstRow] > 0):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < left[firstRow] or (numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] > 0 and right[firstRow] == - 1):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < left[firstRow]):
				return False
		elif(left[firstRow] == - 1 and right[firstRow] > 0):
			if((numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] > 0 and right[firstRow] == 0):
			if((numPositivesFirstRow + firstRowRemainingVerticalPositives) < left[firstRow]):
				return False
		elif(left[firstRow] == 0 and right[firstRow] > 0):
			if((numNegativesFirstRow + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] == 0 and right[firstRow] == - 1):
			if(numPositivesFirstRow > left[firstRow]):
				return False
		elif(left[firstRow] == - 1 and right[firstRow] == 0):
			if(numNegativesFirstRow > right[firstRow]): 
				return False
		elif(left[firstRow] == - 1 and right[firstRow] == - 1):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < 0 and (numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < 0):
				return False
		elif(left[firstRow] == 0 and right[firstRow] == 0):
			if(numPositivesFirstRow > 0 or numNegativesFirstRow > 0):
				return False
		#Column one
		if(top[firstColumn] > 0 and bottom[firstColumn] > 0):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < top[firstColumn] or (numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] > 0 and bottom[firstColumn] == - 1):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < top[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] > 0):
			if((numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] > 0 and bottom[firstColumn] == 0):
			if((numPositivesFirstColumn + firstColumnRemainingHorizontalPositives) < top[firstColumn]):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] > 0):
			if((numNegativesFirstColumn + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] == - 1):
			if(numPositivesFirstColumn > top[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] == 0):
			if(numNegativesFirstColumn > bottom[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] == - 1):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < 0 and (numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < 0):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] == 0):
			if(numPositivesFirstColumn > 0 or numNegativesFirstColumn > 0):
				return False
		#Column two
		if(top[secondColumn] > 0 and bottom[secondColumn] > 0):
			if((numPositivesSecondColumn + secondColumnRemainingVerticalPositives + secondColumnRemainingHorizontalPositives) < top[secondColumn] or (numNegativesSecondColumn + secondColumnRemainingVerticalNegatives + secondColumnRemainingHorizontalNegatives) < bottom[secondColumn]):
				return False
		elif(top[secondColumn] > 0 and bottom[secondColumn] == - 1):
			if((numPositivesSecondColumn + secondColumnRemainingVerticalPositives + secondColumnRemainingHorizontalPositives) < top[secondColumn]):
				return False
		elif(top[secondColumn] == - 1 and bottom[secondColumn] > 0):
			if((numNegativesSecondColumn + secondColumnRemainingVerticalNegatives + secondColumnRemainingHorizontalNegatives) < bottom[secondColumn]):
				return False
		elif(top[secondColumn] > 0 and bottom[secondColumn] == 0):
			if((numPositivesSecondColumn + secondColumnRemainingHorizontalPositives) < top[secondColumn]):
				return False
		elif(top[secondColumn] == 0 and bottom[secondColumn] > 0):
			if((numNegativesSecondColumn + secondColumnRemainingHorizontalNegatives) < bottom[secondColumn]):
				return False
		elif(top[secondColumn] == 0 and bottom[secondColumn] == - 1):
			if(numPositivesSecondColumn > top[secondColumn]):
				return False
		elif(top[secondColumn] == - 1 and bottom[secondColumn] == 0):
			if(numNegativesSecondColumn > bottom[secondColumn]):
				return False
		elif(top[secondColumn] == - 1 and bottom[secondColumn] == - 1):
			if((numPositivesSecondColumn + secondColumnRemainingVerticalPositives + secondColumnRemainingHorizontalPositives) < 0 and (numNegativesSecondColumn + secondColumnRemainingVerticalNegatives + secondColumnRemainingHorizontalNegatives) < 0):
				return False
		elif(top[secondColumn] == 0 and bottom[secondColumn] == 0):
			if(numPositivesSecondColumn > 0 or numNegativesSecondColumn > 0):
				return False
	#Vertical placement, rows differ columns are same
	else:		
		#Column
		if(top[firstColumn] > 0 and bottom[firstColumn] > 0):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < top[firstColumn] or (numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] > 0 and bottom[firstColumn] == - 1):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < top[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] > 0):
			if((numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] > 0 and bottom[firstColumn] == 0):
			if((numPositivesFirstColumn + firstColumnRemainingHorizontalPositives) < top[firstColumn]):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] > 0):
			if((numNegativesFirstColumn + firstColumnRemainingHorizontalNegatives) < bottom[firstColumn]):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] == - 1):
			if(numPositivesFirstColumn > top[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] == 0):
			if(numNegativesFirstColumn > bottom[firstColumn]):
				return False
		elif(top[firstColumn] == - 1 and bottom[firstColumn] == - 1):
			if((numPositivesFirstColumn + firstColumnRemainingVerticalPositives + firstColumnRemainingHorizontalPositives) < 0 and (numNegativesFirstColumn + firstColumnRemainingVerticalNegatives + firstColumnRemainingHorizontalNegatives) < 0):
				return False
		elif(top[firstColumn] == 0 and bottom[firstColumn] == 0):
			if(numPositivesFirstColumn > 0 or numNegativesFirstColumn > 0):
				return False
		#Row one
		if(left[firstRow] > 0 and right[firstRow] > 0):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < left[firstRow] or (numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] > 0 and right[firstRow] == - 1):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < left[firstRow]):
				return False
		elif(left[firstRow] == - 1 and right[firstRow] > 0):
			if((numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] > 0 and right[firstRow] == 0):
			if((numPositivesFirstRow + firstRowRemainingVerticalPositives) < left[firstRow]):
				return False
		elif(left[firstRow] == 0 and right[firstRow] > 0):
			if((numNegativesFirstRow + firstRowRemainingVerticalNegatives) < right[firstRow]):
				return False
		elif(left[firstRow] == 0 and right[firstRow] == - 1):
			if(numPositivesFirstRow > left[firstRow]):
				return False
		elif(left[firstRow] == - 1 and right[firstRow] == 0):
			if(numNegativesFirstRow > right[firstRow]): 
				return False
		elif(left[firstRow] == - 1 and right[firstRow] == - 1):
			if((numPositivesFirstRow + firstRowRemainingHorizontalPositives + firstRowRemainingVerticalPositives) < 0 and (numNegativesFirstRow + firstRowRemainingHorizontalNegatives + firstRowRemainingVerticalNegatives) < 0):
				return False
		elif(left[firstRow] == 0 and right[firstRow] == 0):
			if(numPositivesFirstRow > 0 or numNegativesFirstRow > 0):
				return False
		#Row two
		if(left[secondRow] > 0 and right[secondRow] > 0):
			if((numPositivesSecondRow + secondRowRemainingHorizontalPositives + secondRowRemainingVerticalPositives) < left[secondRow] or (numNegativesSecondRow + secondRowRemainingHorizontalNegatives + secondRowRemainingVerticalNegatives) < right[secondRow]):
				return False
		elif(left[secondRow] > 0 and right[secondRow] == - 1):
			if((numPositivesSecondRow + secondRowRemainingHorizontalPositives + secondRowRemainingVerticalPositives) < left[secondRow]):
				return False
		elif(left[secondRow] == - 1 and right[secondRow] > 0):
			if((numNegativesSecondRow + secondRowRemainingHorizontalNegatives + secondRowRemainingVerticalNegatives) < right[secondRow]):
				return False
		elif(left[secondRow] > 0 and right[secondRow] == 0):
			if((numPositivesSecondRow + secondRowRemainingVerticalPositives) < left[secondRow]):
				return False
		elif(left[secondRow] == 0 and right[secondRow] > 0):
			if((numNegativesSecondRow + secondRowRemainingVerticalNegatives) < right[secondRow]):
				return False
		elif(left[secondRow] == 0 and right[secondRow] == - 1):
			if(numPositivesSecondRow > left[secondRow]):
				return False
		elif(left[secondRow] == - 1 and right[secondRow] == 0):
			if(numNegativesSecondRow > right[secondRow]): 
				return False
		elif(left[secondRow] == - 1 and right[secondRow] == - 1):
			if((numPositivesSecondRow + secondRowRemainingHorizontalPositives + secondRowRemainingVerticalPositives) < 0 and (numNegativesSecondRow + secondRowRemainingHorizontalNegatives + secondRowRemainingVerticalNegatives) < 0):
				return False
		elif(left[secondRow] == 0 and right[secondRow] == 0):
			if(numPositivesSecondRow > 0 or numNegativesSecondRow > 0):
				return False
			
	return True


def rowChargeCount(board, currentRow):
	numPositivesInRow = 0
	numNegativesInRow = 0

	#Count # of times + or - in row
	for currentTile in board[currentRow]:
		if (currentTile == "+"):
			numPositivesInRow += 1
		elif (currentTile == "-"):
			numNegativesInRow += 1  
	return numPositivesInRow, numNegativesInRow

def columnChargeCount(board, numRows, currentColumn):
	numPositivesInColumn = 0
	numNegativesInColumn = 0

	#Count # of times + or - in column
	for currentRowIndex in range(numRows):
		if (board[currentRowIndex][currentColumn] ==  "+"):
			numPositivesInColumn += 1
		elif (board[currentRowIndex][currentColumn] ==  "-"):
			numNegativesInColumn += 1	
	return numPositivesInColumn, numNegativesInColumn


def remainingInRow(board, currentRow, numColumns):
	rowRemainingHorizontalPositives = 0
	rowRemainingHorizontalNegatives = 0
	rowRemainingVerticalPositives = 0
	rowRemainingVerticalNegatives = 0
	currentColumn = 0
	while(currentColumn < numColumns):
		currentTile = board[currentRow][currentColumn]
		if(currentTile == "L" and board[currentRow][currentColumn + 1] == "R"):
			rowRemainingHorizontalPositives += 1
			rowRemainingHorizontalNegatives += 1
			currentColumn += 2
		elif(currentTile == "T" or currentTile == "B"):
			rowRemainingVerticalPositives += 1
			rowRemainingVerticalNegatives += 1
			currentColumn += 1
		#+, -, X tiles
		else:
			currentColumn += 1
	return rowRemainingHorizontalPositives, rowRemainingHorizontalNegatives, rowRemainingVerticalPositives, rowRemainingVerticalNegatives

def remainingInColumn(board, currentColumn, numRows):
	columnRemainingHorizontalPositives = 0
	columnRemainingHorizontalNegatives = 0
	columnRemainingVerticalPositives = 0
	columnRemainingVerticalNegatives = 0
	currentRow = 0
	while(currentRow < numRows):
		currentTile = board[currentRow][currentColumn]
		if(currentTile == "T" and board[currentRow + 1][currentColumn] == "B"):
			columnRemainingVerticalPositives += 1
			columnRemainingVerticalNegatives += 1
			currentRow += 2
		elif(currentTile == "L" or currentTile == "R"):
			columnRemainingHorizontalPositives += 1
			columnRemainingHorizontalNegatives += 1
			currentRow += 1
		#+, -, X tiles
		else:
			currentRow += 1
	return columnRemainingVerticalPositives, columnRemainingVerticalNegatives, columnRemainingHorizontalPositives, columnRemainingHorizontalNegatives


def validateRow(board, currentRow, currentColumn, specs):
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


def validateColumn(board, currentRow, currentColumn, specs):
	left, right, top, bottom = specs
	positiveRowCount = 0
	negativeRowCount = 0
	numRows = len(board)
	numColumns = len(board[0])

	#Count # of times + or - in column
	for currentRowIndex in range(numRows):
		if (board[currentRowIndex][currentColumn] ==  "+"):
			positiveRowCount += 1
		if (board[currentRowIndex][currentColumn] ==  "-"):
			negativeRowCount += 1	

	#No constraint limits = -1 and constraints are met when the counts are the same, constraints can either exist in a realm of numbers either -1 or >= 0
	positiveMet = (positiveRowCount == top[currentColumn] or top[currentColumn] == -1)
	negativeMet = (negativeRowCount == bottom[currentColumn] or bottom[currentColumn] == -1)

	return (positiveMet and negativeMet)


def horizontalPlacementExists(currentTile, board, currentRow, currentColumn, numRows, numColumns):
	if ((currentColumn + 1 < numColumns) and currentTile == "L" and board[currentRow][currentColumn+1] == "R"):
		return True
	else:
		return False
	
def verticalPlacementExists(currentTile, board, currentRow, currentColumn, numRows, numColumns):
	if ((currentRow + 1 < numRows) and currentTile == "T" and board[currentRow + 1][currentColumn] == "B"):
		return True
	else:
		return False
	

def preZeroConstraintCheck(board, specs):
	left, right, top, bottom = specs
	numRows = len(board)
	numColumns = len(board[0])

	for currentRow in range(numRows):
		for currentColumn in range(numColumns):
			currentTile = board[currentRow][currentColumn]
			if ((currentTile == "L" or currentTile == "R") and (left[currentRow] == 0 or right[currentRow] == 0)):
				board[currentRow][currentColumn] = "X"
			if ((currentTile == "T" or currentTile == "B") and (top[currentColumn] == 0 or bottom[currentColumn] == 0)):
				board[currentRow][currentColumn] = "X"
			#if ((currentTile == "L" or currentTile == "R") and (top[currentColumn] == 0 or bottom[currentColumn] == 0)):
				#board[currentRow][currentColumn] = "X"
			#if ((currentTile == "T" or currentTile == "B") and (left[currentRow] == 0 or right[currentRow] == 0)):
				#board[currentRow][currentColumn] = "X"
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

	#for currentColumn in range(numColumns):
		#if(top[currentColumn] == 0 or bottom[currentColumn] == 0):
			#for currentRow in range(numRows):
				#board9[currentRow][currentColumn] = "X"

	#print_board(board9, "chickenwong")
	result9 = solve(board9, specs9)
	print_board(result9, "Solution:")


if __name__ == "__main__":
    main()




