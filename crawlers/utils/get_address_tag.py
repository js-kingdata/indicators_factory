import json
import os


class GetAddressTag:

    tagType = ''

    def __init__(self, _tagType):
        
        self.tagType = _tagType

    def get_tag_json(self):
        tag_json = {}
        if self.tagType == 'cex' or self.tagType == 'user' :
            folder_path = os.getcwd() + '/%s_address' % self.tagType
            file_names = os.listdir(folder_path)
            for file_name in file_names : 
                file_path = folder_path + '/' + file_name
                with open(file_path) as f :
                    file_json = json.load(f)
                    tag_json.update(file_json)
        return tag_json