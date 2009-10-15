VOWELS = 'aeiouy'

vc_groups = {}
cv_groups = {}
for word in open('wordlist.txt'):
    word = word.strip()
    if word.endswith('s'):
        continue
    word = '^' + word + '$'
    index = 0
    v_group = c_group = ''
    while index < len(word):
        # Vowels
        start = index
        while index < len(word) and word[index] in VOWELS:
            index += 1
        v_group = word[start:index]
        if c_group and v_group:
            cv_group = c_group + v_group
            cv_groups[cv_group] = cv_groups.get(cv_group, 0) + 1
        # Consonants
        start = index
        while index < len(word) and word[index] not in VOWELS:
            index += 1
        c_group = word[start:index].replace("'", "")
        if v_group and c_group:
            vc_group = v_group + c_group
            vc_groups[vc_group] = vc_groups.get(vc_group, 0) + 1

cv_list = [(cv_groups[group], group) for group in cv_groups]
cv_list.sort()
cv_list.reverse()

print 'START_VOWEL = """'
print ' '.join(group[1:] for count, group in cv_list[:400]
               if group.startswith('^'))
print '""".split()'

print 'CONSONANT_VOWEL = """'
print ' '.join(group for count, group in cv_list[:400]
               if not group.startswith('^'))
print '""".split()'


vc_list = [(vc_groups[group], group) for group in vc_groups]
vc_list.sort()
vc_list.reverse()

print 'VOWEL_CONSONANT = """'
print ' '.join(group for count, group in vc_list[:400]
               if not group.endswith('$'))
print '""".split()'

print 'VOWEL_END = """'
print ' '.join(group[:-1] for count, group in vc_list[:400]
               if group.endswith('$'))
print '""".split()'
