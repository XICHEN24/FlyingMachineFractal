"""
complex plane functions and class for getting pixels in three different measuring systems
"""
import numpy as np

print_order = ['upper_left', 'top_center', 'upper_right',
               'left_center', 'center_point', 'right_center',
              'bottom_left', 'bottom_center', 'bottom_right']

def get_frame_from_dict(def_dict):
    """ complex_frame, def_dict = get_frame_from_dict(def_dict)
        legacy wrapper function.
    Args:
        def_dict: definition dictionary with keys:
                    'center_point', 'zoom', 'theta', 'n_rows', 'n_cols'
    Returns:
        complex_frame:
        def_dict:
    """
    complex_frame = get_complex_frame(
        def_dict['center_point'],
        def_dict['zoom'],
        def_dict['theta'],
        def_dict['n_rows'],
        def_dict['n_cols'])

    return complex_frame, def_dict

def get_complex_frame(CP, ZM, theta, h=1, w=1):
    """ get the complex numbers at ends and centers of a frame  """
    frame_dict = {'center_point':CP}
    if w >= h:
        frame_dict['top_center'] = np.exp(1j*(np.pi/2 + theta))/ZM
        frame_dict['right_center'] = (w/h) * np.exp(1j * theta) / ZM
    else:
        frame_dict['top_center'] = (h/w) * np.exp(1j*(np.pi/2 + theta)) / ZM
        frame_dict['right_center'] = np.exp(1j * theta) / ZM

    frame_dict['bottom_center'] = frame_dict['top_center'] * -1
    frame_dict['left_center'] = frame_dict['right_center'] * -1
    frame_dict['upper_right'] = frame_dict['right_center'] + frame_dict['top_center']
    frame_dict['bottom_right'] = frame_dict['right_center'] + frame_dict['bottom_center']

    frame_dict['upper_left'] = frame_dict['left_center'] + frame_dict['top_center']
    frame_dict['bottom_left'] = frame_dict['left_center'] + frame_dict['bottom_center']

    for k in frame_dict.keys():
        frame_dict[k] = frame_dict[k] + CP

    return frame_dict


def complex_to_string(z, N_DEC=6):
    """ format single complex number to string with n decimal places """
    MAX_DEC = 17
    MIN_DEC = 1

    n = max(min(MAX_DEC, round(N_DEC)), MIN_DEC)
    fs = '%%0.%df'%n

    zr = np.real(z)
    zi = np.imag(z)

    if np.sign(zi) < 0:
        s1 = ' ' + fs % zi + 'j'
    else:
        s1 = ' +' + fs % zi + 'j'

    if np.sign(zr) < 0:
        z_str = fs % zr + s1
    else:
        z_str = ' ' + fs % zr + s1

    return z_str


def get_aligned_dict_string(d, N_DEC=3):
    """ pretty_string = z_plane.get_aligned_dict_string(d, N_DEC=3) """
    INDENT = 16
    out_string = ''
    for k in sorted(list(d.keys())):
        
        v = d[k]
        if type(v) == str:
            s = v
        elif v == 0:
            s = '0'
        elif np.iscomplex(v):
            s = complex_to_string(v, N_DEC)
        elif np.round(v) == v:
            s = '%d'%(v)
        else:
            f_str = '%s%s%d%s'%('%','0.',N_DEC,'f')
            s = f_str%(v)
        
        if len(out_string) == 0:
            out_string = ' ' * max(0,(INDENT - len(k))) + k + ': ' + s
        else:
            out_string = out_string + '\n' + ' ' * max(0,(INDENT - len(k))) + k + ': ' + s
            
    return out_string + '\n'


def complex_frame_dict_to_string(frame_dict, N_DEC=4):
    """ get a formatted list of strings """
    STR_L = 14
    frame_string = ''
    row = 0
    for k in print_order:
        z_str = complex_to_string(frame_dict[k], N_DEC)
        PAD = ' ' * (STR_L - len(z_str))
        frame_string += k + ':' + PAD + z_str
        row += 1
        if np.mod(row,3) == 0:
            frame_string += '\n'
        else:
            frame_string += '\t'
    return frame_string


def show_complex_matrix(Z0,N_DEC=3):
    """ display a complex matrix or array """
    SPC = ' ' * 2
    if Z0.shape[0] == Z0.size:
        row_str = ''
        for col in range(0, Z0.shape[0]):
            row_str += complex_to_string(Z0[col], N_DEC) + SPC + '\n'
        print(row_str)
   
    else:
        for row in range(0,Z0.shape[0]):
            row_str = ''
            for col in range(0, Z0.shape[1]):
                row_str += complex_to_string(Z0[row, col], N_DEC) + SPC

            print(row_str)

class ComplexPlane:
    
    
    def __init__(self, CP=0.0+0.0*1j, ZM=1.0, theta=0.0, h=5, w=5):
        self._center_point = CP
        self._zoom_factor = max(ZM, 1e-15)
        self._theta = theta
        self._n_rows = max(round(h), 1)
        self._n_cols = max(round(w), 1)

    def display_self(self):
        pd = self.get_parameters_dict()
        s = get_aligned_dict_string(pd)
        print(s)
    
    def load_dict(self, parameters_dict):
        """ self.load_dict(parameters_dict) """
        if 'center_point' in parameters_dict:
            self._center_point = parameters_dict['center_point']
        if 'zoom_factor' in parameters_dict:
            self._zoom_factor = parameters_dict['zoom_factor']
        if 'theta' in parameters_dict:
            self._theta = parameters_dict['theta']
        if 'n_rows' in parameters_dict:
            self._n_rows = parameters_dict['n_rows']
        if 'n_cols' in parameters_dict:
            self._n_cols = parameters_dict['n_cols']


    def get_parameters_dict(self):
        """ parameters_dict = self.get_parameters_dict() """
        parameters_dict = {}
        parameters_dict['center_point'] = self._center_point
        parameters_dict['zoom_factor'] = self._zoom_factor
        parameters_dict['theta'] = self._theta
        parameters_dict['n_rows'] = self._n_rows
        parameters_dict['n_cols'] = self._n_cols    
        return parameters_dict

    
    def get_escape_bound(self):
        """ escape time algorithm best infinity safe iteration distance """
        corner_scale = max(self._n_rows/self._n_cols, self._n_cols/self._n_rows)
        return corner_scale * 12 / self._zoom_factor
    
    
    def get_complex_axes(self):
        """ horiz_axis, vert_axis = self.get_complex_axes() """
        frame_dict = get_complex_frame(self._center_point, self._zoom_factor, self._theta, self._n_rows, self._n_cols)
        vert_axis = np.linspace(frame_dict['top_center'], frame_dict['bottom_center'], self._n_cols) + 0.0j
        horiz_axis = np.linspace(frame_dict['left_center'], frame_dict['right_center'], self._n_cols) + 0.0j

        return horiz_axis, vert_axis


    def get_rails(self):
        """ top_rail, bottom_rail = self.get_styles() """
        frame_dict = get_complex_frame(self._center_point, self._zoom_factor, self._theta, self._n_rows, self._n_cols)
        top_rail = np.linspace(frame_dict['upper_left'], frame_dict['upper_right'], self._n_cols) + 0.0j
        bottom_rail = np.linspace(frame_dict['bottom_left'], frame_dict['bottom_right'], self._n_cols) + 0.0j

        return top_rail, bottom_rail


    def get_styles(self):
        """ left_style, right_style = self.get_styles() """
        frame_dict = get_complex_frame(self._center_point, self._zoom_factor, self._theta, self._n_rows, self._n_cols)
        left_style = np.linspace(frame_dict['upper_left'], frame_dict['bottom_left'], self._n_rows) + 0.0j
        right_style = np.linspace(frame_dict['upper_right'], frame_dict['bottom_right'], self._n_rows) + 0.0j

        return left_style, right_style


    def get_complex_row(self, row_number):
        """ row_vectors = self.get_complex_row() """
        left_style, right_style = self.get_styles()

        return np.linspace(left_style[row_number], right_style[row_number], self._n_cols) + 0.0j


    def get_complex_col(self, col_number):
        """ col_vectors = self.get_complex_col() """
        top_rail, bottom_rail = self.get_styles()

        return np.linspace(top_rail[col_number], bottom_rail[col_number], self._n_rows) + 0.0j


    def get_complex_pixels(self):
        """ complex_pixels = self.get_complex_pixels() """
        left_style, right_style = self.get_styles()
        complex_pixels = np.zeros((self._n_rows, self._n_cols)) + np.zeros((self._n_rows, self._n_cols)) * 1j

        for k in range(0, self._n_rows):
            complex_pixels[k, :] = np.linspace(left_style[k], right_style[k], self._n_cols)

        return complex_pixels

    
""" class ComplexPlane:  bottom line - wuf wuf """

# This is the "we are all adults here" pythonic traditional way for abstract classes
class exampl_base():

    def haka_haka(self):
        return NotImplementedError('Fix me! Fix me!')


class exampl_implement(exampl_base):

    def haka_haka(self):
        return 'whadayaexpect4free?'


# This is the newer way ...
from abc import ABCMeta, abstractmethod

class EquationIterator(metaclass=ABCMeta):

    def __init__(self, p=1.0, ETM=32, ETB=32, cpObj=ComplexPlane()):
        """ parameters, EscapeTimeMax, EscapeTimeBoundry, complexplaneObject  """
        self._ETM = ETM
        self._ETB = ETB
        self._p = p
        self._cpObj = cpObj

    @abstractmethod
    def iter_mat(self, dakine='DUCK'):
        """ test dakine """
        # print(dakine)
        # return 'de_nada'



class DoDaKine(EquationIterator):


    def iter_mat(self, dakine='Quack_Quack'):
        print(self._p, '\t', dakine)
        return 'hey_hey'
















""" EOF  """