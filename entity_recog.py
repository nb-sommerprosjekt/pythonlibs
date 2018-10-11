from polyglot.text import Text
import sys
sys.path.append("/home/tensor")
import os
from pythonlibs.xmlHandler import xmlHandler
from pythonlibs.sandboxLogger import SandboxLogger
import nltk
sys.path.append("/home/tensor/pythonlibs")

class entity_recognizer():
    def __init__(self):
        self.text = None
        self.entities = None
        self.tags = None
        self.prettyEntities = None
        self.entity_logger = SandboxLogger("entity-recognizer-testlogger", "logging_config.config")
        self.entity_logger.info("Entity object intialized.")

    def extractEntities(self, text = None, filePath = None):
        if text and filePath:
           self.entity_logger.error("Fatal error: text (string) and file-input cannot be input at the same time. Undefined behavior")
           sys.exit(0)
        if text:
            self.text =text
            self.text.replace("-", " - ")
            self.text.replace("-"," ")
            self.entities = Text(self.text, hint_language_code ='no').entities
            self.entity_logger.info(message = "Ekstraksjon av entiteter gjennomfort fra tekst-string")
        if filePath:
            if  os.path.isfile(filePath):
                with open(filePath) as f:
                    self.text = f.read()
                self.text.replace("-", " - ")
                self.entities = Text(self.text, hint_language_code = 'no').entities
                self.entity_logger.info("Entities extracted from {}".format( filePath))
                self.entity_logger.info("Following entitites: {} was extracted from file: {}".format(self.entities, filePath))
        self.formatEntities()

    def formatEntities(self):
        tags = {"I-LOC" : "Lokasjon", "I-PER" : "Person", "I-ORG" : "Organisasjon"}
        self.prettyEntities = []
        for entity in self.entities:
            self.prettyEntities.append((str(tags[entity.tag]) , ' '.join((entity))))

    def extractPositionOfEntity(self, entity):
        self.entity_logger.info("Finding positions of entity: {}".format(entity))
        tokenized_text = nltk.word_tokenize(self.text, language="norwegian")

        positions_of_entity = []
        for i in range(0,len(tokenized_text)):
            entity_len = len(entity.split())
            if i<len(tokenized_text)-entity_len:
                    comp_str = ' '.join(tokenized_text[i:i+entity_len]).lower()
                    comp_str.replace("-","")
                    comp_str.replace("&"," ")
                    if entity.lower() == comp_str:
                        positions_of_entity.append(i)
        return positions_of_entity
    def currentPosition(entity):
        current_position = 0 
        return currentPosition
    def getLengthOfEntity(self, entity):
        return(len(entity.split()))

    def printEntitiesToFile(self,output_file):
        with open(output_file, "w") as f:
            for entity in self.prettyEntities:
                f.write(' '.join(entity) + "\n")
        self.entity_logger.debug("Entites printed to {}".format(output_file))
    #def processFolderOfTexts(self, input_folder, output_folder):

    def printAsXML(self, printToScreen=True, printToFile = False, output_file_name = None):
        xml = xmlHandler(inputXmlFile = None, rootNodeName="entities")
        root = xml.getRootNode()
        for entity in self.prettyEntities:
            entity_text = entity[1].replace('&',' ')
            entity_text = entity_text.replace('<', ' ')
            entity_text = entity_text.replace('>', ' ')
            entity_length = self.getLengthOfEntity(entity[1])
            entity_position = self.extractPositionOfEntity(entity = entity[1])
            if entity_length <4:
                  attrib = {"entity_type":entity[0], "entity_length" : str(entity_length), "entity_positions" : entity_position}
                  nn = xml.makeElement("entity", entity_text,attrib)
                  xml.addNode(nn)
        if printToScreen:
            xml.prettyPrintToScreen()
        if printToFile:
            if output_file_name:
                xml.printTreeToFile(output_file_name)
            else:
                self.entity_logger.error("FATAL ERROR: Filepath not defined. XML cannot be printed")


