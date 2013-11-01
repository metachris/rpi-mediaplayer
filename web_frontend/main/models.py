# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

