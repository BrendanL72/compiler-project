#lexer() reads the program files character by character and determines if the characters forms valid lexemes
#It then adds these lexemes into a list of lexemes to be examined for syntax by the parser
#This code is very heavily based off of the code found in the book, except in Python
def lexer(fileHandle):
   #tokens are going to be strings because python doesn't support define
   token_list = {
      "(": "PAREN_OPEN",
      ")": "PAREN_CLOSE",
      "+": "OP_ADD",
      "-": "OP_SUB",
      "*": "OP_MULT",
      "/": "OP_DIV",
      "%": "OP_MOD",
      ">": "COMP_",
      ">=": "COMP_GTE",
      "<": "COMP_LT",
      "<=": "COMP_LTE",
      "!=": "COMP_NE",
      "==": "COMP_EQ",
      "=": "ASSIGN",
      ";": "STMT_END"
   }

   keywords = ["if", "then", "else", "end", 
               "for", "while", "do", "end", 
               "not", "and", "or", 
               "print", "get"]

   special_chars = ["\t", "\n", "\"", "\\"]

   lexeme = ""
   nextChar = fileHandle.read(1)
   if not nextChar:
      nextChar = "EOF"
   token = ""

   #getChar() gets the next character from the file and checks if it has reached the EOF
   def getChar():
      nonlocal nextChar
      nextChar = fileHandle.read(1)
      if not nextChar:
         nextChar = "EOF"
         

   #addChar() adds the character and checks to see if the lexeme is too long to avoid errors
   def addChar():
      nonlocal lexeme
      if (len(lexeme) < 50):
         lexeme += nextChar
         return True
      else:
         print("Error, lexeme is too long.")
         return False

   #getNonBlank() calles getChar() until it finds a character that isn't whitespace
   def getNonBlank():
      while (nextChar.isspace()):
         getChar()

   #get the next non-blank character to determine state
   getNonBlank()
   if (nextChar == "EOF"):
      return (nextChar, nextChar)
   elif (nextChar == "_" or nextChar.islower()):
      #IDs and keywords
      #keywords such as 'if' are handled here and will override IDs
      addChar()
      getChar()

      while (not nextChar.isspace() and not nextChar in token_list and addChar()):
         getChar()

      if nextChar in token_list:
         fileHandle.seek(fileHandle.tell()-1)

      #determine if the entire word is a keyword, if not, then it's an ID
      if (lexeme in keywords):
         token = "KEYWORD"
      else:
         token = "ID"

   elif (nextChar == "\""):
      #STRINGs
      getChar()
      while (nextChar != '\"' and len(lexeme) < 50):
         #special characters
         if (nextChar == '\\'):
            getChar()
            if ("\\"+nextChar in special_chars):
               lexeme = lexeme + "\\" + nextChar
         addChar()
         getChar()
      token = "STRING"

   elif (nextChar.isnumeric()):
      #INTs
      getChar()
      while (nextChar.isnumeric() and addChar()):
         getChar()
      token = "INT"

   elif (nextChar in token_list):
      #miscellaneous tokens such as + or (
      addChar()
      getChar()
      #determine if next char is just < or <=
      if (lexeme + nextChar in token_list):
         token = token_list[lexeme+nextChar]
      else:
         token = token_list[lexeme]

   else:
      print("Error, invalid character?")
      return (1,0)
   #print((token,lexeme))
   return (token, lexeme)

#parser() takes the list of lexemes and determines if they are in a valid order using Recursive Descent Parsing
#It returns an int that reperesents an error code. 0 means that the order is valid. Anything else means that the order is invalid.
def parser(fileHandle):
   print("parsing...")
   nextLexeme = (0,0)

   variables = {}

   def getNextLexeme():
      nonlocal nextLexeme
      nextLexeme = lexer(fileHandle)
      print(nextLexeme)

   def error(missingItem, place):
      print("Parser Error: did not find " + missingItem + " at " + place)

   #value term
   def value():
      print("Entering value")
      #open parentheses
      getNextLexeme()
      if (nextLexeme[0] == "PAREN_OPEN"):
         getNextLexeme()
         expr1 = expr()
         if (nextLexeme[0] == "PAREN_CLOSE"):
            getNextLexeme()
            return expr1
         else:
            error("PAREN_CLOSE", "value")
            return 0

      #not <value>
      elif (nextLexeme[1] == "not"):
         getNextLexeme()
         if (value() == 0):
            return 1
         else:
            return 0
      #negative sign
      elif (nextLexeme[0] == "OP_SUB"):
         getNextLexeme()
         return -1 * value()
      #token is an ID or an INT
      elif (nextLexeme[0] == "ID"):
         if (nextLexeme[1] in variables.keys()):
            thing = nextLexeme[1]
            getNextLexeme()
            return variables[thing]
         else:
            print("Variable does not exist.")
      elif (nextLexeme[0] == "INT"):
         thing = nextLexeme[1]
         getNextLexeme()
         return int(thing)
      #error, invalid value
      else:
         print("ERROR: VALUE")
         return 0

   def factor():
      print("Entering factor")
      comparison_ops = [">", ">=", "<", "<=", "==", "!="] 
      value1 = value()
      if (nextLexeme[1] in comparison_ops):
         comp_value = nextLexeme[1]
         getNextLexeme()
         value2 = value()
         if (comp_value == comparison_ops[0]):
            return value1 > value2
         elif (comp_value == comparison_ops[1]):
            return value1 >= value2
         elif (comp_value == comparison_ops[2]):
            return value1 < value2
         elif (comp_value == comparison_ops[3]):
            return value1 < value2
         elif (comp_value == comparison_ops[4]):
            return value1 < value2
         elif (comp_value == comparison_ops[5]):
            return value1 < value2
         else:
            #error
            return 0
      else:
         #error
         return 0
   
   def term():
      print("Entering term")
      mult_ops = ["*", "/", "%"]
      factor1 = factor()
      while(nextLexeme[0] in mult_ops):
         mult_value = nextLexeme[1]
         getNextLexeme()
         factor2 = factor()
         if (mult_value == mult_ops[0]):
            return factor1 * factor2
         elif (mult_value == mult_ops[1]):
            return factor1 / factor2
         elif (mult_value == mult_ops[2]):
            return factor1 % factor2
         else:
            #error
            return 0

   def n_expr():
      print("Entering n_expr")
      term1 = term()
      add_ops = ["+", "-"]
      if (nextLexeme[0] == "OP_ADD" or nextLexeme[0] == "OP_SUB"):
         add_value = nextLexeme[1]
         getNextLexeme()
         term2 = term()
         if (add_value == add_ops[0]):
            return term1 + term2
         elif (add_value == add_ops[1]):
            return term1 - term2
         else:
            #error
            return 0

   def expr():
      print("Entering expr")
      n1 = n_expr()
      if (nextLexeme[1] == "and" or nextLexeme[1] == "or"):
         logical_value = nextLexeme[1]
         getNextLexeme()
         n2 = n_expr()
         if (logical_value == "and"):
            return n1 and n2
         elif (logical_value == "or"):
            return n1 or n2
         else:
            #error
            return 0
      else:
         #print error
         error("AND or OR", "expr")
         return 0

   def stmt():
      print("Entering stmt")
      #print
      if (nextLexeme[1] == "print"):
         getNextLexeme()
         if (nextLexeme[0] == "STRING"):
            print(nextLexeme[1])
            getNextLexeme()
         else:
            expr()
      #input
      elif (nextLexeme[1] == "get"):
         getNextLexeme()
         if (nextLexeme[0] == "ID"):
            userInput = input()
            if (userInput.isnumeric):
               variables[nextLexeme[1]] = int(userInput)
            else:
               variables[nextLexeme[1]] = userInput
            getNextLexeme()
            print(variables)
      #if statement 
      elif (nextLexeme[1] == "if"):
         getNextLexeme()
         expr()
         if (nextLexeme[1] == "then"):
            getNextLexeme()
            stmt_list()
            if (nextLexeme[1] == "else"):
               getNextLexeme()
               stmt_list()
            if (nextLexeme[1] == "end"):
               getNextLexeme()
            else:
               error("END or ELSE", "IF_STMT")
      #for loops
      elif (nextLexeme[1] == "for"):
         pass
      #assign
      elif (nextLexeme[0] == "ID"):
         var_name = nextLexeme[1]
         getNextLexeme()
         #equals
         if (nextLexeme[0] == "ASSIGN"):
            getNextLexeme()
            result = expr()
            variables[var_name] = result
            print(variables)
         else:
            error("ASSIGN","ASSIGN_STMT")
      else:
         return 0

   def stmt_list():
      print("Entering stmt_list")
      stmt()
      while(nextLexeme[0] == "STMT_END"):
         getNextLexeme()
         stmt()

   getNextLexeme()
   stmt_list()
   return 0

#main() is the driver program responsible for file handling and control flow between the lexer, parser, and runner.
def main():
   #take a file name from the user and read it into an array
   fileName = input("What is the file name of the program you wish to parse? ")
   fHandle = open(fileName, "r")
   #declare an array of tuples that will keep track of the lexemes and tokens recognized by the lexer in order
   parser(fHandle)

   #while (nextToken != ("EOF","EOF") and nextToken != (1,0)):
      #tokens.append(nextToken)
      #print(nextToken)
      #nextToken = lexer(fHandle)

   #if (nextToken != (1,0)):
      #print("Parser still under development.")
      #if (parser() == 0):
         #pass
      #else:
         #print("The parser detected an error.")
   #else:
      #print("The lexer ran into an issue.")
   
   fHandle.close()


main()
