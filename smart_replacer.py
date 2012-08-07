from smart_file_manip import SmartFileManip

import sys,re

class SmartReplacer(SmartFileManip):
    
    def __init__(self,base_path=''):
        super(SmartReplacer, self).__init__(base_path) ## call parent init for full functionality
        self._search_filters = []
        self._replace = False

    ######
    ## Add a search filter
    ######
    def add_search_filter(self,filter):
        """Add a find and replace rule set.
        
        Careful, multiple rules will be parsed in order... regex -> substr
        This method supports multiple finds but only one replace string per find set.
        Arguments:
        filter -- of form {'regex': ['regexstrings','multipleallowed'],
                           'substr': ['multiple','substrings','allowed'],
                           'replace': 'One replace string here'
                           'callback': method(groups, match, replace)
                                arguments:
                                    matches: string for substr
                                    re.match.groups() for re
                                    the orig replacement pattern
                                return tuple(match,replace) # match
                            }
        """
        
        callback = filter['callback'] if 'callback' in filter else None
        
        if 'regex' in filter:
            for reg in filter['regex']:
                if(not isinstance(reg,self._retype)):
                    reg = self.re.compile(reg)
                self._search_filters.append({'find':reg, 'replace':filter['replace'],'callback':callback})
        if 'substr' in filter:
            for substr in filter['substr']:
                self._search_filters.append({'find':substr,'replace':filter['replace'],'callback':callback})
    
    ######
    ## Local replace method uses find from smart_file_manip
    ######
    def replace(self,string, pattern, subst, nPerLine):
        if(isinstance(pattern,type('string'))):
            return string.replace(pattern, subst, nPerLine)


    ######
    ## The file replace guts
    ######
    def file_replace(self,file, find, replace, callback, nLines=-1, nPerLine=-1):
        """Replace a files contents based on a pattern.
            
            Arguments:
            file     -- path of the target file to find/replace (string)
            pattern  -- a string or regex pattern to be replaced - ensure regex has been re.compile
            replace  -- boolean True to replace or false to stdout (default True)
            nLines   -- replace N matching lines in the file -1 for all
            nPerLine -- replace N matches per mathing line in file -1 for all
            """
            
        #Create temp file
        if self._replace:
            fh, abs_path = mkstemp()
            new_out = open(abs_path,'w')
        else:
            new_out = sys.stdout
        
        old_file = open(file)
        
        n = 0
        for line in old_file:
            match = self.find(line,find)
            if match and (nLines == -1 or n < nLines):
                if callback: ### callback(groups, match, replace) return string to replace callbacks are defined in add_search_filter()###
                    match,replace = callback(self.find(line,find,True),match,replace)
                new_out.write(self.replace(line, match, replace,nPerLine))
                n+=1
            else:
                new_out.write(line)
        
        old_file.close()
        
        #close temp file
        if self._replace:
            file_out.close()
            self.close(fh)
            #Move new file
            self.remove(file)
            move(abs_path, file)
            
    ######
    ## Run current task
    ######
    def run(self, replace=False):
        self._replace = replace
        super(SmartReplacer,self).run(self.exec_callback)
    
    def exec_callback(self,root,file):
        for filter in self._search_filters:
            self.file_replace(root+file, filter['find'],filter['replace'],filter['callback'])