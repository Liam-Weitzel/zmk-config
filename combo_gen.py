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

    def generate_sway_binding(self, mods, f_key, snippet):
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


        clipboard_text = snippet.replace('[cursor]', '')
        left_steps = 0
        if '[cursor]' in snippet:
            left_steps = len(snippet) - snippet.index('[cursor]') - len('[cursor]')

        clipboard_text = clipboard_text.replace('[suffix]', '')
        suffix_steps = 0
        if '[suffix]' in snippet:
            suffix_steps = 1

        clipboard_text = clipboard_text.replace('[right]', '')
        right_steps = 0
        if '[right]' in snippet:
            right_steps = snippet.count('[right]')

        return f'bindcode {mod_string}{keycode} exec sh ~/.bash_scripts/combo.sh "{clipboard_text}" {left_steps} {suffix_steps} {right_steps}'


    def generate_configs(self, dictionary):
        mod_combinations = self.generate_mod_combinations()
        f_keys = self.f_keys
        total_possible_combos = len(mod_combinations) * len(f_keys)

        if len(dictionary) > total_possible_combos:
            raise ValueError(f"Too many entries! Maximum possible combinations: {total_possible_combos}")

        zmk_configs = []
        sway_configs = []

        for idx, (trigger, snippet) in enumerate(dictionary):
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

            # Replace square brackets with underscores for the combo name
            combo_name = trigger.replace('[', '_').replace(']', '_')

            zmk_config = f"""
            {combo_name} {{
                key-positions = <{' '.join(map(str, key_positions))}>;
                bindings = <{self.generate_zmk_binding(mods, f_key)}>;
            }};"""
            zmk_configs.append(zmk_config)

            sway_config = self.generate_sway_binding(mods, f_key, snippet)
            sway_configs.append(sway_config)

        return zmk_configs, sway_configs

    def get_key_utilization_report(self):
        """Generate a detailed key utilization report"""
        report = []
        for key, count in self.key_usage.most_common():
            char = self.KEY_TO_CHAR[key]
            report.append(f"Key {key} ({char}): {count} combos")
        return report

def main():
    generator = ComboGenerator()
    dictionary = [
        # Don't use over 6 chars in the combo unless you are using NKRO
        ('stn', 'std::'),
        ('aro', '->'),
        ('sig', 'unsigned '),
        ('con', 'const '),
        ('npr', 'nullptr '),
        ('vir', 'virtual '),
        ('sta', 'static '),
        ('voi', 'void '),
        ('aut', 'auto '),
        ('ret', 'return [cursor];'),
        ('inc', '#include <[cursor]>'),
        ('def', '#define '),
        ('str[backspace]', 'std::string '),
        ('ty[space]', 'std::typeid([cursor])'),
        ('map[backspace]', 'std::unordered_map<[cursor]> '),
        ('set[backspace]', 'std::unordered_set<[cursor]> '),
        ('deq[backspace]', 'std::dequeue<[cursor]> '),
        ('pai[backspace]', 'std::pair<[cursor]> '),
        ('npai[backspace]', 'std::make_pair([cursor]) '),
        ('ple[backspace]', 'std::tuple<[cursor]> '),
        ('vec[backspace]', 'std::vector<[cursor]> '),

        ('fex', 'for example '),
        ('i[backspace]o', 'in my opinion '),
        ('not[backspace]', 'note that '),

        ('bra', 'Best regards,\\n'),
        ('thx', 'Thanks,\\n'),
        ('lam', 'Liam Weitzel '),
        ('ros', 'Diuni Roshani Appuhami Raja Paksha Pathiranalage'),

        ('it[backspace]', '[suffix]ity[right]'),
        ('tion', '[suffix]tion[right]'),
        ('ous', '[suffix]ous[right]'),
        ('ious', '[suffix]ious[right]'),
        ('ial', '[suffix]ial[right]'),
        ('ive', '[suffix]ive[right]'),
        ('acti', '[suffix]ative[right]'),
        ('ship', '[suffix]ship[right]'),
        ('hod', '[suffix]hood[right]'),
        ('enc', '[suffix]ence[right]'),
        ('ance', '[suffix]ance[right]'),
        ('er[backspace]', '[suffix]er[right]'),
        ('or[backspace]', '[suffix]or[right]'),
        ('est', '[suffix]est[right]'),
        ('ish', '[suffix]ish[right]'),
        ('ism', '[suffix]ism[right]'),
        ('ist', '[suffix]ist[right]'),
        ('ing', '[suffix]ing[right]'),
        ('ed[backspace]', '[suffix]ed[right]'),
        ('abl', '[suffix]able[right]'),
        ('ibl', '[suffix]ible[right]'),
        ('ment', '[suffix]ment[right]'),
        ('nes', '[suffix]ness[right]'),
        ('ful', '[suffix]ful[right]'),
        ('les', '[suffix]less[right]'),
        ('ize', '[suffix]ize[right]'),
        ('ise', '[suffix]ise[right]'),
        ('ist[backspace]', '[suffix]istic[right]'),
        ('olg', '[suffix]ology[right]'),
        ('ary', '[suffix]ary[right]'),
        ('ory', '[suffix]ory[right]'),
        ('ister', '[suffix]ister[right]'),

        ('infra', 'infrastructure '),
        ('iden', 'identification '),
        ('dicr', 'discrimination '),
        ('prion', 'representation '),
        ('reps', 'reprasentative '),
        ('reco', 'recommendation '),
        ('cont', 'constitutional '),
        ('inter', 'interpretation '),
        ('trans', 'transportation '),
        # ('', 'representative '),
        # ('', 'responsibility '),
        # ('', 'substantially '),
        # ('', 'undergraduate '),
        # ('', 'old-fashioned '),
        # ('', 'philosophical '),
        # ('', 'developmental '),
        # ('', 'confrontation '),
        # ('', 'unprecedented '),
        # ('', 'instructional '),
        ('inst', 'institutional '),
        # ('', 'collaboration '),
        # ('', 'revolutionary '),
        # ('', 'automatically '),
        # ('', 'determination '),
        # ('', 'technological '),
        # ('', 'traditionally '),
        # ('', 'uncomfortable '),
        # ('', 'questionnaire '),
        # ('', 'effectiveness '),
        # ('', 'consciousness '),
        # ('', 'institutional '),
        # ('', 'manufacturing '),
        # ('', 'demonstration '),
        # ('', 'controversial '),
        # ('', 'sophisticated '),
        # ('', 'correspondent '),
        # ('', 'comprehensive '),
        # ('', 'establishment '),
        # ('', 'concentration '),
        # ('', 'extraordinary '),
        # ('', 'consideration '),
        # ('', 'approximately '),
        # ('', 'psychological '),
        # ('', 'entertainment '),
        # ('', 'congressional '),
        # ('', 'participation '),
        # ('', 'unfortunately '),
        # ('', 'significantly '),
        # ('', 'understanding '),
        # ('', 'communication '),
        # ('', 'investigation '),
        # ('', 'international '),
        # ('', 'environmental '),
        # ('', 'middle-class '),
        # ('', 'economically '),
        # ('', 'surveillance '),
        # ('', 'availability '),
        # ('', 'jurisdiction '),
        # ('', 'considerably '),
        # ('', 'deliberately '),
        # ('', 'thanksgiving '),
        # ('', 'constitution '),
        # ('', 'installation '),
        # ('', 'conservation '),
        # ('', 'consequently '),
        # ('', 'commissioner '),
        # ('', 'appreciation '),
        # ('', 'metropolitan '),
        # ('', 'christianity '),
        # ('', 'entrepreneur '),
        # ('', 'practitioner '),
        # ('', 'productivity '),
        # ('', 'refrigerator '),
        # ('', 'carbohydrate '),
        # ('', 'historically '),
        # ('', 'compensation '),
        # ('', 'respectively '),
        # ('', 'transmission '),
        # ('', 'announcement '),
        # ('', 'consistently '),
        # ('', 'overwhelming '),
        # ('', 'architecture '),
        # ('', 'civilization '),
        # ('', 'unemployment '),
        # ('', 'experimental '),
        # ('', 'surprisingly '),
        # ('', 'dramatically '),
        # ('', 'prescription '),
        # ('', 'successfully '),
        # ('', 'agricultural '),
        # ('', 'photographer '),
        # ('', 'psychologist '),
        # ('', 'significance '),
        # ('', 'introduction '),
        # ('', 'presentation '),
        # ('', 'headquarters '),
        # ('', 'intellectual '),
        # ('', 'considerable '),
        # ('', 'satisfaction '),
        # ('', 'nevertheless '),
        # ('', 'conventional '),
        # ('', 'occasionally '),
        # ('', 'distribution '),
        # ('', 'championship '),
        # ('', 'independence '),
        # ('', 'investigator '),
        # ('', 'manufacturer '),
        # ('', 'specifically '),
        # ('', 'contemporary '),
        # ('', 'intervention '),
        # ('', 'conservative '),
        # ('', 'circumstance '),
        # ('', 'contribution '),
        # ('', 'presidential '),
        # ('', 'increasingly '),
        # ('', 'intelligence '),
        # ('', 'construction '),
        # ('', 'conversation '),
        # ('', 'neighborhood '),
        # ('', 'relationship '),
        # ('', 'simultaneous '),
        # ('', 'professional '),
        # ('', 'particularly '),
        # ('', 'organization '),
        # ('', 'sustainable '),
        # ('', 'convenience '),
        # ('', 'electronics '),
        # ('', 'importantly '),
        # ('', 'contributor '),
        # ('', 'sovereignty '),
        # ('', 'consecutive '),
        # ('', 'neighboring '),
        # ('', 'devastating '),
        # ('', 'contemplate '),
        # ('', 'theological '),
        # ('', 'distinctive '),
        # ('', 'supermarket '),
        # ('', 'grandparent '),
        # ('', 'emotionally '),
        # ('', 'calculation '),
        # ('', 'shareholder '),
        # ('', 'programming '),
        # ('', 'demographic '),
        # ('', 'marketplace '),
        # ('', 'exclusively '),
        # ('', 'sensitivity '),
        # ('', 'desperately '),
        # ('', 'speculation '),
        # ('', 'preliminary '),
        # ('', 'surrounding '),
        # ('', 'encouraging '),
        # ('', 'legislature '),
        # ('', 'experienced '),
        # ('', 'flexibility '),
        # ('', 'fortunately '),
        # ('', 'statistical '),
        # ('', 'translation '),
        # ('', 'influential '),
        # ('', 'mathematics '),
        # ('', 'cooperative '),
        # ('', 'self-esteem '),
        # ('', 'documentary '),
        # ('', 'ideological '),
        # ('', 'coordinator '),
        # ('', 'fascinating '),
        # ('', 'reliability '),
        # ('', 'spectacular '),
        # ('', 'willingness '),
        # ('', 'agriculture '),
        # ('', 'inspiration '),
        # ('', 'credibility '),
        # ('', 'outstanding '),
        # ('', 'photography '),
        # ('', 'practically '),
        # ('', 'exploration '),
        # ('', 'destination '),
        # ('', 'acquisition '),
        # ('', 'businessman '),
        # ('', 'residential '),
        # ('', 'counterpart '),
        # ('', 'transaction '),
        # ('', 'theoretical '),
        # ('', 'health-care '),
        # ('', 'uncertainty '),
        # ('', 'accommodate '),
        # ('', 'intelligent '),
        # ('', 'replacement '),
        # ('', 'prosecution '),
        # ('', 'integration '),
        # ('', 'legislative '),
        # ('', 'correlation '),
        # ('', 'anniversary '),
        # ('', 'nonetheless '),
        # ('', 'distinguish '),
        # ('', 'frustration '),
        # ('', 'measurement '),
        # ('', 'furthermore '),
        # ('', 'orientation '),
        # ('', 'consumption '),
        # ('', 'differently '),
        # ('', 'restriction '),
        # ('', 'cholesterol '),
        # ('', 'examination '),
        # ('', 'maintenance '),
        # ('', 'reservation '),
        # ('', 'scholarship '),
        # ('', 'appointment '),
        # ('', 'composition '),
        # ('', 'celebration '),
        # ('', 'grandfather '),
        # ('', 'distinction '),
        # ('', 'partnership '),
        # ('', 'imagination '),
        # ('', 'controversy '),
        # ('', 'politically '),
        # ('', 'potentially '),
        # ('', 'complicated '),
        # ('', 'electricity '),
        # ('', 'destruction '),
        # ('', 'communicate '),
        # ('', 'cooperation '),
        # ('', 'advertising '),
        # ('', 'corporation '),
        # ('', 'incorporate '),
        # ('', 'effectively '),
        # ('', 'substantial '),
        # ('', 'palestinian '),
        # ('', 'preparation '),
        # ('', 'grandmother '),
        # ('', 'publication '),
        # ('', 'recognition '),
        # ('', 'implication '),
        # ('', 'immigration '),
        # ('', 'engineering '),
        # ('', 'concentrate '),
        # ('', 'arrangement '),
        # ('', 'fundamental '),
        # ('', 'involvement '),
        # ('', 'competitive '),
        # ('', 'enforcement '),
        # ('', 'essentially '),
        # ('', 'negotiation '),
        # ('', 'description '),
        # ('', 'observation '),
        # ('', 'association '),
        # ('', 'personality '),
        # ('', 'interaction '),
        # ('', 'alternative '),
        # ('', 'explanation '),
        # ('', 'achievement '),
        # ('', 'legislation '),
        # ('', 'necessarily '),
        # ('', 'improvement '),
        # ('', 'expectation '),
        # ('', 'requirement '),
        # ('', 'combination '),
        # ('', 'investigate '),
        # ('', 'comfortable '),
        # ('', 'acknowledge '),
        # ('', 'consequence '),
        # ('', 'temperature '),
        # ('', 'educational '),
        # ('', 'instruction '),
        # ('', 'application '),
        # ('', 'appropriate '),
        # ('', 'participate '),
        # ('', 'perspective '),
        # ('', 'demonstrate '),
        # ('', 'responsible '),
        # ('', 'competition '),
        # ('', 'independent '),
        # ('', 'possibility '),
        # ('', 'immediately '),
        # ('', 'traditional '),
        # ('', 'significant '),
        # ('', 'performance '),
        # ('', 'participant '),
        # ('', 'opportunity '),
        # ('', 'interesting '),
        # ('', 'institution '),
        # ('', 'information '),
        # ('', 'environment '),
        # ('', 'development '),
        # ('', 'citizenship '),
        # ('', 'centralized '),
        # ('', 'stereotype '),
        # ('', 'nationwide '),
        # ('', 'accelerate '),
        # ('', 'missionary '),
        # ('', 'accurately '),
        # ('', 'compelling '),
        # ('', 'straighten '),
        # ('', 'accusation '),
        # ('', 'articulate '),
        # ('', 'coordinate '),
        # ('', 'republican '),
        # ('', 'technician '),
        # ('', 'disturbing '),
        # ('', 'confession '),
        # ('', 'ironically '),
        # ('', 'integrated '),
        # ('', 'graduation '),
        # ('', 'projection '),
        # ('', 'conversion '),
        # ('', 'similarity '),
        # ('', 'expedition '),
        # ('', 'constraint '),
        # ('', 'inevitably '),
        # ('', 'conscience '),
        # ('', 'comparable '),
        # ('', 'conception '),
        # ('', 'legislator '),
        # ('', 'wheelchair '),
        # ('', 'suspicious '),
        # ('', 'likelihood '),
        # ('', 'harassment '),
        # ('', 'two-thirds '),
        # ('', 'supposedly '),
        # ('', 'compliance '),
        # ('', 'well-being '),
        # ('', 'journalism '),
        # ('', 'aggression '),
        # ('', 'supportive '),
        # ('', 'ambassador '),
        # ('', 'innovative '),
        # ('', 'attendance '),
        # ('', 'ecological '),
        # ('', 'well-known '),
        # ('', 'reportedly '),
        # ('', 'grandchild '),
        # ('', 'accessible '),
        # ('', 'short-term '),
        # ('', 'equivalent '),
        # ('', 'presumably '),
        # ('', 'incredibly '),
        # ('', 'underlying '),
        # ('', 'creativity '),
        # ('', 'earthquake '),
        # ('', 'manipulate '),
        # ('', 'functional '),
        # ('', 'conspiracy '),
        # ('', 'discourage '),
        # ('', 'revelation '),
        # ('', 'bankruptcy '),
        # ('', 'optimistic '),
        # ('', 'thoroughly '),
        # ('', 'withdrawal '),
        # ('', 'associated '),
        # ('', 'specialize '),
        # ('', 'protective '),
        # ('', 'mysterious '),
        # ('', 'officially '),
        # ('', 'invitation '),
        # ('', 'ridiculous '),
        # ('', 'processing '),
        # ('', 'artificial '),
        # ('', 'automobile '),
        # ('', 'popularity '),
        # ('', 'productive '),
        # ('', 'prevention '),
        # ('', 'diplomatic '),
        # ('', 'regulatory '),
        # ('', 'structural '),
        # ('', 'engagement '),
        # ('', 'altogether '),
        # ('', 'attraction '),
        # ('', 'electrical '),
        # ('', 'meaningful '),
        # ('', 'complexity '),
        # ('', 'behavioral '),
        # ('', 'compromise '),
        # ('', 'contractor '),
        # ('', 'corruption '),
        # ('', 'astronomer '),
        # ('', 'mechanical '),
        # ('', 'wilderness '),
        # ('', 'enthusiasm '),
        # ('', 'separation '),
        # ('', 'indigenous '),
        # ('', 'administer '),
        # ('', 'innovation '),
        # ('', 'continuing '),
        # ('', 'prediction '),
        # ('', 'possession '),
        # ('', 'supervisor '),
        # ('', 'inspection '),
        # ('', 'facilitate '),
        # ('', 'unexpected '),
        # ('', 'inevitable '),
        # ('', 'mainstream '),
        # ('', 'allegation '),
        # ('', 'occasional '),
        # ('', 'excitement '),
        # ('', 'acceptance '),
        # ('', 'presidency '),
        # ('', 'continuous '),
        # ('', 'acceptable '),
        # ('', 'counseling '),
        # ('', 'concerning '),
        # ('', 'adolescent '),
        # ('', 'hypothesis '),
        # ('', 'indication '),
        # ('', 'collective '),
        # ('', 'occupation '),
        # ('', 'widespread '),
        # ('', 'subsequent '),
        # ('', 'competitor '),
        # ('', 'impressive '),
        # ('', 'repeatedly '),
        # ('', 'physically '),
        # ('', 'permission '),
        # ('', 'nomination '),
        # ('', 'instructor '),
        # ('', 'legitimate '),
        # ('', 'anticipate '),
        # ('', 'medication '),
        # ('', 'laboratory '),
        # ('', 'assignment '),
        # ('', 'motivation '),
        # ('', 'adjustment '),
        # ('', 'girlfriend '),
        # ('', 'punishment '),
        # ('', 'helicopter '),
        # ('', 'sufficient '),
        # ('', 'membership '),
        # ('', 'strengthen '),
        # ('', 'conviction '),
        # ('', 'proportion '),
        # ('', 'efficiency '),
        # ('', 'friendship '),
        # ('', 'incredible '),
        # ('', 'preference '),
        # ('', 'limitation '),
        # ('', 'obligation '),
        # ('', 'psychology '),
        # ('', 'capability '),
        # ('', 'vulnerable '),
        # ('', 'distribute '),
        # ('', 'regardless '),
        # ('', 'constitute '),
        # ('', 'profession '),
        # ('', 'originally '),
        # ('', 'attractive '),
        # ('', 'surprising '),
        # ('', 'tremendous '),
        # ('', 'tournament '),
        # ('', 'revolution '),
        # ('', 'reflection '),
        # ('', 'statistics '),
        # ('', 'remarkable '),
        # ('', 'personally '),
        # ('', 'developing '),
        # ('', 'assumption '),
        # ('', 'ingredient '),
        # ('', 'biological '),
        # ('', 'disability '),
        # ('', 'specialist '),
        # ('', 'respondent '),
        # ('', 'impression '),
        # ('', 'employment '),
        # ('', 'aggressive '),
        # ('', 'elementary '),
        # ('', 'reasonable '),
        # ('', 'suggestion '),
        # ('', 'enterprise '),
        # ('', 'constantly '),
        # ('', 'consultant '),
        # ('', 'exhibition '),
        # ('', 'convention '),
        # ('', 'phenomenon '),
        # ('', 'retirement '),
        # ('', 'reputation '),
        # ('', 'electronic '),
        # ('', 'tablespoon '),
        # ('', 'commission '),
        # ('', 'increasing '),
        # ('', 'evaluation '),
        # ('', 'illustrate '),
        # ('', 'accomplish '),
        # ('', 'previously '),
        # ('', 'discipline '),
        # ('', 'foundation '),
        # ('', 'philosophy '),
        # ('', 'resistance '),
        # ('', 'consistent '),
        # ('', 'atmosphere '),
        # ('', 'transition '),
        # ('', 'settlement '),
        # ('', 'comparison '),
        # ('', 'initiative '),
        # ('', 'prosecutor '),
        # ('', 'definition '),
        # ('', 'journalist '),
        # ('', 'depression '),
        # ('', 'assistance '),
        # ('', 'curriculum '),
        # ('', 'definitely '),
        # ('', 'experiment '),
        # ('', 'resolution '),
        # ('', 'everywhere '),
        # ('', 'industrial '),
        # ('', 'opposition '),
        # ('', 'confidence '),
        # ('', 'perception '),
        # ('', 'frequently '),
        # ('', 'basketball '),
        # ('', 'percentage '),
        # ('', 'politician '),
        # ('', 'ultimately '),
        # ('', 'appreciate '),
        # ('', 'difficulty '),
        # ('', 'appearance '),
        # ('', 'regulation '),
        # ('', 'conclusion '),
        # ('', 'photograph '),
        # ('', 'commitment '),
        # ('', 'instrument '),
        # ('', 'impossible '),
        # ('', 'scientific '),
        # ('', 'importance '),
        # ('', 'assessment '),
        # ('', 'literature '),
        # ('', 'expression '),
        # ('', 'historical '),
        # ('', 'relatively '),
        # ('', 'connection '),
        # ('', 'apparently '),
        # ('', 'background '),
        # ('', 'additional '),
        # ('', 'protection '),
        # ('', 'contribute '),
        # ('', 'leadership '),
        # ('', 'interested '),
        # ('', 'university '),
        # ('', 'department '),
        # ('', 'researcher '),
        # ('', 'completely '),
        # ('', 'absolutely '),
        # ('', 'restaurant '),
        # ('', 'eventually '),
        # ('', 'republican '),
        # ('', 'understand '),
        # ('', 'throughout '),
        # ('', 'themselves '),
        # ('', 'television '),
        # ('', 'technology '),
        # ('', 'successful '),
        # ('', 'production '),
        # ('', 'population '),
        # ('', 'particular '),
        # ('', 'management '),
        # ('', 'investment '),
        # ('', 'individual '),
        # ('', 'government '),
        # ('', 'generation '),
        # ('', 'experience '),
        # ('', 'everything '),
        # ('', 'especially '),
        # ('', 'discussion '),
        # ('', 'difference '),
        # ('', 'democratic '),
        # ('', 'conference '),
        # ('', 'commercial '),
        # ('', 'collection '),
        # ('', 'plaintiff '),
        # ('', 'butterfly '),
        # ('', 'warehouse '),
        # ('', 'organized '),
        # ('', 'foreigner '),
        # ('', 'twentieth '),
        # ('', 'biography '),
        # ('', 'frustrate '),
        # ('', 'speculate '),
        # ('', 'one-third '),
        # ('', 'overwhelm '),
        # ('', 'youngster '),
        # ('', 'favorable '),
        # ('', 'invention '),
        # ('', 'sexuality '),
        # ('', 'authorize '),
        # ('', 'policeman '),
        # ('', 'fantastic '),
        # ('', 'overnight '),
        # ('', 'chemistry '),
        # ('', 'objection '),
        # ('', 'regulator '),
        # ('', 'routinely '),
        # ('', 'threshold '),
        # ('', 'privately '),
        # ('', 'voluntary '),
        # ('', 'screening '),
        # ('', 'tolerance '),
        # ('', 'municipal '),
        # ('', 'mortality '),
        # ('', 'allegedly '),
        # ('', 'transport '),
        # ('', 'elaborate '),
        # ('', 'processor '),
        # ('', 'commodity '),
        # ('', 'high-tech '),
        # ('', 'excessive '),
        # ('', 'lightning '),
        # ('', 'specialty '),
        # ('', 'ecosystem '),
        # ('', 'publicity '),
        # ('', 'perceived '),
        # ('', 'curiosity '),
        # ('', 'hurricane '),
        # ('', 'breathing '),
        # ('', 'migration '),
        # ('', 'depressed '),
        # ('', 'worldwide '),
        # ('', 'stimulate '),
        # ('', 'interfere '),
        # ('', 'columnist '),
        # ('', 'placement '),
        # ('', 'partially '),
        # ('', 'sensation '),
        # ('', 'correctly '),
        # ('', 'franchise '),
        # ('', 'anonymous '),
        # ('', 'aesthetic '),
        # ('', 'uncertain '),
        # ('', 'ambitious '),
        # ('', 'touchdown '),
        # ('', 'workplace '),
        # ('', 'isolation '),
        # ('', 'fisherman '),
        # ('', 'execution '),
        # ('', 'alongside '),
        # ('', 'afterward '),
        # ('', 'instantly '),
        # ('', 'courtroom '),
        # ('', 'liability '),
        # ('', 'northeast '),
        # ('', 'sacrifice '),
        # ('', 'sentiment '),
        # ('', 'automatic '),
        # ('', 'undertake '),
        # ('', 'continent '),
        # ('', 'cooperate '),
        # ('', 'hopefully '),
        # ('', 'gathering '),
        # ('', 'realistic '),
        # ('', 'collector '),
        # ('', 'magnitude '),
        # ('', 'inventory '),
        # ('', 'performer '),
        # ('', 'necessity '),
        # ('', 'reception '),
        # ('', 'full-time '),
        # ('', 'suffering '),
        # ('', 'recipient '),
        # ('', 'therapist '),
        # ('', 'expertise '),
        # ('', 'reluctant '),
        # ('', 'indicator '),
        # ('', 'reporting '),
        # ('', 'happiness '),
        # ('', 'departure '),
        # ('', 'conscious '),
        # ('', 'promising '),
        # ('', 'nonprofit '),
        # ('', 'identical '),
        # ('', 'invisible '),
        # ('', 'portfolio '),
        # ('', 'detective '),
        # ('', 'promotion '),
        # ('', 'signature '),
        # ('', 'residence '),
        # ('', 'suspicion '),
        # ('', 'exclusive '),
        # ('', 'apologize '),
        # ('', 'convinced '),
        # ('', 'southeast '),
        # ('', 'undermine '),
        # ('', 'disapoint '),
        # ('', 'amendment '),
        # ('', 'radiation '),
        # ('', 'broadcast '),
        # ('', 'privilege '),
        # ('', 'diagnosis '),
        # ('', 'nightmare '),
        # ('', 'ownership '),
        # ('', 'recession '),
        # ('', 'southwest '),
        # ('', 'companion '),
        # ('', 'inspector '),
        # ('', 'seemingly '),
        # ('', 'developer '),
        # ('', 'estimated '),
        # ('', 'classical '),
        # ('', 'integrity '),
        # ('', 'secondary '),
        # ('', 'integrate '),
        # ('', 'sculpture '),
        # ('', 'interrupt '),
        # ('', 'northwest '),
        # ('', 'boyfriend '),
        # ('', 'highlight '),
        # ('', 'architect '),
        # ('', 'container '),
        # ('', 'defendant '),
        # ('', 'attribute '),
        # ('', 'cognitive '),
        # ('', 'confusion '),
        # ('', 'reinforce '),
        # ('', 'pregnancy '),
        # ('', 'recording '),
        # ('', 'consensus '),
        # ('', 'intensity '),
        # ('', 'continued '),
        # ('', 'discourse '),
        # ('', 'operating '),
        # ('', 'dependent '),
        # ('', 'inflation '),
        # ('', 'extension '),
        # ('', 'economics '),
        # ('', 'offensive '),
        # ('', 'brilliant '),
        # ('', 'temporary '),
        # ('', 'principal '),
        # ('', 'narrative '),
        # ('', 'lifestyle '),
        # ('', 'desperate '),
        # ('', 'publisher '),
        # ('', 'guideline '),
        # ('', 'formation '),
        # ('', 'calculate '),
        # ('', 'admission '),
        # ('', 'explosion '),
        # ('', 'frequency '),
        # ('', 'efficient '),
        # ('', 'economist '),
        # ('', 'counselor '),
        # ('', 'depending '),
        # ('', 'framework '),
        # ('', 'stability '),
        # ('', 'gradually '),
        # ('', 'celebrity '),
        # ('', 'evolution '),
        # ('', 'variation '),
        # ('', 'pollution '),
        # ('', 'prominent '),
        # ('', 'defensive '),
        # ('', 'violation '),
        # ('', 'confident '),
        # ('', 'adventure '),
        # ('', 'extensive '),
        # ('', 'terrorist '),
        # ('', 'regularly '),
        # ('', 'naturally '),
        # ('', 'similarly '),
        # ('', 'awareness '),
        # ('', 'guarantee '),
        # ('', 'interpret '),
        # ('', 'telescope '),
        # ('', 'expansion '),
        # ('', 'translate '),
        # ('', 'incentive '),
        # ('', 'spokesman '),
        # ('', 'initially '),
        # ('', 'encounter '),
        # ('', 'assistant '),
        # ('', 'strategic '),
        # ('', 'infection '),
        # ('', 'mechanism '),
        # ('', 'furniture '),
        # ('', 'testimony '),
        # ('', 'universal '),
        # ('', 'chocolate '),
        # ('', 'satellite '),
        # ('', 'provision '),
        # ('', 'terrorism '),
        # ('', 'precisely '),
        # ('', 'criticize '),
        # ('', 'negotiate '),
        # ('', 'historian '),
        # ('', 'diversity '),
        # ('', 'intention '),
        # ('', 'sensitive '),
        # ('', 'construct '),
        # ('', 'literally '),
        # ('', 'permanent '),
        # ('', 'gentleman '),
        # ('', 'accompany '),
        # ('', 'supporter '),
        # ('', 'perfectly '),
        # ('', 'personnel '),
        # ('', 'dimension '),
        # ('', 'objective '),
        # ('', 'exception '),
        # ('', 'so-called '),
        # ('', 'breakfast '),
        # ('', 'commander '),
        # ('', 'complaint '),
        # ('', 'marketing '),
        # ('', 'implement '),
        # ('', 'volunteer '),
        # ('', 'practical '),
        # ('', 'elsewhere '),
        # ('', 'substance '),
        # ('', 'reduction '),
        # ('', 'coalition '),
        # ('', 'discovery '),
        # ('', 'existence '),
        # ('', 'transform '),
        # ('', 'immediate '),
        # ('', 'territory '),
        # ('', 'remaining '),
        # ('', 'regarding '),
        # ('', 'primarily '),
        # ('', 'selection '),
        # ('', 'excellent '),
        # ('', 'cigarette '),
        # ('', 'childhood '),
        # ('', 'spiritual '),
        # ('', 'criticism '),
        # ('', 'passenger '),
        # ('', 'immigrant '),
        # ('', 'technical '),
        # ('', 'virtually '),
        # ('', 'physician '),
        # ('', 'celebrate '),
        # ('', 'typically '),
        # ('', 'secretary '),
        # ('', 'emphasize '),
        # ('', 'increased '),
        # ('', 'household '),
        # ('', 'essential '),
        # ('', 'vegetable '),
        # ('', 'surprised '),
        # ('', 'seriously '),
        # ('', 'reference '),
        # ('', 'telephone '),
        # ('', 'meanwhile '),
        # ('', 'eliminate '),
        # ('', 'landscape '),
        # ('', 'ourselves '),
        # ('', 'long-term '),
        # ('', 'component '),
        # ('', 'extremely '),
        # ('', 'emergency '),
        # ('', 'currently '),
        # ('', 'basically '),
        # ('', 'recommend '),
        # ('', 'expensive '),
        # ('', 'emotional '),
        # ('', 'carefully '),
        # ('', 'somewhere '),
        # ('', 'corporate '),
        # ('', 'disappear '),
        # ('', 'otherwise '),
        # ('', 'colleague '),
        # ('', 'yesterday '),
        # ('', 'democracy '),
        # ('', 'classroom '),
        # ('', 'following '),
        # ('', 'dangerous '),
        # ('', 'committee '),
        # ('', 'wonderful '),
        # ('', 'influence '),
        # ('', 'procedure '),
        # ('', 'christmas '),
        # ('', 'associate '),
        # ('', 'equipment '),
        # ('', 'principle '),
        # ('', 'technique '),
        # ('', 'advantage '),
        # ('', 'obviously '),
        # ('', 'apartment '),
        # ('', 'christian '),
        # ('', 'potential '),
        # ('', 'tradition '),
        # ('', 'introduce '),
        # ('', 'generally '),
        # ('', 'beginning '),
        # ('', 'insurance '),
        # ('', 'afternoon '),
        # ('', 'encourage '),
        # ('', 'therefore '),
        # ('', 'effective '),
        # ('', 'concerned '),
        # ('', 'treatment '),
        # ('', 'structure '),
        # ('', 'statement '),
        # ('', 'sometimes '),
        # ('', 'something '),
        # ('', 'situation '),
        # ('', 'scientist '),
        # ('', 'represent '),
        # ('', 'religious '),
        # ('', 'recognize '),
        # ('', 'professor '),
        # ('', 'president '),
        # ('', 'political '),
        # ('', 'operation '),
        # ('', 'newspaper '),
        # ('', 'necessary '),
        # ('', 'knowledge '),
        # ('', 'interview '),
        # ('', 'including '),
        # ('', 'important '),
        # ('', 'financial '),
        # ('', 'executive '),
        # ('', 'everybody '),
        # ('', 'establish '),
        # ('', 'education '),
        # ('', 'direction '),
        # ('', 'difficult '),
        # ('', 'different '),
        # ('', 'determine '),
        # ('', 'condition '),
        # ('', 'community '),
        ('char', 'character '),
        # ('', 'challenge '),
        # ('', 'certainly '),
        # ('', 'candidate '),
        # ('', 'behaviour '),
        # ('', 'beautiful '),
        # ('', 'available '),
        # ('', 'authority '),
        # ('', 'attention '),
        # ('', 'agreement '),
        # ('', 'according '),
        # ('', 'yourself '),
        # ('', 'whatever '),
        # ('', 'violence '),
        # ('', 'training '),
        # ('', 'together '),
        # ('', 'thousand '),
        # ('', 'suddenly '),
        # ('', 'strategy '),
        # ('', 'standard '),
        # ('', 'specific '),
        # ('', 'southern '),
        # ('', 'somebody '),
        # ('', 'shoulder '),
        # ('', 'security '),
        # ('', 'response '),
        # ('', 'resource '),
        # ('', 'research '),
        # ('', 'remember '),
        # ('', 'recently '),
        # ('', 'question '),
        # ('', 'property '),
        # ('', 'probably '),
        # ('', 'pressure '),
        # ('', 'practice '),
        ('prio', 'priority '),
        # ('', 'possible '),
        # ('', 'positive '),
        # ('', 'position '),
        # ('', 'politics '),
        # ('', 'physical '),
        # ('', 'personal '),
        # ('', 'painting '),
        # ('', 'official '),
        # ('', 'national '),
        # ('', 'movement '),
        # ('', 'military '),
        # ('', 'material '),
        # ('', 'marriage '),
        # ('', 'majority '),
        # ('', 'maintain '),
        # ('', 'magazine '),
        # ('', 'language '),
        # ('', 'interest '),
        # ('', 'industry '),
        # ('', 'indicate '),
        # ('', 'increase '),
        # ('', 'identify '),
        # ('', 'hospital '),
        # ('', 'evidence '),
        # ('', 'everyone '),
        # ('', 'employee '),
        # ('', 'economic '),
        # ('', 'discover '),
        # ('', 'director '),
        # ('', 'describe '),
        # ('', 'decision '),
        # ('', 'daughter '),
        # ('', 'customer '),
        # ('', 'cultural '),
        # ('', 'continue '),
        # ('', 'contains '),
        # ('', 'consumer '),
        # ('', 'consider '),
        # ('', 'campaign '),
        # ('', 'business '),
        # ('', 'building '),
        # ('', 'audience '),
        # ('', 'progress ')
        # ('', 'attorney '),
        # ('', 'approach '),
        # ('', 'analysis '),
        # ('', 'although '),
        # ('', 'actually '),
        # ('', 'activity '),
        # ('', 'american '),
        # ('', 'without '),
        # ('', 'whether '),
        # ('', 'western '),
        # ('', 'various '),
        # ('', 'usually '),
        # ('', 'trouble '),
        # ('', 'tonight '),
        # ('', 'through '),
        # ('', 'thought '),
        # ('', 'teacher '),
        # ('', 'surface '),
        # ('', 'support '),
        # ('', 'suggest '),
        # ('', 'success '),
        # ('', 'subject '),
        # ('', 'student '),
        # ('', 'station '),
        # ('', 'special '),
        # ('', 'someone '),
        # ('', 'soldier '),
        # ('', 'society '),
        # ('', 'similar '),
        # ('', 'several '),
        # ('', 'service '),
        # ('', 'serious '),
        # ('', 'section '),
        # ('', 'science '),
        # ('', 'respond '),
        # ('', 'require '),
        # ('', 'reflect '),
        # ('', 'receive '),
        # ('', 'realize '),
        # ('', 'reality '),
        # ('', 'quickly '),
        # ('', 'quality '),
        # ('', 'purpose '),
        # ('', 'provide '),
        # ('', 'protect '),
        # ('', 'project '),
        # ('', 'program '),
        # ('', 'product '),
        # ('', 'produce '),
        # ('', 'process '),
        # ('', 'problem '),
        # ('', 'private '),
        # ('', 'prevent '),
        # ('', 'present '),
        # ('', 'prepare '),
        # ('', 'popular '),
        # ('', 'picture '),
        # ('', 'perhaps '),
        # ('', 'perform '),
        # ('', 'pattern '),
        # ('', 'patient '),
        # ('', 'partner '),
        # ('', 'outside '),
        # ('', 'officer '),
        # ('', 'nothing '),
        # ('', 'network '),
        # ('', 'natural '),
        # ('', 'morning '),
        # ('', 'mission '),
        # ('', 'million '),
        # ('', 'message '),
        # ('', 'mention '),
        # ('', 'meeting '),
        # ('', 'medical '),
        # ('', 'measure '),
        # ('', 'manager '),
        # ('', 'machine '),
        # ('', 'kitchen '),
        # ('', 'involve '),
        # ('', 'instead '),
        # ('', 'include '),
        # ('', 'improve '),
        # ('', 'imagine '),
        # ('', 'husband '),
        # ('', 'hundred '),
        # ('', 'however '),
        # ('', 'history '),
        # ('', 'himself '),
        # ('', 'herself '),
        # ('', 'general '),
        # ('', 'forward '),
        # ('', 'foreign '),
        # ('', 'finally '),
        # ('', 'feeling '),
        # ('', 'federal '),
        # ('', 'example '),
        # ('', 'exactly '),
        # ('', 'economy '),
        # ('', 'disease '),
        # ('', 'discuss '),
        # ('', 'develop '),
        # ('', 'current '),
        # ('', 'culture '),
        # ('', 'compare '),
        # ('', 'company '),
        # ('', 'capital '),
        # ('', 'brother '),
        # ('', 'billion '),
        # ('', 'between '),
        # ('', 'because '),
        # ('', 'another '),
        # ('', 'address '),
        # ('', 'account '),
        # ('', 'ability ')
        # ('', 'admin ')
    ]

    try:
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

if __name__ == "__main__":
    main()
