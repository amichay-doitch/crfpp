import sys
log = "/home/administrator/workdir/crfpp/runCRF_L1/logDevelop"

def f2data(f):
    data = []
    logf = open(f, 'r')
    sentence = []
    for line in logf.readlines():
        l = line.strip().split()
        if l:
            sentence.append(l)
        else:
            data.append(sentence)
            sentence = []
    return data


def data2gold_pred(data):
    gold_pred = []
    for sentence in data:
        g_p = []
        for line in sentence:
            gold = line[3]
            pred = line[4]
            g_p.append((gold, pred))
        gold_pred.append(g_p)
    return gold_pred


def concentrate(data):
    my_data = data[:]
    concentration_gold_pred = []
    for sentence in my_data:
        c_g_p = []
        entity = []
        for line in sentence:
            gold = line[3]
            pred = line[4]
            word = line[0]
            if gold[-2:] == "_B":
                if entity:
                    c_g_p.append(entity)
                entity = [(gold, pred, word)]

            elif gold[-2:] == "_M":
                entity.append((gold, pred, word))

            elif gold[-2:] == "_E":
                entity.append((gold, pred, word))
                c_g_p.append(entity)
                entity = []


            else:
                c_g_p.append([(gold, pred, word)])

        concentration_gold_pred.append(c_g_p)
    return concentration_gold_pred




def analyze(concentration_gold_pred):
    goldentitys = set()
    predentitys = set()
    for sentence in concentration_gold_pred:
        for entitys in sentence:
            for g, p, w in entitys:
                if g[-2:] in ["_E", "_M", "_B"]:
                    goldentitys.add(g[0:-2])
                else:
                    goldentitys.add(g)

                if p[-2:] in ["_E", "_M", "_B"]:
                    predentitys.add(p[0:-2])
                else:
                    predentitys.add(p)

    print len(goldentitys), goldentitys
    print len(predentitys), predentitys
    print predentitys ^ goldentitys
    goldmap = print_goldmap(concentration_gold_pred)
    predmap, mess_entities = print_predmap(concentration_gold_pred)
    #print_common(goldmap, predmap)
    messmap = print_messmap(mess_entities)


def print_messmap(mess_entities_):
    mess_entities = mess_entities_[:]
    wrong = 0
    all = 0
    for entity in mess_entities:
        for gold, pred, word in entity:
            all += 1
            if gold != pred:
                wrong += 1
    #print wrong
    #print all
    #print float(wrong)/all
    unientity = {}
    unicount = 0
    for entity in mess_entities:
        if len(entity) == 1:
            unicount += 1
            if entity[0][2] not in unientity:
                unientity[entity[0][2]] = 0
            unientity[entity[0][2]] += 1

    print unicount
    entity_size_map = {}
    for entity in mess_entities:
        if len(entity) > 1:
            if len(entity) not in entity_size_map:
                entity_size_map[len(entity)] = []
            entity_size_map[len(entity)].append(entity)

    def find_errors_in_entity(entity):
        loc = []
        for i in range(len(entity)):
            tup_3 = entity[i]
            if tup_3[0] != tup_3[1]:
                loc.append(i)
        return loc


    for size in entity_size_map:
        location = {}
        for entity in entity_size_map[size]:
            loc = find_errors_in_entity(entity)
            if len(loc) == 1:
                loc = loc[0]
                if loc not in location:
                    location[loc] = 0
                location[loc] += 1
            elif len(loc) > 1:
                loc = tuple(loc)
                if loc not in location:
                    location[loc] = 0
                location[loc] += 1
        for loc in location:
            location[loc] = "{0:.3f}".format(float(location[loc]) / len(entity_size_map[size]))
        print size
        print len(entity_size_map[size])
        print location
        print ""





def print_common(goldmap, predmap):
    print "\n\n"
    keys = goldmap.keys() + predmap.keys()
    for key in keys:
        if key in goldmap:
            print "Gold          {0}: {1}".format(key, goldmap[key])
        if key in predmap:
            print "Predicted     {0}: {1}".format(key, predmap[key])
        print " "


def print_predmap(concentration_gold_pred):
    mess_entities = []
    predmap = {}
    mess = False
    for sentence in concentration_gold_pred:
        for entitys in sentence:
            gold = entitys[0][0]
            if gold[-2:] in ["_E", "_M", "_B"]:
                gold = gold[0:-2]
            checker = entitys[0][1]
            if checker[-2:] in ["_E", "_M", "_B"]:
                checker = checker[0:-2]
            if gold != checker:
                mess = True
            preds = [e[1] for e in entitys]
            for pr in preds:
                if pr[-2:] in ["_E", "_M", "_B"]:
                    pr = pr[0:-2]
                if pr != checker:
                    mess = True
                    break
            if mess:
                mess_entities.append(entitys)
                if "MESS" not in predmap:
                    predmap["MESS"] = {}
                if len(entitys) not in predmap["MESS"]:
                    predmap["MESS"][len(entitys)] = 1
                else:
                    predmap["MESS"][len(entitys)] += 1
                mess = False
                continue
            p = entitys[0][1]
            if p[-2:] in ["_E", "_M", "_B"]:
                p = p[0:-2]
            if p not in predmap:
                predmap[p] = {}
            if len(entitys) not in predmap[p]:
                predmap[p][len(entitys)] = 1
            else:
                predmap[p][len(entitys)] += 1
    print predmap
    return predmap, mess_entities

def print_goldmap(concentration_gold_pred):
    goldmap = {}
    for sentence in concentration_gold_pred:
        for entitys in sentence:
            g = entitys[0][0]
            if g[-2:] in ["_E", "_M", "_B"]:
                g = g[0:-2]
            if g not in goldmap:
                goldmap[g] = {}
            if len(entitys) not in goldmap[g]:
                goldmap[g][len(entitys)] = 1
            else:
                goldmap[g][len(entitys)] += 1
    print goldmap
    return goldmap

def main():
    data = f2data(log)
    gold_pred = data2gold_pred(data)
    concentration_gold_pred = concentrate(data)
    analyze(concentration_gold_pred)


if __name__ == "__main__":
    main()