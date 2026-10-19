import sys
from time import time
sys.setrecursionlimit(100000)
def solve(originalBoard, specs):
	#Tile trackers
	global orientationToCharge
	global board
	global left, right, top, bottom								#Constraints
	global numRows, numColumns
	#Placed already
	global rowPositives											#(+)
	global rowNegatives 										#(-)
	global columnPositives 										#(+)
	global columnNegatives 										#(-)
	#Horizontal magnet placement capacity
	global horizontalMagnetRemainingPositivesInRow				#(L, R)
	global horizontalMagnetRemainingNegativesInRow 				#(L, R)		
	global horizontalMagnetRemainingPositivesInColumn 			#(L, R)	
	global horizontalMagnetRemainingNegativesInColumn 			#(L, R)	
	#Vertical magnet placement capacity
	global verticalMagnetRemainingPositivesInRow 				#(T, B)
	global verticalMagnetRemainingNegativesInRow 				#(T, B)
	global verticalMagnetRemainingPositivesInColumn 			#(T, B)
	global verticalMagnetRemainingNegativesInColumn 			#(T, B)

	global rowNumX												#(X, X)				
	global columnNumX											#(X. X)
	global neighbourLocations 
	global magnetMRVs
	global orientations

	orientationToCharge = {"+-": ("+", "-"), "-+": ("-", "+"), "XX": ("X", "X")}
	left = specs[0]
	right = specs[1]
	top = specs[2]
	bottom = specs[3]
	numRows = len(originalBoard)
	numColumns = len(originalBoard[0])
	board = [list(row) for row in originalBoard]
	board = preZeroConstraintCheck()	
	#Placed already
	rowPositives = [0] * numRows								#(+)
	rowNegatives = [0] * numRows								#(-)
	columnPositives = [0] * numColumns							#(+)
	columnNegatives = [0] * numColumns							#(-)
	#Horizontal magnet placement capacity
	horizontalMagnetRemainingPositivesInRow = [0] * numRows				#(L, R)
	horizontalMagnetRemainingNegativesInRow = [0] * numRows				#(L, R)	
	horizontalMagnetRemainingPositivesInColumn = [0] * numColumns 		#(L, R)	
	horizontalMagnetRemainingNegativesInColumn = [0] * numColumns		#(L, R)	
	#Vertical magnet placement capacity
	verticalMagnetRemainingPositivesInRow = [0] * numRows				#(T, B)
	verticalMagnetRemainingNegativesInRow = [0] * numRows				#(T, B)
	verticalMagnetRemainingPositivesInColumn = [0] * numColumns			#(T, B)
	verticalMagnetRemainingNegativesInColumn = [0] * numColumns 		#(T, B)
	rowNumX = [0] * numRows										#(X, X)				
	columnNumX = [0] * numColumns								#(X. X)	
	magnetLocations = []

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
				magnetLocations.append((currentRow, currentColumn, currentRow, currentColumn + 1))
				#Dealing with 2 tiles at once since merged 4 functions can't rely on doing 1 by 1
				horizontalMagnetRemainingPositivesInRow[currentRow]	+= 1				#(L, R)
				horizontalMagnetRemainingNegativesInRow[currentRow]	+= 1				#(L, R)
				horizontalMagnetRemainingPositivesInColumn[currentColumn] += 1			#(L, R)	
				horizontalMagnetRemainingNegativesInColumn[currentColumn] += 1			#(L, R)	
				horizontalMagnetRemainingPositivesInColumn[currentColumn + 1] += 1		#(L, R)	
				horizontalMagnetRemainingNegativesInColumn[currentColumn + 1] += 1		#(L, R)	
			#Vertical placement, rows differ columns same
			elif((currentTile == "T") and (currentRow + 1 < numRows) and (board[currentRow + 1][currentColumn] == "B")):
				magnetLocations.append((currentRow, currentColumn, currentRow + 1, currentColumn))
				#Dealing with 2 tiles at once since merged 4 functions can't rely on doing 1 by 1
				verticalMagnetRemainingPositivesInRow[currentRow] += 1					#(T, B)
				verticalMagnetRemainingNegativesInRow[currentRow] += 1					#(T, B)
				verticalMagnetRemainingPositivesInRow[currentRow + 1] += 1				#(T, B)
				verticalMagnetRemainingNegativesInRow[currentRow + 1] += 1				#(T, B)
				verticalMagnetRemainingPositivesInColumn[currentColumn] += 1			#(T, B)
				verticalMagnetRemainingNegativesInColumn[currentColumn] += 1			#(T, B)
			#X
			elif(currentTile == "X"):
				rowNumX[currentRow] += 1
				columnNumX[currentColumn] += 1

	#Dictionary key position holds what orientation magnet can fit
	orientations = {}
	#Dictionary organize magnets based off # of placeable orientations they have and hold the location of those magnets in a set (fast lookup)
	magnetMRVs = {1: set(), 2: set(), 3: set()}
	#Dictionary key position holds location of neighbours, adjacency list 
	neighbourLocations = {}
	for position in magnetLocations:
		currentMRVCount, orientations[position] = calcMRV(position)
		magnetMRVs[currentMRVCount].add(position)
		rowOne, columnOne, rowTwo, columnTwo = position
		neighbours = []
		for neighbourPosition in magnetLocations:
			if(neighbourPosition == position):
				continue
			neighbourRowOne, neighbourColumnOne, neighbourRowTwo, neighbourColumnTwo = neighbourPosition
			if(neighbourRowOne == rowOne or neighbourRowOne == rowTwo or neighbourRowTwo == rowOne or neighbourRowTwo == rowTwo or neighbourColumnOne == columnOne or neighbourColumnOne == columnTwo or neighbourColumnTwo == columnOne or neighbourColumnTwo == columnTwo):
				neighbours.append(neighbourPosition)
		neighbourLocations[position] = neighbours	
	global backtrackCallCount
	backtrackCallCount = 0
	result = backtrack()
	print(f"Backtrack calls: {backtrackCallCount}")
	return result

def backtrack():
	global backtrackCallCount
	backtrackCallCount += 1

	#Exhaust the magnets with least amount of options first
	if(len(magnetMRVs[1]) > 0):
		position = next(iter(magnetMRVs[1]))
		magnetMRVs[1].remove(position)
		currentMRVCount = 1
	elif(len(magnetMRVs[2]) > 0):
		position = next(iter(magnetMRVs[2]))
		magnetMRVs[2].remove(position)
		currentMRVCount = 2
	elif(len(magnetMRVs[3]) > 0):
		position = next(iter(magnetMRVs[3]))
		magnetMRVs[3].remove(position)
		currentMRVCount = 3
	else:
		if(validateConfiguration()):
			return [row[:] for row in board]
		return None

	rowOne, columnOne, rowTwo, columnTwo = position
	currentOrientations = orientations[position]

	originalChargeOne = board[rowOne][columnOne]
	originalChargeTwo = board[rowTwo][columnTwo]

	for orientation in currentOrientations:
		#Try Placement
		board[rowOne][columnOne], board[rowTwo][columnTwo] = orientationToCharge[orientation]
		updateTrackers(position, orientation, 1)
		neighboursUpdated = False
		currentNeighbourMRVData = []
		if(forwardCheck(position)):
			#Update neighbouring magnet MRV(s)
			for neighbourPosition in neighbourLocations[position]:
				if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
					#Current MRV
					currentNeighbourMRVCount = 1 if neighbourPosition in magnetMRVs[1] else 2 if neighbourPosition in magnetMRVs[2] else 3
					currentNeighbourMRVData.append((neighbourPosition, currentNeighbourMRVCount, orientations[neighbourPosition]))
					magnetMRVs[currentNeighbourMRVCount].discard(neighbourPosition)
					#New MRV
					neighbourMRV, newOrientations = calcMRV(neighbourPosition)
					orientations[neighbourPosition] = newOrientations
					magnetMRVs[neighbourMRV].add(neighbourPosition)
					
			neighboursUpdated = True		
			result = backtrack()
			if (result):
				return result

		#Backtrack
		board[rowOne][columnOne] = originalChargeOne
		board[rowTwo][columnTwo] = originalChargeTwo	
		updateTrackers(position, orientation, -1)
		#Revert neighbouring magnet MRV(s)
		if(neighboursUpdated):
			for neighbourPosition, currentNeighbourMRVCount, currentNeighbourOrientations in currentNeighbourMRVData:
				magnetMRVs[1].discard(neighbourPosition)
				magnetMRVs[2].discard(neighbourPosition)
				magnetMRVs[3].discard(neighbourPosition)
				orientations[neighbourPosition] = currentNeighbourOrientations
				magnetMRVs[currentNeighbourMRVCount].add(neighbourPosition)
					
	#No valid placement found
	orientations[position] = currentOrientations
	magnetMRVs[currentMRVCount].add(position)
	return None

def updateTrackers (position, orientation, count):
	rowOne, columnOne, rowTwo, columnTwo = position
	firstCharge, secondCharge = orientationToCharge[orientation]

	#Setting the capacities depending on vertical or horizontal placement, vertical placements only change vertical counters and horizontal only changes horizontal
	if(rowOne == rowTwo):
		rowRemainingPositives, rowRemainingNegatives = horizontalMagnetRemainingPositivesInRow, horizontalMagnetRemainingNegativesInRow
		columnRemainingPositives, columnRemainingNegatives = horizontalMagnetRemainingPositivesInColumn, horizontalMagnetRemainingNegativesInColumn
	else:
		rowRemainingPositives, rowRemainingNegatives = verticalMagnetRemainingPositivesInRow, verticalMagnetRemainingNegativesInRow
		columnRemainingPositives, columnRemainingNegatives = verticalMagnetRemainingPositivesInColumn, verticalMagnetRemainingNegativesInColumn

	#Updating the remaining trackers, using a set because if a repeated row or column appears it doesn't duplicate, if were backtracking passing down -1 will make it turn into addition
	for row in {rowOne, rowTwo}:
		rowRemainingPositives[row] -= count
		rowRemainingNegatives[row] -= count
	for column in {columnOne, columnTwo}:
		columnRemainingPositives[column] -= count
		columnRemainingNegatives[column] -= count

	#Depending regardless of its a vertical or a horizontal, a charge add to it's own cordinates positive & negative (row, column) it maps too, if the charge is XX don't do anything
	for row, column, charge in ((rowOne, columnOne, firstCharge), (rowTwo, columnTwo, secondCharge)):
		if(charge == "+"):
			rowPositives[row] += count
			columnPositives[column] += count
		elif(charge == "-"):
			rowNegatives[row] += count
			columnNegatives[column] += count

#charge is either + or -
def placeable(firstRow, firstColumn, secondRow, secondColumn, firstCharge, secondCharge): 
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
		if((firstCharge == "+" or secondCharge == "+") and left[firstRow] != -1 and rowPositives[firstRow] >= left[firstRow]):					#Positive charge count over row constraint limit
			return False
		if((firstCharge == "-" or secondCharge == "-") and right[firstRow] != -1 and rowNegatives[firstRow] >= right[firstRow]):					#Negative charge count over row constraint limit
			return False	
		if(firstCharge == "+" and top[firstColumn] != -1 and columnPositives[firstColumn] >= top[firstColumn]):										#Positive charge count over first column constraint limit
			return False	
		if(firstCharge == "-" and bottom[firstColumn] != -1 and columnNegatives[firstColumn] >= bottom[firstColumn]):								#Negative charge count over first column constraint limit
			return False
		if(secondCharge == "+" and top[secondColumn] != -1 and columnPositives[secondColumn] >= top[secondColumn]):									#Positive charge count over second column constraint limit
			return False	
		if(secondCharge == "-" and bottom[secondColumn] != -1 and columnNegatives[secondColumn] >= bottom[secondColumn]):							#Negative charge count over second column constraint limit
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
		if(firstCharge == "+" and left[firstRow] != -1 and rowPositives[firstRow] >= left[firstRow]):												#Positive charge count over first row constraint limit
			return False
		if(firstCharge == "-" and right[firstRow] != -1 and rowNegatives[firstRow] >= right[firstRow]):											#Negative charge count over first row constraint limit
			return False	
		if(secondCharge == "+" and left[secondRow] != -1 and rowPositives[secondRow] >= left[secondRow]):											#Positive charge count over second row constraint limit
			return False
		if(secondCharge == "-" and right[secondRow] != -1 and rowNegatives[secondRow] >= right[secondRow]):										#Negative charge count over second row constraint limit
			return False	
		if((firstCharge == "+" or secondCharge == "+") and top[firstColumn] != -1 and columnPositives[firstColumn] >= top[firstColumn]):				#Positive charge count over column constraint limit
			return False	
		if((firstCharge == "-" or secondCharge == "-") and bottom[firstColumn] != -1 and columnNegatives[firstColumn] >= bottom[firstColumn]):		#Negative charge count over column constraint limit
			return False

	#Constraint can still be fulfilled in the row
	return True 

def forwardCheck(position):
	rowOne, columnOne, rowTwo, columnTwo = position

	if(left[rowOne] > 0 and right[rowOne] > 0):
		if(rowPositives[rowOne] > left[rowOne] or rowNegatives[rowOne] > right[rowOne] or (rowPositives[rowOne] + horizontalMagnetRemainingPositivesInRow[rowOne] + verticalMagnetRemainingPositivesInRow[rowOne]) < left[rowOne] or (rowNegatives[rowOne] + horizontalMagnetRemainingNegativesInRow[rowOne] + verticalMagnetRemainingNegativesInRow[rowOne]) < right[rowOne]):
			return False
	elif(left[rowOne] > 0 and right[rowOne] == -1):
		if(rowPositives[rowOne] > left[rowOne] or (rowPositives[rowOne] + horizontalMagnetRemainingPositivesInRow[rowOne] + verticalMagnetRemainingPositivesInRow[rowOne]) < left[rowOne]):
			return False
	elif(left[rowOne] == -1 and right[rowOne] > 0):
		if(rowNegatives[rowOne] > right[rowOne] or (rowNegatives[rowOne] + horizontalMagnetRemainingNegativesInRow[rowOne] + verticalMagnetRemainingNegativesInRow[rowOne]) < right[rowOne]):
			return False
	elif(left[rowOne] > 0 and right[rowOne] == 0):
		#Horizontals can't be placed, only verticals contribute positives
		if(rowPositives[rowOne] > left[rowOne] or (rowPositives[rowOne] + verticalMagnetRemainingPositivesInRow[rowOne]) < left[rowOne]):
			return False
	elif(left[rowOne] == 0 and right[rowOne] > 0):
		#Horizontals can't be placed, only verticals contribute negatives
		if(rowNegatives[rowOne] > right[rowOne] or (rowNegatives[rowOne] + verticalMagnetRemainingNegativesInRow[rowOne]) < right[rowOne]):
			return False
	elif(left[rowOne] == 0 and right[rowOne] == -1):
		if(rowPositives[rowOne] > 0):
			return False
	elif(left[rowOne] == -1 and right[rowOne] == 0):
		if(rowNegatives[rowOne] > 0):
			return False
	elif(left[rowOne] == 0 and right[rowOne] == 0):
		if(rowPositives[rowOne] > 0 or rowNegatives[rowOne] > 0):
			return False
	
	if(rowOne != rowTwo):
		if(left[rowTwo] > 0 and right[rowTwo] > 0):
			if(rowPositives[rowTwo] > left[rowTwo] or rowNegatives[rowTwo] > right[rowTwo] or (rowPositives[rowTwo] + horizontalMagnetRemainingPositivesInRow[rowTwo] + verticalMagnetRemainingPositivesInRow[rowTwo]) < left[rowTwo] or (rowNegatives[rowTwo] + horizontalMagnetRemainingNegativesInRow[rowTwo] + verticalMagnetRemainingNegativesInRow[rowTwo]) < right[rowTwo]):
				return False
		elif(left[rowTwo] > 0 and right[rowTwo] == -1):
			if(rowPositives[rowTwo] > left[rowTwo] or (rowPositives[rowTwo] + horizontalMagnetRemainingPositivesInRow[rowTwo] + verticalMagnetRemainingPositivesInRow[rowTwo]) < left[rowTwo]):
				return False
		elif(left[rowTwo] == -1 and right[rowTwo] > 0):
			if(rowNegatives[rowTwo] > right[rowTwo] or (rowNegatives[rowTwo] + horizontalMagnetRemainingNegativesInRow[rowTwo] + verticalMagnetRemainingNegativesInRow[rowTwo]) < right[rowTwo]):
				return False
		elif(left[rowTwo] > 0 and right[rowTwo] == 0):
			#Horizontals can't be placed, only verticals contribute positives
			if(rowPositives[rowTwo] > left[rowTwo] or (rowPositives[rowTwo] + verticalMagnetRemainingPositivesInRow[rowTwo]) < left[rowTwo]):
				return False
		elif(left[rowTwo] == 0 and right[rowTwo] > 0):
			#Horizontals can't be placed, only verticals contribute negatives
			if(rowNegatives[rowTwo] > right[rowTwo] or (rowNegatives[rowTwo] + verticalMagnetRemainingNegativesInRow[rowTwo]) < right[rowTwo]):
				return False
		elif(left[rowTwo] == 0 and right[rowTwo] == -1):
			if(rowPositives[rowTwo] > 0):
				return False
		elif(left[rowTwo] == -1 and right[rowTwo] == 0):
			if(rowNegatives[rowTwo] > 0):
				return False
		elif(left[rowTwo] == 0 and right[rowTwo] == 0):
			if(rowPositives[rowTwo] > 0 or rowNegatives[rowTwo] > 0):
				return False
		
	if(top[columnOne] > 0 and bottom[columnOne] > 0):
		if(columnPositives[columnOne] > top[columnOne] or columnNegatives[columnOne] > bottom[columnOne] or (columnPositives[columnOne] + verticalMagnetRemainingPositivesInColumn[columnOne] + horizontalMagnetRemainingPositivesInColumn[columnOne]) < top[columnOne] or (columnNegatives[columnOne] + verticalMagnetRemainingNegativesInColumn[columnOne] + horizontalMagnetRemainingNegativesInColumn[columnOne]) < bottom[columnOne]):
			return False
	elif(top[columnOne] > 0 and bottom[columnOne] == -1):
		if(columnPositives[columnOne] > top[columnOne] or (columnPositives[columnOne] + verticalMagnetRemainingPositivesInColumn[columnOne] + horizontalMagnetRemainingPositivesInColumn[columnOne]) < top[columnOne]):
			return False
	elif(top[columnOne] == -1 and bottom[columnOne] > 0):
		if(columnNegatives[columnOne] > bottom[columnOne] or (columnNegatives[columnOne] + verticalMagnetRemainingNegativesInColumn[columnOne] + horizontalMagnetRemainingNegativesInColumn[columnOne]) < bottom[columnOne]):
			return False
	elif(top[columnOne] > 0 and bottom[columnOne] == 0):
		#Verticals can't be placed, only horizontals contribute positives
		if(columnPositives[columnOne] > top[columnOne] or (columnPositives[columnOne] + horizontalMagnetRemainingPositivesInColumn[columnOne]) < top[columnOne]):
			return False
	elif(top[columnOne] == 0 and bottom[columnOne] > 0):
		#Verticals can't be placed, only horizontals contribute negatives
		if(columnNegatives[columnOne] > bottom[columnOne] or (columnNegatives[columnOne] + horizontalMagnetRemainingNegativesInColumn[columnOne]) < bottom[columnOne]):
			return False
	elif(top[columnOne] == 0 and bottom[columnOne] == -1):
		if(columnPositives[columnOne] > 0):
			return False
	elif(top[columnOne] == -1 and bottom[columnOne] == 0):
		if(columnNegatives[columnOne] > 0):
			return False
	elif(top[columnOne] == 0 and bottom[columnOne] == 0):
		if(columnPositives[columnOne] > 0 or columnNegatives[columnOne] > 0):
			return False
		
	if(columnOne != columnTwo):	
		if(top[columnTwo] > 0 and bottom[columnTwo] > 0):
			if(columnPositives[columnTwo] > top[columnTwo] or columnNegatives[columnTwo] > bottom[columnTwo] or (columnPositives[columnTwo] + verticalMagnetRemainingPositivesInColumn[columnTwo] + horizontalMagnetRemainingPositivesInColumn[columnTwo]) < top[columnTwo] or (columnNegatives[columnTwo] + verticalMagnetRemainingNegativesInColumn[columnTwo] + horizontalMagnetRemainingNegativesInColumn[columnTwo]) < bottom[columnTwo]):
				return False
		elif(top[columnTwo] > 0 and bottom[columnTwo] == -1):
			if(columnPositives[columnTwo] > top[columnTwo] or (columnPositives[columnTwo] + verticalMagnetRemainingPositivesInColumn[columnTwo] + horizontalMagnetRemainingPositivesInColumn[columnTwo]) < top[columnTwo]):
				return False
		elif(top[columnTwo] == -1 and bottom[columnTwo] > 0):
			if(columnNegatives[columnTwo] > bottom[columnTwo] or (columnNegatives[columnTwo] + verticalMagnetRemainingNegativesInColumn[columnTwo] + horizontalMagnetRemainingNegativesInColumn[columnTwo]) < bottom[columnTwo]):
				return False
		elif(top[columnTwo] > 0 and bottom[columnTwo] == 0):
			#Verticals can't be placed, only horizontals contribute positives
			if(columnPositives[columnTwo] > top[columnTwo] or (columnPositives[columnTwo] + horizontalMagnetRemainingPositivesInColumn[columnTwo]) < top[columnTwo]):
				return False
		elif(top[columnTwo] == 0 and bottom[columnTwo] > 0):
			#Verticals can't be placed, only horizontals contribute negatives
			if(columnNegatives[columnTwo] > bottom[columnTwo] or (columnNegatives[columnTwo] + horizontalMagnetRemainingNegativesInColumn[columnTwo]) < bottom[columnTwo]):
				return False
		elif(top[columnTwo] == 0 and bottom[columnTwo] == -1):
			if(columnPositives[columnTwo] > 0):
				return False
		elif(top[columnTwo] == -1 and bottom[columnTwo] == 0):
			if(columnNegatives[columnTwo] > 0):
				return False
		elif(top[columnTwo] == 0 and bottom[columnTwo] == 0):
			if(columnPositives[columnTwo] > 0 or columnNegatives[columnTwo] > 0):
				return False
		
	return True

def AC3():

	#Check all rows
	for currentRow in range(numRows):
		if(left[currentRow] > 0 and right[currentRow] > 0):
			if(rowPositives[currentRow] > left[currentRow] or rowNegatives[currentRow] > right[currentRow] or (rowPositives[currentRow] + horizontalMagnetRemainingPositivesInRow[currentRow] + verticalMagnetRemainingPositivesInRow[currentRow]) < left[currentRow] or (rowNegatives[currentRow] + horizontalMagnetRemainingNegativesInRow[currentRow] + verticalMagnetRemainingNegativesInRow[currentRow]) < right[currentRow]):
				return False
		elif(left[currentRow] > 0 and right[currentRow] == -1):
			if(rowPositives[currentRow] > left[currentRow] or (rowPositives[currentRow] + horizontalMagnetRemainingPositivesInRow[currentRow] + verticalMagnetRemainingPositivesInRow[currentRow]) < left[currentRow]):
				return False
		elif(left[currentRow] == -1 and right[currentRow] > 0):
			if(rowNegatives[currentRow] > right[currentRow] or (rowNegatives[currentRow] + horizontalMagnetRemainingNegativesInRow[currentRow] + verticalMagnetRemainingNegativesInRow[currentRow]) < right[currentRow]):
				return False
		elif(left[currentRow] > 0 and right[currentRow] == 0):
			#Horizontals can't be placed, only verticals contribute positives
			if(rowPositives[currentRow] > left[currentRow] or (rowPositives[currentRow] + verticalMagnetRemainingPositivesInRow[currentRow]) < left[currentRow]):
				return False
		elif(left[currentRow] == 0 and right[currentRow] > 0):
			#Horizontals can't be placed, only verticals contribute negatives
			if(rowNegatives[currentRow] > right[currentRow] or (rowNegatives[currentRow] + verticalMagnetRemainingNegativesInRow[currentRow]) < right[currentRow]):
				return False
		elif(left[currentRow] == 0 and right[currentRow] == -1):
			if(rowPositives[currentRow] > 0):
				return False
		elif(left[currentRow] == -1 and right[currentRow] == 0):
			if(rowNegatives[currentRow] > 0):
				return False
		elif(left[currentRow] == 0 and right[currentRow] == 0):
			if(rowPositives[currentRow] > 0 or rowNegatives[currentRow] > 0):
				return False

	#Check all columns
	for currentColumn in range(numColumns):
		if(top[currentColumn] > 0 and bottom[currentColumn] > 0):
			if(columnPositives[currentColumn] > top[currentColumn] or columnNegatives[currentColumn] > bottom[currentColumn] or (columnPositives[currentColumn] + verticalMagnetRemainingPositivesInColumn[currentColumn] + horizontalMagnetRemainingPositivesInColumn[currentColumn]) < top[currentColumn] or (columnNegatives[currentColumn] + verticalMagnetRemainingNegativesInColumn[currentColumn] + horizontalMagnetRemainingNegativesInColumn[currentColumn]) < bottom[currentColumn]):
				return False
		elif(top[currentColumn] > 0 and bottom[currentColumn] == -1):
			if(columnPositives[currentColumn] > top[currentColumn] or (columnPositives[currentColumn] + verticalMagnetRemainingPositivesInColumn[currentColumn] + horizontalMagnetRemainingPositivesInColumn[currentColumn]) < top[currentColumn]):
				return False
		elif(top[currentColumn] == -1 and bottom[currentColumn] > 0):
			if(columnNegatives[currentColumn] > bottom[currentColumn] or (columnNegatives[currentColumn] + verticalMagnetRemainingNegativesInColumn[currentColumn] + horizontalMagnetRemainingNegativesInColumn[currentColumn]) < bottom[currentColumn]):
				return False
		elif(top[currentColumn] > 0 and bottom[currentColumn] == 0):
			#Verticals can't be placed, only horizontals contribute positives
			if(columnPositives[currentColumn] > top[currentColumn] or (columnPositives[currentColumn] + horizontalMagnetRemainingPositivesInColumn[currentColumn]) < top[currentColumn]):
				return False
		elif(top[currentColumn] == 0 and bottom[currentColumn] > 0):
			#Verticals can't be placed, only horizontals contribute negatives
			if(columnNegatives[currentColumn] > bottom[currentColumn] or (columnNegatives[currentColumn] + horizontalMagnetRemainingNegativesInColumn[currentColumn]) < bottom[currentColumn]):
				return False
		elif(top[currentColumn] == 0 and bottom[currentColumn] == -1):
			if(columnPositives[currentColumn] > 0):
				return False
		elif(top[currentColumn] == -1 and bottom[currentColumn] == 0):
			if(columnNegatives[currentColumn] > 0):
				return False
		elif(top[currentColumn] == 0 and bottom[currentColumn] == 0):
			if(columnPositives[currentColumn] > 0 or columnNegatives[currentColumn] > 0):
				return False
			
	return True

def rowChargeCount(currentRow):
	numPositivesInRow = 0
	numNegativesInRow = 0

	#Count # of times + or - in row
	for currentTile in board[currentRow]:
		if (currentTile == "+"):
			numPositivesInRow += 1
		elif (currentTile == "-"):
			numNegativesInRow += 1  

	return numPositivesInRow, numNegativesInRow

def columnChargeCount(currentColumn):
	numPositivesInColumn = 0
	numNegativesInColumn = 0

	#Count # of times + or - in column
	for currentRowIndex in range(numRows):
		if (board[currentRowIndex][currentColumn] ==  "+"):
			numPositivesInColumn += 1
		elif (board[currentRowIndex][currentColumn] ==  "-"):
			numNegativesInColumn += 1	

	return numPositivesInColumn, numNegativesInColumn

def remainingInRow(currentRow):
	horizontalMagnetRemainingPositivesInRow = 0
	horizontalMagnetRemainingNegativesInRow = 0
	verticalMagnetRemainingPositivesInRow = 0
	verticalMagnetRemainingNegativesInRow = 0
	currentColumn = 0
	while(currentColumn < numColumns):
		currentTile = board[currentRow][currentColumn]
		if(currentTile == "L" and board[currentRow][currentColumn + 1] == "R"):
			horizontalMagnetRemainingPositivesInRow += 1
			horizontalMagnetRemainingNegativesInRow += 1
			currentColumn += 2
		elif(currentTile == "T" or currentTile == "B"):
			verticalMagnetRemainingPositivesInRow += 1
			verticalMagnetRemainingNegativesInRow += 1
			currentColumn += 1
		#+, -, X tiles
		else:
			currentColumn += 1

	return horizontalMagnetRemainingPositivesInRow, horizontalMagnetRemainingNegativesInRow, verticalMagnetRemainingPositivesInRow, verticalMagnetRemainingNegativesInRow

def remainingInColumn(currentColumn):
	horizontalMagnetRemainingPositivesInColumn = 0
	horizontalMagnetRemainingNegativesInColumn = 0
	verticalMagnetRemainingPositivesInColumn = 0
	verticalMagnetRemainingNegativesInColumn = 0
	currentRow = 0
	while(currentRow < numRows):
		currentTile = board[currentRow][currentColumn]
		if(currentTile == "T" and board[currentRow + 1][currentColumn] == "B"):
			verticalMagnetRemainingPositivesInColumn += 1
			verticalMagnetRemainingNegativesInColumn += 1
			currentRow += 2
		elif(currentTile == "L" or currentTile == "R"):
			horizontalMagnetRemainingPositivesInColumn += 1
			horizontalMagnetRemainingNegativesInColumn += 1
			currentRow += 1
		#+, -, X tiles
		else:
			currentRow += 1

	return verticalMagnetRemainingPositivesInColumn, verticalMagnetRemainingNegativesInColumn, horizontalMagnetRemainingPositivesInColumn, horizontalMagnetRemainingNegativesInColumn

def calcMRV(position):
	rowOne, columnOne, rowTwo, columnTwo = position
	currentOrientations = ["XX"]
	if(placeable(rowOne, columnOne, rowTwo, columnTwo, "+", "-")):
		currentOrientations.append("+-")
	if(placeable(rowOne, columnOne, rowTwo, columnTwo, "-", "+")):
		currentOrientations.append("-+")
		
	return (len(currentOrientations), tuple(currentOrientations))

def validateRow(currentRow):
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

def validateColumn(currentColumn):
	positiveRowCount = 0
	negativeRowCount = 0

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

def horizontalPlacementExists(currentTile,currentRow, currentColumn):
	if ((currentColumn + 1 < numColumns) and currentTile == "L" and board[currentRow][currentColumn+1] == "R"):
		return True
	else:
		return False
	
def verticalPlacementExists(currentTile, currentRow, currentColumn):
	if ((currentRow + 1 < numRows) and currentTile == "T" and board[currentRow + 1][currentColumn] == "B"):
		return True
	else:
		return False

def preZeroConstraintCheck():
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

def validateConfiguration():
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

def runTest(testName, board, specs):
    print("="*60)
    print(testName)
    print("="*60)
    start = time()
    result = solve(board, specs)
    total = time() - start
    if result:
        print(f"Success in {total:.3f} seconds.")
    else:
        print(f"No solution found in {total:.3f} seconds.")
    print_board(result, "Solution:")
    return result

def main():
	# Simple test case - 2x2 board
	specs1 = [
		[1, 1],      # left: + per row (row 0 needs 1 +, row 1 needs 1 +)
		[1, 1],      # right: - per row (row 0 needs 1 -, row 1 needs 1 -)
		[1, 1],      # top: + per column (col 0 needs 1 +, col 1 needs 1 +)
		[1, 1]       # bottom: - per column (col 0 needs 1 -, col 1 needs 1 -)
	]
	board1 = ["LR", "LR"]  # Two horizontal magnets
	runTest("SIMPLE TEST: 2x2 Board", board1, specs1)

	# Test case 2 - 2x2 Board (vertical magnet)
	specs2 = [
		[1, 1],      # left: + per row
		[1, 1],      # right: - per row
		[1, 1],      # top: + per column
		[1, 1]       # bottom: - per column
	]
	board2 = ["TT", "BB"]
	runTest("TEST CASE 2: 2x2 Board (Vertical)", board2, specs2)

	# Test case 3 - 2x2 Board (horizontal, variant)
	specs3 = [
		[1, -1],     # left: + per row
		[1, -1],     # right: - per row
		[1, -1],     # top: + per column
		[-1, 1]      # bottom: - per column
	]
	board3 = ["LR", "LR"]
	runTest("TEST CASE 3: 2x2 Board (Horizontal Variant)", board3, specs3)

	# Test case 4 - 4x4 Board (with 0 constraints)
	specs4 = [
		[0, 1, 2, -1],   # left: + per row
		[0, -1, 1, 2],   # right: - per row
		[1, 1, -1, 1],   # top: + per column
		[1, 1, 0, 2]     # bottom: - per column
	]
	board4 = ["TTLR", "BBLR", "LRTT", "LRBB"]
	runTest("TEST CASE 4: 4x4 Board (with 0 constraints)", board4, specs4)

	# Test case 5 - 4x4 Board (variant)
	specs5 = [
		[1, 2, -1, -1],  # left: + per row
		[-1, 2, -1, 2],  # right: - per row
		[2, -1, 0, 2],   # top: + per column
		[2, -1, 2, 2]    # bottom: - per column
	]
	board5 = ["TLRT", "BLRB", "TLRT", "BLRB"]
	runTest("TEST CASE 5: 4x4 Board (Variant)", board5, specs5)

	# Test case 6 - 5x6 Board
	specs6 = [
		[2, 3, -1, -1, -1],
		[-1, -1, -1, 1, -1],
		[1, -1, -1, 2, 1, -1],
		[2, -1, -1, 2, -1, 3]
	]
	board6 = ["LRLRTT", "LRLRBB", "TTTTLR", "BBBBTT", "LRLRBB"]
	runTest("TEST CASE 6: 5x6 Board", board6, specs6)

	# Test case 7 - 8x8 Board
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
	runTest("TEST CASE 7: 8x8 Board", board7, specs7)

	# Test case 8 - 8x8 Board
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
	runTest("TEST CASE 8: 8x8 Board", board8, specs8)

	# Test case 9 - 16x16 Board
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
	runTest("TEST CASE 9: 16x16 Board", board9, specs9)

if __name__ == "__main__":
    main()