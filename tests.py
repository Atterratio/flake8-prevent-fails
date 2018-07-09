import ast
import unittest
from flake8_prevent_fails import FailsChecker, MESSAGES


class TestIndexes(unittest.TestCase):
    def test_dirty_list(self):
        data = ast.parse('test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list[0]\n'
                         'except AttributeError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list[0]\n'
                         'except (AttributeError, Error):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except AttributeError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except (AttributeError, Error):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

    def test_cleaned_except_list_with_num(self):
        data = ast.parse('try:\n'
                         '    test_var = test_list[0]\n'
                         'except:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list[0]\n'
                         'except IndexError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list[0]\n'
                         'except (AttributeError, IndexError):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

    def test_cleaned_except_list_with_name(self):
        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except IndexError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except (AttributeError, IndexError):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

    def test_cleaned_if_lt_list_with_num(self):
        data = ast.parse('if 0 < len(test_list):\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('if 0 > len(over_list):\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('if 0 < len(test_list):\n'
                         '    test_var = test_list[1]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('if 0 < len(over_list):\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

    def test_cleaned_if_gt_list_with_num(self):
        data = ast.parse('if len(test_list) > 0:\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('if len(test_list) < 0:\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('if len(test_list) > 0:\n'
                         '    test_var = test_list[1]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

        data = ast.parse('if len(over_list) > 0:\n'
                         '    test_var = test_list[0]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF101'), result)

    def test_dirty_dict(self):
        data = ast.parse('test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list["test"]\n'
                         'except AttributeError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

        data = ast.parse('try:\n'
                         '    test_var = test_list["test"]\n'
                         'except (AttributeError, Error):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

    def test_cleaned_except_dict_with_str(self):
        data = ast.parse('try:\n'
                         '    test_var = test_list["test"]\n'
                         'except:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list["test"]\n'
                         'except KeyError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list["test"]\n'
                         'except (AttributeError, KeyError):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

    def test_cleaned_except_dict_with_name(self):
        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except KeyError:\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('try:\n'
                         '    test_var = test_list[var]\n'
                         'except (AttributeError, KeyError):\n'
                         '    pass')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

    def test_cleaned_if_dict_with_str(self):
        data = ast.parse('if test_list.get("test"):\n'
                         '    test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('if test_list.get("tests"):\n'
                         '    test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

        data = ast.parse('if tests_list.get("test"):\n'
                         '    test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

        data = ast.parse('if test_list.let("test"):\n'
                         '    test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)

    def test_cleaned_if_dict_with_name(self):
        data = ast.parse('if test_list.get(var):\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('if test_list.get(vars):\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('if test_list.get("tests"):\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('if tests_list.get(var):\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('if test_list.let(var):\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

    def test_cleaned_for_dict(self):
        data = ast.parse('for var in test_list:\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 0)

        data = ast.parse('for vars in test_list:\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('for var in tests_list:\n'
                         '    test_var = test_list[var]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF103'), result)

        data = ast.parse('for var in tests_list:\n'
                         '    test_var = test_list["test"]')
        checker = FailsChecker(data, None, None)
        results = list(e for e in checker.run())
        self.assertEqual(len(results), 1)
        for result in results:
            self.assertIn(MESSAGES.get('PF102'), result)


if __name__ == '__main__':
    unittest.main()
