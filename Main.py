from Classes.GUI_andErrorChecking import menuMain
from Classes.Decryption import decryption
import time 

alphabet      = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"] #Can be changed but can not contain any of the following characters: "~", "!", "-"
commonErrors  = ["a", "n", "ight", "decision", "acnkowledgment"] #Words counted as an flawed solution. The program outputs the least flawed solution

##Functions-----------------------------------------------------------------------------------------
def runTime(seconds): #Outputs how long the program has been running
  m, s = divmod(int(seconds), 60)
  h, m = divmod(m, 60)
  return "%d:%02d:%02d" % (h, m, s)

def writeToFile(file, line): #This is so if the program is closed mid way a the partial output will still be saves in the file
  f = open(file, "a") 
  f.write(line + "\n")
  f.close()

def getLowest(arr): #Sort for the lowest x and return y in [[x, y], [x, y]...]
  lowest = arr[0]
  for a in arr:
    if a[0] < lowest[0]: lowest = a
  return lowest[1]
  
def decryptAuto(inputLine, dictionary, tWords, alphabet=alphabet):
  attempts = []

  #Print and run ROTX
  print(runTime(time.clock()-start), "START ROTX")
  ans = decryption.deRot(inputLine, dictionary, alphabet[0], alphabet, "auto")
  if ans[0]:
    if isinstance(ans[1], list):
      attempts += ans[1][0]
    else:
      return ans[1]
  else:
    attempts += ans[1]

  #Print and run columner
  print(runTime(time.clock()-start), "START COLUMN")
  ans = decryption.deCol(inputLine, dictionary, "auto")
  if ans[0]:
    if isinstance(ans[1], list):
      attempts += ans[1][0]
    else:
      return ans[1]
  else:
    attempts += ans[1]

  #Print and run Diagonal
  print(runTime(time.clock()-start), "START DIAGONAL")
  ans = decryption.deDia(inputLine, dictionary, "auto")
  if ans[0]:
    if isinstance(ans[1], list):
      attempts += ans[1][0]
    else:
      return ans[1]
  else:
    attempts += ans[1]
    
  #Print and run ROTM
  print(runTime(time.clock()-start), "START MODIFIED ROT")
  ans = decryption.deRot(inputLine, dictionary, data.outTwords, alphabet, "auto")
  if ans[0]:
    if isinstance(ans[1], list):
      attempts += ans[1][0]
    else:
      return ans[1]
  else:
    attempts += ans[1]

  #If no perfect output was returned, return the least flawed output that minimal contained errors
  if len(attempts):
    print(runTime(time.clock()-start), "START CHECKING FOR POSSIBLE ERRORS ("+str(len(attempts))+")")
    return getLowest(attempts)

  #If no perfect or flawed matches were found return a failed line
  return "FAILED: " + inputLine


##Main----------------------------------------------------------------------------------------------
data = menuMain(alphabet) #Run the main menu prompt
if data.output:           #If the main menu was closed via the "run" button being pressed
  start = time.clock()    #Record the starting time for later runtime comparisions
  dictSet = [data.outDict, commonErrors] #Get the dictionary from the menu and the common error words from this script
  print("Starting decryption.\nThe line 'DONE' will be printed when the program has completed.\n") #starting message

  if data.auto: #Automatic decryption
    notFound = [] #Recorded
    count = 0     #recorded for output purposes
    for inLine in data.outInput:
      count += 1
      print("Count:", count, "Length:", len(inLine))          #Print line header
      ans = decryptAuto(inLine.replace(" ", ""), dictSet, data.outTwords, alphabet) #Decrypt the line
      if ans.startswith("FAILED: "): notFound.append(inLine)  #If the line failed, record it
      writeToFile(data.outOutput, ans)                        #Output result
      print(runTime(time.clock()-start), ans, "\n")           #print output

    if len(notFound): print("Failed strings: ", str(len(notFound))+"/"+str(len(data.outInput)), "\n", notFound) #Print failed strings

  else: #If manual data.manual = [cipher type (0-5), args (rot rotation or column number), tword]
    inLine = data.outInput.replace(" ", "") #Remove spaces from input
    output = "FAILED: " + inLine            #Prepare output message
    
    arg = data.manual[1] #If no argument, used default ones with the "auto" tag
    if not arg: arg = "auto"
    
    twords = data.manual[2] #If no technical defined word, pull the list from the file
    if not twords: twords = data.outTwords
    
    if data.manual[0] == 0:
      output = decryptAuto(inLine, dictSet, twords)                 
      print(output)                        #Print output
      writeToFile(data.outOutput, output)  #Write output to fil
    else:
      if data.manual[0] == 1: output = decryption.deRot(inLine, dictSet, alphabet[0], alphabet, arg)  #Dectrypt ROTX
      if data.manual[0] == 2: output = decryption.deRot(inLine, dictSet, twords, alphabet, arg)       #Dectrypt ROTM
      if data.manual[0] == 3: output = decryption.deCol(inLine, dictSet, arg)                         #Dectrypt Columner
      if data.manual[0] == 4: output = decryption.deDia(inLine, dictSet, arg)                         #Dectrypt Diagonal
      
      if isinstance(output[1], list): #If flawed solutions, output the least flawed
        ans = getLowest(output[1])
        print(ans) #Print output
        writeToFile(data.outOutput, ans) #Write output to file
      else: #If perfect or no solution
        print(output[1])                        #Print output
        writeToFile(data.outOutput, output[1])  #Write output to file
    

print("\nDONE") #Print done message
