import os
import sys


currentDirectory = os.getcwd()

filename = currentDirectory + '/' + sys.argv[1]

projectDirectory = "Language"

os.chdir(projectDirectory)
os.system("python3  main.py " + filename)