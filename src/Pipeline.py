# Author        : Sathiyanarayanan S
# Email         : cs15emds11015@iith.ac.in
# File          : Pipeline.py
# Project       : PDF To Text

# Change Logs:
# 2018-06-04      : Base Version



# Importing required libraries
import sys, os
import argparse, configparser
from imp import reload
import logging
import traceback, re
import numpy as np

# Import our classes
from ReadPDF import ReadPDF
from OCRText import OCRText


'''Usage:
    python Pipeline.py <properties file path>"
'''

def usage():
    print("{0} <properties file>".format(sys.argv[0]))
    print(sys.exit(__doc__))
    
def printTraceBack():
    """
        Prints the trace back
        File name, Line number and actual text error
    """
    for frame in traceback.extract_tb(sys.exc_info()[2]):
        fname, lineno, fn, text = frame
        print("ERROR: Error in {0} on line {1}: {2}".format(fname, lineno, text))
        
def getLogger(logFile, logLevel):
    """
        Initializes the logger
        Check specified log file exist, if not create the directory and file
        Add both file and console handlers
        Arguments
        logFile: Log file name with path
        logLevel: Log level for both file and console
    """
    # Check the existence of the file, if not create it
    try:
        if not os.path.exists(logFile):
            (filePath, fileName) = os.path.split(logFile)
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            fo = open(logFile, 'w')
            fo.close()
    except IOError as e:
        print("ERROR: Unable to create log file {0}: {1}".format(logFile, sys.exc_info()[0]))
        printTraceBack()
        sys.exit(10002)

    # Logging
    reload(logging)
    # from https://docs.python.org/2/howto/logging-cookbook.html
    global logger
    logger = logging.getLogger("PTT")
    logger.setLevel(logging.DEBUG)
    # Log formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', "%Y-%m-%d %H:%M:%S")
    # Log to file
    fh = logging.FileHandler(logFile)
    fh.setLevel(logLevel)
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    # Logging to console
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    return logger
    
def parsePropertiesFile(propertiesFile):
    """
        Reads parameters provided in the parameter file
    """
    # Try parsing the configuration file
    try:
        config = configparser.ConfigParser()
        config.read(propertiesFile)
    except:
        print(sys.exc_info())
        sys.exit(10002)

    # Read Log level
    # Declare predefined set of log levels
    # Check user provided the optional log level parameter, 
    # If so check if its part of predefined list, else fall back to the 
    # default of INFO
    logLevels = {'CRITICAL':50, 'ERROR':40, 'WARNING':30, 'INFO':20, 'DEBUG':10, 'NOTSET':0}
    logLevel = 'INFO'
    logLevelNumeric = logLevels[logLevel]
    if config.has_option('optional', 'logLevel'):
        logLevel = config.get('optional', 'logLevel')
        
    if logLevel in logLevels:
        logLevelNumeric = logLevels[logLevel]
    else:
        logLevel = 'INFO'
        logLevelNumeric = logLevels[logLevel]
        
    # Read log file property which is the primary one
    logFile = None
    try:
        logFile = config.get('required', 'logFile')
    except:
        print("ERROR: Missing parameter: logFile")
        printTraceBack()
        sys.exit(10003)
    logger = getLogger(logFile, logLevelNumeric)
    logger.info("Successfully initialized logger at {0}".format(logFile))
    logger.critical("Using log level {0}. [This message is raised at CRITICAL level so that this is visible at all log levels]".format(logLevel))
    
    # Define the configuration dictionary
    inputConfig = {}
    validationFailed = False
    
    # Read input location path
    try:
        inputConfig['inputPath'] = config.get('required', 'inputPath')
    except:
        print("ERROR: Missing parameter: inputPath")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using input location {0}".format(inputConfig['inputPath']))
    # Validate the path exist
    if not os.path.exists(inputConfig['inputPath']):
        validationFailed = True
        logger.info("The specified input path {0} Does not exist, Please Check.".format(inputConfig['inputPath']))

    # Read temporary location path
    try:
        inputConfig['tempPath'] = config.get('required', 'tempPath')
    except:
        print("ERROR: Missing parameter: tempPath")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using temporary location {0}".format(inputConfig['tempPath']))
    # Validate the path exist
    if not os.path.exists(inputConfig['tempPath']):
        logger.info("The specified temporary path {0} Does not exist, Creating it.".format(inputConfig['tempPath']))
        (filePath, fileName) = os.path.split(inputConfig['tempPath'])
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        
        
    # Read output location path
    try:
        inputConfig['outputPath'] = config.get('required', 'outputPath')
    except:
        print("ERROR: Missing parameter: outputPath")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using output location {0}".format(inputConfig['outputPath']))
    # Validate the path exist
    if not os.path.exists(inputConfig['outputPath']):
        logger.info("The specified output path {0} Does not exist, Creating it.".format(inputConfig['outputPath']))
        (filePath, fileName) = os.path.split(inputConfig['outputPath'])
        if not os.path.exists(filePath):
            os.makedirs(filePath)
    
    # Read Image Magic location path
    try:
        inputConfig['magickHome'] = config.get('required', 'magickHome')
    except:
        print("ERROR: Missing parameter: magickHome")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using Image Magick location {0}".format(inputConfig['magickHome']))
    # Validate the path exist
    if not os.path.exists(inputConfig['magickHome']):
        validationFailed = True
        logger.info("The specified Image Magick path {0} Does not exist, Please Check.".format(inputConfig['magickHome']))

    # Read Tesseract location path
    try:
        inputConfig['tesseractHome'] = config.get('required', 'tesseractHome')
    except:
        print("ERROR: Missing parameter: tesseractHome")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using Tesseract location {0}".format(inputConfig['tesseractHome']))
    # Validate the path exist
    if not os.path.exists(inputConfig['tesseractHome']):
        validationFailed = True
        logger.info("The specified Tesseract path {0} Does not exist, Please Check.".format(inputConfig['tesseractHome']))
    
    # Read Tesseract language model location path
    try:
        inputConfig['tessData'] = config.get('required', 'tessData')
    except:
        print("ERROR: Missing parameter: tessData")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using Tesseract Language Model location {0}".format(inputConfig['tessData']))
    # Validate the path exist
    if not os.path.exists(inputConfig['tessData']):
        validationFailed = True
        logger.info("The specified Tesseract Language Model path {0} Does not exist, Please Check.".format(inputConfig['tessData']))
    
    # Read PDF Scan resolution (dpi) path
    try:
        inputConfig['resolution'] = int(config.get('required', 'resolution'))
    except:
        print("ERROR: Missing parameter: resolution")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using scan resolution {0}".format(inputConfig['resolution']))
    
    # Read output file format
    # Check user provided output format
    # If so check if its part of predefined list, else rise error
    fileFormats = ['pdf', 'hocr', 'txt', 'tsv']
    try:
        inputConfig['outputFormat'] = config.get('required', 'outputFormat')
    except:
        print("ERROR: Missing parameter: outputFormat")
        printTraceBack()
        sys.exit(10006)
    logger.info("Using Output format {0}".format(inputConfig['outputFormat']))
    if inputConfig['outputFormat'] not in fileFormats:
        validationFailed = True
        logger.info("The specified Output format is not a valid one. List of valid format are {0}".format(','.join(fileFormats)))
        
    if validationFailed:
        logger.info("Some configuration validation failed, Unable to continue. Please check log for details.")
        printTraceBack()
        sys.exit(10006)
    return inputConfig

def SetEnvironmentVariable(config):
    # Set environment variable
    os.environ['MAGICK_HOME'] = config['magickHome']
    logger.debug("Environment variable MAGICK_HOME = {0}".format(os.environ.get('MAGICK_HOME')))
    sys.path.append(config['tesseractHome'])
    logger.debug("Tesseract Home = {0} added to path".format(config['tesseractHome']))
    os.environ['TESSDATA_PREFIX'] = inputConfig['tessData']
    logger.debug("Environment variable TESSDATA_PREFIX = {0}".format(os.environ.get('TESSDATA_PREFIX')))
    
if __name__ == "__main__":
    # Main execution starts here
    # Read the property
    parser = argparse.ArgumentParser()
    parser.add_argument('propertiesFile', type=str, help='Property file full path')
    args = parser.parse_args()

    if 'propertiesFile'  not in args:
        usage()
        sys.exit(10001)

    # Parse the property file
    inputConfig = parsePropertiesFile(args.propertiesFile)
    logger.info("Successfully all parameters are read")
    
    # set MAGICK_HOME and other environment variable
    SetEnvironmentVariable(inputConfig)
    
    # # Stage 1 convert input pdf files to images
    # readPDF = ReadPDF(inputConfig)
    # readPDF.clearTempDirectory()
    # readPDF.processInputFolder()
    
    # Stage 2 Perform OCR
    ocrText = OCRText(inputConfig)
    ocrText.clearOutputDirectory()
    ocrText.processImages()
    
    
    
    