# Author        : Sathiyanarayanan S
# Email         : cs15emds11015@iith.ac.in
# File          : ReadPDF.py
# Project       : PDF To Text

# Change Logs:
# 2018-06-04      : Base Version

import numpy as np
import logging
from wand.image import Image
from wand.color import Color
import os

class ReadPDF(object):
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
        self.logger.debug(os.environ.get('MAGICK_HOME'))
    
    def clearTempDirectory(self):
        """
            List files from temp folder and delete them
        """
        for file in os.listdir(self.config["tempPath"]):
            self.logger.info("Deleting old file: {0}".format(file))
            os.remove(os.path.join(self.config["tempPath"], file))
            
    def generateImages(self, pdfInputPath):
        """
            Receives path of single PDF file
            Generate image for each of the page and stores in the temp folder
        """
        self.logger.info("Processing the file {0}".format(pdfInputPath))
        pdfInputFullPath = self.config['inputPath'] + pdfInputPath
        pdfInputWithoutExtension = os.path.splitext(pdfInputPath)[0]
        
        im = Image(filename=pdfInputFullPath, resolution=self.config['resolution'])
        for pageNum, page in enumerate(im.sequence):
            with Image(page) as pageImage:
                self.logger.debug("Processing the file {0}, page {1}".format(pdfInputPath, pageNum))
                pageImage.alpha_channel = False
                pageImage.compression_quality = 100
                pageImage.save(filename=(self.config['tempPath'] + pdfInputWithoutExtension + '-Page-{0}.png'.format(pageNum)))
       
    def processInputFolder(self):
        """
            List files in the input folder and 
            calls generateImages for each of the input file
        """
        for file in os.listdir(self.config["inputPath"]):
            self.logger.debug("Calling generateImages for the file: {0}".format(file))
            self.generateImages(file)
            
            
       