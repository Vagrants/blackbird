# -*- coding: utf-8 -*-

import os
import validate

import nose.tools

import blackbird.utils.configread


class TestConfigReaderIsDir(object):

    def test_exist_directory(self):
        nose.tools.ok_(
            blackbird.utils.configread.is_dir(
                os.path.dirname(__file__)
            )
        )

    @nose.tools.raises(validate.VdtValueError)
    def test_non_exist_directory(self):
        blackbird.utils.configread.is_dir(
            '/hogehoge'
        )

    @nose.tools.raises(validate.VdtTypeError)
    def test_exist_file(self):
        blackbird.utils.configread.is_dir(__file__)

    @nose.tools.raises(validate.VdtValueError)
    def test_non_read_permission(self):
        value = os.path.join(
            os.path.dirname(__file__),
            'cannot_read_dir'
        )
        blackbird.utils.configread.is_dir(value)
