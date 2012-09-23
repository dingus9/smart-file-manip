#!/usr/bin/python

from smart_replacer import SmartReplacer
from smart_copy import SmartCopy
import re

######
## Replace example
######

bulk_replace = SmartReplacer('/Users/will5324/Projects/cloudGod')

bulk_replace.add_path_filter('exclude','.git')
bulk_replace.add_path_filter('match','.*\.py$')

bulk_replace.add_search_filter({'substr':['libcloud.types',],'replace':'libcloud.compute.types' })

bulk_replace.run(replace=False) # replace=True to actually replace the files

#bulk_replace.path_debug(2)

