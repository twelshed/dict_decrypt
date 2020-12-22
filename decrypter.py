import enchant
import random
import itertools
import numpy as np

import json
from collections import defaultdict
def get_word_set(dict_json_path):
    derp_set = defaultdict(set)
    with open(dict_json_path) as f:
        derp = json.load(f)
        derp_list = list(derp)
        for word in derp_list:
            derp_set[len(word)].add(word)

    return derp_set

def words_from_len(word_len, word_set):
    return word_set[word_len]

def message_set(msg):
    msg_set = defaultdict(set)
    for word in msg:
        msg_set[len(word)].add(word)

    return msg_set

def match_pattern(word, word_len_set, candidate_set):
    
    rel_pattern = intraword_pattern(word,word)
    for candidate in list(word_len_set):
        if np.array_equal(rel_pattern, intraword_pattern(candidate,candidate)):
            candidate_set[word].add(candidate)

    return candidate_set

def intraword_pattern(word1, word2):
    rel_pos = [[letter in position for position in word2] for letter in word1]
    rel_pos_array = np.array(rel_pos).astype(np.int)

    return rel_pos_array

def optimize_word_pair_order(word_set_list,candidate_set):
    candidate_num = [len(candidate_set[word]) for word in word_set_list]
    opt_word_list = np.asarray(word_set_list)[np.argsort(candidate_num)]

    return opt_word_list

def prune_by_intraword_2(msg_set, candidate_set, inspect_num = 25):
    pruned_candidate_set = defaultdict(set)
    optimized_order = optimize_word_pair_order(list(msg_set),candidate_set)
    words_combos = list(itertools.combinations(optimized_order,2))
    print('Total word combinations to analyze : ' + str(len(words_combos)))
    print('Analyzing : ' + str(inspect_num))
    count = 1
    for i in range(inspect_num):
        word_pair = words_combos[i]  
        #print('On pair: ' + str(count))
        count += 1
        #print(word_pair)
        intra_pat_1 = intraword_pattern(word_pair[0],word_pair[1])
        for word1 in list(candidate_set[word_pair[0]]):
            for word2 in list(candidate_set[word_pair[1]]):
                intra_pat_2 = intraword_pattern(word1,word2)

                if np.array_equal(intra_pat_1,intra_pat_2):
                    pruned_candidate_set[word_pair[0]].add(word1) 
                    pruned_candidate_set[word_pair[1]].add(word2)
        
        candidate_set[word_pair[0]] = pruned_candidate_set[word_pair[0]]
        candidate_set[word_pair[1]] = pruned_candidate_set[word_pair[1]]

    return candidate_set

def letter_possibilities(cipher_letter_set, candidate_set, message_words):
    for word in message_words:
        for i,letter in enumerate(word):
            y = set([cand_word[i] for cand_word in list(candidate_set[word])])
            cipher_letter_set[letter] = cipher_letter_set[letter].intersection(y)

    return cipher_letter_set

def prune_candidates_by_letter_possibilities(candidate_set, cipher_letter_set):
    pruned_candidate_set = defaultdict(set)
    for word in candidate_set:
        for cand_word in candidate_set[word]:
            in_set = np.asarray([cand_word[i] in cipher_letter_set[word[i]] for i in range(len(word))]).astype(np.int)
            if np.all(in_set):
                pruned_candidate_set[word].add(cand_word)
        candidate_set[word] = pruned_candidate_set[word]

    return candidate_set

def check_for_solved_letters(cipher_letter_set):
    for letter in cipher_letter_set:
        if len(cipher_letter_set[letter]) == 1:
            for other_letter in cipher_letter_set:
                if other_letter == letter:
                    continue;
                else:
                    cipher_letter_set[other_letter] = cipher_letter_set[other_letter] - cipher_letter_set[letter]
    return cipher_letter_set

def decode_message(message, candidate_set):
    decoded_message = []
    for word in message:
        decoded_message.append(candidate_set[word])

    print("Decoded message:")
    print(decoded_message)

if __name__ == "__main__":
    full_message = "p onyyhof p lpkk mpf qfzfc jqhlpqx lgie yntyjpq ypf eioefo kpjf lgfq vhn gizf chht bhc pe - chafce acinke"
    message = "p onyyhof p lpkk mpf qfzfc jqhlpqx lgie yntyjpq ypf eioefo kpjf lgfq vhn gizf chht bhc pe"
    #message = "xbvrgige jsusxsfmr vdiv nvigvn vs odrrnr sg usv vs odrrnr vdiv bn vdr pmrnvbsu sjrxrv nsxbxspme"
    #message = "mvv soms it lwvg gwat xws lvissaq xws mvv sowta uow umxgaq mqa vwts"
    message = "hfo admpoi hdo gxglp jn ajboi giirgmmz hd hfo hdu qjvqol ji hfo ighjdigm cddhtgmm mogaro"
    message = "rq erf rkt k erg of pbiq aky lqks kpnfto kyg rfe ybqohtarq"
    ab = "abcdefghijklmnopqrstuvwxyz"

    dict_set = get_word_set('english-words/words_dictionary.json')
    candidate_set = defaultdict(set)
    # The dictionary we load has every letter of the alphabet as a viable word but I disagree
    dict_set[1] = {'i','a'}
    msg_set = message_set(message.split(' '))
    cipher_letter_set = defaultdict(set)

    for letter in set(message):
        cipher_letter_set[letter] = set(ab)

    for word in list(message.split(' ')):
        candidate_set = match_pattern(word,dict_set[len(word)],candidate_set)

    inspect_num = 15
    #inspect_num = 2*(len(message.split(' ')))
    candidate_set = prune_by_intraword_2(list(set(message.split(' '))), candidate_set, inspect_num)
    converged = 0
    cur_candidate_num = [len(candidate_set[word]) for word in candidate_set]
    rounds = 0
    print('Starting letter reduction cycle')
    while not converged:
        print('Reduction round: '+str(rounds))
        print('Current candidates:')
        print(cur_candidate_num)
        prev_candidate_num = cur_candidate_num
        cipher_letter_set = letter_possibilities(cipher_letter_set,candidate_set,message.split(' '))
        cipher_letter_set = check_for_solved_letters(cipher_letter_set)
        candidate_set = prune_candidates_by_letter_possibilities(candidate_set, cipher_letter_set)
        cur_candidate_num = [len(candidate_set[word]) for word in candidate_set]
        rounds +=1
        if sum(cur_candidate_num) == sum(prev_candidate_num):
            converged = 1
    
    print('Convergence after ' + str(rounds) + ' rounds')
    #derp = [len(candidate_set[word]) for word in candidate_set]
    #[print([word,candidate_set[word]]) for word in candidate_set]
    print(cipher_letter_set)
    #print(derp)
    decode_message(message.split(' '),candidate_set)
    # candidate lengths:
    # with 25  word pairs : [2, 21, 472, 169, 153, 86, 2966, 57, 98, 14, 655, 1207, 216, 1679, 239, 974, 32]
    # with 50  word pairs : [2, 21, 472, 169, 153, 86, 2966, 57, 98, 14, 655, 1207, 216, 1679, 239, 974, 32]
    # with 100 word pairs : [2, 21, 472, 169, 153, 86, 2966, 57, 98, 14, 655, 1207, 216, 1679, 239, 974, 32]
    # wtih 136 word pairs : 

    