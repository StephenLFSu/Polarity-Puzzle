import sys
from time import time
import heapq
sys.setrecursionlimit(100000)
	#left = specs[0]  			#row
	#right = specs[1]			#row
	#top = specs[2]				#col
	#bottom = specs[3]			#col
def solve(board, specs):
    board = [list(row) for row in board]
    numRows = len(board)
    numColumns = len(board[0])
    board = preZeroConstraintCheck(board, specs)
    #Tile trackers
    global rowPositives											#(+)
    global rowNegatives 										#(-)
    global columnPositives 										#(+)
    global columnNegatives 										#(-)
    global rowRemainingHorizontalPositives						#(L, R)
    global rowRemainingHorizontalNegatives 						#(L, R)	
    global rowRemainingVerticalPositives 						#(T, B)
    global rowRemainingVerticalNegatives 						#(T, B)
    global columnRemainingVerticalPositives						#(T, B)
    global columnRemainingVerticalNegatives						#(T, B)
    global columnRemainingHorizontalPositives 					#(L, R)	
    global columnRemainingHorizontalNegatives 					#(L, R)	
    global rowNumX												#(X, X)				
    global columnNumX											#(X. X)
    global neighbourLocations 
    global magnetMRVs
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
                rowRemainingHorizontalPositives[currentRow]	+= 1				#(L, R)
                rowRemainingHorizontalNegatives[currentRow]	+= 1				#(L, R)
                columnRemainingHorizontalPositives[currentColumn] += 1			#(L, R)	
                columnRemainingHorizontalNegatives[currentColumn] += 1			#(L, R)	
                columnRemainingHorizontalPositives[currentColumn + 1] += 1		#(L, R)	
                columnRemainingHorizontalNegatives[currentColumn + 1] += 1		#(L, R)	
            #Vertical placement, rows differ columns same
            elif((currentTile == "T") and (currentRow + 1 < numRows) and (board[currentRow + 1][currentColumn] == "B")):
                magnetLocations.append((currentRow, currentColumn, currentRow + 1, currentColumn))
                #Dealing with 2 tiles at once since merged 4 functions can't rely on doing 1 by 1
                rowRemainingVerticalPositives[currentRow] += 1					#(T, B)
                rowRemainingVerticalNegatives[currentRow] += 1					#(T, B)
                rowRemainingVerticalPositives[currentRow + 1] += 1				#(T, B)
                rowRemainingVerticalNegatives[currentRow + 1] += 1				#(T, B)
                columnRemainingVerticalPositives[currentColumn] += 1			#(T, B)
                columnRemainingVerticalNegatives[currentColumn] += 1			#(T, B)
            #X
            elif(currentTile == "X"):
                rowNumX[currentRow] += 1
                columnNumX[currentColumn] += 1

    neighbourLocations = {}
    magnetMRVs = {1: set(), 2: set(), 3: set()}
    for position in magnetLocations:
        countMRV = calcMRV(board, specs, position)
        magnetMRVs[countMRV].add(position)
        rowOne, columnOne, rowTwo, columnTwo = position
        neighbours = []
        for neighbourPosition in magnetLocations:
            if(neighbourPosition == position):
                continue
            neighbourRowOne, neighbourColumnOne, neighbourRowTwo, neighbourColumnTwo = neighbourPosition
            if(neighbourRowOne == rowOne or neighbourRowOne == rowTwo or neighbourRowTwo == rowOne or neighbourRowTwo == rowTwo or neighbourColumnOne == columnOne or neighbourColumnOne == columnTwo or neighbourColumnTwo == columnOne or neighbourColumnTwo == columnTwo):
                neighbours.append(neighbourPosition)
        neighbourLocations[position] = neighbours
    global dfsCallCount
    dfsCallCount = 0
    result = dfs(board, specs, numRows, numColumns)
    print(f"DFS calls: {dfsCallCount}")
    return result

def dfs(board, specs, numRows, numColumns):
    global dfsCallCount
    dfsCallCount += 1
    if(len(magnetMRVs[1]) > 0):
        position = next(iter(magnetMRVs[1]))
        magnetMRVs[1].remove(position)
    elif(len(magnetMRVs[2]) > 0):
        position = next(iter(magnetMRVs[2]))
        magnetMRVs[2].remove(position)
    elif(len(magnetMRVs[3]) > 0):
        position = next(iter(magnetMRVs[3]))
        magnetMRVs[3].remove(position)
    else:
        if(validateConfiguration(board, specs)):
            return [row[:] for row in board]
        return None

    rowOne, columnOne, rowTwo, columnTwo = position

    tileOne = board[rowOne][columnOne]
    tileTwo = board[rowTwo][columnTwo]

    #See if horizontal magnet can exist, columns differ rows are same
    if(horizontalPlacementExists(tileOne, board, rowOne, columnOne, numRows, numColumns)):
        originalFirstCharge = tileOne
        originalSecondCharge = tileTwo
        #Try horizontal magnet in (+, -) orientation
        if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "+", "-", specs)):
            board[rowOne][columnOne] = "+"
            board[rowTwo][columnTwo] = "-"
            rowPositives[rowOne] += 1
            rowNegatives[rowOne] += 1
            columnPositives[columnOne] += 1
            columnNegatives[columnTwo] += 1
            rowRemainingHorizontalPositives[rowOne] -= 1				#(L, R)
            rowRemainingHorizontalNegatives[rowOne] -= 1				#(L, R)
            columnRemainingHorizontalPositives[columnOne] -= 1			#(L, R)
            columnRemainingHorizontalNegatives[columnOne] -= 1			#(L, R)
            columnRemainingHorizontalPositives[columnTwo] -= 1			#(L, R)
            columnRemainingHorizontalNegatives[columnTwo] -= 1			#(L, R)	
            neighboursUpdated = False
            if(forwardCheck(specs, numRows, numColumns)):
                #Update neighbouring magnet MRV(s)
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)
                neighboursUpdated = True		
                result = dfs(board, specs, numRows, numColumns)
                if (result):
                    return result

            #Backtrack
            board[rowOne][columnOne] = originalFirstCharge
            board[rowTwo][columnTwo] = originalSecondCharge
            rowPositives[rowOne] -= 1
            rowNegatives[rowOne] -= 1
            columnPositives[columnOne] -= 1
            columnNegatives[columnTwo] -= 1
            rowRemainingHorizontalPositives[rowOne] += 1				#(L, R)
            rowRemainingHorizontalNegatives[rowOne] += 1				#(L, R)
            columnRemainingHorizontalPositives[columnOne] += 1			#(L, R)
            columnRemainingHorizontalNegatives[columnOne] += 1			#(L, R)
            columnRemainingHorizontalPositives[columnTwo] += 1			#(L, R)
            columnRemainingHorizontalNegatives[columnTwo] += 1			#(L, R)
            #Restore neighbouring magnet MRV(s)
            if(neighboursUpdated):
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)

        #Try horizontal magnet in (-, +) orientation
        if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "-", "+", specs)):
            board[rowOne][columnOne] = "-"
            board[rowTwo][columnTwo] = "+"
            rowPositives[rowOne] += 1
            rowNegatives[rowOne] += 1
            columnNegatives[columnOne] += 1
            columnPositives[columnTwo] += 1
            rowRemainingHorizontalPositives[rowOne] -= 1				#(L, R)
            rowRemainingHorizontalNegatives[rowOne] -= 1				#(L, R)
            columnRemainingHorizontalPositives[columnOne] -= 1			#(L, R)
            columnRemainingHorizontalNegatives[columnOne] -= 1			#(L, R)
            columnRemainingHorizontalPositives[columnTwo] -= 1			#(L, R)
            columnRemainingHorizontalNegatives[columnTwo] -= 1			#(L, R)	
            neighboursUpdated = False
            if(forwardCheck(specs, numRows, numColumns)):
                #Update neighbouring magnet MRV(s)
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)
                neighboursUpdated = True		
                result = dfs(board, specs, numRows, numColumns)
                if (result):
                    return result

            #Backtrack
            board[rowOne][columnOne] = originalFirstCharge
            board[rowTwo][columnTwo] = originalSecondCharge
            rowPositives[rowOne] -= 1
            rowNegatives[rowOne] -= 1
            columnNegatives[columnOne] -= 1
            columnPositives[columnTwo] -= 1
            rowRemainingHorizontalPositives[rowOne] += 1				#(L, R)
            rowRemainingHorizontalNegatives[rowOne] += 1				#(L, R)
            columnRemainingHorizontalPositives[columnOne] += 1			#(L, R)
            columnRemainingHorizontalNegatives[columnOne] += 1			#(L, R)
            columnRemainingHorizontalPositives[columnTwo] += 1			#(L, R)
            columnRemainingHorizontalNegatives[columnTwo] += 1			#(L, R)
            #Restore neighbouring magnet MRV(s)
            if(neighboursUpdated):
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)

        #Try skipping this magnet slot
        board[rowOne][columnOne] = "X"
        board[rowTwo][columnTwo] = "X"
        rowRemainingHorizontalPositives[rowOne] -= 1				#(L, R)
        rowRemainingHorizontalNegatives[rowOne] -= 1				#(L, R)
        columnRemainingHorizontalPositives[columnOne] -= 1			#(L, R)
        columnRemainingHorizontalNegatives[columnOne] -= 1			#(L, R)
        columnRemainingHorizontalPositives[columnTwo] -= 1			#(L, R)
        columnRemainingHorizontalNegatives[columnTwo] -= 1			#(L, R)	
        neighboursUpdated = False
        if(forwardCheck(specs, numRows, numColumns)):
            #Update neighbouring magnet MRV(s)
            for neighbourPosition in neighbourLocations[position]:
                if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                    magnetMRVs[1].discard(neighbourPosition)
                    magnetMRVs[2].discard(neighbourPosition)
                    magnetMRVs[3].discard(neighbourPosition)
                    neighbourMRV = calcMRV(board, specs, neighbourPosition)
                    magnetMRVs[neighbourMRV].add(neighbourPosition)
            neighboursUpdated = True
            result = dfs(board, specs, numRows, numColumns)
            if(result):
                return result

        #Backtrack
        board[rowOne][columnOne] = originalFirstCharge
        board[rowTwo][columnTwo] = originalSecondCharge
        rowRemainingHorizontalPositives[rowOne] += 1				#(L, R)
        rowRemainingHorizontalNegatives[rowOne] += 1				#(L, R)
        columnRemainingHorizontalPositives[columnOne] += 1			#(L, R)
        columnRemainingHorizontalNegatives[columnOne] += 1			#(L, R)
        columnRemainingHorizontalPositives[columnTwo] += 1			#(L, R)
        columnRemainingHorizontalNegatives[columnTwo] += 1			#(L, R)
        #Restore neighbouring magnet MRV(s)
        if(neighboursUpdated):
            for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)
        magnetMRVs[calcMRV(board, specs, position)].add(position)
        return None

    #See if vertical magnet can exist, rows differ columns are same
    if(verticalPlacementExists(tileOne, board, rowOne, columnOne, numRows, numColumns)):
        originalFirstCharge = tileOne
        originalSecondCharge = tileTwo
        #Try vertical magnet in (+, -) orientation
        if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "+", "-", specs)):
            board[rowOne][columnOne] = "+"
            board[rowTwo][columnTwo] = "-"
            rowPositives[rowOne] += 1
            rowNegatives[rowTwo] += 1
            columnNegatives[columnOne] += 1
            columnPositives[columnOne] += 1
            rowRemainingVerticalPositives[rowOne] -= 1					#(T, B)
            rowRemainingVerticalNegatives[rowOne] -= 1					#(T, B)
            rowRemainingVerticalPositives[rowTwo] -= 1					#(T, B)
            rowRemainingVerticalNegatives[rowTwo] -= 1					#(T, B)
            columnRemainingVerticalPositives[columnOne] -= 1			#(T, B)
            columnRemainingVerticalNegatives[columnOne] -= 1			#(T, B)
            neighboursUpdated = False
            if(forwardCheck(specs, numRows, numColumns)):
                #Update neighbouring magnet MRV(s)
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)
                neighboursUpdated = True
                result = dfs(board, specs, numRows, numColumns)
                if (result):
                    return result

            #Backtrack
            board[rowOne][columnOne] = originalFirstCharge
            board[rowTwo][columnTwo] = originalSecondCharge
            rowPositives[rowOne] -= 1
            rowNegatives[rowTwo] -= 1
            columnNegatives[columnOne] -= 1
            columnPositives[columnOne] -= 1
            rowRemainingVerticalPositives[rowOne] += 1					#(T, B)
            rowRemainingVerticalNegatives[rowOne] += 1					#(T, B)
            rowRemainingVerticalPositives[rowTwo] += 1					#(T, B)
            rowRemainingVerticalNegatives[rowTwo] += 1					#(T, B)
            columnRemainingVerticalPositives[columnOne] += 1			#(T, B)
            columnRemainingVerticalNegatives[columnOne] += 1			#(T, B)
            #Restore neighbouring magnet MRV(s)
            if(neighboursUpdated):
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)

        #Try vertical magnet in (-, +) orientation
        if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "-", "+", specs)):
            board[rowOne][columnOne] = "-"
            board[rowTwo][columnTwo] = "+"
            rowNegatives[rowOne] += 1
            rowPositives[rowTwo] += 1
            columnNegatives[columnOne] += 1
            columnPositives[columnOne] += 1
            rowRemainingVerticalPositives[rowOne] -= 1					#(T, B)
            rowRemainingVerticalNegatives[rowOne] -= 1					#(T, B)
            rowRemainingVerticalPositives[rowTwo] -= 1					#(T, B)
            rowRemainingVerticalNegatives[rowTwo] -= 1					#(T, B)
            columnRemainingVerticalPositives[columnOne] -= 1			#(T, B)
            columnRemainingVerticalNegatives[columnOne] -= 1			#(T, B)
            neighboursUpdated = False
            if(forwardCheck(specs, numRows, numColumns)):
                #Update neighbouring magnet MRV(s)
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)
                neighboursUpdated = True
                result = dfs(board, specs, numRows, numColumns)
                if (result):
                    return result

            #Backtrack
            board[rowOne][columnOne] = originalFirstCharge
            board[rowTwo][columnTwo] = originalSecondCharge
            rowNegatives[rowOne] -= 1
            rowPositives[rowTwo] -= 1
            columnNegatives[columnOne] -= 1
            columnPositives[columnOne] -= 1
            rowRemainingVerticalPositives[rowOne] += 1					#(T, B)
            rowRemainingVerticalNegatives[rowOne] += 1					#(T, B)
            rowRemainingVerticalPositives[rowTwo] += 1					#(T, B)
            rowRemainingVerticalNegatives[rowTwo] += 1					#(T, B)
            columnRemainingVerticalPositives[columnOne] += 1			#(T, B)
            columnRemainingVerticalNegatives[columnOne] += 1			#(T, B)
            #Restore neighbouring magnet MRV(s)
            if(neighboursUpdated):
                for neighbourPosition in neighbourLocations[position]:
                    if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                        magnetMRVs[1].discard(neighbourPosition)
                        magnetMRVs[2].discard(neighbourPosition)
                        magnetMRVs[3].discard(neighbourPosition)
                        neighbourMRV = calcMRV(board, specs, neighbourPosition)
                        magnetMRVs[neighbourMRV].add(neighbourPosition)

        #Try skipping this magnet slot
        board[rowOne][columnOne] = "X"
        board[rowTwo][columnTwo] = "X"
        rowRemainingVerticalPositives[rowOne] -= 1					#(T, B)
        rowRemainingVerticalNegatives[rowOne] -= 1					#(T, B)
        rowRemainingVerticalPositives[rowTwo] -= 1					#(T, B)
        rowRemainingVerticalNegatives[rowTwo] -= 1					#(T, B)
        columnRemainingVerticalPositives[columnOne] -= 1			#(T, B)
        columnRemainingVerticalNegatives[columnOne] -= 1			#(T, B)
        neighboursUpdated = False
        if(forwardCheck(specs, numRows, numColumns)):
            #Update neighbouring magnet MRV(s)
            for neighbourPosition in neighbourLocations[position]:
                if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                    magnetMRVs[1].discard(neighbourPosition)
                    magnetMRVs[2].discard(neighbourPosition)
                    magnetMRVs[3].discard(neighbourPosition)
                    neighbourMRV = calcMRV(board, specs, neighbourPosition)
                    magnetMRVs[neighbourMRV].add(neighbourPosition)
            neighboursUpdated = True
            result = dfs(board, specs, numRows, numColumns)
            if (result):
                return result

        # Backtrack
        board[rowOne][columnOne] = originalFirstCharge
        board[rowTwo][columnTwo] = originalSecondCharge
        rowRemainingVerticalPositives[rowOne] += 1					#(T, B)
        rowRemainingVerticalNegatives[rowOne] += 1					#(T, B)
        rowRemainingVerticalPositives[rowTwo] += 1					#(T, B)
        rowRemainingVerticalNegatives[rowTwo] += 1					#(T, B)
        columnRemainingVerticalPositives[columnOne] += 1			#(T, B)
        columnRemainingVerticalNegatives[columnOne] += 1			#(T, B)
        #Restore neighbouring magnet MRV(s)
        if(neighboursUpdated):
            for neighbourPosition in neighbourLocations[position]:
                if(board[neighbourPosition[0]][neighbourPosition[1]] == "L" or board[neighbourPosition[0]][neighbourPosition[1]] == "T"):
                    magnetMRVs[1].discard(neighbourPosition)
                    magnetMRVs[2].discard(neighbourPosition)
                    magnetMRVs[3].discard(neighbourPosition)
                    neighbourMRV = calcMRV(board, specs, neighbourPosition)
                    magnetMRVs[neighbourMRV].add(neighbourPosition)
        magnetMRVs[calcMRV(board, specs, position)].add(position)
        return None

    #No valid placement found
    #heapq.heappush(minMRVHeap, (countMRV, position))
    magnetMRVs[calcMRV(board, specs, position)].add(position)
    return None

#charge is either + or -
def placeable(board, firstRow, firstColumn, secondRow, secondColumn, firstCharge, secondCharge, specs): 
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

def forwardCheck(specs, numRows, numColumns):
	left, right, top, bottom = specs

	#Check all rows
	for currentRow in range(numRows):
		if(left[currentRow] > 0 and right[currentRow] > 0):
			if(rowPositives[currentRow] > left[currentRow] or rowNegatives[currentRow] > right[currentRow] or (rowPositives[currentRow] + rowRemainingHorizontalPositives[currentRow] + rowRemainingVerticalPositives[currentRow]) < left[currentRow] or (rowNegatives[currentRow] + rowRemainingHorizontalNegatives[currentRow] + rowRemainingVerticalNegatives[currentRow]) < right[currentRow]):
				return False
		elif(left[currentRow] > 0 and right[currentRow] == -1):
			if(rowPositives[currentRow] > left[currentRow] or (rowPositives[currentRow] + rowRemainingHorizontalPositives[currentRow] + rowRemainingVerticalPositives[currentRow]) < left[currentRow]):
				return False
		elif(left[currentRow] == -1 and right[currentRow] > 0):
			if(rowNegatives[currentRow] > right[currentRow] or (rowNegatives[currentRow] + rowRemainingHorizontalNegatives[currentRow] + rowRemainingVerticalNegatives[currentRow]) < right[currentRow]):
				return False
		elif(left[currentRow] > 0 and right[currentRow] == 0):
			#Horizontals can't be placed, only verticals contribute positives
			if(rowPositives[currentRow] > left[currentRow] or (rowPositives[currentRow] + rowRemainingVerticalPositives[currentRow]) < left[currentRow]):
				return False
		elif(left[currentRow] == 0 and right[currentRow] > 0):
			#Horizontals can't be placed, only verticals contribute negatives
			if(rowNegatives[currentRow] > right[currentRow] or (rowNegatives[currentRow] + rowRemainingVerticalNegatives[currentRow]) < right[currentRow]):
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
			if(columnPositives[currentColumn] > top[currentColumn] or columnNegatives[currentColumn] > bottom[currentColumn] or (columnPositives[currentColumn] + columnRemainingVerticalPositives[currentColumn] + columnRemainingHorizontalPositives[currentColumn]) < top[currentColumn] or (columnNegatives[currentColumn] + columnRemainingVerticalNegatives[currentColumn] + columnRemainingHorizontalNegatives[currentColumn]) < bottom[currentColumn]):
				return False
		elif(top[currentColumn] > 0 and bottom[currentColumn] == -1):
			if(columnPositives[currentColumn] > top[currentColumn] or (columnPositives[currentColumn] + columnRemainingVerticalPositives[currentColumn] + columnRemainingHorizontalPositives[currentColumn]) < top[currentColumn]):
				return False
		elif(top[currentColumn] == -1 and bottom[currentColumn] > 0):
			if(columnNegatives[currentColumn] > bottom[currentColumn] or (columnNegatives[currentColumn] + columnRemainingVerticalNegatives[currentColumn] + columnRemainingHorizontalNegatives[currentColumn]) < bottom[currentColumn]):
				return False
		elif(top[currentColumn] > 0 and bottom[currentColumn] == 0):
			#Verticals can't be placed, only horizontals contribute positives
			if(columnPositives[currentColumn] > top[currentColumn] or (columnPositives[currentColumn] + columnRemainingHorizontalPositives[currentColumn]) < top[currentColumn]):
				return False
		elif(top[currentColumn] == 0 and bottom[currentColumn] > 0):
			#Verticals can't be placed, only horizontals contribute negatives
			if(columnNegatives[currentColumn] > bottom[currentColumn] or (columnNegatives[currentColumn] + columnRemainingHorizontalNegatives[currentColumn]) < bottom[currentColumn]):
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

def calcMRV(board, specs, position):
	rowOne, columnOne, rowTwo, columnTwo = position
	count = 1
	if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "+", "-", specs)):
		count += 1
	if(placeable(board, rowOne, columnOne, rowTwo, columnTwo, "-", "+", specs)):
		count += 1
	return count

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