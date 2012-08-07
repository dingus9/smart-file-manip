from smart_file_manip import SmartFileManip

import sys,re

class SmartCopy(SmartFileManip):
    
    def __init__(self,copy_base='',copy_target=''):
        """This class copies based on SmartFileManip path rules"""
        super(SmartCopy, self).__init__(copy_base) ## call parent init for full functionality
        self._copy_base = copy_base
        self._copy_target = copy_target
    
    ######
    ## Set the copy base directory
    ######
    def copy_from(self,copy_base):
        self._copy_base = copy_base
        
    def copy_to(self,copy_target):
        self._copy_target = copy_target

    ######
    ## Run the main job
    ######
    def run(self):
        if not self._copy_target:
            raise Exception, "You must specify: "+self.__class__.__name__+".copy_to or "+self.__class__.__name__+"__init__"
        super(SmartCopy,self).run(self.copy_callback)
    
    
    def copy_callback(self,root,file):
        pass