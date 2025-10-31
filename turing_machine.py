import yaml
from typing import List, Set, Dict, Tuple, Optional


class TuringMachineWithCache:
    def __init__(self, config_file: str):
        """Initialize Turing Machine with cache from YAML configuration file."""
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.states: List[str] = config['states']
        self.input_alphabet: List[str] = config['input_alphabet']
        self.tape_alphabet: List[str] = config['tape_alphabet']
        self.cache_alphabet: List[str] = config.get('cache_alphabet', ['B'])
        self.initial_state: str = config['initial_state']
        self.initial_cache: str = config.get('initial_cache', 'B')
        self.accept_states: Set[str] = set(config['accept_states'])
        self.transitions: Dict[Tuple[str, str, str], Tuple[str, str, str, str]] = {}
        self.inputs: List[str] = config.get('inputs', [])
        
        # Parse transitions
        # Format: read: [tape_symbol, cache_symbol]
        #         write: [new_tape_symbol, new_cache_symbol]
        for trans in config['transitions']:
            state = trans['state']
            read_list = trans['read']
            write_list = trans['write']
            move = trans['move']
            next_state = trans['next']
            
            tape_read = read_list[0]
            cache_read = read_list[1]
            tape_write = write_list[0]
            cache_write = write_list[1]
            
            # Key: (state, cache, tape_symbol)
            # Value: (next_state, new_cache, new_tape_symbol, move)
            self.transitions[(state, cache_read, tape_read)] = (next_state, cache_write, tape_write, move)
    
    def run(self, input_string: str, max_steps: int = 10000, verbose: bool = True) -> Tuple[bool, str]:
        """Run the Turing Machine on the given input string."""
        # Initialize tape with start marker $, input, and blank
        tape = ['$'] + list(input_string) + ['B']
        head_position = 1  # Start after the $ marker
        current_state = self.initial_state
        current_cache = self.initial_cache
        steps = 0
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Turing Machine on input: '{input_string}'")
            print(f"{'='*60}")
            self._print_configuration(tape, head_position, current_state, current_cache, steps)
        
        while steps < max_steps:
            # Check if in accept state
            if current_state in self.accept_states:
                if verbose:
                    final_tape = self._get_tape_string(tape)
                    print(f"\n{'='*60}")
                    print(f"✓ ACCEPTED in {steps} steps")
                    print(f"Final tape: {final_tape}")
                    print(f"{'='*60}")
                return True, self._get_tape_string(tape).replace('B', '').replace('$', '')
            
            # Check bounds
            if head_position < 0:
                if verbose:
                    final_tape = self._get_tape_string(tape)
                    print(f"\n{'='*60}")
                    print(f"✗ REJECTED: Head moved off left end")
                    print(f"Final tape: {final_tape}")
                    print(f"{'='*60}")
                return False, self._get_tape_string(tape).replace('B', '').replace('$', '')
            
            # Extend tape if needed
            while head_position >= len(tape):
                tape.append('B')
            
            current_symbol = tape[head_position]
            
            # Look up transition
            key = (current_state, current_cache, current_symbol)
            if key not in self.transitions:
                if verbose:
                    final_tape = self._get_tape_string(tape)
                    print(f"\n{'='*60}")
                    print(f"✗ REJECTED: No transition for δ([{current_state}, {current_cache}], {current_symbol})")
                    print(f"Final tape: {final_tape}")
                    print(f"{'='*60}")
                return False, self._get_tape_string(tape).replace('B', '').replace('$', '')
            
            next_state, new_cache, write_symbol, move = self.transitions[key]
            
            if verbose:
                print(f"\n  Transition: δ([{current_state}, {current_cache}], {current_symbol}) = ([{next_state}, {new_cache}], {write_symbol}, {move})")
            
            # Execute transition
            tape[head_position] = write_symbol
            current_cache = new_cache
            
            if move == 'R':
                head_position += 1
            elif move == 'L':
                head_position -= 1
            
            current_state = next_state
            steps += 1
            
            if verbose:
                self._print_configuration(tape, head_position, current_state, current_cache, steps)
        
        if verbose:
            final_tape = self._get_tape_string(tape)
            print(f"\n{'='*60}")
            print(f"✗ REJECTED: Maximum steps ({max_steps}) reached")
            print(f"Final tape: {final_tape}")
            print(f"{'='*60}")
        return False, self._get_tape_string(tape).replace('B', '').replace('$', '')
    
    def _get_tape_string(self, tape: List[str]) -> str:
        """Get clean string representation of tape."""
        display_tape = tape.copy()
        # Remove trailing blanks
        while len(display_tape) > 1 and display_tape[-1] == 'B':
            display_tape.pop()
        if not display_tape:
            display_tape = ['B']
        return ''.join(display_tape)
    
    def _print_configuration(self, tape: List[str], head_pos: int, state: str, cache: str, step: int):
        """Print current configuration."""
        display_tape = tape.copy()
        while len(display_tape) > 1 and display_tape[-1] == 'B':
            display_tape.pop()
        if not display_tape:
            display_tape = ['B']
        
        tape_str = ' '.join(display_tape)
        head_indicator = ' ' * (head_pos * 2) + '^'
        
        print(f"\nStep {step}:")
        print(f"  State: [{state}, {cache}]")
        print(f"  Tape:  {tape_str}")
        print(f"  Head:  {head_indicator}")
    
    def run_all_inputs(self, verbose: bool = True):
        """Run the Turing Machine on all inputs."""
        results = []
        for input_string in self.inputs:
            result, string = self.run(input_string, verbose=verbose)
            results.append((input_string, result, string))
        
        if verbose:
            print(f"\n{'='*60}")
            print("SUMMARY")
            print(f"{'='*60}")
            for input_str, accepted, string in results:
                status = "✓ ACCEPTED" if accepted else "✗ REJECTED"
                print(f"  Input: '{input_str}' → {status} → {string}")
        
        return results


if __name__ == "__main__":
    tm = TuringMachineWithCache('anbn.yaml')
    tm.run_all_inputs(verbose=True)
    tm = TuringMachineWithCache('reverse.yaml')
    tm.run_all_inputs(verbose=True)