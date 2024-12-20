import argparse
import sys
from simulation import Simulation
from ui import run_app


def main():
    """
    Main entry point of the application.
    Parses command line arguments, creates the simulation object, and runs the GUI.
    """
    parser = argparse.ArgumentParser(description='Sleeping Barber Simulation with PyQt5 GUI')
    parser.add_argument('--config', type=str, default='config.json', help='Path to config file')
    args = parser.parse_args()

    try:
        # Initialize the simulation with the provided config file.
        sim = Simulation(config_file=args.config)

        # Launch the GUI application and pass the simulation instance.
        run_app(sim)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
