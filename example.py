#!/usr/bin/python

from smart_replacer import SmartReplacer
from smart_copy import SmartCopy
import re

######
## Replace example
######
def callback_func1(groups, match, replace):
    """An example callback method to convert specific groups to upper case"""
    string = match
    for group in groups:
        if group == 'php':
            string = string.replace(group,group.upper())
    return match,string

bulk_replace = SmartReplacer('./')

bulk_replace.add_path_filter('exclude','\.git')
bulk_replace.add_path_filter('match','.*\.txt$')

bulk_replace.add_search_filter({'regex':['<(\?)(php)',],'replace':'not be','callback': callback_func1 })

bulk_replace.run() # replace=True to actually replace the files

######
## Smart copy example: make a prunned copy of my puppet dev repository, with only the .pp and .erb files
######

archiver = SmartCopy() # extends SmartFileManip
archiver.set_opts(['prune_empty','full_copy','purge_existing'])
archiver.copy_from('/Users/nickshobe/Projects/puppet_repo')
archiver.copy_to('/Users/nickshobe/Projects/repo_smartcopy')
archiver.add_path_filter('exclude','.*\.git/')
archiver.add_path_filter('exclude','\.svn/')
archiver.add_path_filter('match','.*.pp')
archiver.add_path_filter('match','.*.erb')

#print archiver.find('.gitignore',re.compile('\.git.*'))

archiver.run()

