from itertools import combinations
from collections import Counter
import re

class ComboGenerator:
    def __init__(self):
        self.mod_keys = ['LC', 'RC', 'LS', 'LA', 'RA', 'LG', 'RG']
        self.f_keys = [f'F{i}' for i in range(13, 25)]  # F13 to F24

        self.already_mapped = """
            end_left {
                bindings = <&kp END>;
                key-positions = <27 28 38>;
            };

            home_left {
                bindings = <&kp HOME>;
                key-positions = <27 28 37>;
            };

            esc_left {
                bindings = <&kp ESCAPE>;
                key-positions = <16 15 37>;
            };

            esc_right {
                bindings = <&kp ESCAPE>;
                key-positions = <20 19 40>;
            };

            end_right {
                bindings = <&kp END>;
                key-positions = <31 32 40>;
            };

            home_right {
                bindings = <&kp HOME>;
                key-positions = <39 31 32>;
            };

            shift_copy_left {
                bindings = <&kp LS(LC(C))>;
                key-positions = <38 15 28>;
            };

            shift_paste_left {
                bindings = <&kp LS(LC(V))>;
                key-positions = <38 15 29>;
            };

            ctrl_shift_t_left {
                bindings = <&kp LC(LS(T))>;
                key-positions = <36 15 16>;
            };

            nav_lock {
                bindings = <&tog 2>;
                key-positions = <31 32 33>;
                layers = <1 2 3>;
            };

            func_lock {
                bindings = <&tog 8>;
                key-positions = <26 27 28>;
                layers = <7 8 9>;
            };

            num_lock {
                bindings = <&tog 5>;
                key-positions = <26 27 28>;
                layers = <5 4 6>;
            };

            sys_lock {
                bindings = <&tog 11>;
                key-positions = <31 32 33>;
                layers = <11 11 12>;
            };

            quit_left {
                bindings = <&kp LS(LG(Q))>;
                key-positions = <16 38 1>;
            };

            enter_left {
                bindings = <&kp ENTER>;
                key-positions = <38 15 16>;
            };

            enter_right {
                bindings = <&kp ENTER>;
                key-positions = <20 19 39>;
            };

            backspace_left {
                bindings = <&kp BACKSPACE>;
                key-positions = <15 38 17>;
            };
        """
        already_mapped_key_positions = re.findall(r'key-positions = <([\d\s]+)>', self.already_mapped)
        already_mapped_all_numbers = {tuple(int(num) for num in pos.split()) for pos in already_mapped_key_positions}
        print(already_mapped_all_numbers)
        self.used_key_positions = set(already_mapped_all_numbers)
        self.key_usage = Counter(num for triple in self.used_key_positions for num in triple)


        
        self.KEY_TO_CHAR = {
            1: 'q', 2: 'w', 3: 'f', 4: 'p', 5: 'b', 6: 'm', 7: 'l', 8: 'u', 9: 'y', 10: 'j',
            13: 'a', 14: 'r', 15: 's', 16: 't', 17: 'g', 18: 'num', 19: 'n', 20: 'e', 21: 'i', 22: 'o',
            25: 'z', 26: 'x', 27: 'c', 28: 'd', 29: 'v', 30: 'k', 31: 'h', 32: 'comma', 33: 'dot', 34: 'quote',
            36: 'ctrl', 37: 'space', 38: 'mod', 39: 'shift', 40: 'backspace', 41: 'tab'
        }
        
        self.FKEY_TO_CODE = {
            'F13': '191',
            'F14': '192',
            'F15': '193',
            'F16': '194',
            'F17': '195',
            'F18': '196',
            'F19': '197',
            'F20': '198',
            'F21': '199',
            'F22': '200',
            'F23': '201',
            'F24': '202'
        }

        self.all_keys = list(self.KEY_TO_CHAR.keys())

    def generate_mod_combinations(self):
        """Generate all possible modifier combinations"""
        all_mod_combinations = []
        for r in range(len(self.mod_keys) + 1):
            for combo in combinations(self.mod_keys, r):
                all_mod_combinations.append(list(combo))
        return all_mod_combinations

    def get_key_positions_from_trigger(self, trigger):
        """Convert trigger string to key positions using KEY_TO_CHAR mapping"""
        positions = []
        char_to_key = {char: key for key, char in self.KEY_TO_CHAR.items()}

        # Add special keys to char_to_key map
        for key, value in self.KEY_TO_CHAR.items():
            if len(value) > 1:  # If it's a special key like 'space', 'comma', etc.
                char_to_key[value] = key

        i = 0
        while i < len(trigger):
            if trigger[i] == '[':  # Start of special key
                end = trigger.find(']', i)
                if end == -1:
                    raise ValueError(f"Unclosed bracket in trigger at position {i}")
                special_key = trigger[i+1:end]
                if special_key not in char_to_key:
                    raise ValueError(f"Special key '{special_key}' not found in keyboard layout!")
                positions.append(char_to_key[special_key])
                i = end + 1
            else:
                char = trigger[i].lower()
                if char not in char_to_key:
                    raise ValueError(f"Character '{char}' not found in keyboard layout!")
                positions.append(char_to_key[char])
                i += 1

        # Sort positions to ensure consistent comparison
        positions = sorted(positions)

        # Check if this exact combination already exists
        if tuple(positions) in self.used_key_positions:
            raise ValueError(f"Combo with positions {positions} already exists! {trigger}")
        
        # Track usage of each key
        for key in positions:
            self.key_usage[key] += 1
        
        # Store the complete combination
        self.used_key_positions.add(tuple(positions))
            
        return positions

    def generate_zmk_binding(self, mods, f_key):
        """Generate ZMK binding string with modifiers"""
        if not mods:
            return f'&kp {f_key}'

        # Nest the modifiers properly
        binding = f_key
        for mod in mods:
            binding = f'{mod}({binding})'

        return f'&kp {binding}'

    def generate_sway_binding(self, mods, f_key, snippet, use_typing=False):
        """Generate Sway binding string with modifiers using keycodes"""
        keycode = self.FKEY_TO_CODE[f_key]
        mod_map = {
            'LC': 'Control_L',
            'RC': 'Control_R',
            'LS': 'Shift_L',
            'LA': 'Alt_L',
            'RA': 'Alt_R',
            'LG': 'Super_L',
            'RG': 'Super_R'
        }
        mod_string = '+'.join([f'${mod_map[mod]}' for mod in mods])
        if mod_string:
            mod_string += '+'

        backspace_count = snippet.count('[backspace]')
        clipboard_text = snippet.replace('[backspace]', '')

        left_count = clipboard_text.count('[right]')
        clipboard_text = clipboard_text.replace('[left]', '')

        right_count = clipboard_text.count('[right]')
        clipboard_text = clipboard_text.replace('[right]', '')

        cursor_steps = 0
        if '[cursor]' in snippet:
            cursor_steps = len(clipboard_text) - clipboard_text.index('[cursor]') - len('[cursor]')
        clipboard_text = clipboard_text.replace('[cursor]', '')

        typing_mode = 1 if use_typing else 0
        
        return f'bindcode {mod_string}{keycode} exec sh ~/.bash_scripts/combo.sh "{clipboard_text}" {cursor_steps} {left_count} {right_count} {typing_mode} {backspace_count}'

    def generate_configs(self, dictionary):
        mod_combinations = self.generate_mod_combinations()
        f_keys = self.f_keys
        total_possible_combos = len(mod_combinations) * len(f_keys)

        if len(dictionary) > total_possible_combos:
            raise ValueError(f"Too many entries! Maximum possible combinations: {total_possible_combos}")

        zmk_configs = []
        sway_configs = []

        for idx, (trigger, snippet, use_typing) in enumerate(dictionary):
            # Validate snippet format
            if '<cursor>' in snippet and snippet.count('<cursor>') > 1:
                raise ValueError(f"Error at snippet {idx}: Only one cursor position allowed")

            mod_idx = idx // len(f_keys)
            f_key_idx = idx % len(f_keys)

            mods = mod_combinations[mod_idx]
            f_key = f_keys[f_key_idx]

            try:
                key_positions = self.get_key_positions_from_trigger(trigger)
            except ValueError as e:
                raise ValueError(f"Error at combo {idx}: {str(e)}")

            combo_name = trigger.replace('[', '_').replace(']', '_')

            zmk_config = f"""
            {combo_name} {{
                key-positions = <{' '.join(map(str, key_positions))}>;
                bindings = <{self.generate_zmk_binding(mods, f_key)}>;
            }};"""
            zmk_configs.append(zmk_config)

            sway_config = self.generate_sway_binding(mods, f_key, snippet, use_typing)
            sway_configs.append(sway_config)

        return zmk_configs, sway_configs

    def get_key_utilization_report(self):
        """Generate a detailed key utilization report"""
        report = []
        for key, count in self.key_usage.most_common():
            char = self.KEY_TO_CHAR[key]
            report.append(f"Key {key} ({char}): {count} combos")
        return report

def read_dictionary_file(filepath):
    """Read and parse the dictionary file, skipping comments and empty lines"""
    dictionary = []
    with open(filepath, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # Safely evaluate the tuple string
                entry = eval(line)
                if not isinstance(entry, tuple) or len(entry) not in [2, 3]:
                    print(f"Warning: Skipping invalid entry format: {line}")
                    continue
                # If no typing mode specified, default to False (clipboard mode)
                if len(entry) == 2:
                    entry = (*entry, False)
                dictionary.append(entry)
            except Exception as e:
                print(f"Warning: Failed to parse line: {line}")
                print(f"Error: {str(e)}")
                continue
                
    return dictionary

def main():
    generator = ComboGenerator()
    
    try:
        dictionary = read_dictionary_file('dictionary.txt')
        zmk_configs, sway_configs = generator.generate_configs(dictionary)

        print("=== ZMK Combos ===")
        for combo in zmk_configs:
            print(combo)
        print(generator.already_mapped)

        print("\n=== Sway Bindings ===")
        for binding in sway_configs:
            print(binding)

        print("\n=== Key Utilization Report ===")
        for line in generator.get_key_utilization_report():
            print(line)

        print(f"\nRecommended CONFIG_ZMK_COMBO_MAX_COMBOS_PER_KEY: {max(generator.key_usage.values())}")
        print(f"\nTotal possible combinations: {len(generator.generate_mod_combinations()) * len(generator.f_keys)}")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except FileNotFoundError:
        print("Error: dictionary.txt not found")

if __name__ == "__main__":
    main()
