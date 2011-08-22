Feature: Access Nodes
    Content should be related to different access levels such that they are
    available on different days

    Scenario: Content has no Access Object attached
        Given A piece of content exists
        And it has no access defined
        And a user has no access levels defined
        And the default has_access backend is configured
        When the access check is performed
        Then access should be allowed

    Scenario: Content has everyone Access Node attached
        Given A piece of content exists
        And it has a everyone access node with a date in the past
        And a user has no access levels defined
        And the default has_access backend is configured
        When the access check is performed
        Then access should be allowed

    Scenario: Content has premium Access Node attached
        Given A piece of content exists
        And it has a premium access node with a date in the past
        And a user has no access levels defined
        And the default has_access backend is configured
        When the access check is performed
        Then access should be denied

    Scenario: Content has premium Access Node attached and user is premium
        Given A piece of content exists
        And it has a premium access node with a date in the past
        And a user has the premium access level
        And the default has_access backend is configured
        When the access check is performed
        Then access should be allowed

    Scenario: Content has both premium and everyone nodes attached
        Given A piece of content exists
        And it has a everyone access node with a date in the future
        And it has a premium access node with a date in the past
        And a user has no access levels defined
        And the default has_access backend is configured
        When the access check is performed
        Then access should be denied
