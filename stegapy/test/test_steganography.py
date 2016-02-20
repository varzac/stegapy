from unittest import TestCase
import itertools
from stegapy import ForwardSteganography, FileTooLargeException, BackwardSteganography, dec_2_bin
from PIL import Image


class TestForwardSteganography(TestCase):

    def setUp(self):
        self.steg = ForwardSteganography(color_bits=[1, 1, 1], termination_sequence='\xff\xff')

    def test_get_encode_data_bits(self):
        self.assertListEqual([0, 1, 1, 0],
                              self.steg.get_encode_data_bits([1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1], 1, 4))

    def test_get_decode_bits(self):
        self.assertListEqual([0, 1, 1, 1],
            self.steg.get_decode_data_bits([1, 0, 1, 1, 0, 1, 1, 1], 4))

    def test_encode_full(self):
        message = "\xaa" * 4
        # Message bits + termination sequence bits
        expected_out = [1, 0] * 16 + [1] * 16
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        for out, expected in zip(itertools.chain(*list(out_image.getdata())), expected_out):
            # Mask off all but the last bit of each channel and compare to the expected bit
            self.assertEqual(out & 0x01, expected)

    def test_encode_zero_channel(self):
        message = "\xaa" * 4
        # Message bits + termination sequence bits
        expected_out = [1, 0] * 16 + [1] * 16
        self.steg.color_bits = [1, 2, 0]
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        channel = 0
        out_bits = []
        # For each channel in order
        for out in itertools.chain(*list(out_image.getdata())):
            # For each bit in left to right order in the channel based on self.steg.color_bits
            # The negative xrange iterator is so that you pull out the most significant bits first (i.e
            # you shift 1 pos then mask before you shift 0 pos then mask)
            for bit_pos in xrange(self.steg.color_bits[channel] - 1, -1, -1):
                out_bits.append((out >> bit_pos) & 0x01)
            channel = (channel + 1) % 3
        self.assertListEqual(expected_out, out_bits)

    def test_encode_too_large(self):
        message = "\xaa" * 5
        self.assertRaises(FileTooLargeException, self.steg.encode, message, Image.new('RGB', (4, 4), color="black"))

    def test_encode_not_full(self):
        message = "\xaa" * 2
        # Message bits + termination sequence bits + 0 bits for black base image
        expected_out = [1, 0] * 8 + [1] * 16 + [0] * 16
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        for out, expected in zip(itertools.chain(*list(out_image.getdata())), expected_out):
            # Mask off all but the last bit of each channel and compare to the expected bit
            self.assertEqual(out & 0x01, expected)

    def test_decode_full(self):
        # 32 bytes where the last bits alternate 0 then 1 followed by the termination sequence
        # TODO: Find a better way to create encoded images
        image_bytes = "\x00\xff" * 16 + "\xff" * 16
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str = self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        self.assertListEqual(['0', '1'] * 16, out_bits)

    def test_decode_not_full(self):
        # 16 bytes where the last bits alternate 0 then 1 followed by the termination sequence then whatever
        image_bytes = "\x00\xff" * 8 + "\xff" * 32
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str =  self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        self.assertListEqual(['0', '1'] * 8, out_bits)

    def test_decode_zero_channel(self):
        self.steg.color_bits = [1, 2, 0]
        # Since this grabs 1 2 then 0 bits it should result in 011 repeating
        image_bytes = "\x00\xff\x00" * 10 + "\x00\xff" + "\xff" * 16
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str =  self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        expected_bits = ['0', '1', '1'] * 10 + ['0', '1']
        self.assertListEqual(expected_bits, out_bits)


class TestBackwardSteganography(TestCase):

    def setUp(self):
        self.steg = BackwardSteganography(color_bits=[1, 1, 1], termination_sequence='\xff\xff')

    def test_get_encode_data_bits(self):
        self.assertListEqual([1, 1, 1, 1, 0],
                              self.steg.get_encode_data_bits([1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1], 8, 5))

    def test_get_decode_bits(self):
        self.assertListEqual([1, 1, 1, 0],
            self.steg.get_decode_data_bits([1, 0, 1, 1, 0, 1, 1, 1], 4))

    def test_encode_full(self):
        message = "\xaa" * 4
        # Message bits + termination sequence bits
        expected_out = [1, 0] * 16 + [1] * 16
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        for out, expected in zip(itertools.chain(*list(out_image.getdata())), expected_out):
            # Mask off all but the last bit of each channel and compare to the expected bit
            self.assertEqual(out & 0x01, expected)

    def test_encode_zero_channel(self):
        message = "\xaa" * 4
        # Message bits + termination sequence bits
        expected_out = [1, 0] * 16 + [1] * 16
        self.steg.color_bits = [1, 2, 0]
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        channel = 0
        out_bits = []
        # For each channel in order
        for out in itertools.chain(*list(out_image.getdata())):
            # For each bit in left to right order in the channel based on self.steg.color_bits
            # The positive xrange iterator is so that you pull out the least significant bits first (i.e
            # you shift 0 pos then mask before you shift 1 pos then mask)
            for bit_pos in xrange(self.steg.color_bits[channel]):
                out_bits.append((out >> bit_pos) & 0x01)
            channel = (channel + 1) % 3
        self.assertListEqual(expected_out, out_bits)

    def test_encode_too_large(self):
        message = "\xaa" * 5
        self.assertRaises(FileTooLargeException, self.steg.encode, message, Image.new('RGB', (4, 4), color="black"))

    def test_encode_not_full(self):
        message = "\xaa" * 2
        # Message bits + termination sequence bits + 0 bits for black base image
        expected_out = [1, 0] * 8 + [1] * 16 + [0] * 16
        out_image = self.steg.encode(message, Image.new('RGB', (4, 4), color="black"))
        for out, expected in zip(itertools.chain(*list(out_image.getdata())), expected_out):
            # Mask off all but the last bit of each channel and compare to the expected bit
            self.assertEqual(out & 0x01, expected)

    def test_decode_full(self):
        # 32 bytes where the last bits alternate 0 then 1 followed by the termination sequence
        # TODO: Find a better way to create encoded images
        image_bytes = "\x00\xff" * 16 + "\xff" * 16
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str = self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        self.assertListEqual(['0', '1'] * 16, out_bits)

    def test_decode_not_full(self):
        # 16 bytes where the last bits alternate 0 then 1 followed by the termination sequence then whatever
        image_bytes = "\x00\xff" * 8 + "\xff" * 32
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str =  self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        self.assertListEqual(['0', '1'] * 8, out_bits)

    def test_decode_zero_channel(self):
        self.steg.color_bits = [1, 2, 0]
        # Since this grabs 1 2 then 0 bits it should result in 001 repeating
        image_bytes = "\x00\xaa\x00" * 10 + "\x00\xff" + "\xff" * 16
        im = Image.frombytes('RGB', (4, 4), image_bytes)
        out_str =  self.steg.decode(im)
        out_bits = []
        for char in out_str:
            out_bits.extend(dec_2_bin(ord(char)))
        expected_bits = ['0', '0', '1'] * 10 + ['0', '1']
        self.assertListEqual(expected_bits, out_bits)
