from armstrong.dev.tests.utils import ArmstrongTestCase
from armstrong.dev.tests.utils.concrete import *
from armstrong.dev.tests.utils.users import *

import fudge


class ArmAccessTestCase(ArmstrongTestCase):
    def setUp(self):
        super(ArmAccessTestCase, self).setUp()

    def tearDown(self):
        super(ArmAccessTestCase, self).tearDown()
