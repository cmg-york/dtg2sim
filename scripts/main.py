#!/usr/bin/env python3
import argparse
import json
import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from scripts import GMEnv
from scripts import Tester

def parse_args():
    parser = argparse.ArgumentParser(description='Run RL trials with configurable paths')
    parser.add_argument('pl_file', type=str, help='Path to the Prolog file')
    parser.add_argument('--config', type=str, default='scripts/config.json',
                      help='Path to the config file (default: scripts/config.json)')
    parser.add_argument('--sim-params', type=str, default='[1]',
                      help='Simulation parameters for semi-random simulation (default: [1])')
    return parser.parse_args()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def get_default_config(pl_file):
    """Get default configuration based on file."""
    base_config = {
        "simRandomIter": 100,
        "simCustomIter": 100,
        "simOptimalIter": 100,
        "testingIter": 1000,
        "trainingIter": 1000,
        "learningAlgorithm": "A2C",
        "learningLoggingInterval": 500,
        "dtGologOptimal": 0.9235,
        "simParams": [1],
        "seed": 123,
        "debug": False,
        "exampleType": "discrete",
        "forgivePenalty": True,
        "optimalSimParams": [0, 2],
        "multiRunSimParams": [0, 2, 0, 2],
        "inFeasiblePenalty": -100
    }
    
    # Load config file if it exists
    config_path = 'scripts/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            full_config = json.load(f)
            base_config.update(full_config)
    
    return base_config

class ConfigurableTest(unittest.TestCase):
    # Class variables for state sharing
    simRandom = 0
    simRandomForgive = 0
    simCustom = 0
    simOptimal = 0
    learningOptimal = 0
    learningParams = 0
    
    def __init__(self, method_name, pl_file, config, sim_params):
        super().__init__(method_name)
        self.pl_file = pl_file
        self.config = config
        self.sim_params = sim_params if sim_params else config.get('simParams', [1])
        
        # Set up test parameters from config
        self.simRandomIter = config.get('simRandomIter', 100)
        self.simCustomIter = config.get('simCustomIter', 100)
        self.simOptimalIter = config.get('simOptimalIter', 100)
        self.testingIter = config.get('testingIter', 1000)
        self.trainingIter = config.get('trainingIter', 1000)
        self.learningAlgorithm = config.get('learningAlgorithm', 'A2C')
        self.learningLoggingInterval = config.get('learningLoggingInterval', 500)
        self.dtGologOptimal = config.get('dtGologOptimal', 0.9235)
        self.seed = config.get('seed', 123)
        self.debug = config.get('debug', False)
        self.forgivePenalty = config.get('forgivePenalty', True)
        self.optimalSimParams = config.get('optimalSimParams', [0, 2])
        self.multiRunSimParams = config.get('multiRunSimParams', [0, 2, 0, 2])
        self.inFeasiblePenalty = config.get('inFeasiblePenalty', -100)

    def setUp(self):
        self.env = GMEnv.GMEnv(self.pl_file)
        self.env.setDebug(self.debug)
        self.env.setSeed(self.seed)
        self.t = Tester.TestIt(self.env)
        self.t.debug = self.debug

    def tearDown(self):
        self.env.closeQE()

    def test_semiRandonSim(self):
        """
        A simulation based on a crude policy that assumes certain success of actions.
        """
        result = self.t.simulate(self.simCustomIter, [1])
        ConfigurableTest.simCustom = result

    def test_randonSimForgive(self):
        """
        A random policy with penalty forgiveness
        """
        result = self.t.simulate(self.simRandomIter)
        ConfigurableTest.simRandom = result

    def test_randonSim(self):
        """
        A random policy without penalty forgiveness
        """
        result = self.t.simulate(self.simRandomIter, forgivePenalty=False)
        ConfigurableTest.simRandomForgive = result

    def test_optimalSim(self):
        """
        A simulation based on optimal policy parameters
        """
        if "3Build" in self.pl_file:
            result = self.t.simulate(self.simOptimalIter, [0, 2])
            ConfigurableTest.simOptimal = result
        elif "6BuildMultiRun" in self.pl_file or "5BuildContinuousMultiRun" in self.pl_file:
            result = self.t.simulate(self.simOptimalIter, self.multiRunSimParams)
            ConfigurableTest.simOptimal = result
        elif "2OrderMultiRun" in self.pl_file:
            result = self.t.simulate(self.simOptimalIter, [1, 1])
            ConfigurableTest.simOptimal = result
        elif "9SoSymExample" in self.pl_file:
            result = self.t.simulate(self.simOptimalIter, [0, 2])
            ConfigurableTest.simOptimal = result

    def test_learning(self):
        """
        Training and testing an RL agent
        """
        result, params = self.t.test_learning(
            self.trainingIter,
            self.testingIter,
            logging=self.learningLoggingInterval,
            algo=self.learningAlgorithm
        )
        ConfigurableTest.learningOptimal = result
        ConfigurableTest.learningParams = params
        self.assertAlmostEqual(
            result,
            self.dtGologOptimal,
            places=0,
            msg=f"\n Learning failed: {self.dtGologOptimal} expected, {result} observed"
        )

    def test_advancedpolicy(self):
        """
        Test advanced policy for heating examples
        """
        if "Heating" in self.pl_file:
            # Add advanced policy test implementation here
            pass

    def print_results(self):
        print('DT-Golog - calculated policy reward: {}'.format(self.dtGologOptimal))
        if ConfigurableTest.simOptimal != 0:
            print('DT-Golog - simulated policy reward.: {}'.format(ConfigurableTest.simOptimal))
        print('Partially optimal policy reward....: {}'.format(ConfigurableTest.simCustom))
        print('Random policy reward.............. : {}'.format(ConfigurableTest.simRandom))
        print('Random policy reward.(fg)......... : {}'.format(ConfigurableTest.simRandomForgive))
        print('Learned policy reward..............: {}'.format(ConfigurableTest.learningOptimal))
        print('--> Learning Parameters: \n {}'.format(ConfigurableTest.learningParams))

def get_test_methods(pl_file):
    """Get the appropriate test methods based on the Prolog file."""
    # For 3Build, use exact same order as 3SBuild_Trials.py
    if "3Build" in pl_file:
        return ['test_optimalSim', 'test_randonSimForgive', 'test_randonSim', 'test_learning']
    
    # For 1Order, use exact same order as 1Order_Trials.py
    if "1Order" in pl_file:
        return ['test_semiRandonSim', 'test_randonSimForgive', 'test_randonSim', 'test_learning']
    
    # Base methods that are common to most examples
    base_methods = ['test_semiRandonSim', 'test_randonSimForgive', 'test_randonSim', 'test_learning']
    
    # Remove forgive penalty test for continuous examples
    if 'continuous' in pl_file:
        base_methods.remove('test_randonSimForgive')
    
    # Add optimal simulation for specific examples
    if any(x in pl_file for x in ["6BuildMultiRun", "5BuildContinuousMultiRun", "2OrderMultiRun", "9SoSymExample"]):
        base_methods.insert(1, 'test_optimalSim')
    
    # Add advanced policy test for heating examples
    if "Heating" in pl_file:
        base_methods.append('test_advancedpolicy')
    
    return base_methods

def main():
    args = parse_args()
    
    # Validate paths
    if not os.path.exists(args.pl_file):
        print(f"Error: Prolog file not found: {args.pl_file}")
        sys.exit(1)
    if not os.path.exists(args.config):
        print(f"Warning: Config file not found: {args.config}")
        print("Using default configuration...")
        config = get_default_config(args.pl_file)
    else:
        config = load_config(args.config)
    
    # Override config with command line arguments if provided
    if args.sim_params:
        config['simParams'] = eval(args.sim_params)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Get appropriate test methods for this example
    test_methods = get_test_methods(args.pl_file)
    
    for method_name in test_methods:
        test_case = ConfigurableTest(method_name, args.pl_file, config, args.sim_params)
        suite.addTest(test_case)
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    # Print results from the last test case
    test_case.print_results()

if __name__ == '__main__':
    main() 