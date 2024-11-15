from tests._constants import *
from tests import _utils as utils
from tests._utils import inject_click_at_pos_events, inject_keydown

class TestsEnd():
    def test_end(self):
        utils.running = False