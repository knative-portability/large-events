"""Unit test runner for pageserve service.

Test runner that runs several different test modules.
To see the tests, look at the sibling test_*.py files."""

# Authors: mukobi
# Copyright 2019 The Knative Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import sys

import test_serve


def generate_suite():
    """Generates and loads a test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromModule(test_serve))
    return suite


def run_test_suite():
    """Runs the test suite and exits with correct status code."""
    result = unittest.TextTestRunner().run(generate_suite())
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    run_test_suite()
