from icbc.road_test import RoadTestAppointment, ICBCLoginError
import pytest


def test_failed_login():
    with pytest.raises(ICBCLoginError, match='Couldn`t login'):
         RoadTestAppointment(last_name='', licence_number='', keyword='')
    