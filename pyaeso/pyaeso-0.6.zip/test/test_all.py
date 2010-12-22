# Standard library imports
import unittest
import sys

# Custom test libraries
import libtest

# Testable libraries
import test_examples
import test_ets
import test_marginal_pool_price
import test_csd
import test_aieslog
import test_eventlog
import test_util
import test_mpp
import test_atc
import test_asset

test_modules = (
    test_aieslog,
    test_eventlog,
    test_csd,
    test_util,
    test_mpp,
    test_atc,
    test_asset,
)

loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromModule(test_examples),
    loader.loadTestsFromTestCase(test_marginal_pool_price.TestMarginalPoolPriceServiceBehaviour),
    loader.loadTestsFromModule(test_ets.TestLiveEtsConnection),
]

for module in test_modules:
    try:
        remote_suites.extend(module.remote_suites)
    except AttributeError:
        pass

local_suites = [
    loader.loadTestsFromTestCase(test_marginal_pool_price.TestMarginalPoolPrice),
    loader.loadTestsFromTestCase(test_ets.TestDayBlockIt),
    loader.loadTestsFromTestCase(test_ets.TestPoolPrice),
    loader.loadTestsFromTestCase(test_ets.TestAssetList),
]

for module in test_modules:
    try:
        local_suites.extend(module.local_suites)
    except AttributeError:
        pass

if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
