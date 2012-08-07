from tempfile import mkstemp
from shutil import move
from os import remove as lib_remove, close as lib_close, walk as lib_walk
import sys,re

class SmartFileManip(object):
    """Intelegently Replaces stings in multiple or single files.
    Similar usage to a unix find /base/path/for/search -path '*/match/these/files.txt' -exec replace_script {}\;
    """
    
    def __init__(self,base_path=''):
        self._base_path = base_path
        self._retype = type(re.compile('test'))
        self._strtype = type('string')
        self._path_filters = {}#{'regex':[],'path':[],'no_dir':[],'ext':[]}
        self.re = re
        self.walk = lib_walk
        self.close = lib_close
        self.remove = lib_remove
 
    ######
    ## Set the base path
    ######
    def set_basepath(path):
        self._base_path = path
    
    ######
    ## Return the base path
    ######
    def get_basepath():
        return self._base_path
    
    ######
    ## Add a path filter exclude or match
    ######
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
    
    ######
    ## Return current path filters
    ######
    def get_path_filters(self):
        return self._path_filters
    
    ######
    ## Generic regex/string aware find akin to grep
    ######
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
        
    ######
    ## Run current task
    ######
    def run(self,class_callback):
        if(not self._base_path):
            raise Exception, "You must set the base path see: "+self.__class__.__name__+".set_base_path or "+self.__class__.__name__+"__init__"
        for root, dirs, files in self.walk(self._base_path):
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
                class_callback(root,file)
            
        return 
