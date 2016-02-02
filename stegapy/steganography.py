import random
import math
import time


class SteganograpyException(Exception):
    """A Steganograpy Exception """
    pass

class FileTooLargeException(SteganograpyException):
    '''
    Custom Exception to throw if the file is too large to fit in
    the Image file specified
    '''
    pass

TERMINATION_SEQUENCE = '\xAA\xAA\xAA\xAA'


def will_data_fit(bit_num, image, bits_per_pix):
    """
    Verify that for a given encoding policy and image, all the data will fit
    :param bit_num: The number of data bits to be encoded
    :param image: The PIL image object into which the data will be encoded
    :param bits_per_pix: the number of bits per pixel that will be used for data
    :return: True if the data will fit, False otherwise
    """
    max_bits = reduce(lambda x, y: x * y, image.size) * bits_per_pix
    return bit_num <= max_bits


def dec_2_bin(n):
    '''
    Function to convert an integer to a list of 1s and 0s that is the
    binary equivalent.
    '''
    return list(bin(n)[2:].zfill(8))


def bin_2_dec(n):
    '''
    Function that takes a string of 1s and 0s and converts it back to an
    integer
    '''
    return int(n, 2)


class SteganographyEncoder(object):
    """A generic abstract class for encoding and decoding Steganographically"""

    def encode(self, encode_data, image):
        """
        Encode text data into an image file.
        :param image: a PIL Image object to use as the original image to encode into
        :param encode_data: a string of the data to be encoded in the image
        :return: A PIL Image object that has the data encoded into the image.
        """
        raise NotImplementedError("Not Implemented")

    def decode(self, image):
        """
        Remove text data from an image file
        :param image_file: The image file containing encoded data
        :return: A string of the data that was encoded in the file
        """
        raise NotImplementedError("Not Implemented")


class SimpleSteganography(SteganographyEncoder):

    def __init__(self, termination_sequence=TERMINATION_SEQUENCE):
        self.termination_sequence = termination_sequence

    def encode(self, encode_data, image):
        """
        Encode text data into an image file.
        :param image: a PIL Image object to use as the original image to encode into
        :param encode_data: a string of the data to be encoded in the image
        :return: A PIL Image object that has the data encoded into the image.
        """

        encode_data += self.termination_sequence
        data = ''
        for char in encode_data:
            data += "".join(dec_2_bin(ord(char)))

        if not will_data_fit(len(data), image, sum(self.get_color_bits_used())):
            raise FileTooLargeException("Image to small for current settings.")

        data_encode_pos = 0
        out_image = image.copy()
        curr_pixel_x = -1
        curr_pixel_y = -1
        for pixel in image.getdata():
            # This will hold the new array of R,G,B colors with the
            # embedded data
            new_col_arr = []

            curr_pixel_x = (curr_pixel_x + 1) % out_image.size[0]
            if curr_pixel_x == 0:
                curr_pixel_y += 1

            for curr_color_pos, color in enumerate(pixel):
                # if we still have data to encode
                if data_encode_pos < len(data):

                    # Number of bits to encode for this color
                    bits_to_encode = self.get_color_bits_used()[curr_color_pos]

                    # Encode the number of bits requested
                    tmp_color = dec_2_bin(color)

                    # get the next bits (number) bits from data, reverse (may change) them and
                    # assign them to the last bits (number) bits of the current color.
                    if data_encode_pos + bits_to_encode > len(data):
                        diff = data_encode_pos + bits_to_encode - len(data)
                        # TODO: Use some intelligence to fill in with previous pixel data instead of garbage
                        # We will have already encoded the termination sequence so anything here
                        # will be ignored in decoding, so we can fill with garbage.
                        data += ('0' * diff)

                    # If the bits to encode for a channel is zero, don't change anything.
                    if bits_to_encode != 0:
                        tmp_color[-bits_to_encode:] = self.get_encode_data_bits(data, data_encode_pos, bits_to_encode)

                    data_encode_pos += bits_to_encode

                    # Pull out a new int value for the encoded color
                    new_col = bin_2_dec("".join(tmp_color))
                else:
                    new_col = color

                # Append the new color to our new pixel array
                new_col_arr.append(new_col)

            # Append the new 3 color array to our new image data
            out_image.putpixel((curr_pixel_x, curr_pixel_y), tuple(new_col_arr))

        return out_image

    def decode(self, image):
        """
        Remove text data from an image file
        :param image_file: The image file containing encoded data
        :return: A string of the data that was encoded in the file
        """

        # The data pulled out
        data = []

        # A list to build the individual bits in
        curr_byte_list = []
        decode_complete = False
        for pixel in image.getdata():
            for curr_color_pos, color in enumerate(pixel):
                tmp_color = list(dec_2_bin(color))

                bits = self.get_color_bits_used()[curr_color_pos]

                # Pull out the specified number of bits based on the color

                curr_byte_list.extend(self.get_decode_data_bits(tmp_color, bits))

                # If we have a full byte or more add the bit to the data
                if len(curr_byte_list) >= 8:
                    data.append(chr(bin_2_dec(''.join(curr_byte_list[:8]))))
                    curr_byte_list = curr_byte_list[8:]

                # Stop if we've reached our termination characters
                if len(data) >= len(TERMINATION_SEQUENCE):
                    decode_complete = ''.join(data[-len(TERMINATION_SEQUENCE):]) == TERMINATION_SEQUENCE
                    if decode_complete:
                        break
            if decode_complete:
                break

        # Strip off the termination bytes
        return ''.join(data[:-len(TERMINATION_SEQUENCE)])

    def get_decode_data_bits(self, color_byte, bits_to_decode):
        raise NotImplementedError("Not Implemented")

    def get_encode_data_bits(self, data, start_pos, bits_to_encode):
        raise NotImplementedError("Not Implemented")

    def get_color_bits_used(self):
        raise NotImplementedError("Not Implemented")


class ForwardSteganography(SimpleSteganography):

    def __init__(self, color_bits, termination_sequence=TERMINATION_SEQUENCE):
        self.termination_sequence = termination_sequence
        self.color_bits = color_bits

    def get_encode_data_bits(self, data, start_pos, bits_to_encode):
        return data[start_pos:start_pos + bits_to_encode]

    def get_decode_data_bits(self, color_byte, bits_to_decode):
        if bits_to_decode == 0:
            return []
        return color_byte[-bits_to_decode:]

    def get_color_bits_used(self):
        return self.color_bits


class BackwardSteganography(SimpleSteganography):

    def __init__(self, color_bits, termination_sequence=TERMINATION_SEQUENCE):
        self.termination_sequence = termination_sequence
        self.color_bits = color_bits

    def get_encode_data_bits(self, data, start_pos, bits_to_encode):
        return list(reversed(data[start_pos:start_pos + bits_to_encode]))

    def get_decode_data_bits(self, color_byte, bits_to_decode):
        if bits_to_decode == 0:
            return []
        return list(reversed(color_byte[-bits_to_decode:]))

    def get_color_bits_used(self):
        return self.color_bits


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

