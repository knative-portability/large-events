"""Unit test runner for events service.

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


def run_test_suite():
    """Generate and run test suite and exit with correct status code."""
    suite = unittest.TestLoader().discover(".")
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    run_test_suite()
