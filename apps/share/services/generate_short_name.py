def generate_short_name(name):
    words = name.split()
    if len(words) == 1:
        return words[0][:2].upper()
    else:
        return ''.join([word[0].upper() for word in words])
