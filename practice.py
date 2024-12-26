import enchant

def extract_typing_words(input_file):
    dictionary = enchant.Dict("en_US")
    
    programming_words = []
    phrases = []
    snippets = []
    suffixes = []
    prefixes = []
    root_words = []
    brief = []
    english5k = []
    
    current_section = None
    keywords = ['[cursor]', '[left]', '[right]', '[shift]', '[space]', '[backspace]']
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#'):
                if 'PROGRAMMING' in line:
                    current_section = 'programming'
                elif 'PHRASES' in line:
                    current_section = 'phrases'
                elif 'SNIPPETS' in line:
                    current_section = 'snippets'
                elif 'SUFFIXES' in line:
                    current_section = 'suffixes'
                elif 'PREFIXES' in line:
                    current_section = 'prefixes'
                elif 'ROOT WORDS' in line:
                    current_section = 'roots'
                elif 'BRIEF' in line:
                    current_section = 'brief'
                elif 'ENGLISH 5K' in line:
                    current_section = 'english5k'
                continue
                
            try:
                tuple_data = eval(line.replace('\\n', '\\\\n'))
                if not isinstance(tuple_data, tuple) or len(tuple_data) < 2:
                    continue
                    
                word = tuple_data[1].strip("'\"").strip()
                
                if current_section == 'suffixes':
                    backspace_count = word.count('[backspace]')
                    clean_suffix = word
                    for keyword in keywords:
                        clean_suffix = clean_suffix.replace(keyword, '')
                    clean_suffix = clean_suffix.strip()
                    if clean_suffix:
                        suffixes.append((clean_suffix, backspace_count))
                else:
                    for keyword in keywords:
                        word = word.replace(keyword, '')
                    word = word.replace('\\n', '\\n').strip()
                    
                    if word:
                        if current_section == 'programming':
                            programming_words.append(word)
                        elif current_section == 'phrases':
                            phrases.append(word)
                        elif current_section == 'snippets':
                            snippets.append(word)
                        elif current_section == 'prefixes':
                            prefixes.append(word)
                        elif current_section == 'roots':
                            root_words.append(word)
                        elif current_section == 'brief':
                            brief.append(word)
                        elif current_section == 'english5k':
                            english5k.append(word)
            except:
                continue

    combined_words = []
    word_count = 0
    
    combined_words += programming_words
    word_count += len(programming_words)
    combined_words += phrases
    word_count += len(phrases)
    combined_words += snippets
    word_count += len(snippets)
    combined_words += brief
    word_count += len(brief)
    combined_words += english5k
    word_count += len(english5k)

    for i in range(len(suffixes)):
        suffix, backspace_count = suffixes[i]
        suffixes[i] = (suffix, backspace_count - 1)

    for word in root_words:
        word_count += 1
        combined_words.append(word)
        
        for suffix, backspace_count in suffixes:
            new_word = word[:-backspace_count] + suffix if backspace_count > 0 else word + suffix
            if dictionary.check(new_word):
                word_count += 1
                combined_words.append(new_word)
        
        for prefix in prefixes:
            prefixed_word = prefix + word
            if dictionary.check(prefixed_word):
                word_count += 1
                combined_words.append(prefixed_word)
            
            for suffix, backspace_count in suffixes:
                new_word = prefixed_word[:-backspace_count] + suffix if backspace_count > 0 else prefixed_word + suffix
                if dictionary.check(new_word):
                    word_count += 1
                    combined_words.append(new_word)
    
    print(f"Total real words: {word_count}")
    print('|'.join(w for w in combined_words if w))

extract_typing_words('dictionary.txt')
