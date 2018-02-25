import os
import shutil


class ManagerDir:
    def __init__(self):
        self.path = os.getcwd()

    @staticmethod
    def remove(path):
        if os.path.isfile(path):
            os.remove(path)  # remove the file
        elif os.path.isdir(path):
            shutil.rmtree(path)  # remove dir and all contains
        else:
            raise ValueError("file {} is not a file or dir.".format(path))

    def create(self, name):
        directory = self.path + "/" + name
        if os.path.exists(directory):
            self.remove(directory)

        os.makedirs(directory)

    def folder_test(self, filename) :
        if not os.path.exists(os.path.dirname(filename)) :
            try :
                os.makedirs(os.path.dirname(filename))
            except OSError as error :
                if error.errno != errno.EEXIST :
                    raise
