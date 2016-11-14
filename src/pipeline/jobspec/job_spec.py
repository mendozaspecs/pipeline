# -*- coding: utf-8 -*-

# Full Imports
import json
import simplejson
import collections
import itertools
import six
import sys
import logging

# Specific Imports
from enum import Enum

# Global Variables declaration
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# JobType class
class JobType(Enum):
  ONE_TO_ONE  = 1
  ONE_TO_MANY = 2
  MANY_TO_ONE = 3

# JobSpec class
class JobSpec(object):
  def __init__(self, params_hash, job_type):
    self.params_hash = params_hash
    self.job_type    = job_type

  def get_params_hash(self, key):
    if key in self.params_hash:
      return self.params_hash[key]
    else:
      logger.debug("[JobSpec] Key not found")

  def construct_params_hash(self, **kwargs):
    self.params_hash = kwargs

  def writeJsonToFile(self, ofd):
    """ Function to write JSON object to 
        a file represented by ofd
  
      Args:
        ofd : Output File Descriptor
        json_obj : JSON to be dumped

      Returns:
        No return value

      Raises:
        Exception: If file write fails
    """
    try:
      ofd.write(json.dumps(self.params_hash))
      logger.debug("[JobSpec] Write complete")
    except Exception as inst:
      logger.error(type(inst)) 
      logger.error(inst.args)
      logger.error (inst)