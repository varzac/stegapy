import random
from PIL import Image
import math
from steganography import ForwardSteganography, BackwardSteganography, dec_2_bin, TERMINATION_SEQUENCE, \
    bin_2_dec, FileTooLargeException


def encode(image, encode_data, color_bits=None, forward=True):
    """
    Encode text data into an image file.
    :param image: A PIL image object of the Image to encode data into
    :param encode_data: a string of the data to encode into the image
    :param color_bits: [red_bits, green_bits, blue_bits] where each value describes the number of
    that color's bits to use for data encoding
    :param forward: determines whether for multiple bits for a color it goes from -3, to -2, to -1 (True)
    or goes from position -1, to -2, to -3 (False)
    :return: A tuple with two items. A PIL Image object that has the data encoded into the image.
    And the color_bits encoding used to encode that image  i.e. (image, color_bits)
    """

    if color_bits is None:
        color_bits = get_recommended_encoding(encode_data, image, TERMINATION_SEQUENCE)

    if forward:
        encoder = ForwardSteganography(color_bits)
    else:
        encoder = BackwardSteganography(color_bits)

    return (encoder.encode(encode_data, image), color_bits)


def decode(im_dec, color_bits=None, forward=True):
    """
    Remove text data from an image file
    :param im_dec: The image file containing encoded data
    :param color_bits: [red_bits, green_bits, blue_bits] where each value describes the number of
    that color's bits that containes encoded data
    :param forward: determines whether for multiple bits for a color the data was encoded from -3, to -2, to -1 (True)
    or goes from position -1, to -2, to -3 (False)
    :return: A string of the data that was encoded in the file
    """
    if color_bits is None:
        color_bits = [1, 1, 1]

    in_image = Image.open(im_dec)

    if forward:
        encoder = ForwardSteganography(color_bits)
    else:
        encoder = BackwardSteganography(color_bits)

    return encoder.decode(in_image)


def get_recommended_encoding(encode_data, image, termination_sequence):
    '''
    This will return a list that is the recommended encoding policy for the
    given file to encode (en_filename) and image (image_filename)
    '''
    data_bits = len(encode_data) * 8 + len(termination_sequence) * 8

    num_pix = image.size[0] * image.size[1]
    bits_per_pix = math.ceil(float(data_bits) / num_pix)
    bits_config = []
    for i in xrange(3, 0, -1):
        bits_config.append(int(math.floor(bits_per_pix / float(i))))
        bits_per_pix = bits_per_pix - bits_config[-1]
    if max(bits_config) > 8:
        raise FileTooLargeException("The given data file will not fit into the given image file")
    random.shuffle(bits_config)
    return bits_config


if __name__ == '__main__':
    pass

