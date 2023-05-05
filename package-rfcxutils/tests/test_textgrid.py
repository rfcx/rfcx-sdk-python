from unittest import TestCase

import rfcx

class TextGridTests(TestCase):
    def test_can_get_intervals(self):
        # Arrange
        filename = 'tests/test.TextGrid'
        # Act
        tg = rfcx.TextGrid.fromFile(filename)
        # Assert
        self.assertEqual(1, len(tg))
        self.assertEqual(5, len(tg[0]))
        self.assertEqual(43.018, tg[0][0].minTime)
        self.assertEqual(43.819, tg[0][0].maxTime)
        self.assertEqual('spider_monkey_generic', tg[0][0].mark)
        self.assertEqual(47.203, tg[0][4].minTime)
        self.assertEqual(48.005, tg[0][4].maxTime)
        self.assertEqual('spider_monkey_generic', tg[0][4].mark)
