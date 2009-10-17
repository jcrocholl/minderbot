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
'bringly'
>>> generate_password(digits=2)
'knoways23'

Known problems:
1. The algorithm may generate words that appear in an English dictionary.
2. The algorithm may generate profanities. To work around these problems,
   check the output against a word list and try again if necessary.
3. Without digits, the current version can generate only 67937
   different passwords. Adding digits is highly recommended, because
   it increases the search space for brute force attacks.

If you run this script on the command line without arguments, it will
generate 100 random passwords for you:

$ python english_passwords.py
thuplempt       phrannils       bringly         cembicts        splimpar
phrarcel        triallalk       grartic         squalian        kimpriss
dountits        traked          guident         scassion        kneepuct
juptens         psynug          lansmild        suinems         fountyms
twersess        upproms         deeduals        cheemiff        pratchics
spreactact      splinarks       vokist          trunyms         splinteels
cruidath        mestrams        crappeat        knoways         greemonds
juddlews        glasyms         gernict         tythepts        rhynoun
quotyms         cranucts        glomed          lialals         smenlym
jantly          criscucts       wrammups        gairich         psynym
plunchers       rourcals        slaloll         clupprend       nadvel
skiliers        squarious       phrantly        spevoss         ruiril
caket           spempath        skinnic         swormill        tovia
plandletch      zentask         piffelf         crollork        noublyms
zethept         breerym         sleerom         prebraphs       shobjer
claphin         gollub          glealawn        phobsends       pheprerns
steemas         mepigns         sneatack        choodyms        choodyms
quidants        bentront        waisa           swinfews        twentlyms
gristect        nudgex          wrownews        speeriers       whangign
slaxind         scredly         snostoss        drackigns       keemint

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
        word = '^' + word.strip() + '$'
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
    print "DIGITS = '%s' # Avoid confusing 0 and 1 with O ind I." % DIGITS
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


# This version can generate 67937 different passwords.
DIGITS = '23456789' # Avoid confusing 0 and 1 with O and I.
VOWELS = 'aeiouy' # To split words into groups of letters.
START_VOWEL = {
    '': ['a', 'i', 'e', 'o', 'u', 'ou', 'ea', 'au', 'ai', 'ei'],
    'b': ['a', 'e', 'u', 'o', 'i', 'ea', 'oo', 'ou', 'io', 'ui', 'y',
          'oi', 'ia', 'ee'],
    'bl': ['a', 'o', 'e', 'i'],
    'br': ['i', 'a', 'ea', 'o', 'ee'],
    'c': ['o', 'a', 'u', 'ou', 'i', 'e', 'oo', 'y', 'au', 'oi', 'ea'],
    'ch': ['a', 'e', 'o', 'u', 'i', 'ea', 'ee', 'ai', 'oo', 'oi'],
    'cl': ['a', 'o', 'ea', 'i', 'u', 'ai', 'e'],
    'cr': ['a', 'i', 'o', 'u', 'ea', 'e', 'y', 'ui'],
    'd': ['e', 'i', 'o', 'a', 'u', 'ea', 'ia', 'ee', 'ou', 'oo', 'ie',
          'y'],
    'dr': ['a', 'i', 'o', 'ea', 'u', 'e', 'ai'],
    'f': ['i', 'o', 'a', 'u', 'e', 'ai', 'ou', 'ee', 'oo', 'ea', 'au',
          'ie'],
    'fl': ['a', 'u', 'o', 'oo', 'i', 'e', 'ie'],
    'fr': ['a', 'o', 'ee', 'i', 'ie', 'e', 'u', 'ui', 'ea'],
    'g': ['e', 'a', 'o', 'i', 'ui', 'ua', 'u', 'ue', 'oo', 'eo', 'ea',
          'ai'],
    'gl': ['o', 'a', 'ea'],
    'gr': ['a', 'o', 'i', 'ou', 'ea', 'ee'],
    'h': ['a', 'o', 'i', 'e', 'ea', 'u', 'y', 'ou', 'ai', 'oo', 'ie',
          'ei', 'ee'],
    'j': ['u', 'a', 'oi', 'o', 'ou', 'e', 'ea'],
    'k': ['i', 'ee', 'e'],
    'kn': ['o', 'i', 'ee'],
    'l': ['i', 'o', 'a', 'e', 'ea', 'u', 'oo', 'au', 'ou', 'ie', 'y',
          'ia', 'ai'],
    'm': ['a', 'i', 'o', 'e', 'u', 'ea', 'ai', 'y', 'ou', 'ee', 'oo'],
    'n': ['o', 'e', 'a', 'u', 'i', 'ee', 'ea', 'ai', 'oi', 'ou'],
    'p': ['a', 'o', 'e', 'u', 'i', 'ai', 'oi', 'ea', 'ou', 'oo', 'au',
          'ie', 'eo', 'ee'],
    'ph': ['o', 'y', 'a', 'i', 'e'],
    'phr': ['a'],
    'pl': ['a', 'ea', 'u', 'o', 'ai'],
    'pr': ['o', 'e', 'i', 'a', 'ea', 'io', 'oo', 'ie'],
    'ps': ['y'],
    'q': ['ua', 'ui', 'ue', 'uo'],
    'r': ['e', 'a', 'ea', 'i', 'o', 'u', 'ou', 'ai', 'ei', 'oo',
          'ui'],
    'rh': ['y'],
    's': ['u', 'e', 'i', 'a', 'o', 'y', 'ou', 'ee', 'ea', 'ui', 'ai',
          'ue', 'oo'],
    'sc': ['a', 'o', 'ie', 'e'],
    'sch': ['e', 'oo', 'o'],
    'scr': ['a', 'o', 'ea', 'e', 'i', 'ee'],
    'sh': ['o', 'a', 'i', 'e', 'ou', 'u', 'oo', 'ee'],
    'sk': ['i', 'e'],
    'sl': ['i', 'o', 'a', 'ee'],
    'sm': ['a', 'o', 'i', 'e', 'oo'],
    'sn': ['ea', 'o', 'a'],
    'sp': ['e', 'o', 'i', 'a', 'ee', 'ea', 'oi', 'u', 'oo'],
    'spl': ['i'],
    'spr': ['i', 'ea'],
    'sq': ['ua'],
    'st': ['a', 'u', 'o', 'i', 'e', 'ee', 'ea', 'ai', 'y'],
    'str': ['i', 'u', 'e', 'a', 'o', 'ai', 'ee', 'ea'],
    'sw': ['a', 'i', 'ea', 'ee', 'o'],
    't': ['e', 'a', 'o', 'i', 'u', 'ea', 'y', 'ou', 'ai', 'oo', 'ee',
          'ie', 'oi'],
    'th': ['e', 'i', 'eo', 'a', 'ou', 'o', 'ie', 'u', 'ei'],
    'thr': ['ea', 'o', 'u', 'ou', 'e'],
    'tr': ['a', 'i', 'u', 'ea', 'ai', 'e', 'ou', 'ia', 'oo', 'ie',
           'ee'],
    'tw': ['i', 'e'],
    'v': ['a', 'e', 'i', 'o', 'ie', 'io', 'oi', 'ia'],
    'w': ['i', 'a', 'o', 'e', 'ea', 'ee', 'ai', 'oo', 'ei', 'ou'],
    'wh': ['i', 'e', 'o', 'a', 'oo', 'ee'],
    'wr': ['i', 'e', 'a', 'o'],
    'z': ['o', 'e'],
    }
VOWEL_CONSONANT = {
    'a': ['t', 'r', 'll', 'g', 'n', 'bl', 'l', 'm', 'd', 'ss', 'c',
          'nc', 'ct', 'cc', 'pp', 'b', 'rr', 's', 'st', 'ng', 'v',
          'k', 'tt', 'nt', 'nd', 'dv', 'rt', 'p', 'ck', 'rg', 'nn',
          'sh', 'th', 'w', 'ppr', 'rd', 'dd', 'rk', 'z', 'lt', 'gr',
          'dm', 'ch', 'tch', 'rm', 'mp', 'gg', 'ff', 'x', 'ppl',
          'ttr', 'pt', 'ph', 'lc', 'sc', 'rch', 'mpl', 'mb', 'f',
          'bs', 'ntl', 'nsm', 'mm', 'cr', 'rl', 'rc', 'nsl', 'ngl',
          'ttl', 'str', 'ns', 'ndl'],
    'ai': ['n', 'l', 'nt', 'r', 's'],
    'au': ['s', 't'],
    'e': ['r', 'l', 'm', 'c', 'nt', 'v', 'ct', 't', 's', 'n', 'ss',
          'd', 'f', 'nd', 'g', 'nc', 'st', 'rv', 'x', 'rs', 'rt', 'p',
          'ns', 'q', 'xp', 'rr', 'rm', 'sp', 'xpl', 'rl', 'pr', 'xc',
          'tt', 'rf', 'rn', 'll', 'str', 'rc', 'w', 'h', 'ntl', 'gr',
          'ng', 'b', 'pt', 'rpr', 'rg', 'mpl', 'mb', 'xt', 'cr',
          'xtr', 'tr', 'nl', 'ff', 'scr', 'th', 'sc', 'pl', 'ntr',
          'mbl', 'cl', 'nv', 'rst', 'j', 'ck', 'ch', 'xpr', 'xcl',
          'mp', 'dl', 'dg', 'br', 'nj', 'lv', 'fl'],
    'ea': ['s', 't', 'd', 'r', 'l', 'n', 'v', 'ch', 'k', 'th', 'g',
           'ct'],
    'ee': ['d', 'm', 'r', 'p'],
    'ei': ['v'],
    'eo': ['r'],
    'i': ['t', 'n', 'c', 'v', 's', 'd', 'm', 'l', 'f', 'nt', 'st',
          'r', 'g', 'nd', 'b', 'nc', 'nv', 'sh', 'bl', 'sc', 'ct',
          'll', 'tt', 'gn', 'p', 'ns', 'ss', 'nf', 'mp', 'ght', 'mpl',
          'ng', 'str', 'mpr', 'ck', 'nh', 'k', 'pp', 'nst', 'rr',
          'pl', 'ngl', 'ff', 'sg', 'rc', 'nn', 'z', 'sl', 'ncl',
          'nsp', 'mm', 'dd', 'x', 'nstr', 'tl', 'sp', 'scr', 'q',
          'ntr', 'nj', 'gg', 'cl', 'rt', 'ft', 'cr'],
    'ia': ['t', 'll', 'bl', 'l'],
    'ie': ['v', 'nc', 'nt', 'w'],
    'io': ['n', 'l'],
    'iou': ['sl'],
    'o': ['r', 'v', 'n', 'm', 'l', 't', 's', 'p', 'd', 'c', 'mp',
          'rt', 'ns', 'w', 'mm', 'nt', 'rr', 'll', 'g', 'rm', 'nd',
          'nc', 'nv', 'ntr', 'k', 'mpl', 'nf', 'pp', 'rd', 'b', 'th',
          'ff', 'nstr', 'ss', 'lv', 'pt', 'nn', 'ng', 'mpr', 'ck',
          'cc', 'st', 'rg', 'ld', 'bs', 'tt', 'ph', 'nst', 'gr', 'f',
          'rc', 'mb', 'wn', 'rk', 'rb', 'bl', 'rn', 'h', 'bj', 'x',
          'wl', 'sp', 'rp', 'ncl', 'cr'],
    'oi': ['nt', 's'],
    'oo': ['k', 'd'],
    'ou': ['nt', 'r', 'nd', 's', 'nc', 't', 'sl', 'tr', 'rc', 'bl'],
    'u': ['r', 'l', 't', 'n', 's', 'nd', 'm', 'ct', 'st', 'c', 'd',
          'lt', 'p', 'rr', 'll', 'ff', 'tt', 'str', 'gg', 'sp', 'pp',
          'nn', 'sh', 'nc', 'rs', 'nt', 'ns', 'nl', 'nct', 'cc', 'bl',
          'rv', 'rg', 'ck', 'rn', 'pt', 'ppl', 'mm', 'nch', 'mp',
          'mbl', 'ss', 'rd', 'nf', 'mb', 'f', 'dg', 'rpr', 'rch',
          'ppr', 'pl', 'ddl', 'bj', 'b'],
    'ua': ['t', 'll', 'l', 'r'],
    'ue': ['nc', 'st'],
    'ui': ['t', 's', 'd', 'r', 'n'],
    'uo': ['t'],
    'y': ['p', 'cl', 'st', 's', 'n', 'th'],
    }
CONSONANT_VOWEL = {
    'b': ['i', 'u', 'e', 'o', 'a', 'y'],
    'bj': ['e'],
    'bl': ['e', 'i', 'y'],
    'br': ['a'],
    'bs': ['e', 'o'],
    'c': ['a', 'e', 'i', 'o', 'u', 'ia', 'ie', 'y', 'iou'],
    'cc': ['u', 'e', 'o'],
    'ch': ['e', 'i'],
    'ck': ['e', 'i'],
    'cl': ['e', 'i'],
    'cr': ['o', 'i'],
    'ct': ['i', 'io', 'e', 'o', 'u', 'a', 'ua'],
    'ctl': ['y'],
    'd': ['e', 'i', 'u', 'a', 'y', 'o', 'ua', 'ie', 'io'],
    'dd': ['i', 'e'],
    'ddl': ['e'],
    'dg': ['e'],
    'dl': ['y'],
    'dm': ['i'],
    'dv': ['e', 'i', 'a'],
    'f': ['i', 'e', 'ie', 'u', 'y', 'yi', 'o', 'a'],
    'ff': ['e', 'i'],
    'fl': ['e'],
    'ft': ['e'],
    'g': ['e', 'i', 'a', 'o', 'y', 'u', 'ue'],
    'gg': ['e', 'i'],
    'ght': ['e'],
    'gn': ['i', 'e', 'a', 'o'],
    'gr': ['a', 'ee', 'e'],
    'h': ['o', 'i', 'e'],
    'j': ['e'],
    'k': ['e', 'i'],
    'l': ['e', 'i', 'a', 'y', 'o', 'u', 'ie', 'ia', 'ua'],
    'lc': ['u', 'o'],
    'ld': ['e'],
    'll': ['y', 'e', 'o', 'i', 'a', 'u'],
    'lt': ['e', 'i', 'a', 'y'],
    'lv': ['e'],
    'm': ['e', 'i', 'a', 'o', 'u'],
    'mb': ['e', 'i', 'a'],
    'mbl': ['e'],
    'mm': ['e', 'i', 'u', 'a', 'o'],
    'mp': ['e', 'a', 'o', 'i', 'u', 'ai'],
    'mpl': ['e', 'i'],
    'mpr': ['e', 'o', 'i'],
    'n': ['e', 'a', 'i', 'o', 'y', 'u', 'ie', 'ue', 'io', 'ua', 'ou',
          'eou'],
    'nc': ['e', 'o', 'i', 'y', 'a', 'ou'],
    'nch': ['e'],
    'ncl': ['u'],
    'nct': ['io'],
    'nd': ['e', 'i', 'a', 'u', 'o'],
    'ndl': ['e'],
    'nf': ['i', 'o', 'e', 'u'],
    'ng': ['e', 'i', 'ui'],
    'ngl': ['y', 'e'],
    'nh': ['a', 'e'],
    'nj': ['u'],
    'nl': ['y', 'i'],
    'nn': ['e', 'i', 'o'],
    'ns': ['i', 'e', 'u', 'o', 'io', 'a'],
    'nsl': ['a'],
    'nsm': ['i'],
    'nsp': ['i'],
    'nst': ['a', 'i'],
    'nstr': ['u', 'ai'],
    'nt': ['e', 'i', 'a', 'io', 'ai', 'ia', 'u', 'ee', 'y'],
    'ntl': ['y'],
    'ntr': ['a', 'i', 'o'],
    'nv': ['e', 'i', 'o', 'a'],
    'p': ['e', 'a', 'o', 'i', 'u', 'ie', 'ea'],
    'ph': ['i', 'e'],
    'pl': ['e', 'i', 'a'],
    'pp': ['e', 'i', 'o', 'ea', 'oi', 'a'],
    'ppl': ['ie'],
    'ppr': ['e', 'o'],
    'pr': ['e', 'o'],
    'ps': ['e'],
    'pt': ['io', 'i', 'e'],
    'q': ['ue', 'ui', 'ua'],
    'r': ['e', 'a', 'i', 'y', 'ie', 'ia', 'o', 'ou', 'io', 'iou',
          'ea'],
    'rb': ['i', 'a'],
    'rc': ['e', 'u', 'i', 'a'],
    'rch': ['i', 'e'],
    'rd': ['e', 'i'],
    'rf': ['e', 'o', 'a'],
    'rg': ['e', 'i', 'o'],
    'rk': ['e', 'i'],
    'rl': ['y', 'i'],
    'rm': ['i', 'a', 'e'],
    'rn': ['a', 'i', 'e'],
    'rp': ['o'],
    'rpr': ['e', 'i'],
    'rr': ['e', 'i', 'o', 'a', 'u', 'ie', 'y'],
    'rs': ['e', 'o', 'i', 'a'],
    'rsh': ['i'],
    'rst': ['a'],
    'rt': ['i', 'e', 'a', 'ai', 'u', 'io', 'y'],
    'rth': ['e'],
    'rv': ['e', 'i', 'a'],
    's': ['e', 'i', 'o', 'a', 'u', 'io', 'y', 'ua'],
    'sc': ['o', 'e', 'a', 'i', 'u', 'ou'],
    'scr': ['i'],
    'sg': ['ui'],
    'sh': ['e', 'i'],
    'sl': ['y'],
    'sp': ['e', 'o', 'i'],
    'ss': ['e', 'i', 'io', 'o', 'u', 'a'],
    'st': ['i', 'e', 'a', 'o', 'io', 'y', 'u'],
    'stl': ['y'],
    'str': ['a', 'i', 'o'],
    't': ['e', 'io', 'i', 'y', 'a', 'o', 'u', 'ie', 'ia', 'ua', 'ai'],
    'tch': ['e', 'i'],
    'th': ['e', 'i', 'o'],
    'tl': ['y'],
    'tr': ['a'],
    'tt': ['e', 'i', 'a', 'o'],
    'ttl': ['e'],
    'ttr': ['a'],
    'v': ['e', 'i', 'a', 'o', 'ia', 'ie', 'oi'],
    'w': ['e', 'i', 'a', 'ay'],
    'wl': ['e'],
    'wn': ['e'],
    'x': ['i', 'e', 'a', 'ua'],
    'xc': ['e'],
    'xcl': ['u'],
    'xp': ['e', 'o'],
    'xpl': ['o'],
    'xpr': ['e'],
    'xt': ['e'],
    'xtr': ['a'],
    'z': ['e', 'i'],
    }
VOWEL_END = {
    'a': ['l', 'nt', 'r', '', 'n', 'ls', 'rd', 'nd', 'ck', 't', 'nts',
          'll', 'ct', 'rds', 'p', 'sh', 's', 'nds', 'cks', 'st', 'ss',
          'ps', 'ns', 'm', 'rt', 'rs', 'rk', 'nk', 'lls', 'g', 'cts',
          'w', 'ng', 'mp', 'd', 'tch', 'rts', 'rm', 'ts', 'sts',
          'nks', 'ws', 'wn', 'rms', 'rks', 'mps', 'ft', 'x', 'th',
          'sk', 'rch', 'phs', 'ph', 'ms', 'lk', 'gs', 'ch', 'bs',
          'b'],
    'ai': ['n', 'ns', 'l', 'r', 'rs', 'ls', 'd', 'nt', 'm', 'nts'],
    'au': ['lt'],
    'ay': ['', 's'],
    'aye': ['d', 'rs', 'r'],
    'ayi': ['ng'],
    'e': ['', 'd', 's', 'r', 'nt', 'rs', 'n', 'st', 'ss', 't', 'nts',
          'ct', 'cts', 'ts', 'nd', 'nds', 'l', 'ns', 'ls', 'w', 'rt',
          'll', 'rts', 'sts', 'rn', 'lf', 'm', 'lls', 'pt', 'ms',
          'ds', 'x', 'ws', 'mpt', 'xt', 'tch', 'sh', 'rns', 'pts',
          'lt', 'ck'],
    'ea': ['r', 'd', 't', 'rs', 'ts', 'l', 'ds', 'm', 'ls', 'k', 'ch',
           'ns', 'n', '', 'ks', 'th', 's', 'ms', 'st', 'p'],
    'ee': ['d', '', 'n', 's', 'r', 'p', 'ds', 'rs', 't', 'l', 'ts',
           'ps', 'ls', 'k'],
    'eei': ['ng'],
    'ei': ['n', 'ght'],
    'eou': ['s'],
    'ey': ['', 's'],
    'i': ['ng', 'c', 't', 'st', 'ngs', 'ts', 'p', 'ght', 'd', 'cs',
          'n', 'sts', 'sh', 's', 'ps', 'll', 'nd', 'ct', 'ck', 'm',
          'l', 'x', 'sm', 'ns', 'nk', 'nds', 'lls', 'ghts', 'cts',
          'cks', 'nt', 'gns', 'gn', 'tch', 'ss', 'nks', 'g', 'ft',
          'ds', '', 'sk', 'rt', 'pt', 'nts', 'ls', 'ld', 'fts', 'ff',
          'ch'],
    'ia': ['l', 'n', '', 'ns', 'ls', 'r', 'nt'],
    'ie': ['s', 'd', 'r', 'nt', 'st', '', 'f', 'w', 'rs', 'nts',
           'ws'],
    'io': ['n', 'ns', 'r', '', 's'],
    'iou': ['s'],
    'iu': ['m'],
    'o': ['r', 'n', '', 'w', 'rs', 't', 'ws', 'wn', 'rt', 'ns', 'm',
          'rts', 'p', 'rm', 'rd', 'ld', 'ck', 'ps', 'ng', 'cks', 'ts',
          'g', 'st', 'rn', 'rms', 'ss', 'rk', 'rds', 's', 'nd', 'l',
          'd', 'x', 'wns', 'rth', 'nt', 'ngs', 'ms', 'll', 'gs', 'b',
          'sts', 'rks', 'nds', 'ls', 'lls'],
    'oa': ['d', 't', 'rd', 'ts', 'ds', 'n'],
    'oe': ['s', ''],
    'oi': ['ng', 'nt', 'nts', 'l', 'd', 'n'],
    'oo': ['k', 'd', 'm', 'l', 'ks', 'n', 't', 'ls', 'ds', 'ts', 'r',
           'ps', 'p', 'ns', 'f'],
    'ou': ['s', 'nd', 't', 'nds', 'gh', 'r', 'ght', 'nts', 'nt', 'ts',
           'd', 'rs', 'ld', 'th', 'p', 'n'],
    'oy': ['', 's'],
    'oya': ['l'],
    'oye': ['d'],
    'oyi': ['ng'],
    'u': ['l', 's', 'm', 't', 'st', 'ts', 'n', 'ck', 'g', 'sh', 'lt',
          'll', 'r', 'ns', 'nk', 'ng', 'mp', 'gs', 'cts', 'ct', 'cks',
          'sts', 'pt', 'nch', 'ms', 'mps', 'lts', 'ss', 'rns', 'rn',
          'nt', 'mb', 'b', 'rs', 'rb', 'pts', 'ps', 'p', 'nts', 'nks',
          'nd', 'mn', 'ff', 'ch'],
    'ua': ['l', 'ls', 'rds', 'rd'],
    'ue': ['', 's', 'd', 'nt', 'st', 'l', 'sts'],
    'ui': ['ng', 't', 'ts', 'lt', 'sh', 'n', 'lds', 'ld', 'd'],
    'uou': ['s'],
    'uu': ['m'],
    'uy': ['s', ''],
    'y': ['', 'ms', 'm'],
    'ye': [''],
    'yi': ['ng'],
    }

if __name__ == '__main__':
    main()
