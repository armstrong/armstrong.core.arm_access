from armstrong.dev.tests.utils.users import generate_random_user

from ._utils import *
from ..models import *
from .arm_access_support.models import *


class AccessModelsTestCase(ArmAccessTestCase):
    def testAccessMembershipStr(self):
        args = {}
        args['user'] = generate_random_user()
        args['level'] = Level(name="foo", is_protected=False)
        args['start_date'] = datetime.datetime.now()
        args['end_date'] = datetime.datetime.now()
        self.assertEqual('%s (foo)' % (args['user']),
                         str(AccessMembership(**args)))

