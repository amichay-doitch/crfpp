#!/usr/bin/env python
import xml.etree.ElementTree as ET
import xml.etree.cElementTree as eTree
import os
import sys
import time
import glob

OUT = "/home/administrator/workdir/git_folder/crf_project/feat/src_DA/out.txt"


ugly = set(['(AS_WELL_AS', '(BUT_NOT', '(THAN',
            '(AND_NOT', '(TO', '(VERSUS', '(AND', '(OR', '(AND/OR', '(NEITHER_NOR', '(NOT_ONLY_BUT_ALSO'])

class Sentence(object):
    countbad = 0
    countgood = 0

    def __init__(self, text, entities):
        self.no_type = False
        self.B = "_B"
        self.M = "_M"
        self.E = "_E"
        self.tagged = ""
        self.text = text
        self.clean_entities = []
        self.dirty_text = []
        self.concentrated_text = []
        self.dirty = False
        self.clean_lower_hierarchies_and_clean_entities(entities)
        if not self.dirty:
            self.concentrate()
            self.clean()
            self.tag_ordinary_sentence()
        else:
            self.get_dirty_tagged(entities)

    def get_dirty_tagged(self, entities):
        words_tags = []
        text = self.text[:]
        while '' in text:
            text.pop(text.index(''))


        while text:
            added = False
            curr_orig = "_".join(text.pop(0).split(" "))
            curr = curr_orig.lower()
            if words_tags and words_tags[-1][-1]:
                if "_".join((words_tags[-1][0].lower(), curr)) in words_tags[-1][-1].lower() or "_".join((words_tags[-1][0].lower(), curr)) in words_tags[-1][-1].lower() + 's':
                    added = True
                    words_tags[-1][0] = "_".join((words_tags[-1][0], curr_orig))
            else:
                for d in self.clean_entities:
                    if len(d) == 1:
                        if curr in d[0]['lex'].lower() or curr in d[0]['lex'].lower() + 's':
                            added = True
                            words_tags.append([curr_orig, d[0]['sem'], d[0]['lex']])
                            self.clean_entities.pop(self.clean_entities.index(d))
                            break
                    else:
                        primary = d[0]
                        lex_primary = primary['lex']
                        sem_primary = primary['sem']
                        if lex_primary[0] == "(":
                            lex_primary = lex_primary[1:]
                        if lex_primary[-1] == ")":
                            lex_primary = lex_primary[:-1]

                        if sem_primary[0] == "(":
                            sem_primary = sem_primary[1:]
                        if sem_primary[-1] == ")":
                            sem_primary = sem_primary[:-1]
                        sem_primary = sem_primary.split(" ")

                        sem_primary.pop(0)
                        lex_primary = lex_primary.split(" ")
                        TYPE = lex_primary.pop(0)



                        exist = False
                        for prime in lex_primary:
                            prime = prime.lower()
                            if curr in prime:
                                exist = True
                                break
                        if exist:
                            all_prime = "_".join(lex_primary)
                            key = 2
                            while True:
                                if text:
                                    plain = text[0].replace(" ", "")
                                if text and (not plain.isalnum() or text[0] in all_prime or "_".join((text[0])) in all_prime or \
                                                TYPE.lower() in text[0].lower() or '-and' in text[0] or \
                                                '-or' in text[0] or '-,' in text[0] or \
                                                     "_".join(text[0].split(" ")) in all_prime or \
                                                     ("_".join(text[0].split(" "))[-1] == 's' and "_".join(text[0].split(" "))[0:-1] in all_prime)):
                                    text.pop(0)
                                else:
                                    break
                            sep = "_" + TYPE.lower() + "_"
                            words_tags.append([sep.join(lex_primary), sem_primary[0], "_".join(lex_primary)])

                            self.clean_entities.pop(self.clean_entities.index(d))
                            added = True

            if not added:
                words_tags.append([curr_orig, None, None])

        for w, t, lex in words_tags:
            add_me = ""
            words = w.split("_")
            if t == None:
                for word in words:
                    if word != "":
                        add_me += " ".join((word, 'NE' + "\n"))
            elif len(words) == 1:
                add_me = " ".join((words[0], t + "\n"))
            else:
                add_me += " ".join((words[0], t + self.B + "\n"))
                for j in range(1, len(words) - 1):
                    add_me += " ".join((words[j], t + self.M + "\n"))
                add_me += " ".join((words[-1], t + self.E + "\n"))
            self.tagged += add_me

    def clean(self):
        while [''] in self.concentrated_text:
            self.concentrated_text.pop(self.concentrated_text.index(['']))

    def tag_ordinary_sentence(self):
        i = 0
        for line in self.concentrated_text:

            add_me = ""
            try:
                entity = self.clean_entities[i][0]
            except:
                entity = None
            if entity and (line[0].lower() == entity['lex'].lower() or line[0].lower() == entity['lex'].lower() + 's'):
                s_line = line[0].split('_')
                if len(s_line) == 1:
                    add_me += " ".join((s_line[0], entity['sem'] + "\n"))
                else:
                    add_me += " ".join((s_line[0], entity['sem'] + self.B + "\n"))
                    for j in range(1, len(s_line) - 1):
                        add_me += " ".join((s_line[j], entity['sem'] + self.M + "\n"))
                    add_me += " ".join((s_line[-1], entity['sem'] + self.E + "\n"))

                i += 1
            else:
                s_line = line[0].split('_')
                for k in range(len(s_line)):
                    add_me += " ".join((s_line[k], "NE" + "\n"))
            self.tagged += add_me

    def check(self):
        for d in self.clean_entities:
            lex = d[0]['lex']
            if ',' in lex:
                print ','
                print self.concentrated_text
            if '.' in lex:
                print '.'
                print self.concentrated_text

    def get_highest_hierarchy(self, entity):
        max = 0
        highest = None
        for d in entity:
            if len(d['lex']) > max:
                max = len(d['lex'])
                highest = d
        return highest

    def is_dirty(self, entity):
        for d in entity:
            lex = d['lex']
            for u in ugly:
                if lex.startswith(u):
                    return True


    def clean_lower_hierarchies_and_clean_entities(self, entities):
        """
        remove lower hierarchies from entities
        :rtype : None, however, update the member self.clean_entities
        """
        for d in entities:
            while len(d) > 1:
                if self.is_dirty(d):
                    Sentence.countbad += 1
                    self.dirty = True
                    break

                highest_hierarchy = self.get_highest_hierarchy(d)
                sep = "_" if "_" in highest_hierarchy['lex'] else " "
                s_highest_hierarchy = highest_hierarchy['lex'].split(sep)

                if d[0] != highest_hierarchy:
                    always = True
                    if d[1]['lex'] in highest_hierarchy['lex']:
                        always = True
                    else:
                        found = False
                        sep = "_" if "_" in d[0]['lex'] else " "
                        for part in d[0]['lex'].split(sep):
                            for s in s_highest_hierarchy:
                                if part.lower() in s.lower():
                                    found = True
                                if not found:
                                    if part.endswith('s'):
                                        part = part[:-1]
                                    if s.endswith('s'):
                                        s = s[:-1]
                                        if part.lower() in s.lower():
                                            found = True
                            if not found:
                                always = False
                    if always:
                        Sentence.countgood += 1
                        d.pop(d.index(d[0]))

                elif d[1] != highest_hierarchy:
                    always = True
                    if d[1]['lex'] in highest_hierarchy['lex']:
                        always = True
                    else:
                        found = False
                        sep = "_" if "_" in d[1]['lex'] else " "
                        for part in d[1]['lex'].split(sep):
                            for s in s_highest_hierarchy:
                                if part.lower() in s.lower():
                                    found = True
                                if not found:
                                    if part.endswith('s'):
                                        part = part[:-1]
                                    if s.endswith('s'):
                                        s = s[:-1]
                                        if part.lower() in s.lower():
                                            found = True
                            if not found:
                                always = False
                    if always:
                        Sentence.countgood += 1
                        d.pop(d.index(d[1]))
                elif d[0] == d[1]:
                    d.pop(d.index(d[1]))


            self.clean_entities.append(d)


    def clean_lower_hierarchies_and_clean_entities_orig(self, entities):
        """
        remove lower hierarchies from entities
        :rtype : None, however, update the member self.clean_entities
        """
        for d in entities:
            while len(d) > 1:
                d0 = d[0]
                d1 = d[1]
                if d0['lex'] in d1['lex']:
                    Sentence.countgood += 1
                    d.pop(d.index(d0))
                elif d1['lex'] in d0['lex']:
                    Sentence.countgood += 1
                    d.pop(d.index(d1))
                else:
                    Sentence.countbad += 1
                    self.dirty = True
                    #self.clean_entities.append(d)
                    break
            self.clean_entities.append(d)


    def concentrate(self):
        def get_me_possible_concentrations(i_text, i, d):
            lex = d[0]['lex']
            count = 1
            combi = set()
            step = {}
            for j in range(0, len(i_text) + 1):
                add_me = i_text[i:j]
                if add_me:
                    add_me = " ".join(add_me)
                    combi.add(' '.join(add_me.split()))
                    step[' '.join(add_me.split())] = count
                    count += 1

            for co in combi:
                c = "_".join(co.lower().split())
                if c == lex.lower() or c == lex.lower() + 's':
                    return co, step[co]
            return None, None

        found_entities = []
        clean_entities = self.clean_entities[:]
        concentrated_text = []
        text = self.text[:]
        i = 0
        while i < len(text):
            curr = self.text[i]
            curr_orig = "_".join(curr.split())
            curr = "_".join(curr.lower().split())
            found = -1
            for d in clean_entities:
                cu, step = get_me_possible_concentrations(text, i, d)
                if cu != None and step != None:
                    concentrated_text.append(["_".join(cu.split())])
                    i += step
                    found = clean_entities.index(d)
                    found_entities.append(clean_entities[found])
                    clean_entities.pop(found)
                    break
            else:
                concentrated_text.append([curr_orig])
                i += 1
        self.concentrated_text = concentrated_text


class GeniaParser(object):
    def __init__(self, f):
        if not os.path.isfile(f):
            sys.exit("file not found: {0}".format(f))
        self.sentences = []
        self.path = f
        self.parse()
        print Sentence.countbad
        print Sentence.countgood

    def parse(self):
        tree = ET.parse(self.path)
        root = tree.getroot()
        for r in root:
            if r.tag == "PubmedArticleSet":
                for elem in r:
                    if elem.tag == "PubmedArticle":
                        for eleme in elem:
                            if eleme.tag == "MedlineCitation":
                                for elemen in eleme:
                                    if elemen.tag in ["Article", "Abstract"]:
                                        for element in elemen:
                                            print element.tag
                                            if element.tag in ["ArticleTitle", "Abstract"]:
                                                for child in element:
                                                    if child.tag == "sentence":
                                                        self.parse_sentence(child)
                                                    if child.tag == "AbstractText":
                                                        for child_child in child:
                                                            if child_child.tag == "sentence":
                                                                self.parse_sentence(child_child)

    def parse_sentence(self, element):
        text = []
        entities = []
        for it in element.itertext():
            text.append(it.strip())

        for data in element:
            attr_dicts = list()
            attr_dicts.append(data.attrib)
            for inner_data in data:
                attr_dicts.append(inner_data.attrib)
                for inner_inner_data in inner_data:
                    attr_dicts.append(inner_inner_data.attrib)
                    for inner_inner_inner_data in inner_inner_data:
                        attr_dicts.append(inner_inner_inner_data.attrib)
            entities.append(attr_dicts)

        sentence = Sentence(text, entities)
        self.sentences.append(sentence)

        # doc = eTree.parse(xml_mail)
        # for nightly_elem in doc.iter("nightly"):
        #     for elem in nightly_elem.iter("address"):
        #         addresses.append(elem.get("value"))


class DAParser():
    def __init__(self, f):
        if not os.path.isfile(f):
            sys.exit("file not found: {0}".format(f))
        self.sentences = []
        self.path = f
        self.parse()

    def parse(self):
        doc = ET.parse(self.path)
        for PubmedArticleSet in doc.iter("PubmedArticleSet"):
            for PubmedArticle in PubmedArticleSet.iter("PubmedArticle"):
                for MedlineCitation in PubmedArticle.iter("MedlineCitation"):
                    for Article in MedlineCitation.iter("Article"):
                        for ArticleTitle in Article.iter("ArticleTitle"):
                            for sentence in ArticleTitle.iter("sentence"):
                                self.parse_sentence(sentence)
                        for Abstract in Article.iter("Abstract"):
                            for AbstractText in Abstract.iter("AbstractText"):
                                for sentence in AbstractText.iter("sentence"):
                                    self.parse_sentence(sentence)

    def parse_sentence(self, sentence):
        text = []
        entities = []
        for it in sentence.itertext():
            text.append(it.strip())

        for data in sentence:
            attr_dicts = list()
            attr_dicts.append(data.attrib)
            for inner_data in data:
                if 'lex' in inner_data.attrib and 'sem' in inner_data.attrib:
                    attr_dicts.append(inner_data.attrib)
                for inner_inner_data in inner_data:
                    if 'lex' in inner_inner_data.attrib and 'sem' in inner_inner_data.attrib:
                        attr_dicts.append(inner_inner_data.attrib)
                    for inner_inner_inner_data in inner_inner_data:
                        if 'lex' in inner_inner_inner_data.attrib and 'sem' in inner_inner_inner_data.attrib:
                            attr_dicts.append(inner_inner_inner_data.attrib)
            for d in attr_dicts:
                if 'lex' not in d or 'sem' not in d:
                    break
                else:
                    entities.append(attr_dicts)

        sentence = Sentence(text, entities)
        self.sentences.append(sentence)






def main(f):
    G = DAParser(f)
    print G
    print OUT
    out = open(OUT, 'a')
    untyped = 0
    for s in G.sentences:
        out.write(s.tagged)
        out.write("\n")
    out.close()
    out = open(OUT, 'r')
    sentence = []
    sentences = []
    signs = set(['&', '*', ',', '/', '.', ';', ':', '?'])
    for line in out.readlines():
        s_line = line.strip().split(" ")
        if s_line != ['']:
            if len(s_line) < 2:
                continue
            if s_line[1] == "NE":
                sign = s_line[0][-1]
                if sign in signs and s_line[0] not in signs:
                    sentence.append(" ".join((s_line[0][0:-1], "NE")))

                    sentence.append(" ".join((s_line[0][-1], "NE")))
                else:
                    sentence.append(" ".join(s_line))
            else:
                sentence.append(" ".join(s_line))
        else:
            sentences.append(sentence)
            sentence = []
    out.close()
    out = open(OUT+'new', 'a')
    for sent in sentences:
        for s in sent:
            out.write(s + "\n")
        out.write("\n")

if __name__ == "__main__":
    dir_ = "/home/administrator/workdir/git_folder/crf_project/feat/DomainAdaptation/Meta-knowledge_GENIA_corpus/Meta-knowledge_GENIA_Corpus/Corpus"
    import os
    os.chdir(dir_)
    for file in glob.glob("*.xml"):
        main(os.path.join(dir_, file))
