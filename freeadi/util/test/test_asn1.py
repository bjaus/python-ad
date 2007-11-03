#
# This file is part of FreeADI. FreeADI is free software that is made
# available under the MIT license. Consult the file "LICENSE" that is
# distributed together with this file for the exact licensing terms.
#
# FreeADI is copyright (c) 2007 by the FreeADI authors. See the file
# "AUTHORS" for a complete overview.

import py.test
from freeadi.util import asn1

class TestEncoder(object):
    """Test suite for ASN1 Encoder."""

    def test_boolean(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(True, asn1.Boolean)
        res = enc.output()
        assert res == '\x01\x01\xff'

    def test_integer(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(1)
        res = enc.output()
        assert res == '\x02\x01\x01'

    def test_long_integer(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(0x0102030405060708090a0b0c0d0e0fL)
        res = enc.output()
        assert res == '\x02\x0f\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'

    def test_negative_integer(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(-1)
        res = enc.output()
        assert res == '\x02\x01\xff'

    def test_long_negative_integer(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(-0x0102030405060708090a0b0c0d0e0fL)
        res = enc.output()
        assert res == '\x02\x0f\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf1'

    def test_twos_complement_boundaries(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(127)
        res = enc.output()
        assert res == '\x02\x01\x7f'
        enc.start()
        enc.write(128)
        res = enc.output()
        assert res == '\x02\x02\x00\x80'
        enc.start()
        enc.write(-128)
        res = enc.output()
        assert res == '\x02\x01\x80'
        enc.start()
        enc.write(-129)
        res = enc.output()
        assert res == '\x02\x02\xff\x7f'

    def test_octet_string(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write('foo')
        res = enc.output()
        assert res == '\x04\x03foo'

    def test_null(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(None)
        res = enc.output()
        assert res == '\x05\x00'

    def test_enumerated(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write(1, asn1.Enumerated)
        res = enc.output()
        assert res == '\x0a\x01\x01'

    def test_sequence(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(asn1.Sequence)
        enc.write(1)
        enc.write('foo')
        enc.leave()
        res = enc.output()
        assert res == '\x30\x08\x02\x01\x01\x04\x03foo'

    def test_sequence_of(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(asn1.Sequence)
        enc.write(1)
        enc.write(2)
        enc.leave()
        res = enc.output()
        assert res == '\x30\x06\x02\x01\x01\x02\x01\x02'

    def test_set(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(asn1.Set)
        enc.write(1)
        enc.write('foo')
        enc.leave()
        res = enc.output()
        assert res == '\x31\x08\x02\x01\x01\x04\x03foo'

    def test_set_of(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(asn1.Set)
        enc.write(1)
        enc.write(2)
        enc.leave()
        res = enc.output()
        assert res == '\x31\x06\x02\x01\x01\x02\x01\x02'

    def test_context(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(1, asn1.ClassContext)
        enc.write(1)
        enc.leave()
        res = enc.output()
        assert res == '\xa1\x03\x02\x01\x01'

    def test_application(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(1, asn1.ClassApplication)
        enc.write(1)
        enc.leave()
        res = enc.output()
        assert res == '\x61\x03\x02\x01\x01'

    def test_private(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(1, asn1.ClassPrivate)
        enc.write(1)
        enc.leave()
        res = enc.output()
        assert res == '\xe1\x03\x02\x01\x01'

    def test_long_tag_id(self):
        enc = asn1.Encoder()
        enc.start()
        enc.enter(0xffff)
        enc.write(1)
        enc.leave()
        res = enc.output()
        assert res == '\x3f\x83\xff\x7f\x03\x02\x01\x01'

    def test_long_tag_length(self):
        enc = asn1.Encoder()
        enc.start()
        enc.write('x' * 0xffff)
        res = enc.output()
        assert res == '\x04\x82\xff\xff' + 'x' * 0xffff

    def test_error_init(self):
        enc = asn1.Encoder()
        py.test.raises(asn1.Error, enc.enter, asn1.Sequence)
        py.test.raises(asn1.Error, enc.leave)
        py.test.raises(asn1.Error, enc.write, 1)
        py.test.raises(asn1.Error, enc.output)

    def test_error_stack(self):
        enc = asn1.Encoder()
        enc.start()
        py.test.raises(asn1.Error, enc.leave)
        enc.enter(asn1.Sequence)
        py.test.raises(asn1.Error, enc.output)
        enc.leave()
        py.test.raises(asn1.Error, enc.leave)


class TestDecoder(object):
    """Test suite for ASN1 Decoder."""

    def test_boolean(self):
        buf = '\x01\x01\xff'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Boolean, asn1.TypePrimitive, asn1.ClassUniversal)
        val = dec.read()
        assert isinstance(val, int)
        assert val == True
        buf = '\x01\x01\x01'
        dec.start(buf)
        val = dec.read()
        assert isinstance(val, int)
        assert val == True
        buf = '\x01\x01\x00'
        dec.start(buf)
        val = dec.read()
        assert isinstance(val, int)
        assert val == False

    def test_integer(self):
        buf = '\x02\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Integer, asn1.TypePrimitive, asn1.ClassUniversal)
        val = dec.read()
        assert isinstance(val, int)
        assert val == 1

    def test_long_integer(self):
        buf = '\x02\x0f\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        dec = asn1.Decoder()
        dec.start(buf)
        val = dec.read()
        assert val == 0x0102030405060708090a0b0c0d0e0fL

    def test_negative_integer(self):
        buf = '\x02\x01\xff'
        dec = asn1.Decoder()
        dec.start(buf)
        val = dec.read()
        assert val == -1

    def test_long_negative_integer(self):
        buf = '\x02\x0f\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf1'
        dec = asn1.Decoder()
        dec.start(buf)
        val = dec.read()
        assert val == -0x0102030405060708090a0b0c0d0e0fL

    def test_twos_complement_boundaries(self):
        buf = '\x02\x01\x7f'
        dec = asn1.Decoder()
        dec.start(buf)
        val = dec.read()
        assert val == 127
        buf = '\x02\x02\x00\x80'
        dec.start(buf)
        val = dec.read()
        assert val == 128
        buf = '\x02\x01\x80'
        dec.start(buf)
        val = dec.read()
        assert val == -128
        buf = '\x02\x02\xff\x7f'
        dec.start(buf)
        val = dec.read()
        assert val == -129

    def test_octet_string(self):
        buf = '\x04\x03foo'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.OctetString, asn1.TypePrimitive, asn1.ClassUniversal)
        val = dec.read()
        assert isinstance(val, str)
        assert val == 'foo'

    def test_null(self):
        buf = '\x05\x00'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Null, asn1.TypePrimitive, asn1.ClassUniversal)
        val = dec.read()
        assert val is None

    def test_enumerated(self):
        buf = '\x0a\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Enumerated, asn1.TypePrimitive, asn1.ClassUniversal)
        val = dec.read()
        assert isinstance(val, int)
        assert val == 1

    def test_sequence(self):
        buf = '\x30\x08\x02\x01\x01\x04\x03foo'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Sequence, asn1.TypeConstructed, asn1.ClassUniversal)
        dec.enter()
        val = dec.read()
        assert val == 1
        val = dec.read()
        assert val == 'foo'

    def test_sequence_of(self):
        buf = '\x30\x06\x02\x01\x01\x02\x01\x02'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Sequence, asn1.TypeConstructed, asn1.ClassUniversal)
        dec.enter()
        val = dec.read()
        assert val == 1
        val = dec.read()
        assert val == 2

    def test_set(self):
        buf = '\x31\x08\x02\x01\x01\x04\x03foo'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Set, asn1.TypeConstructed, asn1.ClassUniversal)
        dec.enter()
        val = dec.read()
        assert val == 1
        val = dec.read()
        assert val == 'foo'

    def test_set_of(self):
        buf = '\x31\x06\x02\x01\x01\x02\x01\x02'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (asn1.Set, asn1.TypeConstructed, asn1.ClassUniversal)
        dec.enter()
        val = dec.read()
        assert val == 1
        val = dec.read()
        assert val == 2

    def test_context(self):
        buf = '\xa1\x03\x02\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (1, asn1.TypeConstructed, asn1.ClassContext)
        dec.enter()
        val = dec.read()
        assert val == 1

    def test_application(self):
        buf = '\x61\x03\x02\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (1, asn1.TypeConstructed, asn1.ClassApplication)
        dec.enter()
        val = dec.read()
        assert val == 1

    def test_private(self):
        buf = '\xe1\x03\x02\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (1, asn1.TypeConstructed, asn1.ClassPrivate)
        dec.enter()
        val = dec.read()
        assert val == 1

    def test_long_tag_id(self):
        buf = '\x3f\x83\xff\x7f\x03\x02\x01\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        tag = dec.peek()
        assert tag == (0xffff, asn1.TypeConstructed, asn1.ClassUniversal)
        dec.enter()
        val = dec.read()
        assert val == 1

    def test_long_tag_length(self):
        buf = '\x04\x82\xff\xff' + 'x' * 0xffff
        dec = asn1.Decoder()
        dec.start(buf)
        val = dec.read()
        assert val == 'x' * 0xffff

    def test_error_init(self):
        dec = asn1.Decoder()
        py.test.raises(asn1.Error, dec.peek)
        py.test.raises(asn1.Error, dec.read)
        py.test.raises(asn1.Error, dec.enter)
        py.test.raises(asn1.Error, dec.leave)

    def test_error_stack(self):
        buf = '\x30\x08\x02\x01\x01\x04\x03foo'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.leave)
        dec.enter()
        dec.leave()
        py.test.raises(asn1.Error, dec.leave)

    def test_no_input(self):
        dec = asn1.Decoder()
        dec.start('')
        tag = dec.peek()
        assert tag is None

    def test_error_missing_tag_bytes(self):
        buf = '\x3f'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.peek)
        buf = '\x3f\x83'
        dec.start(buf)
        py.test.raises(asn1.Error, dec.peek)

    def test_error_no_length_bytes(self):
        buf = '\x02'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_missing_length_bytes(self):
        buf = '\x04\x82\xff'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_too_many_length_bytes(self):
        buf = '\x04\xff' + '\xff' * 0x7f
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_no_value_bytes(self):
        buf = '\x02\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_missing_value_bytes(self):
        buf = '\x02\x02\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_non_normalized_positive_integer(self):
        buf = '\x02\x02\x00\x01'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

    def test_error_non_normalized_negative_integer(self):
        buf = '\x02\x02\xff\x80'
        dec = asn1.Decoder()
        dec.start(buf)
        py.test.raises(asn1.Error, dec.read)

