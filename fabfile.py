from armstrong.dev.tasks import *


settings = {
    'DEBUG': True,
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'armstrong.core.arm_access',
        'armstrong.core.arm_access.arm_access_support',
        'lettuce.django',
    ),
}

tested_apps = ("arm_access", )
