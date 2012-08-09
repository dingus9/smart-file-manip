from tempfile import mkstemp
from shutil import move
from os import remove as lib_remove, close as lib_close, walk as lib_walk, path as lib_path
import sys,re

class SmartFileManip(object):
    """Intelegently Replaces stings in multiple or single files.
    Similar usage to a unix find /base/path/for/search -path '*/match/these/files.txt' -exec replace_script {}\;
    """
    
    def __init__(self,base_path=''):
        ##
        # internalize libraries
        self.re = re
        self.walk = lib_walk
        self.close = lib_close
        self.remove = lib_remove
        self.path_lib = lib_path
        ##
        # Init data structures
        self._retype = type(re.compile('test'))
        self._strtype = type('string')
        self.set_basepath(base_path)
        self._path_filters = {'exclude':[],'match':[]} # Init cont for add_path_filter
        self._path_debug = False
        

 
    ######
    ## Set the base path
    ######
    def set_basepath(self,path):
        if path and isinstance(path,self._strtype):
            if self.path_lib.exists(path):
                self._base_path = self.path_lib.abspath(path)
            else:
                raise Exception, self.__class__.__name__ + ".set_basepath: Path does not exist"
    
    ######
    ## Return the base path
    ######
    def get_basepath(self):
        return self._base_path
    
    ######
    ## Add a path filter exclude or match
    ######
    def add_path_filter(self, type, filter):
        """Adds a filter to the list of filters.
        Files are only parsed if a filter returns true and no_dir removes directories that match. All files are matched if no filters are defined.
        Arguments:
        type    -- one of match or exclude:
        filter  -- the filter rule
        type:filters get stored as seperat dictionaries in a list
            {'match':'some regex rule as a string or re.compiled regex'}
            {'exclude:"Exclude this regex"}
        Tips:
            * Use os.path.sep for valid /\ path seps...
            * Dirs are matched with an ending / while file paths are not
            * Exclude single direcotries like .git or .svn with:
                - {'exclude': '\.git/'}
                - more globally match all git stuff with '\.git.*' which will match .gitignore and .git dir etc.
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
            for dir in tuple(dirs): #remove excluded directories
                for reg in self._path_filters['exclude']:
                    regmatch = self.find(dir+self.path_lib.sep, reg)
                    if regmatch == dir+self.path_lib.sep:
                        dirs.remove(dir)
            
            files_this_go = []
            
            for file in tuple(files):
                for reg in self._path_filters['exclude']:
                    regmatch = self.find(root+self.path_lib.sep+file, reg)
                    if regmatch == root+self.path_lib.sep+file:
                        files.remove(file)
                
                for reg in self._path_filters['match']:
                    regmatch = self.find(root+self.path_lib.sep+file, reg)
                    if regmatch == root+self.path_lib.sep+file:
                        files_this_go.append(file)
            
            ##
            # Run class callbacks
            if(not self._path_debug):
                class_callback(root) # first dir call make root dir
                if len(self._path_filters['match']):
                    for file in files_this_go:
                        class_callback(root,file)
                else:
                    for file in files:
                        class_callback(root,file)
            else:
                self._path_debug['files'] += len(files_this_go)
                self._path_debug['dirs'] += 1
                self._path_debug['items'].append(root)
                self._path_debug['items'].append(files_this_go)
            
        return
    
    ######
    ## Replace method
    ######
    def replace(self,string, pattern, subst, nPerLine):
        if(isinstance(pattern,type('string'))):
            return string.replace(pattern, subst, nPerLine)
        
    def path_debug(self,level=1):
        self._path_debug = {'files':0,'dirs':0,'items':[]}
        self.run()
        if level:
            print self._path_debug['files'], self._path_debug['dirs']
        if level > 1:
            for x in self._path_debug['items']:
                print x