from smart_file_manip import SmartFileManip

import re,shutil,os,sys

class SmartCopy(SmartFileManip):
    
    def __init__(self,copy_base='',copy_target='',opts=''):
        """This class copies based on SmartFileManip path rules"""
        super(SmartCopy, self).__init__(copy_base) ## call parent init for full functionality
        self._copy_target = copy_target
        if opts:
            self._opts = opts
        else:
            self._opts = []
            
        self._item_stack = {}
        self._item_stackOrdered = [] #used to actually loop through and garuntee orderly execution
        
        self._dir_count = {}
        self._dir_file_count = {}
    
    ######
    ## Set the copy base directory
    ######
    def copy_from(self,copy_base=''):
        if copy_base:
            super(SmartCopy,self).set_basepath(copy_base)
        else:
            return self._base_path
        
    def copy_to(self,copy_target=''):
        if copy_target and isinstance(copy_target, self._strtype):
            self._copy_target = copy_target
        else:
            return self._copy_target
    
    def set_opts(self, opts):
        """send a list of opt strings []
        'full_copy' = make as full of a copy as possible
        """
        self._opts = opts
    
    ######
    ## Run the main job
    ######
    def run(self):
        if 'purge_existing' in self._opts:
            shutil.rmtree(self._copy_target)
        if not self.copy_to() or not self.copy_from():
            raise Exception, "You must specify: "+self.__class__.__name__+".copy_to() and copy_from() or "+self.__class__.__name__+"__init__(to, from)"
        super(SmartCopy,self).run(self.copy_callback)
        self.exec_stack()
    
    ######
    ## Count files beneith the parent directories to allow for pruning
    ######
    def inc_file_count(self,file):
        """Count files beneith the parent directories to allow for pruning"""
        path = self.path_lib.dirname(file)
        while path != self._base_path:
            self._dir_file_count[path] += 1
            path = self.path_lib.dirname(path)
        self._dir_file_count[path] += 1 # patch in the root dir so that it gets created too...

    ######
    ## Callback method that adds files and dirs to the copy que... this method is meant to be run from a recusive file os.walk rutine
    ######
    def copy_callback(self,root,file=''):
        if file:
            src = root + self.path_lib.sep + file
            tgt = self.copy_to() + self.replace(root,self.copy_from(),'',1)+ self.path_lib.sep + file
            self._item_stack[src] = {'tgt':tgt,'type':'file'}
            self._item_stackOrdered.append(src)
            self.inc_file_count(src) # track file counts below parent directory -- totals used to prune unused trees
        else:
            src = root
            tgt = self.copy_to() + self.replace(root,self.copy_from(),'',1)
            self._item_stack[src] = {'tgt':tgt,'type':'dir'}
            self._item_stackOrdered.append(src)
            
            if self.path_lib.dirname(src) in self._dir_count:
                self._dir_count[self.path_lib.dirname(src)] += 1
            
            ##
            # new dir counts
            self._dir_count[src] = 0
            self._dir_file_count[src] = 0
    
    ######
    ## Run the final copy que
    ######
    def exec_stack(self):
        """should only be run after copy_callback has added all of the copy items to the item stacks and counted files and dirs etc"""
        for item in self._item_stackOrdered:
            src = item
            tgt = self._item_stack[item]['tgt']
            if self._item_stack[item]['type'] == 'file':
                if 'full_copy' in self._opts:
                    shutil.copy2(src, tgt)
                else:
                    shutil.copy(src, tgt)
            elif 'prune_empty' in self._opts and self._dir_file_count[item] or 'prune_empty' not in self._opts:
                os.mkdir(tgt)
        return