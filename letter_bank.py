

class LetterBank:
    def __init__(self):
        self.letter_bank = letter_bank = {
                                            'a': 9,
                                            'b': 2,
                                            'c': 2,
                                            'd': 4,
                                            'e': 12,
                                            'f': 2,
                                            'g': 3,
                                            'h': 6,
                                            'i': 9,
                                            'j': 1,
                                            'k': 1,
                                            'l': 4,
                                            'm': 2,
                                            'n': 6,
                                            'o': 8,
                                            'p': 2,
                                            'q': 1,
                                            'r': 6,
                                            's': 4,
                                            't': 6,
                                            'u': 4,
                                            'v': 2,
                                            'w': 2,
                                            'x': 1,
                                            'y': 2,
                                            'z': 1,
                                            '0': 2, # bank tiles
                                        }
        self.letter_bank_total = sum(letter_bank.values())
        