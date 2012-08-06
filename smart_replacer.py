from tempfile import mkstemp
from shutil import move
from os import remove, close, walk
import sys,re

class SmartReplace:
    """Intelegently Replaces stings in multiple or single files.
    Similar usage to a unix find /base/path/for/search -path '*/match/these/files.txt' -exec replace_script {}\;
    """
    
    def __init__(self,base_path=''):
        self._base_path = base_path
        self._retype = type(re.compile('test'))
        self._strtype = type('string')
        self._path_filters = {}#{'regex':[],'path':[],'no_dir':[],'ext':[]}
        self._search_filters = []
        self._replace = False
    
    def  set_basepath(path):
        self._base_path = path
        
    def get_basepath():
        return self._base_path
    
    def add_path_filter(self, type, filter):
        """Adds a filter to the list of filters.
        Files are only parsed if a filter returns true and no_dir removes directories that match. All files are matched if no filters are defined.
        Arguments:
        type    -- one of regex, str, ext,no_dir remember to use os.path.sep:
        filter  -- the filter rule
        type:filters get stored as seperat dictionaries in a list
            {'match':'some regex rule as a string or re.compiled regex'}
            {'exclude:"Exclude this regex"}
        """
        if(not isinstance(filter, self._retype)):
            filter = re.compile(filter) # compile re string to a re object if it's not one already
        if type in self._path_filters:
            self._path_filters[type].append(filter)
        else:
            self._path_filters[type] = [filter]
        
    def get_path_filters(self):
        return self._path_filters
    
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
                                return string will replace the replace string per match
                            }
        """
        
        callback = filter['callback'] if 'callback' in filter else None
        
        if 'regex' in filter:
            for reg in filter['regex']:
                if(not isinstance(reg,self._retype)):
                    reg = re.compile(reg)
                self._search_filters.append({'find':reg, 'replace':filter['replace'],'callback':callback})
        if 'substr' in filter:
            for substr in filter['substr']:
                self._search_filters.append({'find':substr,'replace':filter['replace'],'callback':callback})
    
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
            close(fh)
            #Move new file
            remove(file)
            move(abs_path, file)
    
    ##
    ## Run find replace
    ##
    def run(self, replace=False):
        self._replace = replace
        if(not self._base_path):
            raise Exception, "You must set the base path see: "+self.__class__.__name__+".set_base_path or "+self.__class__.__name__+"__init__"
        for root, dirs, files in walk(self._base_path):
            for dir in dirs: #remove excluded directories
                for reg in self._path_filters['exclude']:
                    if self.find(dir, reg):
                        dirs.remove(dir)
            
            files_this_go = []
            
            for file in files:
                for reg in self._path_filters['exclude']:
                    if self.find(root+file, reg):
                        del files[file]
                for reg in self._path_filters['match']:
                    if self.find(root+file, reg):
                        files_this_go.append(file)
            
            for file in files_this_go:
                for filter in self._search_filters:
                    self.file_replace(root+file, filter['find'],filter['replace'],filter['callback'])
            return
        
        return 
    
    def find(self,string, search,groups=False):
        """Find the index of the matching string based on search pattern.
        Arguments:
        string -- subject string.
        search -- pattern to search for, can be regex or string
        """
        if isinstance(search,self._retype):
            m = search.match(string)
            if m:
                return m.groups() if groups else m.group()
        else:
            s = string.find(search)
            return search if s != -1 else None
    
    def replace(self,string, pattern, subst, nPerLine):
        if(isinstance(pattern,type('string'))):
            return string.replace(pattern, subst, nPerLine)
