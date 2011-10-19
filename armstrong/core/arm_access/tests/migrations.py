from south.creator import changes, actions
from south.migration.base import Migrations

from ._utils import ArmAccessTestCase as TestCase

class BasicMigrationsAreRunnableTestCase(TestCase):
    def test_verify_invalid_code_is_not_created(self):
        m = Migrations("arm_access_support", force_creation=False)
        c = changes.InitialChanges(m)
        params = c.get_changes().next()[1]
        actor = actions.AddModel(**params)
        code = actor.forwards_code()
        self.assertNotRegexpMatches(code, r"to=orm\['arm_access.AccessObject'\]")
