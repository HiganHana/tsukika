import unittest

from tsukika.db import DbProfile
import inspect
from sqlalchemy.orm.attributes import InstrumentedAttribute

class test_proof_of_concept(unittest.TestCase):
    def test_1(self):
        """
        this is to check whether db model classes can be easily inspected
        """
        names = []
        
        for name, obj in inspect.getmembers(DbProfile):
            if isinstance(obj, InstrumentedAttribute):
                names.append(name)
                
        pass