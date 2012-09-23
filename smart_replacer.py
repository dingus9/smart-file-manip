from smart_file_manip import SmartFileManip
import tempfile

import sys,re,os

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
    ## The file replace guts
    ######
    def file_replace(self,orig_file,new_file, find, replace, callback, nLines=-1, nPerLine=-1):
        """Replace a files contents based on a pattern.
            
            Arguments:
            file     -- path of the target file to find/replace (string)
            pattern  -- a string or regex pattern to be replaced - ensure regex has been re.compile
            replace  -- boolean True to replace or false to stdout (default True)
            nLines   -- replace N matching lines in the file -1 for all
            nPerLine -- replace N matches per mathing line in file -1 for all
            """
        #old_file becomes file, and new_out becomes new_file
        n = 0
        for line in orig_file:
            match = self.find(line,find)
            if match and (nLines == -1 or n < nLines):
                if callback: ### callback(groups, match, replace) return string to replace callbacks are defined in add_search_filter()###
                    match,replace = callback(self.find(line,find,True),match,replace)
                new_file.write(self.replace(line, match, replace,nPerLine))
                n+=1
            else:
                new_file.write(line)
            
    ######
    ## Run current task
    ######
    def run(self, replace=False):
        self._replace = replace
        super(SmartReplacer,self).run(self.exec_callback)
    
    def exec_callback(self,root,file=''):
        if file: #ignore directory only call... only op on files
            
            ###
            ## Print file sep headers
            ###
            print ''
            print '-------------------------------------------------------'
            print root+self.path_lib.sep+file
            print '-------------------------------------------------------'
            in_file = open(root+self.path_lib.sep+file)
            tempfiles=[]
            for filter in self._search_filters:
                out_file = tempfile.NamedTemporaryFile(delete=False) #Create temp file
                tempfiles.append(out_file)
                self.file_replace(in_file,out_file, filter['find'],filter['replace'],filter['callback'])
                out_file.seek(0,0)
                in_file.close()
                if self._replace:
                    os.remove(in_file.name) #Remove all tempfiles+source except the last which is renamed below
                in_file = out_file
            
            if self._replace:               #Rename last tempfile to working file
                os.rename(out_file.name,root+self.path_lib.sep+file)
            else:                           #Print to std output and then remove tempfiles
                for line in out_file:
                    sys.stdout.write(line)
                for tmpfile in tempfiles:   #Remove tempfiles
                    tmpfile.close()
                    os.remove(tmpfile.name)
        else:
            return