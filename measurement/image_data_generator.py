# Standard library imports
import os

# Major library imports
from numpy import genfromtxt

# Enthought library imports
from traits.api import HasTraits, Str, Int, Array


class ImageDataGenerator(HasTraits):
    """ Generator of Image Data
    """
    file_path = Str
    full_image = Array
    current_index = Int

    def __init__(self, *args, **kwargs):
        super(ImageDataGenerator, self).__init__(*args, **kwargs)
        current_path = os.path.dirname(__file__)
        self.file_path = os.path.join(current_path, 'sample_image.csv')
        self.full_image = genfromtxt(self.file_path, delimiter=',')
        self.current_index = 0

    def get_new_line(self):
        """ Returns one row of data matrix specified by self.current_index
        """
        total_lines = self.full_image.shape[0]
        # use current index mod by total lines in case index exceeds total number
        new_line = self.full_image[self.current_index % total_lines]
        self.current_index += 1
        return new_line

    def reset_index(self):
        self.current_index = 0
