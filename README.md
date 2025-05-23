# RL Gen
Title: _Tool and Reproducibility Package for: Model-driven Design and Generation of Training Simulators for Reinforcement Learning_



## Overview
This repository contains the scripts and examples that accompany the conference submission "Model-driven Design and Generation of Domain Simulators for Reinforcement Learning". 

The python scripts implementing GMEnv and and Query Interface can be found in `/scripts`
The example goal models and various tests and experiments against them can be found in `/examples`


## Prerequisites
- Python 3.13 (latest) - This project has been tested with Python 3.13 and may not work with other versions
- SWI-Prolog (for running the DT-Golog code)
- Git

## Installation and Setup Instructions

### Option 1: Using Docker (Recommended)
The easiest way to run the project is using Docker. This method requires no manual installation of dependencies.

1. **Install Docker**
   - Install Docker from [docker.com](https://www.docker.com/products/docker-desktop)

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dtg2sim
   ```

3. **Use the pre-built Docker image**
   ```bash
   # Pull the latest image from GitHub Container Registry
   docker pull ghcr.io/cmg-york/dtg2sim:latest
   ```

   OR

   **Build the Docker image locally**
   ```bash
   docker build -t rlgen .
   ```

4. **Run simulations or training**
   ```bash
   # Using the pre-built image
   docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/3Build.pl --mode simulate --config scripts/config.json

   # OR using locally built image
   docker run -it rlgen python scripts/main.py examples/discrete/3Build.pl --mode simulate --config scripts/config.json

   # For training
   docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/3Build.pl --mode train --config scripts/config.json
   ```

### Option 2: Manual Installation
If you prefer to run the project directly on your system, follow these steps:

1. **Clone the repository locally.**
   ```bash
   git clone <repository-url>
   cd dtg2sim
   ```

2. **Verify Python version and create virtual environment:**
   ```bash
   # Check Python version
   python --version  # Should show Python 3.13.x
   ```
   ```bash
   # Create virtual environment with Python 3.13
   python -m venv venv
    ```
   
   ```bash
   
   source venv/bin/activate  # On Linux/Mac
   # OR
   venv\Scripts\activate     # On Windows
   ```
   
   On Windows, you may need to open in Powershell as administrator and give:

	```
	Set-ExecutionPolicy RemoteSigned 
	```
	Watch for `(venv)` to appear at the beginning of your commant prompt to verify that the virtual environment is active.

3. **Install the required dependencies:**
   ```bash
   # Install project dependencies
   python -m pip install -r requirements.txt
   ```

   This will install all necessary packages with the correct versions for this project.

4. **Acquire the DT-Golog code** from [its creator's page](https://www.cs.ryerson.ca/~mes/publications/appendix/appendixC/dtgolog), and place it in a file called `DT-Golog.pl` under `/scripts/QE/`

5. **Make the following changes so that it runs on SWI-Prolog**
  - Comment out the following:
    ```
    /* :- pragma(debug).  */
    ```
  - Add:
    ```
    :- op(900, fy, [not]).
    (not X) := (\+ X).
    cputime(5).
    ```
6. **Run the test and trial scripts in the `/examples` folder from your IDE.**

## The Models

* Several models have been developed for tests and experiments. They can be reviewed in GoalModels.drawio which can be opened using https://app.diagrams.net/
* The corresponding specifications can be found in the `.pl` file in the `/examples` folder. The same model may have both a discrete and a continuous implementation (which are different only in one line of code whereby the state space is specified).
* Files named `[XXX]_Tests.py` contain simple python `unittest` tests.
* Files named `[XXX]_Trials.py` contain simulation and learning experiments. 
  * For running simulations or learning be sure to give meaningful iteration numbers to `simRandomIter`, `simOptimalRandomIter`, `trainingIter` (number of training steps) `testingIter` (number of testing episodes). `10,000` is a good number to start with.
  * `learningAlgorithm` can be one of `A2C`, `PPO`, or `DQN` implemented as part of [stable-baselines3](https://stable-baselines3.readthedocs.io/en/master/guide/algos.html)

## Running Simulations and Training

The project provides a unified command-line interface through `scripts/main.py` for running both simulations and training. This replaces the need to run individual trial scripts directly.

### Command Line Interface

```bash
  python scripts/main.py <pl_file> --mode {simulate,train} --config <config_file> [--sim-params <params>]
```

Required arguments:
- `pl_file`: Path to the Prolog file containing the domain specification (e.g., `examples/discrete/3Build.pl`)
- `--mode`: Operation mode, either `simulate` or `train`
- `--config`: Path to the JSON configuration file (e.g., `scripts/config.json`)

Optional arguments:
- `--sim-params`: Simulation parameters for semi-random simulation (default: `[1]`)

### Configuration File

The configuration file (`config.json`) controls various parameters for both simulation and training modes. Here's an example configuration:

```json
{
    "debug": false,
    "seed": 123,
    "simRandomIter": 100,
    "simCustomIter": 100,
    "simOptimalIter": 100,
    "testingIter": 1000,
    "trainingIter": 1000,
    "learningAlgorithm": "PPO",
    "learningLoggingInterval": 500,
    "optimalSimParams": [0, 2],
    "dtGologOptimal": 0.476
}
```

Configuration parameters:
- `debug`: Enable/disable debug output
- `seed`: Random seed for reproducibility
- `simRandomIter`: Number of iterations for random simulation
- `simCustomIter`: Number of iterations for custom simulation
- `simOptimalIter`: Number of iterations for optimal simulation
- `testingIter`: Number of testing episodes for training
- `trainingIter`: Number of training steps
- `learningAlgorithm`: Learning algorithm to use (`A2C`, `PPO`, or `DQN`)
- `learningLoggingInterval`: Interval for logging during training
- `optimalSimParams`: Parameters for optimal simulation
- `dtGologOptimal`: Expected optimal reward value

### Example Usage

1. Running simulations:
```bash
python scripts/main.py examples/discrete/3Build.pl --mode simulate --config scripts/config.json
```

2. Running training:
```bash
python scripts/main.py examples/discrete/3Build.pl --mode train --config scripts/config.json
```

The script will output results in a format consistent with the original trial scripts, including:
- For simulation mode:
  - DT-Golog simulated policy reward
  - Random simulated policy reward (with and without penalty forgiveness)
- For training mode:
  - Learned policy reward
  - Learning parameters

# Contact

Please send questions, issues, bugs and recommendations to [liaskos@yorku.ca](mailto:liaskos@yorku.ca?Subject=RLGen).

## Quick Start with Docker

The easiest way to use this project is through Docker. Follow these steps:

1. **Install Docker**
   - Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
   - Verify installation by running `docker --version`

2. **Pull the Docker Image**
   ```bash
   docker pull ghcr.io/cmg-york/dtg2sim:latest
   ```

3. **Run Examples**
   ```bash
   # Run a simulation using the 3Build example
   docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/3Build.pl --mode simulate --config scripts/config.json

   # Run training using the 3Build example
   docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/3Build.pl --mode train --config scripts/config.json
   ```

4. **Try Different Examples**
   - Replace `3Build.pl` with any other .pl file from the `examples/discrete` or `examples/continuous` directories
   - For example:
     ```bash
     # Run 1Order example
     docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/1Order.pl --mode simulate --config scripts/config.json
     ```

5. **Customize Configuration**
   - The default configuration is in `scripts/config.json`
   - You can modify parameters like:
     - `simRandomIter`: Number of random simulation iterations
     - `trainingIter`: Number of training steps
     - `learningAlgorithm`: Choose between "A2C", "PPO", or "DQN"

6. **Save Output**
   - To save the output to a file:
     ```bash
     docker run -it ghcr.io/cmg-york/dtg2sim:latest python scripts/main.py examples/discrete/3Build.pl --mode simulate --config scripts/config.json > output.txt
     ```

7. **Interactive Shell**
   - To get an interactive shell in the container:
     ```bash
     docker run -it ghcr.io/cmg-york/dtg2sim:latest /bin/bash
     ```
   - This allows you to explore the environment and run multiple commands

## Available Examples

The project includes several example models in the `examples` directory:

### Discrete Models
- `1Order.pl`: Simple ordering system
- `2OrderMultiRun.pl`: Multi-run ordering system
- `3Build.pl`: Building construction example
- `6BuildMultiRun.pl`: Multi-run building construction
- `7HeatingMultiRun4.pl`: Heating system example
- `9SoSymExample.pl`: Social system example

### Continuous Models
- Similar examples with continuous state spaces

## Configuration Options

The `config.json` file supports the following parameters:

```json
{
    "debug": false,                    // Enable debug output
    "seed": 123,                       // Random seed
    "simRandomIter": 100,              // Random simulation iterations
    "simCustomIter": 100,              // Custom simulation iterations
    "simOptimalIter": 100,             // Optimal simulation iterations
    "testingIter": 1000,               // Testing episodes
    "trainingIter": 1000,              // Training steps
    "learningAlgorithm": "PPO",        // A2C, PPO, or DQN
    "learningLoggingInterval": 500,    // Logging frequency
    "optimalSimParams": [0, 2],        // Optimal simulation parameters
    "dtGologOptimal": 0.476           // Expected optimal reward
}
```

## Troubleshooting

1. **Permission Issues**
   - If you get permission errors, try running Docker with sudo:
     ```bash
     sudo docker run -it ghcr.io/cmg-york/dtg2sim:latest ...
     ```

2. **Container Not Found**
   - If the image pull fails, ensure you're connected to the internet and try:
     ```bash
     docker pull ghcr.io/cmg-york/dtg2sim:latest --no-cache
     ```

3. **Memory Issues**
   - If you encounter memory issues during training, you can limit container memory:
     ```bash
     docker run -it --memory="4g" ghcr.io/cmg-york/dtg2sim:latest ...
     ```

## Manual Installation

If you prefer to run the project directly on your system, follow these steps:

1. **Clone the repository locally.**
   ```bash
   git clone <repository-url>
   cd dtg2sim
   ```

2. **Verify Python version and create virtual environment:**
   ```bash
   # Check Python version
   python --version  # Should show Python 3.13.x
   ```
   ```bash
   # Create virtual environment with Python 3.13
   python -m venv venv
    ```
   
   ```bash
   
   source venv/bin/activate  # On Linux/Mac
   # OR
   venv\Scripts\activate     # On Windows
   ```
   
   On Windows, you may need to open in Powershell as administrator and give:

	```
	Set-ExecutionPolicy RemoteSigned 
	```
	Watch for `(venv)` to appear at the beginning of your commant prompt to verify that the virtual environment is active.

3. **Install the required dependencies:**
   ```bash
   # Install project dependencies
   python -m pip install -r requirements.txt
   ```

   This will install all necessary packages with the correct versions for this project.

4. **Acquire the DT-Golog code** from [its creator's page](https://www.cs.ryerson.ca/~mes/publications/appendix/appendixC/dtgolog), and place it in a file called `DT-Golog.pl` under `/scripts/QE/`

5. **Make the following changes so that it runs on SWI-Prolog**
  - Comment out the following:
    ```
    /* :- pragma(debug).  */
    ```
  - Add:
    ```
    :- op(900, fy, [not]).
    (not X) := (\+ X).
    cputime(5).
    ```
6. **Run the test and trial scripts in the `/examples` folder from your IDE.**

  
    

    

