import os
import sys
import hashlib
import stegapy
from PIL import Image


def test_encode(tmp_image_file=None, tmp_text_file=None, *args):
    (image, color_bits) = stegapy.encode(*args)
    image.save(tmp_image_file)
    if isinstance(args[-1], bool):
        out_data = stegapy.decode(tmp_image_file, color_bits=color_bits, forward=args[-1])
    else:
        out_data = stegapy.decode(tmp_image_file, color_bits=color_bits)
    with open(tmp_text_file, 'wb') as f:
        f.write(out_data)
    out_text = open(tmp_text_file, 'r').read()
    decode_hash = hashlib.md5()
    decode_hash.update(out_text)
    decoded = decode_hash.digest()
    text_hash = hashlib.md5()
    text_hash.update(macbeth_data)
    from_text = text_hash.digest()
    return decoded == from_text


def test_forward_encode(tree_image, macbeth_data, tmp_image_file, tmp_text_file):
    args = (tree_image, macbeth_data, [2, 2, 3])
    return test_encode(tmp_image_file, tmp_text_file, *args)


def test_backward_encode(tree_image, macbeth_data, tmp_image_file, tmp_text_file):
    args = (tree_image, macbeth_data, [2, 2, 3], False)
    return test_encode(tmp_image_file, tmp_text_file, *args)


def test_autosize(tree_image, macbeth_data, tmp_image_file, tmp_text_file):
    args = (tree_image, macbeth_data)
    return test_encode(tmp_image_file, tmp_text_file, *args)


if __name__ == "__main__":
    dir = os.path.abspath(sys.modules['__main__'].__file__).rsplit(os.path.sep, 1)[0]
    macbeth_file = os.path.join(dir, os.pardir, os.pardir, 'resources', 'Macbeth.txt')
    tree_file = os.path.join(dir, os.pardir, os.pardir, 'resources', 'Tree.PNG')
    tmp_image_file = os.path.join(dir, os.pardir, os.pardir, 'resources', 'tmp.png')
    tmp_text_file = os.path.join(dir, os.pardir, os.pardir, 'resources', 'tmp.txt')

    tree_image = Image.open(tree_file, 'r')
    macbeth_data = ""
    with open(macbeth_file, 'r') as mf:
        macbeth_data = mf.read()

    print "TESING ENCODE FORWARD"
    status = "PASSED" if test_forward_encode(tree_image, macbeth_data, tmp_image_file, tmp_text_file) else "FAILED"
    print "{} ENCODE FORWARD".format(status)

    print "TESING ENCODE BACKWARD"
    status = "PASSED" if test_backward_encode(tree_image, macbeth_data, tmp_image_file, tmp_text_file) else "FAILED"
    print "{} ENCODE BACKWARD".format(status)

    print "TESING AUTOSIZE"
    status = "PASSED" if test_autosize(tree_image, macbeth_data, tmp_image_file, tmp_text_file) else "FAILED"
    print "{} AUTOSIZE".format(status)
