#!/usr/bin/env python3

import unittest

from qdu import parse_args


class ArgparseTest(unittest.TestCase):
    def test_only_file_argument(self):
        args = parse_args(['foobar'])
        self.assertIn('foobar', args.files)
        self.assertFalse(args.in_kibibytes)
        self.assertEqual(args.user, 'admin')
        self.assertEqual(args.password, 'admin')
        self.assertEqual(args.port, 8000)

    def test_in_kibibytes_true_shorthand(self):
        args = parse_args(['-k', 'foobar'])
        self.assertTrue(args.in_kibibytes)

    def test_in_kibibytes_true_longhand(self):
        args = parse_args(['--in-kibibytes', 'foobar'])
        self.assertTrue(args.in_kibibytes)

    def test_user_shorthand(self):
        args = parse_args(['-u', 'my_user', 'foobar'])
        self.assertEqual(args.user, 'my_user')

    def test_user_longhand(self):
        args = parse_args(['--user', 'my_user', 'foobar'])
        self.assertEqual(args.user, 'my_user')

    def test_password_shorthand(self):
        args = parse_args(['-p', 'my_password', 'foobar'])
        self.assertEqual(args.password, 'my_password')

    def test_password_longhand(self):
        args = parse_args(['--password', 'my_password', 'foobar'])
        self.assertEqual(args.password, 'my_password')

    def test_port_shorthand(self):
        args = parse_args(['-P', '8001', 'foobar'])
        self.assertEqual(args.port, 8001)

    def test_port_longhand(self):
        args = parse_args(['--port', '8001', 'foobar'])
        self.assertEqual(args.port, 8001)


if __name__ == '__main__':
    unittest.main()

