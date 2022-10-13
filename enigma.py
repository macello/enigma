ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

I =    ([4, 9, 10, 2, 7, 1, 23, 9, 13, 16, 3, 8, 2, 9, 10, 18, 7, 3, 0, 22, 6, 13, 5, 20, 4, 10], 16) #EKMFLGDQVZNTOWYHXUSPAIBRCJ; Ü=16
II =   ([0, 8, 1, 7, 14, 3, 11, 13, 15, 18, 1, 22, 10, 6, 24, 13, 0, 15, 7, 20, 21, 3, 9, 24, 16, 5], 4)  #AJDKSIRUXBLHWTMCQGZNPYFVOE; Ü=4
III =  ([1, 2, 3, 4, 5, 6, 22, 8, 9, 10, 13, 10, 13, 0, 10, 15, 18, 5, 14, 7, 16, 17, 24, 21, 18, 15], 21) #BDFHJLCPRTXVZNYEIWGAKMUSQO; Ü=21
UKWB = [24, 16, 18, 4, 12, 13, 5, 22, 7, 14, 3, 21, 2, 23, 24, 19, 14, 10, 13, 6, 8, 1, 25, 12, 2, 20]     #YRUHQSLDPXNGOKMIEBFZCWVJAT

DIC_ROTORS = {
    'I': I,
    'II': II,
    'III': III
}

#--- Wandelt Absolute Konfiguration in relative um,
#--- wird im fertigen Code nicht benötigt.
def convertRotor(configuration):
    for i in range(26):
        if configuration[i]-i<0:
            configuration[i] = configuration[i]-i+26
        else:
            configuration[i] = configuration[i]-i
    print(configuration)

    out = []
    for i in range(26):
        x = configuration[i]+i-26
        out.append(ALPHABET[x])
    print(out)

class Rotor:
    def __init__(self, configuration):
        global ALPHABET
        self.carryover = configuration[1]
        self.config = []
        self.config = configuration[0]
        self.anticonfig = []
        for i in range(26):
            self.anticonfig.append(0)
        for i in range(26):
            self.anticonfig[i+self.config[i]-26] = 26-self.config[i]
        for i in range(26):
            self.config[i] = [self.config[i], self.anticonfig[i], ALPHABET[i+self.config[i]-26]]

    def rotate(self, doCarry=True):
        temp = self.config.pop(0)
        self.config.append(temp)
        if doCarry:
            if self.carryover==0:
                self.carryover = 25
            else:
                self.carryover -= 1

class Ukw:
    def __init__(self, configuration):
        self.config = configuration

class Plugboard:
    def __init__(self, configuration):
        global ALPHABET
        self.config =[]
        for i in range(26):
            self.config.append(0)
        for i in range(len(configuration)):
            x = ALPHABET.index(configuration[i][0])
            y = ALPHABET.index(configuration[i][1])
            self.config[x] = y-x
            self.config[y] = x-y

def turn():
    global rotor0, rotor1, rotor2
    if rotor1.carryover == 0:
        # 1, 2, 3 drehen
        rotor0.rotate()
        rotor1.rotate()
        rotor2.rotate()
    elif rotor0.carryover == 0:
        # 1, 2 drehen
        rotor0.rotate()
        rotor1.rotate()
    else:
        # 1 dreht
        rotor0.rotate()

def codeLetter(letter):
    global rotor0, rotor1, rotor2, ukw
    rotors = (rotor0, rotor1, rotor2)
    srotor = (rotor2, rotor1, rotor0)
    if letter==' ' or letter=='\n':
        pass
    else:
        turn()
        x = ALPHABET.index(letter)
        x += plugboard.config[x]
        x %= 26
        for rotor in rotors:
            x += rotor.config[x][0]
            x %= 26
        x += ukw.config[x]
        x %= 26
        for rotor in srotor:
            x += rotor.config[x][1]
            x %= 26
        x += plugboard.config[x]
        x %= 26
        letter = ALPHABET[x]
    return letter

def codeText(text):
    out = ''
    for i in range(len(text)):
        out += codeLetter(text[i])
    return out

def key(raw_key):
    global rotor0, rotor1, rotor2, ukw, plugboard, ALPHABET
    #key in Liste der richtigen Form bringen
    raw_key = raw_key.split(',')
    for i in range(len(raw_key)):
        raw_key[i] = raw_key[i].lstrip()
    rotors = raw_key[0].split(' ')
    rings = raw_key[1].split(' ')
    for i in range(len(rings)):
        rings[i] = int(rings[i])
    starts = raw_key[2].split(' ')
    connections = raw_key[3].split(' ')
    message = raw_key[-1]
    # Rotoren konfigurieren
    rotor0 = Rotor(DIC_ROTORS[rotors[0]])
    rotor1 = Rotor(DIC_ROTORS[rotors[1]])
    rotor2 = Rotor(DIC_ROTORS[rotors[2]])
    ukw = Ukw(UKWB)
    rotors = (rotor0, rotor1, rotor2)
    # Ringstellung konfigurieren
    for i in range(3):
        for j in range(rings[i]):
            rotors[i].rotate(False)
    # Grundstellung konfigurieren
    for i in range(3):
        while rotors[i].config[0][2] != starts[i]:
            rotors[i].rotate()
    # Steckerbrett konfigurieren
    plugboard = Plugboard(connections)
    return message

def key_light(raw_key):
    global rotor0, rotor1, rotor2
    rotors = (rotor0, rotor1, rotor2)
    raw_key = raw_key.split(',')
    for i in range(len(raw_key)):
        raw_key[i] = raw_key[i].lstrip()
    starts = raw_key[0].split(' ')
    message = raw_key[-1]
    # neue Grundstellung
    for i in range(3):
        while rotors[i].config[0][2] != starts[i]:
            rotors[i].rotate()
    return message

def check_key(raw_key):
    global ALPHABET, DIC_ROTORS
    valid = True
    error = ''
    raw_key = raw_key.split(',')
    for i in range(len(raw_key)):
        raw_key[i] = raw_key[i].lstrip()
    rotors = raw_key[0].split(' ')
    rings = raw_key[1].split(' ')
    for i in range(len(rings)):
        rings[i] = int(rings[i])-1
    starts = raw_key[2].split(' ')
    connections = raw_key[3].split(' ')
    message = raw_key[-1]
    #print(message)

    # Rotoren
    for rotor in rotors:
        if not rotor in DIC_ROTORS.keys():
            valid = False
            error += 'Es wurde mindestens ein ungültiger Rotor im Schlüssel verwendet.\n'
            break
    for i in DIC_ROTORS.keys():
        if rotors.count(i) > 1:
            valid = False
            error += 'Ein Rotor wurde mehrmals im Schlüssel verwendet.\n'
            break
    if len(rotors) != 3:
        valid = False
        error += 'Es wurden mehr oder weniger als 3 Rotoren angegeben.\n'

    # Ringstellung
    for i in rings:
        if i<0 or i>25:
            valid = False
            error += 'Eine Zahl bei den Ringstellungen ist kleiner als 1 oder grösser als 26.\n'
            break
    if len(rings) != 3:
        valid = False
        error += 'Es wurden mehr oder weniger als 3 Ringstellungen angegeben.\n'

    # Grundstellung
    for i in starts:
        if not i in ALPHABET:
            valid = False
            error += 'Eine Grundstellung ist nicht mit einem einzigen Buchstaben angegeben.\n'
            break
    if len(starts) != 3:
        valid = False
        error += 'Es wurden mehr oder weniger als 3 Grundstellungen angegeben.\n'

    #Steckerbrett
    check = ''
    for i in connections:
        check += i
    for letter in ALPHABET:
        if check.count(letter) > 1:
            valid=False
            error += 'Beim Steckerbrett wurde ein Buchstabe mehrmals verwendet.\n'

    # Nachricht
    for i in range(len(message)):
        if message[i] ==' ' or message[i] == '\n':
            pass
        elif not message[i] in ALPHABET:
            valid = False
            error += 'In der Nachricht sind nicht ausschliesslich Buchstaben enthalten\n'
            break

    return valid, error

def check_key_light(raw_key):
    global ALPHABET
    error = ''
    valid = True

    raw_key = raw_key.split(',')
    starts = raw_key[0].split(' ')
    message = raw_key[-1][1:]

    # Grundstellung
    for i in starts:
        if not i in ALPHABET:
            valid = False
            error += 'Eine Grundstellung ist nicht mit einem einzigen Buchstaben angegeben.\n'
            break
    if len(starts) != 3:
        valid = False
        error += 'Es wurden mehr oder weniger als 3 Grundstellungen angegeben.\n'

    # Nachricht
    for i in range(len(message)):
        if message[i] == ' ' or message[i] == '\n':
            pass
        elif not message[i] in ALPHABET:
            valid = False
            error += 'In der Nachricht sind nicht ausschliesslich Buchstaben enthalten\n'
            break

    return valid, error

raw_key = input('''\n\nSchlüssel und Nachricht in folgender Form eingeben:
Rotoren(römische Zahlen I-III), Ringstellung(Zahlen 1-26), Grundstellung(Buchstaben), Steckverbindungen(Buchstaben), Nachricht(Buchstaben)
Die Buchstaben (ohne Umlaute) müssen nicht zwingend gross geschrieben werden.
Beispiel: II I III, 12 25 3, A B C, AB KS FQ RT, BEISPIEL EINER NACHRICHT
Bei einem kleineren Eingabefehler gibt das Programm eine Fehlermeldung aus.
Bei einem grösseren Eingabefehler stürzt das Programm ab und Sie müssen den Fehler selbst suchen ;)\n\n''').upper()
valid, error = check_key(raw_key)
if valid:
    message = codeText(key(raw_key))
    print('\n--------------------ver-/entschlüsselte Nachricht--------------------')
    print(message)
else:
    print(error)

active = True
while active:
    raw_key = input('''\n\nGrundstellung und Nachricht wie im folgenden Beispiel eingeben:
A B C, BEISPIEL EINER NACHRICHT
Hierbei entsprechen die restlichen Schlüsselkomponenten den zuvor eingegebenen.
Um das Programm zu beenden, geben Sie "exit" ein.\n\n''').upper()
    if raw_key == 'EXIT':
        active = False
        break
    valid, error = check_key_light(raw_key)
    if valid:
        message = codeText(key_light(raw_key))
        print('\n--------------------ver-/entschlüsselte Nachricht--------------------')
        print(message)
    else:
        print(error)
