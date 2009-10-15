import random
import re

VOWELS = 'aeiouy'
vc_match = re.compile(r'^([aeiouy]+)(.*)$').match
cv_match = re.compile(r'^(qu|.*?)([aeiouy]+)$').match


def find_vowel_matches(vowels, choices):
    count = len(vowels)
    return [choice for choice in choices if choice.startswith(vowels)
            and (len(choice) == count or choice[count] not in VOWELS)]


def find_consonant_matches(consonants, choices):
    count = len(consonants)
    return [choice for choice in choices if choice.startswith(consonants)
            and (len(choice) == count or choice[count] in VOWELS)]


def generate_password(digits=0):
    choice = random.choice(START_VOWEL)
    consonants, vowels = cv_match(choice).groups()
    parts = [consonants]
    # print parts, choice, consonants, vowels

    matches = find_vowel_matches(vowels, VOWEL_CONSONANT)
    choice = random.choice(matches)
    vowels, consonants = vc_match(choice).groups()
    parts.append(vowels)
    # print parts, choice, vowels, consonants

    matches = find_consonant_matches(consonants, CONSONANT_VOWEL)
    choice = random.choice(matches)
    consonants, vowels = cv_match(choice).groups()
    parts.append(consonants)
    # print parts, choice, consonants, vowels

    matches = find_vowel_matches(vowels, VOWEL_END)
    parts.append(random.choice(matches))
    for d in range(digits):
        parts.append(random.choice('23456789'))
    # print parts
    return ''.join(parts)


START_VOWEL = """
a i e co re di de u o ca ma pa su mi ba pro pe po ha mo bu se fo sa li
ho pre ra si ta wa me fi be la te pi fa pu wi so ga mu to sta do tra
cu gra lo no bo ou bi ri hu he cha le ve ti ru vi fu va hi ne tu da
hea ro ge wo na du go sha fe ki au cra cou ce bla lu gu sto ju sca pri
fla ea pla chi sho rea ni tri ci qua spa boo sti cla nu hy ja bra gi
whi sy stu vo bri ste cri spe we gri lea clo cru bro cro sla tru
dea qui spi sou sno plu foo spo thi sli cli bea stra ski fra cho brea
blo sea flu swi pho ai jo mou cre che
""".split()

CONSONANT_VOWEL = """
te re ve ne tio ti li ra ri me se de ni na le ca nce ty la nte pe ce
mi si ta ge nde to di ma ble ste ke sti tte lo nti ci ry sse vi lle
lly cke ly ga gi ndi va nge she ctio nta bi the fi co no we rie mo cu
tu cti ssi pi lli po mpe fe rti sa rte so ppe rse be nsi ro pa gra rre
tie mme nne rmi da che llo do lla dge nse ze sta tti bu ba xi ffe fie
wi rge rma fu gge ria du xe ssio rde nci bo nda rri cto cia sio spe nu
vo cki nco go ffi su rne ki cte sto nve lu nke rro mbe ppi ny wa
rce rme nsu mpa tche rni lde rdi sco que lie ncy dde pu rna mu ghte
mpo sly ntly lte bbe rra ngi ndo cy phe bly lve sce gy nfi ple ngle
ttle rve die mmi rta cle mble pti lti ptio bli nie gu sso nni lia dia
qui mple llu rke nto cie tra mma rou ntra mpli tri rsi stra ggi xa
nche dy cra ssa nfe cce nso ckle xpe tho ddle cta nki tto rso ndu thi
ru nfo mpi fte nca sca gni fa ccu wo mmo bbi pli mba gna ctu rpe rcu
ddi stle rrie nsa cro
""".split()

VOWEL_CONSONANT = """
at er it in ic ar el iv or on en em et al ol il ur id om is ag ov ec
ent im an ac ed all ev ad if am ul es ot ect abl int ut av anc os est
op ess ir enc ef eg ist ass ion od ap ab ig un us og oc ow end ill ast
ep ant ib ers ort and ind iat ak und arr ens att as act ell oll inc
ert ew imp ing erm app omp ang um omm ons art ish erv ud ip ous iss
ick ob eas itt err ull ack eb acc ont isc ann orm ust ett ock inf eat
utt ins ern ok eq etr ash ain onc up ond ibl orr az amp urr opp
ath uct oss erc ict uff inv ost inn esp ult ott ord uc uat onv ik aph
onf ight yp ount ead umm oth ard esc imm aff ush ipp ear aw ail
arm ign istr isp amm ogr atr arg agg ingl ept emb egr uit erg eep
of entr ecr ach ark ank abb ugg oph iq ub orn ax ink eak unn unk ox
ound ontr irr add impl eav ubb ong eal angl ompl aut ipl amb urg
unt unc old eng ump udg our iev estr alt esh epl onn ienc erp
urs eed entl arn yr obb umb ors org itch eth off orc iff urn ogg igr
apt yn ual atch ug ounc iol upp ans umbl oot omb edg acr
out ift eel ecl obl
""".split()

VOWEL_END = """
ing ed e y er ion ier iest est al ent ic en ied or ying a ist o et ant
an on ial ay ul it el ism ar ish ow ue ip in and ack id ard ect ight
ee ain ot ie um ia ound ian own at op ey end ick aying all ual ead ap
ued out i ew ock eed uing ill ail ood ient ort ium ash eat ear
oing oon om ut ork am
""".split()


if __name__ == '__main__':
    for row in range(20):
        print ''.join('%-16s' % generate_password() for column in range(5))
