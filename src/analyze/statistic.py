#!/usr/bin/env python
import sys
import operator
from src.utils import equals, entity2clean_entity

import logging
formatter = logging.Formatter('%(message)s')
fh = logging.FileHandler(r"log\log.log", mode='w')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
#logging.basicConfig(level=logging.DEBUG, filename='info.log', filemode='w')
_logger = logging.getLogger("")
_logger.setLevel(logging.INFO)
logging.getLogger('').addHandler(fh)
_logger.addHandler(fh)


class Sentence():
    def __init__(self, sentence):
        self._sentence = sentence
        self._groups = []
        self._generate_groups()

    def _generate_groups(self):
        group = []
        for line in self._sentence:
            #[word, shape, golden_entity, predicted_entity]
            word, shape, golden_entity, predicted_entity = line
            if golden_entity.endswith('_B'):
                if group:
                    self._groups.append(group)
                group = [line]
            elif golden_entity.endswith('_M'):
                group.append(line)
            elif golden_entity.endswith('_E'):
                group.append(line)
                self._groups.append(group)
                group = []
            else:
                self._groups.append([line])
                group = []

    @property
    def groups(self):
        return self._groups


class Statistics():
    def __init__(self, log):
        self._log = log
        self._data = None
        self._sentences = []
        self._success_map = {}
        self._general_map = {}
        self._un_success_map = {}
        self._un_success_groups = [] #[group1, group2, ...]
                                     #group 1 = [[w1,s1,g1,p1],[w2,2,g2,p2], ...]
        self._general_groups = []
        self._file2data()
        self._make_sentences()
        self._statistics()
        self.print_dict(self._success_map, "Success Map")
        self.print_dict(self._un_success_map, "Un-Success Map")
        self.print_dict(self._general_map, "General Map")
        self._analyze_un_success_groups()
        self._common_mistakes()
        #self._confusion()

    def _confusion(self):
        _logger.info("Confusion")
        entities_groups = {}
        #for group in self._general_groups:
        for group in self._un_success_groups:
            word, shape, golden_entity, predicted_entity = group[0]
            gold = entity2clean_entity(golden_entity)
            if gold not in entities_groups:
                entities_groups[gold] = []
            entities_groups[gold].append(group)

        map = {}
        for key in entities_groups:
            if key not in map:
                map[key] = {}
            for group in entities_groups[key]:
                for line in group:
                    word, shape, golden_entity, predicted_entity = line
                    pred = entity2clean_entity(predicted_entity)
                    if pred == key:
                        continue
                    if pred not in map[key]:
                        map[key][pred] = 0
                    map[key][pred] += 1
        import matplotlib.pyplot as plt
        labels = []
        sizes = []
        print map
        for entity in map:
            for tag in map[entity]:
                labels.append(tag)
                sizes.append(map[entity][tag])
            self.pie = plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, )
            plt.axis('equal')
            print entity
            d = map[entity]
            sam = sum([d[k] for k in d])
            for k in d:
                print "{0}:{1:.3f}".format(k, float(d[k])/sam),
            print "total:", sam, "\n"
            plt.show()
            labels = []
            sizes = []


    def _common_mistakes(self):
        _logger.info("Common Errors")
        entities_groups = {}
        for group in self._un_success_groups:
            word, shape, golden_entity, predicted_entity = group[0]
            gold = entity2clean_entity(golden_entity)
            if gold not in entities_groups:
                entities_groups[gold] = []
            entities_groups[gold].append(group)
        for key in entities_groups:
            mistakes_counter = {}
            for group in entities_groups[key]:
                for line in group:
                    word, shape, golden_entity, predicted_entity = line
                    if word not in mistakes_counter:
                        mistakes_counter[word] = 0
                    mistakes_counter[word] += 1
            sorted_x = sorted(mistakes_counter.items(), key=operator.itemgetter(1), reverse=True)
            _logger.info(key)
            _logger.info(sorted_x[0:10])


    def _analyze_un_success_groups(self):
        """
            entities_groups =  {entity: size,
                                entity: size,
                                                }
            size = {len_of_group : [group1, group2, ...],
                    len_of_group : [group1, group2, ...]
                                                            }
        """
        entities_groups = {}
        for group in self._un_success_groups:
            word, shape, golden_entity, predicted_entity = group[0]
            gold = entity2clean_entity(golden_entity)
            if gold not in entities_groups:
                entities_groups[gold] = {}
            n = len(group)
            if n not in entities_groups[gold]:
                entities_groups[gold][n] = []
            entities_groups[gold][n].append(group)
        for key in entities_groups:
            _logger.info("Entity: {0}".format(key))
            for size in entities_groups[key]:
                #size is the length of the entity
                _logger.info("\n\tThere are {0} Entities of length {1}".format(len(entities_groups[key][size]), size))

                self.groups_2_stat(entities_groups[key][size])

        _logger.info("General Error details")
        self.groups_2_stat(self._un_success_groups)

    def get_tag_errors_locations_of_group(self, group):
        tag_errors_locations = []
        word_counter = 0
        for line in group:
            word_counter += 1
            word, shape, golden_entity, predicted_entity = line
            if not equals(golden_entity, predicted_entity):
                tag_errors_locations.append(word_counter)
        if len(tag_errors_locations) == 0:
            _logger.info("ERROR!!!, group {0} is fine".format(group))
        elif len(tag_errors_locations) == 1:
            tag_errors_locations = tag_errors_locations[0]
            ret = (tag_errors_locations, )
        else:
            ret = tuple(tag_errors_locations)
        return ret

    def groups_2_stat(self, groups):
        n = len(groups)
        map = {} #map location of tag-error to count of it.
        for group in groups:
            tag_errors_locations = self.get_tag_errors_locations_of_group(group)
            if tag_errors_locations not in map:
                map[tag_errors_locations] = 0
            map[tag_errors_locations] += 1

        sorted_x = sorted(map.items(), key=operator.itemgetter(0))
        _logger.info("\t\t{0}".format(sorted_x))



    def print_dict(self, d, title):
        def print_sum(map):
            sum = 0
            if type(map) == dict:
                for key in map:
                    try:
                        sum += float(key) * float(map[key])
                    except:
                        pass
            return sum
        _logger.info(title)
        for key in d:
            _logger.info("{0}:{1} {2}".format(key, d[key], print_sum(d[key])))



    def _statistics(self):
        def is_group_correct(group):
            for line in group:
                gold = line[2]
                pred = line[3]
                if not equals(gold, pred):
                    return False

            return True

        for sentecse in self._sentences:
            groups = sentecse.groups
            for group in groups:
                self._general_groups.append(group)
                if is_group_correct(group):
                    #group = groups[0]
                    word, shape, golden_entity, predicted_entity = group[0]
                    entity = entity2clean_entity(golden_entity)
                    if entity not in self._success_map:
                        self._success_map[entity] = {}
                    n = len(group)
                    if n not in self._success_map[entity]:
                        self._success_map[entity][n] = 0
                    self._success_map[entity][n] += 1
                else:
                    #group = groups[0]
                    self._un_success_groups.append(group)
                    word, shape, golden_entity, predicted_entity = group[0]
                    entity = entity2clean_entity(golden_entity)
                    if entity not in self._un_success_map:
                        self._un_success_map[entity] = {}
                    n = len(group)
                    if n not in self._un_success_map[entity]:
                        self._un_success_map[entity][n] = 0
                    self._un_success_map[entity][n] += 1

                #group = groups[0]
                word, shape, golden_entity, predicted_entity = group[0]
                entity = entity2clean_entity(golden_entity)
                if entity not in self._general_map:
                    self._general_map[entity] = {}
                n = len(group)
                if n not in self._general_map[entity]:
                    self._general_map[entity][n] = 0
                self._general_map[entity][n] += 1

    def _make_sentences(self):
        for sentence in self._data:
            self._sentences.append(Sentence(sentence))

    def _file2data(self):
        f = open(self._log, 'r')
        data = []
        sentence = []
        k = 0
        for line in f.readlines():
            if not line.strip():
                data.append(sentence)
                sentence = []
            else:
                l = line.strip().split()
                # l = [word, shape, golden_entity, predicted_entity]
                sentence.append(l)
        self._data = data


    @property
    def sentences(self):
        return self._sentences

def analyze(s):
    table = {}
    for group in s._un_success_groups:

        for line in group:
            word, shape, golden_entity, predicted_entity = line
            pred = entity2clean_entity(predicted_entity)
            if entity2clean_entity(golden_entity) == "cell_type":
                val = " ".join((word,pred))
                if val not in table:
                    table[val] = 0
                table[val] += 1
    sorted_x = sorted(table.items(), key=operator.itemgetter(1))
    for key in sorted_x:
        print key


def frequent_words_analysis(s):
    words = {}
    for group in s._general_groups:
        for line in group:
            word, shape, golden_entity, predicted_entity = line
            if word not in words:
                words[word] = 0
            words[word] += 1
    words = sort_dict_by_val(words)
    data = []
    for info in words:
        word, freq = info
        if freq >= 10 :
            #_logger.info("\nThe word '{0}' appears {1} times".format(word, freq))
            correct_tags_map = count_correct_tags(s, word, freq)
            incorrect_tags_map = count_incorrect_tags(s, word, freq)
            #if incorrect_tags_map:
            if True:
                data.append([word, freq, correct_tags_map, incorrect_tags_map])
    rated = {}
    frequent = {}
    NES = {}
    for line in data:
        word, freq, correct_tags_map, incorrect_tags_map = line
        _logger.info("\nThe word '{0}' appears {1} times".format(word, freq))
        _logger.info("Correct tags:")
        s_c = sum([correct_tags_map[k] for k in correct_tags_map])
        s_c_no_NE = s_c - correct_tags_map["NE"] if "NE" in correct_tags_map else s_c
        _logger.info("{0}, SUM={1}, SUM_NO_NE={2}".format(correct_tags_map, s_c, s_c_no_NE))
        _logger.info("In-Correct tags:")
        s_i = sum([incorrect_tags_map[k] for k in incorrect_tags_map])
        _logger.info("{0}, SUM={1}".format(incorrect_tags_map, s_i))
        rate = float(s_c_no_NE)/(s_c_no_NE + s_i) if s_c_no_NE + s_i > 0 else None
        _logger.info("Success: {0}".format(rate))
        rated[word] = rate
        frequent[word] = freq
        NES[word] = correct_tags_map["NE"] if "NE" in correct_tags_map else 0
    rated_sorted = sort_dict_by_val(rated)
    for line in rated_sorted:
        w, r = line
        _logger.error("word '{0}' appers '{1}' times and got success '{2}'. NE predicted correctly '{3}' times".format(w, frequent[w], r, NES[w]))

#This file contains, for each word, the correct and incorrect tags it the word get. (sorted from the most frequent)
def count_correct_tags(s, word, freq):

    map = {}
    for group in s._general_groups:
        for line in group:
            wo, shape, golden_entity, predicted_entity = line
            if wo == word and equals(golden_entity, predicted_entity):
                ent = entity2clean_entity(golden_entity)
                if ent not in map:
                    map[ent] = 0
                map[ent] += 1
    return map

def count_incorrect_tags(s, word, freq):

    map = {}
    for group in s._general_groups:
        for line in group:
            wo, shape, golden_entity, predicted_entity = line
            if wo == word and not equals(golden_entity, predicted_entity):
                pred = entity2clean_entity(predicted_entity)
                gold = entity2clean_entity(golden_entity)
                ent = " instead of ".join((pred, gold))
                if ent not in map:
                    map[ent] = 0
                map[ent] += 1
    return map

def confusion_map(s):
    c_m = {}
    gold_count = {}
    for group in s._general_groups:
        for line in group:
            wo, shape, golden_entity, predicted_entity = line
            g = entity2clean_entity(golden_entity)
            p = entity2clean_entity(predicted_entity)
            if g not in c_m:
                c_m[g] = {}
            if p not in c_m[g]:
                c_m[g][p] = 0
            c_m[g][p] += 1
            if g not in gold_count:
                gold_count[g] = 0
            gold_count[g] += 1
    for g in c_m:
        print "GOLD: ", g, gold_count[g]
        for p in c_m[g]:
            print g, p, c_m[g][p]




def sort_dict_by_val(d):
    sorted_x = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_x

def entities_distribution(s):
    total_entities = 0
    e_counter = {}
    for group in s._general_groups:
        for line in group:
            total_entities += 1
            wo, shape, golden_entity, predicted_entity = line
            g = entity2clean_entity(predicted_entity)
            if g not in e_counter:
                e_counter[g] = 0
            e_counter[g] += 1
    for e in e_counter:
        print e, e_counter[e], float(e_counter[e])/total_entities


def main():
    s = Statistics(r'C:\Users\user\Dropbox\logDevAnan\DA\logOut')
    print s
    #analyze(s)
    #frequent_words_analysis(s)
    #confusion_map(s)
    entities_distribution(s)

if __name__ == "__main__":
    main()