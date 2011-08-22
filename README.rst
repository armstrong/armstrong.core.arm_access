armstrong.core.arm_access
=========================
Code for creating access levels for armstrong.

.. warning:: This is development level software.  Please do not unless you are
             familiar with what that means and are comfortable using that type
             of software.

Usage
-----

Make sure that ``armstrong.core.arm_content`` is installed in your
environment and has been added to your ``INSTALLED_APPS``. You will also need
to make sure the models have been installed in your database via ``armstrong
syncdb``. See the 'Restricting Content' and 'User Memberships' sections for more
information.


Restricting Content
-------------------

Content objects can have access restricted to certain levels by having them
inherit from the ``armstrong.core.arm_access.mixins.AccessMixin`` class. This
will allow for the association of
``armstrong.core.arm_access.models.Assignment``'s which specify levels that
grant access to that object for a specific time frame.

For the basic paywall scenario where some stories are always premium and others
are always public, create two ``armstrong.core.arm_access.models.Level``'s. One
will be your premium level which will have ``is_protected`` set to ``True``
while the other will be your public level which will have ``is_protected`` set
to ``False``. When publishing an article, assign one of the two levels to the
content.

For content which is premium for a period and then becomes public, create two
levels as before. Assign new content to the premium level with an
immediate ``start_date``, and also assign it to the public
level with a ``start_date`` when you would like the content to become freely
available.

To restrict access to your archives to only premium subscribers you would add
content to the public level with an immediate ``start_date`` and an
``end_date`` of when you want to no longer offer free access. You will then
need to add the content to the premium level with an immediate ``start_date``
and no ``end_date`` (which will default to ``datetime.datetime.max``).

User Memberships
----------------

Users are granted access to Levels via
``armstrong.core.arm_access.models.AccessMembership``'s. Each membership has a
``start_date`` and ``end_date`` which defines the time frame for which the
membership is valid. Each memrbership also has an ``active`` boolean field
which can be set to False to invalidate the membership. A user's active
memberships can be queried with ``user.access_memberships.current()``

Paywalls
--------

The actual process of preventing a user from accessing a piece of content is
handled via the paywalls in the ``armstrong.core.arm_access.paywalls`` package.
Currently the only provided paywall is
``armstrong.core.arm_access.paywalls.subscription.SubscriptionPaywall`` which
checks for current memberships. The SubscriptionPaywall only works on a view
which returns a TemplateResponse.

To use the SubscriptionPaywall in the demo app, you would use code like the
following::

    ...

    paywall = SubscriptionPaywall()
    protected_detail = paywall.protect(object_detail)

    ...

    url(r'^article/(?P<slug>[-\w]+)/', protected_detail, {
                        'queryset':Article.published.all().select_subclasses(),
                        'template_name':'article.html',
                        'slug_field':'slug',
                    },
            name='article_detail'),

An AccessDenied would be raised any time a user visited an article that was
protected with an access Level that they didn't have a membership for.
SubscriptionPaywall takes an additional argument ``permission_denied`` that
determines what action to take on failure. The argument must be a callable that
takes one argument, a TemplateResponse, and returns a Response object
representing what to do on access denied. For example::
    
    # to redirect to a new url entirely
    from armstrong.core.arm_access.paywalls import redirect_on_deny
    redirecting_paywall = SubscriptionPaywall(
            permission_denied=redirect_on_deny='/membership/signup')

    # to render the request's context with a new template (to provide teaser
    # content)
    from armstrong.core.arm_access.paywalls import render_on_deny
    rendering_paywall = SubscriptionPaywall(
            permission_denied=render_on_deny='/membership/upsell.html')

If you wanted to only render ads for users without a premium access level, you
could use the SubscriptionPaywall with a default template that doesn't render
ads and a render_on_deny that does.

To only allow an anonymous user a certain number of full article views and then
display the paywall, you would need to build a custom paywall implementation,
but the SubscriptionPaywall should provide a decent template. If you do
implement it, it would be an excellent candidate for inclusion in this package.


Installation
------------

::

    name="armstrong.core.arm_access"
    pip install -e git://github.com/armstrong/$name#egg=$name


Contributing
------------

* Create something awesome -- make the code better, add some functionality,
  whatever (this is the hardest part).
* `Fork it`_
* Create a topic branch to house your changes
* Get all of your commits in the new topic branch
* Submit a `pull request`_

.. _pull request: http://help.github.com/pull-requests/
.. _Fork it: http://help.github.com/forking/


State of Project
----------------
Armstrong is an open-source news platform that is freely available to any
organization.  It is the result of a collaboration between the `Texas Tribune`_
and `Bay Citizen`_, and a grant from the `John S. and James L. Knight
Foundation`_.  The first release is scheduled for June, 2011.

To follow development, be sure to join the `Google Group`_.

``armstrong.apps.articles`` is part of the `Armstrong`_ project.  You're
probably looking for that.

.. _Texas Tribune: http://www.texastribune.org/
.. _Bay Citizen: http://www.baycitizen.org/
.. _John S. and James L. Knight Foundation: http://www.knightfoundation.org/
.. _Google Group: http://groups.google.com/group/armstrongcms
.. _Armstrong: http://www.armstrongcms.org/


License
-------
Copyright 2011 Bay Citizen and Texas Tribune

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
