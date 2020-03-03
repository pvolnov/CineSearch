import os
import unittest
from unittest import TestCase

from models import Users, db
from predict.UserGroupClassifiter import UserGroupClassifiter


class TestUserGroupClassifier(TestCase):
    def setUp(self):
        db.manual_commit()
        db.begin()
        os.environ.setdefault("TEST","Predict")
        self.gg = UserGroupClassifiter()

    def tearDownModule(self):
        db.rollback()
        db.close()
        os.environ.pop("TEST")


    def test_user_preparation(self):
        u=Users.get()
        from playhouse.shortcuts import model_to_dict
        u=model_to_dict(u)
        u = self.gg.user_preparation(u)
        self.assertIsInstance(u,list)

    def test_get_group(self):
        u = Users.get()
        group = self.gg.get_group(u)
        self.assertIsInstance(group,int)

    # @unittest.skip("lererning skipping")
    def test_upload_all_groups(self):
        self.gg.upload_all_groups()
