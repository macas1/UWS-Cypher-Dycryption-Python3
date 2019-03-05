###Libraries----------------------------------------------------------------------------------------
from math import ceil
from itertools import repeat, combinations

###Functions not called by __main__-----------------------------------------------------------------
def formatOutputData(string): #Adds spaces every 5 characters and capitalises
  string = string.replace(" ", "")
  newString = ""
  count = 0
  for char in string:
    newString += char.upper()
    count+=1
    if count % 5 == 0: newString += " "
  return newString.strip()

def formatOutputInt(intIn, intMax): #Creates a negative from positive int for output
  if intIn <= intMax/2:
    return str(intIn)
  else:
    return str(intIn-intMax)  

def sentenceFoundInString(string, dictionary): #Changes the data from senenceFoundInStringOne()[0] to booleans
  out = sentenceFoundInStringOne(string, dictionary[0], dictionary[1])
  if out[0] == "": return [True, out[1]]
  return [False, out[1]]
           
def sentenceFoundInStringOne(string, dictionary, errorWords, currentError=0): #Finds if a string without spaces countains only valid words
  newStrings = []
  for word in dictionary: #If string starts with a dict word then remove that dict word add it to newStrings
    if string.startswith(word):
      newStrings.append([string.replace(word, "", 1), currentError])

  for word in errorWords: #Similar to the above loop, but if an error word is found increment the currentError
    if string.startswith(word):
      newStrings.append([string.replace(word, "", 1), currentError+1])
  
  lowest = [] #Find solutions (empty strings) with the lowest output rate or continue recursive algorithm
  if len(newStrings):
    for s in newStrings:
      if s[0] != "" and s[0] != "~": s = sentenceFoundInStringOne(s[0], dictionary, errorWords, s[1]) #If the string is not a final solution and can be further shortened run it again
      if s[0] == "" and ((len(lowest)<1) or (s[1] < lowest[1])): lowest=s #If the string is a final solution and has less errors the the prevous lowest, make this the current lowest
  if len(lowest)>0: return lowest #If there is at least one final solution return it 
  return ["~", -1] #If no final solutions found  

###Functions called by __main__---------------------------------------------------------------------
class decryption:
  def deRot(inputLine, dictList, fileRotWords, alphabet, arg): #ROTX and ROTM decryption algorithm
    if arg == "auto": #If "auto" then give default arguments
      arg = [0, 26]
    else:
      arg = [arg, arg+1]

    attempts = [] #Record flawed outputs for later comparision
    for i in range(arg[0], arg[1]):
      for tWord in fileRotWords:  #this will only run once if ROTX
        newAlphabet = alphabet
        
        if fileRotWords != alphabet[0]: #If it's a modified ROT then create a new alphabet
          newAlphabet = []
          for letter in list(tWord) + alphabet: #Add technical word letters then alphabet letters to the new alphabet with no duplicates
            if letter not in newAlphabet:
              newAlphabet.append(letter)
      
        shiftedString  = ""  #Create output string letter by letter from the old and new alphabets and the shift distance
        for letter in inputLine:
          shiftedString += alphabet[(newAlphabet.index(letter)-i) % len(alphabet)]
      
        found = ""      #If only one possible output add "Found: " if it forms a valid sentence
        if arg != [0, 26]: 
          found = "Found: "
          
        ans = sentenceFoundInString(shiftedString, dictList)[1] #Check if the output string forms a valid sentence
        if ans == 0: #If a perfect solution is found
          if tWord == alphabet[0]: return [True, found + formatOutputData(shiftedString) + ",C," + str(formatOutputInt(i, 26))] #Non-modified rot return
          return [True, found + formatOutputData(shiftedString) + ",M," + tWord + "," + str(formatOutputInt(i, 26))] #Modified rot output return

        if ans > 0: #If a flawed solution is found
          if tWord == alphabet[0]:
            attempts.append([ans, found + formatOutputData(shiftedString) + ",C," + str(formatOutputInt(i, 26))]) #Non-modified rot added to attempts
          else:
            attempts.append([ans, found + formatOutputData(shiftedString) + ",M," + tWord + "," + str(formatOutputInt(i, 26))]) #Modified rotoutput added to attempts
          if arg != [0, 26]: return attempts[0]

        if arg != [0, 26]: #If no solution and only one solution, output the result anyway with a not found message
          if tWord == alphabet[0]:
            return [False, "Valid sentence not found: " + formatOutputData(shiftedString) + ",C," + str(formatOutputInt(i, 26))]
          else:
            return [False, "Valid sentence not found: " + formatOutputData(shiftedString) + ",M," + tWord + "," + str(formatOutputInt(i, 26))]    
    return [False, attempts] #If multiple possible solutions and none are prefect, return the possible flawed solutions

  def deCol(inputLine, dictList, arg): #Colomner transposition decryption algorithm
    if arg == "auto": #If "auto" then give default arguments
      arg = [1, len(inputLine)]
    else:
      arg = [arg-1, arg]

    attempts = [] #Record flawed outputs for later comparision
    for rowNo in range(arg[1], arg[0], -1): #This line loops through backwards. While testing the questions I've come to the assumption that this is the order we should search in

      highestMultipleOfRowNo = rowNo #Find the amount of blank spaces required (gaps) and the required amount of columns
      while len(inputLine) > highestMultipleOfRowNo:
        highestMultipleOfRowNo += rowNo
      gaps = highestMultipleOfRowNo % len(inputLine)
      columnNo = int(highestMultipleOfRowNo/rowNo)

      columns = [[] for i in repeat(None, rowNo)] #Create correct amount of columns
 
      count = len(columns)-1 #Insert gaps into final column
      for x in range(gaps):
        columns[count].append("-")
        count -= 1
        if count < 0: count = len(columns)-1

      count = 0             #Insert all other characters
      for row in columns:
        while len(row) < columnNo:
          row.append(inputLine[count])
          count+=1

      for row in columns: #Move gaps from front to end of column
        while row[0] == "-":
          row.pop(0)
          row.append("-")

      columns = list(map(list, zip(*columns))) #transpose matrix

      string = ""         #Get new string from columns ignoring gap characters 
      for row in columns:
        for data in row:
          if data != "-": string += data
    
      ans = sentenceFoundInString(string, dictList)[1] #Check if the output string forms a valid sentence
      if ans == 0: #If a perfect solution is found
        if arg == [1, len(inputLine)]: return [True, formatOutputData(string) + ",T," + str(rowNo)] #Return if in automatic mode
        return [True, "Found: " + formatOutputData(string) + ",T," + str(rowNo)] #Return the "Found: " string if manual

      if ans > 0: #If a flawed solution is found
        if arg == [1, len(inputLine)]:
          attempts.append([ans, formatOutputData(string) + ",T," + str(rowNo)]) #Add flawed solution to attemts is in automatic mode
        else:
          return [ans, "Found: " + formatOutputData(string) + ",T," + str(rowNo)] #Return flawed attempt if manual mode

      if arg != [1, len(inputLine)]: #If no answer and in manual mode output the result anyway
        return [False, "Valid sentence not found: " + formatOutputData(string) + ",T," + str(rowNo)]
    return [False, attempts]   #If multiple possible solutions and none are prefect, return the possible flawed solutions


  def deDia(inputLine, dictList, arg): #Diagonal transposition decryption algorithm
    negative = False #If "auto" then give default arguments, negative is used in manual mode to display the correct output
    if arg == "auto":
      arg = [1, len(inputLine)]
    else:
      if arg < 0:
        arg = arg*-1
        negative = True
      arg = [arg, arg+1]

    attempts = [] #Record flawed outputs for later comparision
    for rowNo in range(arg[0], arg[1]):
      highestMultipleOfRowNo = rowNo  #Find the amount of blank spaces required (gaps) and the required amount of columns
      while len(inputLine) > highestMultipleOfRowNo:
        highestMultipleOfRowNo += rowNo
      gaps = highestMultipleOfRowNo % len(inputLine)
      columnNo = int(highestMultipleOfRowNo/rowNo)

      maxDiagLen = columnNo  #Find longest and shortest side of the matrix
      longestSide = rowNo
      if rowNo < columnNo:
        maxDiagLen = rowNo
        longestSide = columnNo
    
      #Find max diagonals
      smallerDiagCount = maxDiagLen-1             #Find the amount smaller diagonals for each corner
      totalDiagCount = smallerDiagCount*2         #Add the smaller diagonals to the total
      largestDiagCount = longestSide-maxDiagLen+1 #Find the amount of max length diagonals in the center
      totalDiagCount += largestDiagCount          #Add all the longest diagonals to the total

      columnsPos = [[] for i in repeat(None, columnNo)] #Create correct amount of columns
      columnsNeg = [[] for i in repeat(None, columnNo)]
      columnIndex = [] #A list of indecies representing rows. Relative to the positions of each character in the input sting

      firstNumber = columnNo  #This is the first number for the process of appended input string characters to rows. Start at the end, build it backwards
      loopCount = 0           #Used to find diagonal lengths based on what diagonal we are processing
      currentDiagLen = 1
      while firstNumber >= 0:
        loopCount += 1
        count = firstNumber-currentDiagLen #Follow a diagonal line and add the row indexes for each relative character
        for i in range(currentDiagLen):  
          columnIndex.append(count)
          count += 1

        if loopCount >= rowNo: #If the current diagonal is up to left wall of matrix where the first number begins to decrement 
          firstNumber -=1
        if loopCount <= smallerDiagCount: #If the in the first corner and the current diagonal length is increasing
          currentDiagLen += 1
        if loopCount >= smallerDiagCount + largestDiagCount: #If the in the last corner and the current diagonal length is decreasing
          currentDiagLen -= 1

      columnIndexPos = columnIndex[:] #Solve for both positive and negative
      columnIndexNeg = columnIndex[:] 
      columnIndexNeg.reverse()      #Reverse index list to solve for negative
      count = 0
      for i in range(gaps):         #Remove "0" values from index lists
        columnIndexPos.remove(0)
        columnIndexNeg.remove(0)
      
      columnIndexPos.reverse() #Create text matricies from indexes
      columnIndexNeg.reverse()
      for x in range(len(inputLine)):
        columnsPos[columnIndexPos[x]].append(inputLine[x])
        columnsNeg[columnIndexNeg[x]].append(inputLine[x])

      columnsPos.reverse()  #Flatten list into columns and get strings from text matricies. Also rotate the negative one by 1 position
      newList = []  
      for subList in columnsPos:
        newList += subList
      outPos = "".join(newList)

      columnsNeg.reverse()
      newList = []  
      for subList in columnsNeg:
        newList += subList
      outNeg = "".join(newList)

      #Check if it can form a valid solutions with either positive or negative
      ansNeg = [sentenceFoundInString(outNeg, dictList)[1], formatOutputData(outNeg) + ",D,-" + str(rowNo)] 
      ansPos = [sentenceFoundInString(outPos, dictList)[1], formatOutputData(outPos) + ",D," + str(rowNo)]

      if arg != [1, len(inputLine)]: #If in single output mode
        if negative:    #If manually looking for negative
          if ansNeg[0] == 0: return [True, "Found: " + formatOutputData(outNeg) + ",D,-" + str(rowNo)] #If perfect negative solution found return it
          elif ansNeg[0] > 0: attempts.append([ansNeg[1], "Found: " + formatOutputData(outNeg) + ",D,-" + str(rowNo)]) #If flawed negative solution found add it to attempts
          else: return [False, "Valid sentence not found: " + formatOutputData(outNeg) + ",D,-" + str(rowNo)] #If no solutions found return it
        else: #If manually looking for positive
          if ansPos[0] == 0: return [True, "Found: " + formatOutputData(outPos) + ",D," + str(rowNo)] #If perfect positive solution found return it
          elif ansPos[0] > 0: attempts.append([ansPos[1], "Found: " + formatOutputData(outPos) + ",D," + str(rowNo)]) #If positive answer with errors found add it to attempts
          else: return [False, "Valid sentence not found: " + formatOutputData(outPos) + ",D," + str(rowNo)] #If no solutions found return it
      else: #It autiomatic mode
        if ansNeg[0] == 0: return [True, formatOutputData(outNeg) + ",D,-" + str(rowNo)] #If perfect negative solution found
        if ansNeg[0] > 0: attempts.append([ansNeg[0], formatOutputData(outNeg) + ",D,-" + str(rowNo)]) #If flawed negative solution found add it to attempts
        if ansPos[0] == 0: return [True, formatOutputData(outPos) + ",D," + str(rowNo)] #If perfect positive solution found
        if ansPos[0] > 0: attempts.append([ansPos[0], formatOutputData(outPos) + ",D," + str(rowNo)]) #If flawed positive solution found add it to attempts
    return [False, attempts] #If multiple possible solutions and none are prefect, return the possible flawed solutions
