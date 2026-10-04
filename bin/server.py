#!/usr/bin/env python3
import os
from common import config
c=config();h=c['herdr']
os.execvp(h,[h,'--session',c['session'],'server'])
