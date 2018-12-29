# Author        : Sathiyanarayanan S
# Email         : cs15emds11015@iith.ac.in
# File          : OCRText.py
# Project       : PDF To Text

# Change Logs:
# 2018-06-04      : Base Version

import logging
import os
import pytesseract

class OCRText(object):
    def __init__(self, configuration):
        """ Initialize the model with configuration. 
        Arguments:
            configuration: dictionary with lots of configurations
        Short Description:
            This class read PDF and generate images.
            It scans the input folder, 
            list PDF file within it and generate images for each page
            ImageMagin and GhostScript are used to perform this task
        """
        self.logger = logging.getLogger("PTT")
        self.config = configuration
        # Set the pytesseract installation path
        pytesseract.pytesseract.tesseract_cmd = self.config['tesseractHome'] + "tesseract"
        self.logger.info("Tesseract version {0}".format(pytesseract.get_tesseract_version()))
        
    def clearOutputDirectory(self):
        """
            List files from output folder and delete them
        """
        for file in os.listdir(self.config["outputPath"]):
            self.logger.info("Deleting old output file: {0}".format(file))
            os.remove(os.path.join(self.config["outputPath"], file))
        
    def generateText(self, imageInputPath):
        """
            Receives path of single iamge file
            Generate text from each of the image
        """
        self.logger.info("Processing the image {0}".format(imageInputPath))
        imageInputFullPath = self.config['tempPath'] + imageInputPath
        imageInputWithoutExtension = os.path.splitext(imageInputPath)[0]
        outputPath = self.config['outputPath'] + imageInputWithoutExtension + ".txt"
        outputPath = self.config['outputPath'] + imageInputWithoutExtension
        
        tessConfig = ('--oem 1 --psm 3')
        # Run tesseract OCR on image
        pytesseract.pytesseract.run_tesseract(imageInputFullPath, outputPath, extension=self.config['outputFormat'], lang="eng", config=tessConfig)
        self.logger.debug("Processed the image {0}, OutputPath {1}".format(imageInputPath, outputPath))
        
        # tessConfig = ('-l eng --oem 1 --psm 3')
        # tessConfig = ('--oem 1 --psm 3 -c textonly_pdf=1')
        # # Read image from disk
        # im = cv2.imread(imageInputFullPath, cv2.IMREAD_COLOR)
        # text = pytesseract.image_to_string(im, config=tessConfig)
        # with open(outputPath, mode="w", encoding="utf8") as outFile:
            # outFile.write(text)
        
    def processImages(self):
        """
            List files in the temp folder and 
            calls generateText for each of the input images
        """
        for file in os.listdir(self.config["tempPath"]):
            self.logger.debug("Calling generateImages for the file: {0}".format(file))
            self.generateText(file)
            
            
       