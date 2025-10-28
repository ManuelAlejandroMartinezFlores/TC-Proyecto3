import yaml
from typing import List, Set, Dict, Tuple


class TuringMachine:
    def __init__(self, config_file: str):
        """Initialize Turing Machine from YAML configuration file."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.states: List[str] = config['states']
        self.input_alphabet: List[str] = config['input_alphabet']
        self.tape_alphabet: List[str] = config['tape_alphabet']
        self.initial_state: str = config['initial_state']
        self.accept_states: Set[str] = set(config['accept_states'])
        self.transitions: Dict[Tuple[str, str], Tuple[str, str, str]] = {}
        self.inputs: List[str] = config.get('inputs', [])
        
        # Parse transitions
        for trans in config['transitions']:
            state = trans['state']
            read_symbols = trans['read']
            write_symbols = trans['write']
            move = trans['move']
            next_state = trans['next']
            
            # Handle multiple read/write symbols
            if not isinstance(read_symbols, list):
                read_symbols = [read_symbols]
            if not isinstance(write_symbols, list):
                write_symbols = [write_symbols]
            
            # Create transition for each combination
            for read_sym, write_sym in zip(read_symbols, write_symbols):
                self.transitions[(state, read_sym)] = (next_state, write_sym, move)
    
    def run(self, input_string: str, max_steps: int = 10000, verbose: bool = True) -> bool:
        """
        Run the Turing Machine on the given input string.
        
        Args:
            input_string: Input string to process
            max_steps: Maximum number of steps to prevent infinite loops
            verbose: If True, print step-by-step execution
            
        Returns:
            True if the machine accepts, False otherwise
        """
        # Initialize tape with input and blank symbol
        tape = list(input_string) + ['B']
        head_position = 0
        current_state = self.initial_state
        steps = 0
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Turing Machine on input: '{input_string}'")
            print(f"{'='*60}")
            self._print_configuration(tape, head_position, current_state, steps)
        
        while steps < max_steps:
            # Check if in accept state
            if current_state in self.accept_states:
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"✓ ACCEPTED in {steps} steps")
                    print(f"{'='*60}")
                return True
            
            # Get current symbol under head
            if head_position < 0:
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"✗ REJECTED: Head moved off left end of tape")
                    print(f"{'='*60}")
                return False
            
            # Extend tape if necessary
            while head_position >= len(tape):
                tape.append('B')
            
            current_symbol = tape[head_position]
            
            # Look up transition
            key = (current_state, current_symbol)
            if key not in self.transitions:
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"✗ REJECTED: No transition for state '{current_state}' reading '{current_symbol}'")
                    print(f"{'='*60}")
                return False
            
            next_state, write_symbol, move = self.transitions[key]
            
            # Execute transition
            tape[head_position] = write_symbol
            
            if move == 'R':
                head_position += 1
            elif move == 'L':
                head_position -= 1
            # 'S' for stay would keep head_position unchanged
            
            current_state = next_state
            steps += 1
            
            if verbose:
                self._print_configuration(tape, head_position, current_state, steps)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"✗ REJECTED: Maximum steps ({max_steps}) reached")
            print(f"{'='*60}")
        return False
    
    def _print_configuration(self, tape: List[str], head_pos: int, state: str, step: int):
        """Print current configuration of the Turing Machine."""
        # Clean up tape display (remove trailing blanks)
        display_tape = tape.copy()
        while len(display_tape) > 1 and display_tape[-1] == 'B':
            display_tape.pop()
        if not display_tape:
            display_tape = ['B']
        
        # Create tape string with head indicator
        tape_str = ' '.join(display_tape)
        head_indicator = ' ' * (head_pos * 2) + '^'
        
        print(f"\nStep {step}:")
        print(f"  State: {state}")
        print(f"  Tape:  {tape_str}")
        print(f"  Head:  {head_indicator}")
    
    def run_all_inputs(self, verbose: bool = True):
        """Run the Turing Machine on all inputs specified in the configuration."""
        results = []
        for input_string in self.inputs:
            result = self.run(input_string, verbose=verbose)
            results.append((input_string, result))
        
        # Summary
        if verbose:
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            for input_str, accepted in results:
                status = "✓ ACCEPTED" if accepted else "✗ REJECTED"
                print(f"  '{input_str}': {status}")
        
        return results


if __name__ == "__main__":
    # Example usage
    tm = TuringMachine('anbn.yaml')
    
    # Run all inputs from config
    tm.run_all_inputs(verbose=True)
    