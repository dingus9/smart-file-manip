#!/usr/bin/python


from smart_replacer import SmartReplace

def callback_func1(groups, match, replace):
    """An example callback method to convert specific groups to upper case"""
    string = match
    for group in groups:
        if group == 'php':
            string = string.replace(group,group.upper())
    return match,string

bulk_replace = SmartReplace('./')

bulk_replace.add_path_filter('exclude','\.git')
bulk_replace.add_path_filter('match','.*\.txt$')

bulk_replace.add_search_filter({'regex':['<(\?)(php)',],'replace':'not be','callback': callback_func1 })


bulk_replace.run()