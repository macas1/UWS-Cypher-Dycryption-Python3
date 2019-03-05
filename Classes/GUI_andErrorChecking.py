##Imports-----------------------------------------------------------------------------------------------------------------------------------
try: #Trys to import it for windows Py3. if it fails try for UNIX Py3 (Untested on UNIX)
  from tkinter import *
  from tkinter import messagebox
  from tkinter.filedialog import askopenfile, asksaveasfilename
except ImportError:
  from Tkinter import *
  import tkMessageBox as messagebox
  from tkFileDialog import askopenfile, asksaveasfilename

from os.path import dirname, abspath, join, basename, isfile
from itertools import repeat
import glob

##Variables and functions that don't rely on self-------------------------------------------------------------------------------------------
parentPath = dirname(dirname(abspath(__file__)))

def specialIn(string, array): #Checks if a string is in an array reguardless of types of spacer ("", " ", "_")
  arr = []
  for x in array: #Include *_file in the search
    arr.append(x)
    arr.append(x + "_file")
               
  if string in arr: return True
  for x in arr:
    x = x.replace("_", " ")
    if string == x: return True
               
    x = x.replace(" ", "")
    if string == x: return True
  return False

def fixPath(path): #Fixes the name string to the OS's desafult path divider
  for x in ["\\", "/"]:
    if x in path:
      path = join(*path.split(x))

  path = path.replace(":", ":\\") #Fixes the output for windows. UNIX has no issue
  return join(path)

def selectTxtFile(strTitle, path=parentPath): #Opens a prompt where a user can select a text file to import, returns its path (or False if none chosen)
  fileName = askopenfile(initialdir = path,
                        title       = strTitle,
                        filetypes   = (("Text files","*.txt"), ("Text files","*.txt")))
  if fileName: #If it's not NoneType
    fileName = fileName.name
    return fixPath(fileName)
  else:
    False

def errorCheck(files): #Returns a list of the errors for each file
  errors = [[] for i in repeat(None, len(files))]

  for index in range(len(files)):
    filePath = files[index]

    auto = True #If manual mode, the one input line is checked not a whole file
    if filePath.startswith("::::"):
      filePath = filePath[4:]
      auto = False

    if auto and not isfile(filePath): #Check if the file exists
      errors[index].append("exist")
    elif auto and not filePath.endswith(".txt"): #Check that it's a text file
      errors[index].append("txt")
    else:    #Check for invalid formats
      file = [filePath.strip()] #Make sure you are reading from the input and from the file in the correct situations
      if auto: file = open(filePath).read().strip().split("\n")

      for i in range(len(file)):
        line = file[i]
        if len(file) < 2 and not line.replace(" ", ""): #Check if the whole file is blank
          errors[index].append("blank")
          break
        
        if "blank"    not in errors[index] and i < len(file)-1 and not line.replace(" ", ""): errors[index].append("blank")#Check if lines are blank (ignoring final one)
        if "letters"  not in errors[index] and not line.replace(" ", "").isalpha(): errors[index].append("letters")       #Check if file only contains spaces and letters
        if "oneWord"  not in errors[index] and line != line.replace(" ", ""): errors[index].append("oneWord")             #Check if there in only one word per line
        if "inSpaces" not in errors[index]: #Check if the input file format is wrong (5 spaces per section)
          words = line.split(" ")
          for w in range(len(words)):
            if (w < len(words)-1 and len(words[w]) < 5) or len(words[w]) > 5: #Checks not last word and length of word = 5
              errors[index].append("inSpaces") 
              break
  return errors

def menuBar_credits(): #A messagebox output for the menubar
  msg = ("This program was coded by Bradley McInerney as an\n"
         "assessment for Computer Security at the University\n"
         "of Western Sydney 2017.")
  messagebox.showinfo("Credits", msg)
      
class menuMain:
  def __init__(self, alphabet):
    ##Create GUI window-------------------------------------------------------------
    self.root = Tk() #Create the window that will be be packed
    self.root.wm_title("Cipher Text Decrypter - Main Menu") #Window title
    self.root.resizable(0,0) #Make window not resizeable

    ###Initialization---------------------------------------------------------------
    self.auto = True          #The window opend in automatic mode
    self.alphabet = alphabet  #Add the alphabet

    self.inputFilePos = "" #Used to store inputs when switching modes back and fourth
    self.radioPos = 0 
    self.in1Pos = ""
    self.in2Pos = ""
    self.in3Pos = ""

    self.output = False #Flag, will be true if the menu closes via the "run" button
    self.packWindow()       #Pack top part of window
    self.packWindow_auto()  #Pack bottom (auto) part of window
    self.act_search()       #Seach for default files
    self.root.mainloop()    #Run window

  ##Functions---------------------------------------------------------------------
  def packWindow(self): #Packs the part of the window used by both automatic and manual modes
    ##Constants
    self.borderPad = 16
    self.textPad = 8
    ##Menu bar-----------
    menuBar = Menu(self.root)

    menuAbout = Menu(menuBar, tearoff=0) #Create the "About" menu
    menuAbout.add_command(label="Credits", command=menuBar_credits)
    menuBar.add_cascade(label="About", menu=menuAbout)

    self.root.config(menu=menuBar) #Display the menubar

    ##Window face--------
    #Heading
    Label(self.root, text="""Cipher Text Decrypter - Bradley McInerney 2017""").grid(row=0, columnspan=3, pady=(self.borderPad, 0))
    Label(self.root, text="""-"""*103).grid(row=1, columnspan=3)

    #File path inputs
    Label(self.root, text="""Dictionary File:""").grid(row=2, column=0, sticky=E, padx=(self.borderPad,0), pady=(self.textPad, 0))
    self.entry_dict = Entry(self.root, width=46)
    self.entry_dict.grid(row=2, column=1, columnspan=5, sticky=W, padx=(self.textPad, 0), pady=(self.textPad, 0))
    Button(self.root, text="Change", command=self.button_changeDictFile, width=10).grid(row=2, column=2, padx=(self.textPad, self.borderPad), pady=(self.textPad, 0))

    Label(self.root, text="""Technical Words File:""").grid(row=3, column=0, sticky=E, padx=(self.borderPad,0))
    self.entry_tWords = Entry(self.root, width=46)
    self.entry_tWords.grid(row=3, column=1, sticky=W, padx=(self.textPad, 0))
    Button(self.root, text="Change", command=self.button_changeTwordFile, width=10).grid(row=3, column=2, padx=(self.textPad, self.borderPad))

    Label(self.root, text="""Output File:""").grid(row=4, column=0, sticky=E, padx=(self.borderPad,0))
    self.entry_output = Entry(self.root, width=46)
    self.entry_output.grid(row=4, column=1, sticky=W, padx=(self.textPad, 0))
    Button(self.root, text="Change", command=self.button_changeOutputFile, width=10).grid(row=4, column=2, padx=(self.textPad, self.borderPad))
    
  def packWindow_auto(self): #Packs part of the window only used in automatic mode
    self.lowerFrame = Frame(self.root)
    self.lowerFrame.grid(row=5, columnspan=3, sticky=E)
    Label(self.lowerFrame, text="""Input File:""").grid(row=0, column=0, sticky=E, padx=(self.borderPad,0))
    self.entry_input = Entry(self.lowerFrame, width=46)
    self.entry_input.grid(row=0, column=1, sticky=W, padx=(self.textPad, 0))
    self.entry_input.insert(0, self.inputFilePos)
    Button(self.lowerFrame, text="Change", command=self.button_changeInputFile, width=10).grid(row=0, column=2, padx=(self.textPad, self.borderPad))

    #Lower buttons (From right to left)
    buttonFrame = Frame(self.lowerFrame)
    buttonFrame.grid(row=1, column=1, columnspan=2, sticky=SE, padx=(0, self.borderPad), pady=(self.borderPad, self.borderPad))
    Button(buttonFrame, text="Run", command=self.button_run, width=10).grid(row=0, column=2, padx=(self.textPad, 0), sticky=E)
    Button(buttonFrame, text="Search For Paths", command=self.button_search, width=14).grid(row=0, column=1, padx=(self.textPad, 0), sticky=E)
    Button(buttonFrame, text="Manual Decryption", command=self.button_manual, width=15).grid(row=0, column=0, sticky=E)
    
  def packWindow_manual(self):#Packs part of the window only used in manual mode
    self.lowerFrame = Frame(self.root)
    self.lowerFrame.grid(row=5, columnspan=3, sticky=E)

    self.radioFrame = Frame(self.lowerFrame)
    self.radioFrame.grid(row=0, sticky=E)
    Label(self.radioFrame, text="""Encryption Type:""").grid(row=0, column=0, sticky=W, padx=(self.borderPad,0), pady=(self.borderPad,0)) #Pack radio button
    inputModes = [("Unknown", 0),
                  ("ROTX Cipher", 1),
                  ("Modified ROT Cipher", 2),
                  ("Columnar Transposition Cipher", 3),
                  ("Diagonal Transposition Cipher", 4)]
    self.inMode = IntVar()
    self.inMode.set(self.radioPos)
    x = 0
    for text, mode in inputModes:
      py = 0 #Pad y, only apllies on final line
      if x == 4: py = self.borderPad
      b = Radiobutton(self.radioFrame, text=text, variable=self.inMode, value=x, command=self.radioButtonPack)
      b.grid(row=x+1, column=0, sticky=W, padx=(self.borderPad,0), pady=(0,py))
      x += 1

    self.firstPack = True #Will be false when running radioButtonPack from the onChange command
    self.radioButtonPack()

    #Lower buttons (From right to left)
    buttonFrame = Frame(self.lowerFrame)
    buttonFrame.grid(row=0, column=1, columnspan=2, sticky=SE, padx=(0, self.borderPad), pady=(self.borderPad, self.borderPad))
    Button(buttonFrame, text="Run", command=self.button_run, width=10).grid(row=0, column=2, padx=(self.textPad, 0), sticky=E)
    Button(buttonFrame, text="Search For Paths", command=self.button_search, width=14).grid(row=0, column=1, padx=(self.textPad, 0), sticky=E)
    Button(buttonFrame, text="Automatic Decryption", command=self.button_auto, width=18).grid(row=0, column=0, padx=(self.textPad+2, 0), sticky=E)

  def radioButtonPack(self): #Runs every time the radio button is changed. Packs input entries relative to cipher mode
    if not self.firstPack: #Use data from last time if not it's firt time being packed
      self.in1Pos = self.entryIn1.get()
      self.inputFrame.grid_forget()
      self.inputFrame.destroy()

    self.inputFrame = Frame(self.lowerFrame)
    self.inputFrame.grid(row=0, column=1, columnspan=2, sticky=NE)
    
    #Create Main input (cipher text)
    Label(self.inputFrame, text="""Cipher Text:""").grid(row=0, column=0, sticky=W, padx=(self.textPad,0), pady=(self.borderPad,0))
    self.entryIn1 = Entry(self.inputFrame, width=30)
    self.entryIn1.grid(row=0, column=1, sticky=W, padx=(self.textPad,self.borderPad), pady=(self.borderPad,0))
    self.entryIn1.insert(0, self.in1Pos)

    #Create Second input (rotation or column size depending on cipher type)
    if self.inMode.get():
      text = "Rotation (If Known):"
      if self.inMode.get() > 2:
        text = "Column Size (If Known):"
      
      Label(self.inputFrame, text=""+text+"").grid(row=1, column=0, sticky=W, padx=(self.textPad,0))
      self.entryIn2 = Entry(self.inputFrame, width=30)
      self.entryIn2.grid(row=1, column=1, sticky=W, padx=(self.textPad,self.borderPad))
      if self.firstPack: self.entryIn2.insert(0, self.in2Pos)

    if self.inMode.get() == 2: #Create technical word input
      Label(self.inputFrame, text="""Technical Word (If Known):""").grid(row=2, column=0, sticky=W, padx=(self.textPad,0))
      self.entryIn3 = Entry(self.inputFrame, width=30)
      self.entryIn3.grid(row=2, column=1, sticky=W, padx=(self.textPad,self.borderPad))
      if self.firstPack: self.entryIn3.insert(0, self.in3Pos)
      
    if self.firstPack: self.firstPack = False          
  
  def act_search(self): #Look for and create default paths for input files
    assumedPathDict   = ""
    assumedPathTwords = ""
    assumedPathInput  = ""
    assumedPathOutput = ""

    for filePath in glob.glob(join(parentPath, "*.txt")): #List all .txt files in the parent folder
      fileName = basename(filePath)[:-4].lower()
      #Try to find possible files via their assumed names
      if specialIn(fileName, ["dict_en", "dict", "dictionary"]): assumedPathDict = filePath
      if specialIn(fileName, ["words", "t_words", "technical_words"]): assumedPathTwords = filePath
      if specialIn(fileName, ["out", "output"]): assumedPathOutput = filePath
      if self.auto and specialIn(fileName, ["in", "input"]): assumedPathInput = filePath
    if not assumedPathOutput: assumedPathOutput = join(parentPath, "output.txt") #If there is no output file, add a path because a new one will be created

    #Refresh entry widgets
    self.entry_dict.delete(0, END)
    self.entry_dict.insert(0, assumedPathDict)
    self.entry_tWords.delete(0, END)
    self.entry_tWords.insert(0, assumedPathTwords)
    self.entry_output.delete(0, END)
    self.entry_output.insert(0, assumedPathOutput)
    if self.auto:
      self.entry_input.delete(0, END)
      self.entry_input.insert(0, assumedPathInput)

  def button_search(self): #Warning when searching for new file paths
    message = ("Are you sure you would like to search the parent folder for file paths.\n"
               "Only file names known by the program in the parent directory of this script will be found.\n"
               "The new paths will replace the ones in the menu.\n\n"
               "(Unless the files have been changed, the paths will become the same as when the program was opened)")
  
    if messagebox.askyesno("Are you sure?", message):
      self.act_search()

  def button_manual(self): #Switches to manual mode
    #Save data for when it is switched back
    self.inputFilePos = self.entry_input.get()

    #Remove frames not needed for the change then pack new ones
    self.lowerFrame.grid_forget()
    self.lowerFrame.destroy()
    self.auto = False
    self.packWindow_manual()

  def button_auto(self): #Switches to automatic mode
    #Save data for when it is switched back
    self.radioPos = self.inMode.get()
    self.in1Pos = self.entryIn1.get()
    if self.radioPos: self.in2Pos = self.entryIn2.get()
    if self.radioPos == 2: self.in3Pos = self.entryIn3.get()

    #Remove frames not needed for the change then pack new ones
    self.lowerFrame.grid_forget()
    self.lowerFrame.destroy()
    self.auto = True
    self.packWindow_auto()

  def button_changeDictFile(self): #Opens a prompt to find a new txt file. Active on button
    file = selectTxtFile("Select dictionary file")
    if file:
      self.entry_dict.delete(0, END)
      self.entry_dict.insert(0, file)

  def button_changeTwordFile(self): #Opens a prompt to find a new txt file. Active on button
    file = selectTxtFile("Select technical word file")
    if file:
      self.entry_tWords.delete(0, END)
      self.entry_tWords.insert(0, file)

  def button_changeInputFile(self): #Opens a prompt to find a new txt file. Active on button
    file = selectTxtFile("Select input file")
    if file:
      self.entry_input.delete(0, END)
      self.entry_input.insert(0, file)
                     
  def button_changeOutputFile(self): #Opens a prompt to find or create a new txt file. Active on button
    file = asksaveasfilename(initialdir = parentPath,
                            title       = "Select or create output file",
                            filetypes   = (("Text files","*.txt"), ("Text files","*.txt")))
  
    if file: #If it's not NoneType
      if not file.endswith(".txt"): file += ".txt" #Make it text files only
      file = fixPath(file)
      self.entry_output.delete(0, END)
      self.entry_output.insert(0, file)

  def button_run(self): #Activates on run button, checks for errors befor running
    
    inCheck = "" #Create a variable for the input regaurdless if it's from an automatic or manual window
    if self.auto:
      inCheck = self.entry_input.get()
    else:
      inCheck = "::::" + self.entryIn1.get()

    manual = [None]*3 #Holds manual arguments to pe processed in the main file
    files = [self.entry_dict.get(), self.entry_tWords.get(), self.entry_output.get(), inCheck] #Get in a list
    errors = errorCheck(files) #Get list of errors for each file
    
    #Check for errors that would prevent runing
    errorMessage = "The following errors are preventing the script from running:\n\nDictionary File:\n"
    if "exist"    in errors[0]: errorMessage += "    >This file does not exist.\n"
    if "txt"      in errors[0]: errorMessage += "    >This file is not a .txt file.\n"
    if "blank"    in errors[0]: errorMessage += "    >This file has blank lines in it.\n"
    if "letters"  in errors[0]: errorMessage += "    >This file can only contain letters and new line characters\n"
    if "oneWord"  in errors[0]: errorMessage += "    >One or more lines in this file contain more than one word.\n"

    errorMessageT = "Technical Words File:\n"
    if "txt"      in errors[1]: errorMessageT += "    >This file is not a .txt file.\n"
    if "blank"    in errors[1]: errorMessageT += "    >This file has blank lines in it.\n"
    if "letters"  in errors[1]: errorMessageT += "    >This file can only contain letters and new line characters\n"
    if "oneWord"  in errors[1]: errorMessageT += "    >One or more lines in this file contain more than one word.\n"

    #Input Section----------------------------------------------------------------------------------------------------
    if self.auto:
      errorMessage += "\n" + errorMessageT
      errorMessage += "\nInput File:\n"
      if "txt"      in errors[3]: errorMessage += "    >This file is not a .txt file.\n"
      if "blank"    in errors[3]: errorMessage += "    >This file has blank lines in it.\n"
      if "letters"  in errors[3]: errorMessage += "    >This file can only contain letters, spaces and new line characters\n"
      if "inSpaces" in errors[3]: errorMessage += "    >This file is not correctly spaced to be a valid input file.\n       (Every 5 letters must be followed by a space).\n"
    else: #If manual input mode
      if self.inMode.get() == 2: #Id mod rot (requres third input)
        inp3 = self.entryIn3.get()
        if inp3:
          files[1] = "::::" + inp3.strip()
          errors[1] = errorCheck([files[1]])
          errors[1] = errors[1][0]
          errorMessage += "\nTechnical Words Input:\n"
          if "blank"    in errors[1]: errorMessage += "    >This input has blank lines in it.\n"
          if "letters"  in errors[1]: errorMessage += "    >This input can only contain letters and new line characters\n"
          if "oneWord"  in errors[1]: errorMessage += "    >This input can not contain more than one word.\n"
          manual[2] = [inp3.strip()] #Add twords to the manual output
        else:
          errorMessage += "\nNo manual input detected - " + errorMessageT #If manual tword not used use the errors for the file precessed earlier

      #Solve for other input
      errorMessage += "\nInput Data:\n"
      if "letters"  in errors[3]: errorMessage += "    >The input can only contain letters, spaces and new line characters\n"
      if "blank"    in errors[3]: errorMessage += "    >The input is blank.\n"
      if "inSpaces" in errors[3]: errorMessage += "    >The input is not correctly spaced to be a valid input file.\n       (Every 5 letters must be followed by a space).\n"

      #Solve for second input (rotation or column size)
      manual[0] = self.inMode.get()
      if self.inMode.get(): #If not all modes
        inp2 = self.entryIn2.get()
        if inp2: #Make sure the second input is not blank
          if self.inMode.get() > 2: #If transposition type
            try:
              inp2 = int(inp2) #Check if it can become an integer
              manual[1]=inp2
              
              #Check if in range
              if inp2 < 0: #If colomner, can't be negative
                if self.inMode.get() == 3:errorMessage += "    >Column Size must be positive.\n" 
                inp2 *= -1 #If negative make positive
              if inp2 > len(inCheck.replace(" ", "")): #Check for max range
                errorMessage += "    >Column Size must not be over input size.\n       (After spaces are removed).\n" #Remove spaces and : from input, round up by one then ceil and half it
              if inp2 != 0: #Can't be 0
                errorMessage += "    >Column Size must not be 0.\n"
                
            except ValueError: #If it fails to become an it
              errorMessage += "    >Column Size must be an integer.\n"
          else: #If rot, try to make the rotation an integer
            try:
              manual[1] = int(inp2)
            except:
              errorMessage += "    >Rotaton must be an integer.\n"
        else:
          manual[1] = False #If no input added

    #print(errors)
    run = True #The program will run unless an error it found
    if ">" in errorMessage: #The ">" character is used for every error
      messagebox.showerror("ERROR", errorMessage)
      run = False
    else:      
      #Show 'are you sure messages' for running without functionality and overwrite
      msg = ("The technial words file can not be found.\n"
            "Would you like to run the script without the modified rot function?")
      if "exist" in errors[1] and not messagebox.askyesno("Are you sure?", msg):
        messagebox.showerror("ERROR", "Then please select a new technical words file")
        run = False

      #Ask for output file
      msg = ("The output file selected already exists.\n"
            "Would you like to overwrite?")
      if "exist" in errors[3]: msg = ("The output file selected doesn't exist.\n"
                                        "Would you like to create a one?")
        
      if not messagebox.askyesno("Are you sure?", msg):
        messagebox.showerror("ERROR", "Then please select a new output file")
        run = False
          
    if run:
      #Test to see if we have permission to create the output file
      try:
        testFile = open(files[2], "w")
        testFile.close()
      except:
        messagebox.showerror("ERROR", "The output file could not be written.\nThis could be because the program does not have permission.")
        run = False
          
    if run: #If no errors
      self.output = True #Turn the output flag to true
      self.outDict = open(files[0], "r").read().strip().split("\n")  #Make a list of the dict file
      
      if files[1].startswith("::::"): #Make a list of either the manually inputed keyword or the file
        self.outTwords = [files[1][4:]]
      else:
        self.outTwords = open(files[1], "r").read().strip().split("\n")

      if files[3].startswith("::::"): #Make a list of either the manually inputed input or the file
        self.outInput = files[3][4:]
      else:
        self.outInput = open(files[3], "r").read().strip().split("\n")

      self.manual = manual #Release manual data to be called
      self.outOutput = files[2] #Realase the path to the output file
      self.root.destroy() #Close the window
