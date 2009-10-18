#!/usr/bin/python
# Copyright (C) 2009 Johann C. Rocholl <johann@rocholl.net>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Simple readable random password generator in one Python file

This is a random password generator based on the most common
combinations of vowels and consonants in the English language. It
makes passwords that are simple to read and remember, but safe from
dictionary attacks. You can use this module in your program like this:

>>> from english_passwords import generate_password
>>> generate_password()
'cheedorth'
>>> generate_password(digits=2)
'gnorious23'

Known problems:
1. The algorithm may generate words that appear in an English dictionary.
2. The algorithm may generate profanities. To work around these problems,
   check the output against a word list and try again if necessary.
3. Without digits, the current version can generate only 140860
   different passwords. Adding digits is highly recommended, because
   it increases the search space for brute force attacks.

If you run this script on the command line without arguments, it will
generate 100 random passwords for you:

$ python english_passwords.py
steakent        mnefres         ghoptiod        ghonteps        veivetch
genthelms       rhymbest        glanswelps      nurthet         psystithms
smorbicts       toanioms        shackyst        candmeds        nibang
truenteeds      threarou        biablelp        whirious        cloublids
spouchatch      nuisew          ghappoils       sleckisc        wrisfarts
scettlisps      straintids      wridgerms       gnowips         weedlyths
prectlyl        fagults         sphersed        mnellals        sphetweipt
phansminds      postlyst        heybough        mnephirls       liallords
needeft         fronfrorks      zobjeck         criencies       splenlyl
joymerr         mnerbifts       streerus        brientlengths   flousipts
rhympail        gansior         funcherb        grairolls       oaninch
stoorilm        troubly         smarvirms       stricaught      ghamposts
vobtair         schechamps      pootnol         slinhept        clupom
stymbidth       foomirls        renthels        naireit         strurtoh
spheffi         fientlemns      steareir        culgength       shootnolt
wrojuch         glatyms         phrantlerbs     stoosough       chailief
chaffompts      schojers        reinstabs       psypyl          twitas
baudags         smorchilms      drossutt        peemuns         claudeal
roomul          spoilians       phrarblers      pimbild         pumains
loadioms        spoutrields     fleelouts       brexplairs      glonciews

This file is ready to use with common English letter combinations, but
you can also use it to generate combination dicts for other languages.
Then you can replace the dicts in this file with the new ones, and you
have a password generator for your own language, e.g. Klingon.

$ python english_passwords.py wordlist.txt 1000

The file wordlist.txt should contain one lowercase word on each line.
To make a simple wordlist for use with this script, download and
unpack SCOWL-6 and then run the following commands:

$ cd scowl-6/final
$ cat english-words.{10,20} | grep -v "'" | grep -v $'\xe9' > wordlist.txt
"""

import random


def generate_password(digits=0):
    parts = []
    choice = random.choice(START_VOWEL.keys())
    parts.append(choice)
    choice = random.choice(START_VOWEL[choice])
    parts.append(choice)
    choice = random.choice(VOWEL_CONSONANT[choice])
    parts.append(choice)
    choice = random.choice(CONSONANT_VOWEL[choice])
    parts.append(choice)
    choice = random.choice(VOWEL_END[choice])
    parts.append(choice)
    for d in range(digits):
        parts.append(random.choice(DIGITS))
    return ''.join(parts)


def count_groups(filename='wordlist.txt'):
    groups = {}
    for word in open(filename):
        word = '^' + word.strip().lower() + '$'
        index = 0
        v_group = c_group = ''
        while index < len(word):
            # Find some consonants.
            start = index
            while index < len(word) and word[index] not in VOWELS:
                index += 1
            c_group = word[start:index]
            if v_group and c_group:
                pair = (v_group, c_group)
                groups[pair] = groups.get(pair, 0) + 1
            # Find some vowels.
            start = index
            while index < len(word) and word[index] in VOWELS:
                index += 1
            v_group = word[start:index]
            if c_group and v_group:
                pair = (c_group, v_group)
                groups[pair] = groups.get(pair, 0) + 1
    group_list = []
    for pair, count in groups.iteritems():
        group1, group2 = pair
        group_list.append((count, group1, group2))
    group_list.sort()
    group_list.reverse() # Highest count first.
    return group_list


def build_prefix_dict(groups, group2_allow=None, cutoff=100):
    prefix_dict = {}
    for triple in groups:
        count, group1, group2 = triple
        group1 = group1.lstrip('^')
        group2 = group2.rstrip('$')
        if group2_allow and group2 not in group2_allow:
            continue
        if group1 not in prefix_dict:
            prefix_dict[group1] = []
        prefix_dict[group1].append(group2)
        cutoff -= 1
        if not cutoff:
            break
    return prefix_dict


def print_prefix_dict(name, prefix_dict):
    import textwrap
    prefixes = prefix_dict.keys()
    prefixes.sort()
    print name, '= {'
    for prefix in prefixes:
        suffixes = prefix_dict[prefix]
        line = "    '%s': ['%s']," % (prefix, "', '".join(suffixes))
        indent = line.index('[') + 1
        print textwrap.fill(line, subsequent_indent=' ' * indent)
    print '    }'


def strength(dicts, suffix=None):
    last = dicts[-1]
    first = dicts[:-1]
    sum = 0
    for key in last.keys():
        if suffix is None or suffix in last[key]:
            sum += strength(first, key) if first else 1
    # l = len(dicts)
    # print "%sstrength(%d, '%s'): %d" % ('    ' * (4 - l), l, suffix, sum)
    return sum


def process_wordlist(filename='wordlist.txt', cutoff=100):
    groups = count_groups(filename)
    vowel_end = build_prefix_dict(
        [triple for triple in groups if triple[2].endswith('$')],
        cutoff=cutoff)
    consonant_vowel = build_prefix_dict(
        [triple for triple in groups
         if not triple[1].startswith('^') and not triple[2].endswith('$')],
        vowel_end.keys(), cutoff=cutoff)
    vowel_consonant = build_prefix_dict(
        [triple for triple in groups
         if not triple[1].startswith('^') and not triple[2].endswith('$')],
        consonant_vowel.keys(), cutoff=cutoff)
    start_vowel = build_prefix_dict(
        [triple for triple in groups if triple[1].startswith('^')],
        vowel_consonant.keys(), cutoff=cutoff)
    print "# This version can generate %d different passwords." % strength(
        [start_vowel, vowel_consonant, consonant_vowel, vowel_end])
    print "DIGITS = '%s' # Avoid confusing 0 and 1 with O and I." % DIGITS
    print "VOWELS = '%s' # To split words into groups of letters." % VOWELS
    print_prefix_dict('START_VOWEL', start_vowel)
    print_prefix_dict('VOWEL_CONSONANT', vowel_consonant)
    print_prefix_dict('CONSONANT_VOWEL', consonant_vowel)
    print_prefix_dict('VOWEL_END', vowel_end)
    print
    print "if __name__ == '__main__':"
    print "    main()"


def main():
    import sys
    if len(sys.argv) == 3:
        filename = sys.argv[1] # For example, wordlist.txt with english words.
        cutoff = int(sys.argv[2]) # For example, 10 for the top ten choices.
        process_wordlist(filename, cutoff)
    else:
        for row in range(20):
            for column in range(4):
                print '%-15s' % generate_password(),
            print generate_password()


# This version can generate 140860 different passwords.
DIGITS = '23456789' # Avoid confusing 0 and 1 with O and I.
VOWELS = 'aeiouy' # To split words into groups of letters.
START_VOWEL = {
    '': ['a', 'i', 'e', 'o', 'u', 'ou', 'ea', 'au', 'ai', 'you', 'ei',
         'oi', 'oa', 'io'],
    'b': ['a', 'e', 'u', 'o', 'i', 'ea', 'oo', 'ou', 'io', 'ui', 'y',
          'oi', 'oa', 'ia', 'ee', 'eau', 'oy', 'ei', 'au'],
    'bl': ['a', 'o', 'e', 'i', 'ue', 'oo', 'u'],
    'br': ['i', 'a', 'ea', 'o', 'oa', 'ee', 'u', 'ie', 'e', 'ai',
           'ou'],
    'c': ['o', 'a', 'u', 'ou', 'i', 'e', 'oo', 'y', 'au', 'oi', 'oa',
          'ea', 'ue', 'ei'],
    'ch': ['a', 'e', 'o', 'u', 'i', 'ea', 'ee', 'ai', 'oo', 'oi',
           'ie'],
    'cl': ['a', 'o', 'ea', 'i', 'u', 'ai', 'e', 'ue', 'ou', 'ie',
           'au'],
    'cr': ['a', 'i', 'o', 'u', 'ea', 'e', 'y', 'ui', 'ue', 'ie',
           'ee'],
    'd': ['e', 'i', 'o', 'a', 'u', 'ea', 'ia', 'ee', 'ou', 'oo', 'ie',
          'y', 'oe', 'ue', 'ua', 'oi', 'ei', 'au', 'ai'],
    'dr': ['a', 'i', 'o', 'ea', 'u', 'e', 'ai', 'ie', 'y'],
    'f': ['i', 'o', 'a', 'u', 'e', 'ai', 'ou', 'ee', 'oo', 'ea', 'au',
          'ie', 'ue', 'oa'],
    'fl': ['a', 'u', 'o', 'oo', 'i', 'oa', 'e', 'ie', 'y', 'ui', 'ue',
           'ou', 'ee'],
    'fr': ['a', 'o', 'ee', 'i', 'ie', 'e', 'u', 'ui', 'ea', 'y',
           'au'],
    'g': ['e', 'a', 'o', 'i', 'ui', 'ua', 'u', 'ue', 'oo', 'eo', 'ea',
          'ai', 'oa', 'oi', 'oe', 'ia'],
    'gh': ['o', 'a'],
    'gl': ['o', 'a', 'ea', 'ue'],
    'gn': ['o'],
    'gr': ['a', 'o', 'i', 'ou', 'ea', 'ee', 'oa', 'ie', 'e', 'ai'],
    'h': ['a', 'o', 'i', 'e', 'ea', 'u', 'y', 'ou', 'ai', 'oo', 'ie',
          'ei', 'ee', 'ey'],
    'j': ['u', 'a', 'oi', 'o', 'ou', 'e', 'ea', 'ui', 'oy', 'ai'],
    'k': ['i', 'ey', 'ee', 'e'],
    'kn': ['o', 'i', 'ee', 'e'],
    'l': ['i', 'o', 'a', 'e', 'ea', 'u', 'oo', 'au', 'oa', 'ou', 'ie',
          'y', 'ia', 'ai', 'io', 'ei'],
    'm': ['a', 'i', 'o', 'e', 'u', 'ea', 'ai', 'y', 'ou', 'oa', 'ee',
          'oo'],
    'mn': ['e'],
    'n': ['o', 'e', 'a', 'u', 'i', 'ee', 'ea', 'ai', 'oi', 'ou', 'ui',
          'oo', 'ei', 'au'],
    'p': ['a', 'o', 'e', 'u', 'i', 'ai', 'oi', 'ea', 'ou', 'oe', 'oo',
          'au', 'ie', 'eo', 'ee', 'y', 'ia'],
    'ph': ['o', 'y', 'a', 'i', 'e', 'oe'],
    'phr': ['a'],
    'pl': ['a', 'ea', 'u', 'o', 'ai', 'oy', 'e', 'au'],
    'pr': ['o', 'e', 'i', 'a', 'ea', 'io', 'oo', 'ie', 'ou', 'ai'],
    'ps': ['y'],
    'q': ['ua', 'ui', 'ue', 'uo', 'uie', 'uee'],
    'r': ['e', 'a', 'ea', 'i', 'o', 'u', 'ou', 'ai', 'ei', 'oo', 'ui',
          'oa', 'io'],
    'rh': ['y', 'e'],
    's': ['u', 'e', 'i', 'a', 'o', 'y', 'ou', 'ee', 'ea', 'ui', 'ai',
          'ue', 'oo', 'oi', 'oa', 'au'],
    'sc': ['a', 'o', 'ie', 'e', 'u'],
    'sch': ['e', 'oo', 'o'],
    'scr': ['a', 'o', 'ea', 'e', 'i', 'ee'],
    'sh': ['o', 'a', 'i', 'e', 'ou', 'u', 'oo', 'ee', 'oe', 'y'],
    'sk': ['i', 'e', 'y', 'u'],
    'sl': ['i', 'o', 'a', 'ee', 'e'],
    'sm': ['a', 'o', 'i', 'e', 'oo', 'u'],
    'sn': ['ea', 'o', 'a', 'i', 'ai'],
    'sp': ['e', 'o', 'i', 'a', 'ee', 'ea', 'oi', 'u', 'oo', 'y', 'ou',
           'ie'],
    'sph': ['e'],
    'spl': ['i', 'e'],
    'spr': ['i', 'ea', 'u', 'a'],
    'sq': ['ua', 'uee'],
    'st': ['a', 'u', 'o', 'i', 'e', 'ee', 'ea', 'ai', 'y', 'oo'],
    'str': ['i', 'u', 'e', 'a', 'o', 'ai', 'ee', 'ea'],
    'sw': ['a', 'i', 'ea', 'ee', 'o', 'u', 'e'],
    't': ['e', 'a', 'o', 'i', 'u', 'ea', 'y', 'ou', 'ai', 'oo', 'ee',
          'ie', 'oy', 'oi', 'oe', 'oa', 'au'],
    'th': ['e', 'i', 'eo', 'a', 'ou', 'o', 'ie', 'u', 'ei', 'y', 'ey',
           'ee'],
    'thr': ['ea', 'o', 'u', 'ou', 'oa', 'e', 'ee'],
    'tr': ['a', 'i', 'u', 'ea', 'ai', 'e', 'ou', 'ia', 'oo', 'ie',
           'ee', 'y', 'ue', 'o'],
    'tw': ['i', 'e', 'o'],
    'v': ['a', 'e', 'i', 'o', 'ie', 'io', 'oi', 'ia', 'u', 'ou', 'ei',
          'ai'],
    'w': ['i', 'a', 'o', 'e', 'ea', 'ee', 'ai', 'oo', 'ei', 'ou'],
    'wh': ['i', 'e', 'o', 'a', 'oo', 'ee', 'y', 'oe'],
    'wr': ['i', 'e', 'a', 'o'],
    'z': ['o', 'e', 'oo'],
    }
VOWEL_CONSONANT = {
    'a': ['t', 'r', 'll', 'g', 'n', 'bl', 'l', 'm', 'd', 'ss', 'c',
          'nc', 'ct', 'cc', 'pp', 'b', 'rr', 's', 'st', 'ng', 'v',
          'k', 'tt', 'nt', 'nd', 'dv', 'rt', 'p', 'ck', 'rg', 'nn',
          'sh', 'th', 'w', 'ppr', 'rd', 'dd', 'rk', 'z', 'lt', 'gr',
          'dm', 'ch', 'tch', 'rm', 'mp', 'gg', 'ff', 'x', 'ppl',
          'ttr', 'pt', 'ph', 'lc', 'sc', 'rch', 'nsf', 'mpl', 'mb',
          'f', 'bs', 'ntl', 'nsm', 'mm', 'dj', 'cr', 'rl', 'rc',
          'nsl', 'ngl', 'ttl', 'str', 'ns', 'ndl', 'cq', 'bbr', 'tr',
          'rtl', 'nsp', 'lv', 'lg', 'ffl', 'ckl', 'bb', 'rv', 'rs',
          'rn', 'rbl', 'rb', 'ps', 'nsw', 'nk', 'ndw', 'lph', 'gn',
          'dh', 'ddr', 'ckn', 'stl', 'sk', 'rtm', 'rp', 'ndm', 'gm',
          'ft', 'dl'],
    'ai': ['n', 'l', 'nt', 'r', 's', 'm', 't', 'nl'],
    'au': ['s', 't', 'th', 'd', 'st', 'nch', 'ght'],
    'e': ['r', 'l', 'm', 'c', 'nt', 'v', 'ct', 't', 's', 'n', 'ss',
          'd', 'f', 'nd', 'g', 'nc', 'st', 'rv', 'x', 'rs', 'rt', 'p',
          'ns', 'q', 'xp', 'rr', 'rm', 'sp', 'xpl', 'rl', 'pr', 'xc',
          'tt', 'rf', 'rn', 'll', 'str', 'rc', 'w', 'h', 'ntl', 'gr',
          'ng', 'b', 'pt', 'rpr', 'rg', 'mpl', 'mb', 'xt', 'cr',
          'xtr', 'tr', 'nl', 'ff', 'scr', 'th', 'sc', 'pl', 'ntr',
          'mbl', 'cl', 'nv', 'rst', 'mpt', 'j', 'ck', 'ch', 'xpr',
          'xcl', 'mp', 'ctr', 'xh', 'dl', 'dg', 'br', 'wr', 'nj',
          'lv', 'fl', 'chn', 'tw', 'ttl', 'tch', 'rb', 'nh', 'lc',
          'gl', 'fr', 'dd', 'ctl', 'xch', 'sh', 'rwh', 'rsh', 'ph',
          'nth', 'nf', 'ncl', 'wh', 'ssl', 'ssf', 'rp', 'rd', 'nn',
          'lt', 'lm'],
    'ea': ['s', 't', 'd', 'r', 'l', 'n', 'v', 'ch', 'k', 'th', 'g',
           'ct', 'rl', 'rch', 'p', 'ss', 'rr', 'dl', 'rn', 'm',
           'lth'],
    'eau': ['t'],
    'ee': ['d', 'm', 'r', 'p', 'z', 'dl', 'n', 'l', 'k'],
    'ei': ['v', 'nst'],
    'eo': ['r', 'l', 'v', 't', 'pl'],
    'eou': ['sl'],
    'ey': ['w', 'str', 'b'],
    'i': ['t', 'n', 'c', 'v', 's', 'd', 'm', 'l', 'f', 'nt', 'st',
          'r', 'g', 'nd', 'b', 'nc', 'nv', 'sh', 'bl', 'sc', 'ct',
          'll', 'tt', 'gn', 'p', 'ns', 'ss', 'nf', 'mp', 'ght', 'mpl',
          'ng', 'str', 'mpr', 'ck', 'nh', 'k', 'pp', 'nst', 'rr',
          'pl', 'ngl', 'ff', 'sg', 'rc', 'nn', 'z', 'sl', 'ncl', 'sr',
          'nsp', 'mm', 'dd', 'x', 'sf', 'nstr', 'tl', 'spl', 'sp',
          'scr', 'q', 'ntr', 'nj', 'nfl', 'ncr', 'gg', 'cl', 'thdr',
          'rt', 'nk', 'ft', 'dn', 'cr', 'sm', 'sd', 'pt', 'gr',
          'ghtl', 'ghl', 'ddl', 'xt', 'tn', 'tch', 'np', 'nct', 'nch',
          'lt', 'ghtn', 'dg', 'ch', 'br', 'zz', 'tm', 'th', 'sk',
          'shm', 'rm', 'nfr', 'ndl', 'mb', 'gnm', 'ckn', 'tr', 'stl',
          'ph', 'lm', 'gh', 'dl', 'bb'],
    'ia': ['t', 'll', 'bl', 'l', 's', 'r', 'gn', 'g', 'ngl', 'nc',
           'm', 'gr', 'b'],
    'ie': ['v', 'nc', 'nt', 'w', 't', 'ntl', 'wp', 'r', 'ndl', 'c'],
    'io': ['n', 'l', 'r', 's', 'nsh', 'gr', 'd'],
    'iou': ['sl'],
    'o': ['r', 'v', 'n', 'm', 'l', 't', 's', 'p', 'd', 'c', 'mp',
          'rt', 'ns', 'w', 'mm', 'nt', 'rr', 'll', 'g', 'rm', 'nd',
          'nc', 'nv', 'ntr', 'k', 'mpl', 'nf', 'pp', 'rd', 'b', 'th',
          'ff', 'nstr', 'ss', 'lv', 'pt', 'nn', 'ng', 'mpr', 'ck',
          'cc', 'st', 'rg', 'ld', 'bs', 'tt', 'ph', 'nst', 'gr', 'f',
          'rc', 'mb', 'wn', 'rk', 'rb', 'bl', 'rn', 'h', 'bj', 'x',
          'rw', 'wl', 'sp', 'rp', 'ncl', 'cr', 'bt', 'bsc', 'z', 'pr',
          'ppr', 'nsc', 'j', 'ws', 'stp', 'rth', 'nfr', 'nfl', 'mf',
          'gg', 'bstr', 'wd', 'rsh', 'rs', 'nm', 'lt', 'ggl', 'ffs',
          'bb', 'ttl', 'stl', 'sm', 'rch', 'pm', 'nsp', 'nl', 'nk',
          'nj', 'ngl', 'mpt', 'dg', 'ct', 'bbl'],
    'oa': ['d', 'dc', 'ch', 't', 'n'],
    'oe': ['v'],
    'oi': ['nt', 's', 'l', 'n', 'c', 't', 'ntm', 'd', 'ntl', 'nc'],
    'oo': ['k', 'd', 's', 'l', 'rd', 'tn', 'r', 'p', 'n', 'm'],
    'ou': ['nt', 'r', 'nd', 's', 'nc', 't', 'sl', 'tr', 'rc', 'bl',
           'tl', 'rn', 'rs', 'pl', 'ntr', 'ch', 'tw', 'ts', 'tp',
           'rt', 'p', 'ns', 'ld', 'ghl', 'd'],
    'oy': ['m'],
    'u': ['r', 'l', 't', 'n', 's', 'nd', 'm', 'ct', 'st', 'c', 'd',
          'lt', 'p', 'rr', 'll', 'ff', 'tt', 'str', 'gg', 'sp', 'pp',
          'nn', 'sh', 'nc', 'rs', 'nt', 'ns', 'nl', 'nct', 'cc', 'bl',
          'rv', 'rg', 'ck', 'bst', 'rn', 'pt', 'ppl', 'mm', 'nr',
          'nch', 'mp', 'mbl', 'ss', 'rd', 'nf', 'mb', 'ls', 'f', 'dg',
          'rpr', 'rch', 'ppr', 'pl', 'ddl', 'bm', 'bj', 'b', 'zzl',
          'rb', 'ps', 'pgr', 'pd', 'lg', 'ggl', 'btl', 'bs', 'rth',
          'rt', 'nh', 'mpt', 'g', 'dd', 'stm', 'rp', 'rk', 'rf', 'pr',
          'ncl', 'lf', 'br', 'bb'],
    'ua': ['t', 'll', 'l', 'r', 'd', 'bl', 'sh', 'nt', 'rt', 'rd',
           'g'],
    'ue': ['nc', 'st', 'ss', 'ntl', 'r', 'nt', 'l'],
    'uee': ['z'],
    'ui': ['t', 's', 'd', 'r', 'n', 'sh', 'ld', 'c', 'v', 'pp', 'ck'],
    'uie': ['t'],
    'uo': ['t'],
    'y': ['p', 'cl', 'st', 's', 'n', 'th', 't', 'm', 'l', 'ch', 'r',
          'nt', 'mp', 'mb', 'wh', 'mpt', 'mm', 'b'],
    'yo': ['n'],
    'you': ['rs', 'ng'],
    }
CONSONANT_VOWEL = {
    'b': ['i', 'u', 'e', 'o', 'a', 'y', 'ui', 'ou'],
    'bb': ['i', 'e'],
    'bbl': ['e'],
    'bbr': ['e'],
    'bj': ['e'],
    'bl': ['e', 'i', 'y'],
    'bm': ['i'],
    'bn': ['o'],
    'br': ['a'],
    'bs': ['e', 'o'],
    'bsc': ['u'],
    'bst': ['i', 'a'],
    'bstr': ['u'],
    'bt': ['ai'],
    'btl': ['e'],
    'c': ['a', 'e', 'i', 'o', 'u', 'ia', 'ie', 'y', 'iou', 'ei', 'ee',
          'ea', 'au'],
    'cc': ['u', 'e', 'o', 'ou', 'i', 'ee', 'a'],
    'ch': ['e', 'i', 'ie', 'o', 'a'],
    'chn': ['i'],
    'ck': ['e', 'i', 'y', 'o', 'a'],
    'ckl': ['e'],
    'ckn': ['o'],
    'cl': ['e', 'i', 'a'],
    'cq': ['ui'],
    'cr': ['o', 'i', 'e', 'ui', 'ea', 'a'],
    'ct': ['i', 'io', 'e', 'o', 'u', 'a', 'ua'],
    'ctl': ['y'],
    'ctr': ['o', 'i'],
    'd': ['e', 'i', 'u', 'a', 'y', 'o', 'ua', 'ie', 'io', 'ia', 'ea',
          'ay', 'iu', 'eo'],
    'dc': ['a'],
    'dd': ['i', 'e'],
    'ddl': ['e'],
    'ddr': ['e'],
    'dg': ['e'],
    'dh': ['e'],
    'dj': ['u'],
    'dl': ['y', 'e', 'i'],
    'dm': ['i'],
    'dn': ['a'],
    'dv': ['e', 'i', 'a', 'o'],
    'f': ['i', 'e', 'ie', 'u', 'y', 'yi', 'o', 'a', 'ea'],
    'ff': ['e', 'i', 'o'],
    'ffl': ['e'],
    'ffs': ['e'],
    'fl': ['e'],
    'fr': ['e'],
    'ft': ['e'],
    'g': ['e', 'i', 'a', 'o', 'y', 'u', 'ue', 'io', 'ui', 'ai'],
    'gg': ['e', 'i'],
    'ggl': ['e'],
    'gh': ['e'],
    'ghl': ['i', 'y'],
    'ght': ['e', 'i'],
    'ghtl': ['y'],
    'ghtn': ['i'],
    'gl': ['e'],
    'gm': ['e', 'a'],
    'gn': ['i', 'e', 'a', 'o'],
    'gnm': ['e'],
    'gr': ['a', 'ee', 'e'],
    'h': ['o', 'i', 'e', 'a'],
    'j': ['e', 'u'],
    'k': ['e', 'i'],
    'l': ['e', 'i', 'a', 'y', 'o', 'u', 'ie', 'ia', 'ua', 'ou', 'ea',
          'ue', 'ay'],
    'lc': ['u', 'o'],
    'ld': ['e', 'i'],
    'lf': ['i'],
    'lg': ['e'],
    'll': ['y', 'e', 'o', 'i', 'a', 'u', 'io', 'ie', 'ia'],
    'lm': ['e'],
    'lph': ['a'],
    'ls': ['e'],
    'lt': ['e', 'i', 'a', 'y', 'u', 'ie'],
    'lth': ['y'],
    'lv': ['e', 'i'],
    'm': ['e', 'i', 'a', 'o', 'u', 'ou', 'ai', 'y'],
    'mb': ['e', 'i', 'a', 'o'],
    'mbl': ['e', 'i'],
    'mf': ['o'],
    'mm': ['e', 'i', 'u', 'a', 'o'],
    'mp': ['e', 'a', 'o', 'i', 'u', 'ai'],
    'mpl': ['e', 'i', 'ai', 'a', 'oye', 'oy', 'y'],
    'mpr': ['e', 'o', 'i'],
    'mpt': ['io', 'i', 'e'],
    'n': ['e', 'a', 'i', 'o', 'y', 'u', 'ie', 'ue', 'io', 'ua', 'ou',
          'eou', 'ui', 'ee', 'ea'],
    'nc': ['e', 'o', 'i', 'y', 'a', 'ou', 'u', 'ie', 'ei', 'ea',
           'ia'],
    'nch': ['e', 'i'],
    'ncl': ['u', 'i', 'o'],
    'ncr': ['ea', 'e'],
    'nct': ['io'],
    'nd': ['e', 'i', 'a', 'u', 'o', 'ou'],
    'ndl': ['e', 'y'],
    'ndm': ['e'],
    'ndw': ['i'],
    'nf': ['i', 'o', 'e', 'u', 'a'],
    'nfl': ['ue', 'i'],
    'nfr': ['o', 'a'],
    'ng': ['e', 'i', 'ui', 'a', 'u'],
    'ngl': ['y', 'e'],
    'nh': ['a', 'e', 'i'],
    'nj': ['u', 'oy'],
    'nk': ['i', 'e'],
    'nl': ['y', 'i', 'o', 'a'],
    'nm': ['e'],
    'nn': ['e', 'i', 'o', 'ou', 'y', 'ie'],
    'np': ['u'],
    'nr': ['ea', 'e'],
    'ns': ['i', 'e', 'u', 'o', 'io', 'a'],
    'nsc': ['iou'],
    'nsf': ['o', 'e'],
    'nsh': ['i'],
    'nsl': ['a'],
    'nsm': ['i'],
    'nsp': ['i', 'e', 'o'],
    'nst': ['a', 'i'],
    'nstr': ['u', 'ai', 'a'],
    'nsw': ['e'],
    'nt': ['e', 'i', 'a', 'io', 'ai', 'ia', 'u', 'ee', 'y', 'o',
           'ou'],
    'nth': ['e'],
    'ntl': ['y', 'e'],
    'ntm': ['e'],
    'ntr': ['a', 'i', 'o', 'y'],
    'nv': ['e', 'i', 'o', 'a'],
    'p': ['e', 'a', 'o', 'i', 'u', 'ie', 'ea', 'y', 'ai'],
    'pd': ['a'],
    'pgr': ['a'],
    'ph': ['i', 'e', 'y', 'o'],
    'pl': ['e', 'i', 'a', 'y', 'ie'],
    'pm': ['e'],
    'pp': ['e', 'i', 'o', 'ea', 'oi', 'a', 'y'],
    'ppl': ['ie', 'i', 'e'],
    'ppr': ['e', 'o', 'oa'],
    'pr': ['e', 'o', 'i', 'ia'],
    'ps': ['e'],
    'pt': ['io', 'i', 'e', 'u', 'a'],
    'q': ['ue', 'ui', 'ua'],
    'r': ['e', 'a', 'i', 'y', 'ie', 'ia', 'o', 'ou', 'io', 'iou',
          'ea', 'eo', 'u', 'ei'],
    'rb': ['i', 'a'],
    'rbl': ['e'],
    'rc': ['e', 'u', 'i', 'a', 'ei', 'ui', 'o'],
    'rch': ['i', 'e', 'a'],
    'rd': ['e', 'i'],
    'rf': ['e', 'o', 'a', 'u'],
    'rg': ['e', 'i', 'o', 'a', 'ue'],
    'rk': ['e', 'i', 'a'],
    'rl': ['y', 'i', 'oo', 'oa', 'ie'],
    'rm': ['i', 'a', 'e', 'o'],
    'rn': ['a', 'i', 'e', 'ey'],
    'rp': ['o', 'e'],
    'rpr': ['e', 'i'],
    'rr': ['e', 'i', 'o', 'a', 'u', 'ie', 'y', 'ou', 'yi'],
    'rs': ['e', 'o', 'i', 'a', 'ua', 'io', 'ue'],
    'rsh': ['i'],
    'rst': ['a'],
    'rt': ['i', 'e', 'a', 'ai', 'u', 'io', 'y', 'o', 'oo', 'ie',
           'ia'],
    'rth': ['e'],
    'rtl': ['e'],
    'rtm': ['e'],
    'rv': ['e', 'i', 'a', 'ie'],
    'rw': ['a'],
    'rwh': ['e'],
    's': ['e', 'i', 'o', 'a', 'u', 'io', 'y', 'ua', 'ea', 'ou', 'ie'],
    'sc': ['o', 'e', 'a', 'i', 'u', 'ou'],
    'scr': ['i', 'e'],
    'sd': ['i'],
    'sf': ['a'],
    'sg': ['ui', 'u'],
    'sh': ['e', 'i', 'io', 'o'],
    'shm': ['e'],
    'sk': ['e'],
    'sl': ['y', 'i', 'ea', 'a'],
    'sm': ['i', 'a'],
    'sp': ['e', 'o', 'i'],
    'spl': ['a'],
    'sr': ['e', 'ea'],
    'ss': ['e', 'i', 'io', 'o', 'u', 'a', 'y', 'ue'],
    'ssf': ['u'],
    'ssl': ['y'],
    'ssw': ['o'],
    'st': ['i', 'e', 'a', 'o', 'io', 'y', 'u', 'ai'],
    'stl': ['y', 'e'],
    'stm': ['e'],
    'stp': ['o'],
    'str': ['a', 'i', 'o', 'e', 'ai', 'y', 'u', 'ia'],
    't': ['e', 'io', 'i', 'y', 'a', 'o', 'u', 'ie', 'ia', 'ua', 'ai',
          'ue'],
    'tch': ['e', 'i'],
    'th': ['e', 'i', 'o', 'ei', 'y'],
    'thdr': ['a'],
    'tl': ['y', 'i', 'e'],
    'tm': ['e', 'o'],
    'tn': ['e', 'o'],
    'tp': ['u'],
    'tr': ['a', 'y', 'o', 'ie', 'i'],
    'ts': ['e'],
    'tt': ['e', 'i', 'a', 'o', 'y', 'ee'],
    'ttl': ['e', 'i'],
    'ttr': ['a', 'i'],
    'tw': ['o', 'ei'],
    'v': ['e', 'i', 'a', 'o', 'ia', 'ie', 'oi', 'ea', 'ai', 'iou'],
    'w': ['e', 'i', 'a', 'ay', 'o', 'ai', 'ye'],
    'wb': ['a'],
    'wc': ['o'],
    'wd': ['e'],
    'wf': ['u'],
    'wh': ['e'],
    'wl': ['e', 'y'],
    'wn': ['e', 'i'],
    'wp': ['oi'],
    'wr': ['i'],
    'ws': ['e'],
    'wsl': ['e'],
    'wsp': ['a'],
    'x': ['i', 'e', 'a', 'ua', 'y', 'io'],
    'xc': ['e', 'i', 'ee', 'u'],
    'xch': ['a'],
    'xcl': ['u'],
    'xh': ['au', 'i'],
    'xp': ['e', 'o', 'i', 'a', 'aye'],
    'xpl': ['o', 'oi', 'ai', 'a', 'i'],
    'xpr': ['e'],
    'xt': ['e'],
    'xtb': ['oo'],
    'xtr': ['a', 'e'],
    'z': ['e', 'i', 'o', 'a', 'y'],
    'zz': ['y', 'a'],
    'zzl': ['e'],
    }
VOWEL_END = {
    'a': ['l', 'nt', 'r', '', 'n', 'ls', 'rd', 'nd', 'ck', 't', 'nts',
          'll', 'ct', 'rds', 'p', 'sh', 's', 'nds', 'cks', 'st', 'ss',
          'ps', 'ns', 'm', 'rt', 'rs', 'rk', 'nk', 'lls', 'g', 'cts',
          'w', 'ng', 'mp', 'd', 'tch', 'rts', 'rm', 'ts', 'sts',
          'nks', 'ws', 'wn', 'rms', 'rks', 'mps', 'ft', 'x', 'th',
          'sk', 'rch', 'phs', 'ph', 'ms', 'lk', 'gs', 'ch', 'bs', 'b',
          'ths', 'sp', 'sks', 'rp', 'pt', 'lt', 'lks', 'lf'],
    'ai': ['n', 'ns', 'l', 'r', 'rs', 'ls', 'd', 'nt', 'm', 'nts',
           'ts', 't', 'ms', 'ds', 'c'],
    'au': ['lt', 'lts', 'ght', 'd'],
    'ay': ['', 's'],
    'aye': ['d', 'rs', 'r'],
    'ayi': ['ng'],
    'e': ['', 'd', 's', 'r', 'nt', 'rs', 'n', 'st', 'ss', 't', 'nts',
          'ct', 'cts', 'ts', 'nd', 'nds', 'l', 'ns', 'ls', 'w', 'rt',
          'll', 'rts', 'sts', 'rn', 'lf', 'm', 'lls', 'pt', 'ms',
          'ds', 'x', 'ws', 'mpt', 'xt', 'tch', 'sh', 'rns', 'pts',
          'lt', 'ck', 'xts', 'rb', 'nth', 'ngth', 'nch', 'mpts', 'g',
          'ft', 'sk', 'rr', 'rms', 'rm', 'rk', 'rd', 'rbs', 'pths',
          'pth', 'ps', 'p', 'ngths', 'mns', 'mn', 'lps', 'lp', 'lms',
          'lm'],
    'ea': ['r', 'd', 't', 'rs', 'ts', 'l', 'ds', 'm', 'ls', 'k', 'ch',
           'ns', 'n', '', 'ks', 'th', 's', 'ms', 'st', 'p', 'rns',
           'rn', 'rd', 'rch', 'lth', 'f', 'ths', 'sts', 'rts', 'rth',
           'rt', 'rds', 'nt', 'lt', 'lms', 'lm', 'cts', 'ct'],
    'ee': ['d', '', 'n', 's', 'r', 'p', 'ds', 'rs', 't', 'l', 'ts',
           'ps', 'ls', 'k', 'ms', 'm', 'ks', 'th', 'ns', 'f', 'ch'],
    'eei': ['ng'],
    'ei': ['n', 'ght', 'gn', 'gh', 't', 'sts', 'st', 'sm', 'rs', 'rd',
           'r', 'pt', 'ngs', 'ng', 'ghts', 'ghth', 'ghs'],
    'eo': ['', 'n', 'f'],
    'eou': ['s'],
    'eu': ['r', 'ms', 'm'],
    'ey': ['', 's'],
    'eye': ['d', 's', ''],
    'eyi': ['ng'],
    'eyo': ['nd'],
    'i': ['ng', 'c', 't', 'st', 'ngs', 'ts', 'p', 'ght', 'd', 'cs',
          'n', 'sts', 'sh', 's', 'ps', 'll', 'nd', 'ct', 'ck', 'm',
          'l', 'x', 'sm', 'ns', 'nk', 'nds', 'lls', 'ghts', 'cts',
          'cks', 'nt', 'gns', 'gn', 'tch', 'ss', 'nks', 'g', 'ft',
          'ds', '', 'sk', 'rt', 'pt', 'nts', 'ls', 'ld', 'fts', 'ff',
          'ch', 'th', 'sp', 'sms', 'sks', 'rst', 'rms', 'rm', 'rd',
          'r', 'nct', 'nch', 'ms', 'mbs', 'mb', 'gs', 'gh', 'dth',
          'xth', 'thms', 'thm', 'sps', 'scs', 'sc', 'rth', 'rs',
          'rls', 'rl', 'rds', 'pts', 'lst', 'lms', 'lm', 'lk', 'fth',
          'f'],
    'ia': ['l', 'n', '', 'ns', 'ls', 'r', 'nt', 's', 'sm', 'nts'],
    'ie': ['s', 'd', 'r', 'nt', 'st', '', 'f', 'w', 'rs', 'nts', 'ws',
           'nd', 'th', 't', 'sts', 'ns', 'nds', 'n', 'lds', 'ld',
           'fs'],
    'io': ['n', 'ns', 'r', '', 's', 't', 'm', 'ts', 'ms', 'ds', 'd'],
    'iou': ['s'],
    'iu': ['m', 's', 'ms', 'mph'],
    'o': ['r', 'n', '', 'w', 'rs', 't', 'ws', 'wn', 'rt', 'ns', 'm',
          'rts', 'p', 'rm', 'rd', 'ld', 'ck', 'ps', 'ng', 'cks', 'ts',
          'g', 'st', 'rn', 'rms', 'ss', 'rk', 'rds', 's', 'nd', 'l',
          'd', 'x', 'wns', 'rth', 'nt', 'ngs', 'ms', 'll', 'gs', 'b',
          'sts', 'rks', 'nds', 'ls', 'lls', 'th', 'pts', 'pt', 'nts',
          'lt', 'lf', 'lds', 'ds', 'bs', 'wth', 'wl', 'wds', 'wd',
          'tch', 'rst', 'rlds', 'rld', 'rbs', 'rb', 'nths', 'nth',
          'ngst', 'mpts', 'mpt', 'mbs', 'mb', 'lts', 'lks', 'lk', 'h',
          'ft', 'ff', 'f', 'dds', 'dd', 'c'],
    'oa': ['d', 't', 'rd', 'ts', 'ds', 'n', 'st', 'rds', 'ns', 'l',
           'ch', 'r', 'p', 'm', 'ls'],
    'oe': ['s', '', 'ts', 't', 'ms', 'm', 'd'],
    'oi': ['ng', 'nt', 'nts', 'l', 'd', 'n', 'ns', 'ls', 'ts', 't',
           'r', 'ds', 'c'],
    'oia': [''],
    'oo': ['k', 'd', 'm', 'l', 'ks', 'n', 't', 'ls', 'ds', 'ts', 'r',
           'ps', 'p', 'ns', 'f', 'th', 'rs', 'ms', '', 'st', 'fs'],
    'ou': ['s', 'nd', 't', 'nds', 'gh', 'r', 'ght', 'nts', 'nt', 'ts',
           'd', 'rs', 'ld', 'th', 'p', 'n', 'l', 'ch', 'rts', 'rth',
           'rt', 'ps', 'ns', 'ls', 'ghts', 'ds', 'bts', 'bt', ''],
    'oy': ['', 's'],
    'oya': ['l'],
    'oye': ['d', 'rs', 'r'],
    'oyee': ['s', ''],
    'oyi': ['ng'],
    'u': ['l', 's', 'm', 't', 'st', 'ts', 'n', 'ck', 'g', 'sh', 'lt',
          'll', 'r', 'ns', 'nk', 'ng', 'mp', 'gs', 'cts', 'ct', 'cks',
          'sts', 'pt', 'nch', 'ms', 'mps', 'lts', 'ss', 'rns', 'rn',
          'nt', 'mb', 'b', 'rs', 'rb', 'pts', 'ps', 'p', 'nts', 'nks',
          'nd', 'mn', 'ff', 'ch', 'tts', 'tt', 'ths', 'th', 'rts',
          'rt', 'rsts', 'rst', 'rnt', 'rks', 'rk', 'rd', 'rch', 'rbs',
          'ngs', 'nds', 'mns', 'lp', 'lls', 'lk', 'lf', 'lbs', 'lb',
          'h', 'gh', 'ffs', 'd', 'bs', ''],
    'ua': ['l', 'ls', 'rds', 'rd', 'sh', 'd'],
    'ue': ['', 's', 'd', 'nt', 'st', 'l', 'sts', 'ss', 'nts'],
    'uee': ['ns', 'n'],
    'ueue': ['s', 'd', ''],
    'ui': ['ng', 't', 'ts', 'lt', 'sh', 'n', 'lds', 'ld', 'd', 'z',
           'ps', 'p', 'ns', 'ck'],
    'uie': ['t'],
    'uo': ['r'],
    'uou': ['s'],
    'uu': ['m'],
    'uy': ['s', ''],
    'uye': ['rs', 'r'],
    'uyi': ['ng'],
    'y': ['', 'ms', 'm', 'ths', 'thm', 'th', 'st', 'l'],
    'ya': ['wn', 'rds', 'rd'],
    'ye': ['', 't', 's', 'rs', 'r'],
    'yea': ['rs', 'r'],
    'yi': ['ng'],
    'yie': ['lds', 'ld'],
    'you': ['th', 'rs', 'r', 'ng', ''],
    }

if __name__ == '__main__':
    main()
