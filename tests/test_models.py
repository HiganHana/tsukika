import unittest
from tsukika.models import Profile, Trophy, TrophyRecord, base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class t_models(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        base.metadata.create_all(self.engine)
        
    @contextmanager
    def session_scope(self):
        session = sessionmaker(bind=self.engine)()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
    

    def test_profile(self):
        with self.session_scope() as session:
            profile = Profile(discord_id=1234567890)
            session.add(profile)
            session.commit()
            self.assertEqual(profile.discord_id, 1234567890)
            
            test = session.query(Profile).filter_by(discord_id=1234567890).first()
            self.assertEqual(test.discord_id, 1234567890)
       

    def test_trophy(self):
        with self.session_scope() as session:
            trophy = Trophy(name="test trophy", unique=True)
            session.add(trophy)
            session.commit()
            
            test = session.query(Trophy).filter_by(name="test trophy").first()
            self.assertEqual(test.name, "test trophy")
            self.assertEqual(test.unique, True)

    def test_trophy_record(self):
        with self.session_scope() as session:
            trophy = Trophy(name="test trophy", unique=True)
            session.add(trophy)
            session.commit()
            
            record = TrophyRecord.create(1234567890, "test trophy")
            session.add(record)
            session.commit()
            
            test = session.query(TrophyRecord).filter_by(unique_string="1234567890_test trophy").first()
            self.assertEqual(test.unique_string, "1234567890_test trophy")
            self.assertEqual(test.discord_id, 1234567890)
            self.assertEqual(test.trophy_name, "test trophy")