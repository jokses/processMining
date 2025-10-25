# Joachim Knudsen s072446

import xml.etree.ElementTree as ET

from datetime import datetime

class PetriNet():

    def __init__(self):
        self.places = {}
        self.transistion = {}
        self.edgeTS = {}
        self.edgeST = {}
        self.missingTokens = {}
        self.consumedTokens = 0
        self.producedTokens = 0
    def add_place(self, name):
        self.places[name] = 0
        self.missingTokens[name] = 0
        return self
    def add_transition(self, name, id):
        self.transistion[name] = id
        return self
    def transition_name_to_id(self, name):
        return self.transistion[name]
    def add_edge(self, source, target):
        self.edgeTS.setdefault(target, []).append(source)
        self.edgeST.setdefault(source, []).append(target)
        return self
    def get_tokens(self, place):
        return self.places[place]

    def is_enabled(self, transition):
        result = self.edgeTS.setdefault(transition,[])
        for i in result:
            if self.places[i] ==0:
                return False
        return True

    def add_marking(self, place):
        self.places[place] = self.places[place] + 1
        self.producedTokens +=1
    def fire_transition(self, transition):

        if self.is_enabled(transition):
            for i in self.edgeTS[transition]:
                self.places[i] = self.places[i] - 1
                self.consumedTokens +=1
        else:
            for i in self.edgeTS[transition]:
                self.missingTokens[self.places[i]] +=1
                self.consumedTokens +=1
        for i in self.edgeST[transition]:
            self.places[i] = self.places[i] + 1
            self.producedTokens +=1

    def remainingToken(self):
        return sum(self.places.values())
    def missingToken(self):
        return sum(self.missingTokens.values())
    def consumedToken(self):
        return self.consumedTokens
    def producedToken(self):
        return self.producedTokens
    def done(self):
        if(self.places[99999] ==0):
            self.missingTokens[self.places[99999]] +=1
            self.consumedTokens +=1
        else:
            self.places[99999] -=1
            self.consumedTokens +=1

    def reInit(self):
        self.places = self.places.fromkeys(self.places,0)
        self.missingTokens = self.missingTokens.fromkeys(self.missingTokens,0)
        self.consumedTokens = 0
        self.producedTokens = 0
        self.add_marking(0)



def log_as_dictionary(fileString):
    log = {}
    for line  in fileString.strip().split("\n"):
        if len(line)>0:
            task , case, user, timestamp = line.split(";")
            log.setdefault(case,[]).append(task)
    return log

def dependency_graph_inline(log):
    dg ={}
    for l in log:
        for t in range(len(log[l])-1):
            dg.setdefault(log[l][t],{})
            dg[log[l][t]][log[l][t+1]] = 1+dg[log[l][t]].setdefault(log[l][t+1],0)
    return dg

def read_from_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    log = {}
    ns = {'xes' :"http://www.xes-standard.org/"}
    for trace in root.findall('xes:trace',ns):
        for string in trace.findall('xes:string',ns):
            if string.attrib['key'] == 'concept:name':

                # print(string.attrib['value'])
                log[string.attrib['value']] ={}
                count =0 ;
                for evn in trace.findall('xes:event',ns):

                    log[string.attrib['value']][count] ={}
                    for str in  evn.findall('xes:string',ns):
                        if str.attrib['key'] == 'concept:name':
                            log[string.attrib['value']][count]['concept:name'] = str.attrib['value']
                        if  str.attrib['key'] == 'org:resource':
                            log[string.attrib['value']][count]['org:resource'] = str.attrib['value']
                        if  str.attrib['key'] == 'lifecycle:transition':
                            log[string.attrib['value']][count]['lifecycle:transition'] = str.attrib['value']
                    for date in  evn.findall('xes:date',ns):
                        if  date.attrib['key'] == 'time:timestamp':
                            log[string.attrib['value']][count]['time:timestamp'] = datetime.strptime( date.attrib['value'][0:19], '%Y-%m-%dT%H:%M:%S') #1970-01-01T02:00:00+01:00
                    for num in  evn.findall('xes:int',ns):
                        if  num.attrib['key'] == 'cost':
                            log[string.attrib['value']][count]['cost'] = int(num.attrib['value'])
                    count +=1
    return log
def dependency_graph_file(file):
    dg ={}
    for case in file:
        for t in range(len(file[case])-1):
            dg.setdefault(file[case][t]["concept:name"],{})
            dg[file[case][t]["concept:name"]][file[case][t+1]["concept:name"]] = 1+dg[file[case][t]["concept:name"]].setdefault(file[case][t+1]["concept:name"],0)
    return dg
def alpha(log):
    ti = []
    to = []
    for l in log:
        if log[l][0]["concept:name"] not in ti:
            ti.append(log[l][0]["concept:name"])
        if log[l][len(log[l])-1]["concept:name"] not in to:
            to.append(log[l][len(log[l])-1]["concept:name"])
    Xw_list = []
    Tw_list = []
    matrix = {}
    file =dependency_graph_file(log)
    for i in file:
        if i not in Tw_list:
            Tw_list.append(i)
        for y in file[i]:
            if y not in Tw_list:
                Tw_list.append(y)
    for i in Tw_list:
        matrix[i] ={}
        for j in Tw_list:
            matrix[i][j] ="#"
    for i in file:
        for j in file[i]:
            if (matrix[i][j] =="#" )& (matrix[j][i] =="#") :
                matrix[i][j] ="-->"
                matrix[j][i] ="<--"
            else:
                matrix[i][j] ="||"
                matrix[j][i] ="||"
    for i in matrix:
        listAppend =[]
        for j in matrix[i]:
            if matrix[i][j] =="-->":
                listAppend.append(j)
                Xw_list.append([[i],[j]])
        comb =   combs(listAppend)
        # print(comb)
        for j in comb:
            if len(j)<2:
                continue
            count=1
            for t in j:
                if matrix[t][j[count]] != "#":
                    break
                count += 1
                if count == len(j):
                    Xw_list.append([[i],j])
                    break
    for i in matrix:
        listAppend =[]
        for j in matrix[i]:
            if matrix[i][j] =="<--":
                listAppend.append(j)
                Xw_list.append([[j],[i]])
        comb =   combs(listAppend)
        for j in comb:
            if len(j)<2:
                continue
            count=1
            for t in j:
                if matrix[t][j[count]] != "#":
                    break
                count += 1
                if count == len(j):
                    Xw_list.append([j,[i]])
                    break
    net = PetriNet()
    cn =  0
    while(len(Xw_list)>=cn):
        for j in range(cn+1,len(Xw_list)):
            if  Xw_list[cn] == Xw_list[j]:
                Xw_list.remove(Xw_list[cn])
                cn -=  1
                break
            if j == len(Xw_list)-1:
                break
        cn +=1
    y_log = []
    cn = 0
    while(len(Xw_list)>cn):
        noCandidate = True
        for j in range(0,len(Xw_list)):
            parrentX = False
            if len(Xw_list[j][0]) >len(Xw_list[cn][0]):

                for val in Xw_list[cn][0]:
                    if val in (Xw_list[j][0]) and (Xw_list[cn][1][0] in (Xw_list[j][1]) ):
                        parrentX = True
                    else:
                        parrentX = False

            parrentY = False

            if len(Xw_list[j][1]) > len(Xw_list[cn][1]):
                for val in Xw_list[cn][1]:

                    if val in (Xw_list[j][1]) and (Xw_list[cn][0][0] in (Xw_list[j][0]) ):
                        parrentY = True
                    else:
                        parrentY = False

            if parrentY ==True or parrentX ==True:

                noCandidate = False
        if noCandidate:
            y_log.append(Xw_list[cn])
        cn +=1
    count =-1
    Xw_list = y_log
    for n in matrix:
        net.add_transition(n,count)
        count -=1
    count =1
    net.add_place(0)
    net.add_place(99999)
    for starts in ti:
        net.add_edge(0,net.transition_name_to_id(starts))
    for ends in to:
        net.add_edge(net.transition_name_to_id(ends),99999)
    for x in Xw_list:
        for w in x[0]:
            net.add_place(count)
            net.add_edge(net.transition_name_to_id(w),count)
        for w in x[1]:
            net.add_place(count)
            net.add_edge(count,net.transition_name_to_id(w))
        count +=1
    net.add_marking(0)
    return net
def combs(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in combs(a[1:]):
        cs += [c, c+[a[0]]]
    return cs

def fitness_token_replay(file, net):
    # log
    dg ={}
    sum_m = 0
    sum_r = 0
    sum_c = 0
    sum_p = 0
    for case in file:
        list = []
        for t in range(len(file[case])):
            net.fire_transition(net.transition_name_to_id(file[case][t]["concept:name"]))
            list.append(file[case][t]["concept:name"])
        net.done()
        # print(list)
        # print(f"m: {net.missingToken()}, r: {net.remainingToken()}, c: {net.consumedToken()}, p: {net.producedToken()}")

        sum_m += net.missingToken()
        sum_r += net.remainingToken()
        sum_c += net.consumedToken()
        sum_p += net.producedToken()
        net.reInit()
    # print(sum_m)
    # print(sum_r)
    # print(sum_c)
    # print(sum_p)
    result =0.5*(1-sum_m/sum_c)+0.5*(1-sum_r/sum_p)
    return result


# log = read_from_file("extension-log-4.xes")
# log_noisy = read_from_file("extension-log-noisy-4.xes")
# # print(log)
# mined_model = alpha(log)
# print(round(fitness_token_replay(log, mined_model), 5))
# print(round(fitness_token_replay(log_noisy, mined_model), 5))
#

# mined_model = alpha(read_from_file("extension-log-4.xes"))
#
# def check_enabled(pn):
#     ts = ["record issue", "inspection", "intervention authorization", "action not required", "work mandate", "no concession", "work completion", "issue completion"]
#     for t in ts:
#         # print(t)
#         print (pn.is_enabled(pn.transition_name_to_id(t)))
#
#     print("")
# #
# #issue completion"/>"action not required"/> inspection"/>record issue
# trace = ["record issue", "inspection", "intervention authorization", "work mandate", "work completion", "issue completion"]
#
# for a in trace:
#     check_enabled(mined_model)
#     mined_model.fire_transition(mined_model.transition_name_to_id(a))
# mined_model.done()
# m = mined_model.missingToken()
# r = mined_model.remainingToken()
# c = mined_model.consumedToken()
# p = mined_model.producedToken()
# result =1- 0.5*(m/c)-0.5*(r/p)
# print (m )
# print (r )
# print (c )
# print (p )
# print (result)
#




# log = read_from_file("extension-log.xes")

# general statistics: for each case id the number of events contained
# for case_id in sorted(log):
#     print((case_id, len(log[case_id])))
#
# # details for a specific event of one case
# case_id = "case_123"
# event_no = 0
# print((log[case_id][event_no]["concept:name"], log[case_id][event_no]["org:resource"], log[case_id][event_no]["time:timestamp"],  log[case_id][event_no]["cost"]))
# # f = """
# Task_A;case_1;user_1;2019-09-09 17:36:47
# Task_B;case_1;user_3;2019-09-11 09:11:13
# Task_D;case_1;user_6;2019-09-12 10:00:12
# Task_E;case_1;user_7;2019-09-12 18:21:32
# Task_F;case_1;user_8;2019-09-13 13:27:41
#
# Task_A;case_2;user_2;2019-09-14 08:56:09
# Task_B;case_2;user_3;2019-09-14 09:36:02
# Task_D;case_2;user_5;2019-09-15 10:16:40
#
# Task_G;case_1;user_6;2019-09-18 19:14:14
# Task_G;case_2;user_6;2019-09-19 15:39:15
# Task_H;case_1;user_2;2019-09-19 16:48:16
# Task_E;case_2;user_7;2019-09-20 14:39:45
# Task_F;case_2;user_8;2019-09-22 09:16:16
#
# Task_A;case_3;user_2;2019-09-25 08:39:24
# Task_H;case_2;user_1;2019-09-26 12:19:46
# Task_B;case_3;user_4;2019-09-29 10:56:14
# Task_C;case_3;user_1;2019-09-30 15:41:22"""
#
# log = log_as_dictionary(f)
# print(log)
# dg = dependency_graph_inline(log)
# dg = dependency_graph_file(log)
# for ai in sorted(dg.keys()):
#     for aj in sorted(dg[ai].keys()):
#         print (ai, '->', aj, ':', dg[ai][aj])
#
