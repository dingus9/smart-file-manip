#!/usr/bin/python

from smart_replacer import SmartReplacer
from smart_copy import SmartCopy
import re

######
## Smart copy example: make a prunned copy of my puppet dev repository, with only the .pp and .erb files
######

archiver = SmartCopy() # extends SmartFileManip
archiver.set_opts(['prune_empty','full_copy','purge_existing'])
archiver.copy_from('/var/www')
archiver.copy_to('/home/user/test_site')
archiver.add_path_filter('exclude','.*\.git/')
archiver.add_path_filter('exclude','\.svn/')
archiver.add_path_filter('exclude','aggregator/')

archiver.add_path_filter('match','.*aggregate_js')
archiver.add_path_filter('match','.*aggregator')
#archiver.add_path_filter('match','.*site/.*\.css')
archiver.add_path_filter('match','.*\.php')
#print archiver.find('.gitignore',re.compile('\.git.*'))

archiver.run()
print archiver.get_stats()

######
## Replace example
######
#def callback_func1(groups, match, replace):
#    """rebuild the livewhale require"""
#    print groups
#    print match
#    print replace
#    raise Exception, "dumby"
#    string = match
#    for group in groups:
#        if group == 'php':
#            string = string.replace(group,group.upper())
#    return match,string
#
#bulk_replace = SmartReplacer()
#bulk_replace.set_basepath('/home/nickshobe/test_site')
#bulk_replace.add_path_filter('exclude','\.git')
##bulk_replace.add_path_filter('exclude','chronicle/')
#bulk_replace.add_path_filter('exclude','.*\/')
#
#bulk_replace.add_path_filter('match','.*\.php')
#
#bulk_replace.path_debug(2)
#
##require_once($_SERVER['LIVEWHALE_ROOT'] . 'livewhale/cache.livewhale.php');
#bulk_replace.add_search_filter({'substr':["require_once($_SERVER['LCLARK_ROOT'] . 'site/php/classes/1.2/Site.inc');",],'replace':'', })
#bulk_replace.add_search_filter({'regex':["(require_once|include_once)(.*)livewhale.php",],'replace':'require', 'callback':callback_func1 })

#bulk_replace.run() # replace=True to actually replace the files
