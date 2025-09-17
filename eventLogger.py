# Joachim Knudsen s072446

import xml.etree.ElementTree as ET
import petrinet
from datetime import datetime
from unittest import skipIf


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
    Xw_list = []
    Tw_list = []
    matrix = {}
    # for case in log:
    #     for t in range(len(log[case])-1):
    #         Tw_list.setdefault(log[case][t]["concept:name"],{})
    #         Tw_list[log[case][t]["concept:name"]][log[case][t+1]["concept:name"]] = 1+Tw_list[log[case][t]["concept:name"]].setdefault(log[case][t+1]["concept:name"],0)
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
        print(matrix[i])
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
    net = petrinet.PetriNet()
    place = ["start","end"]
    # edgeTS = {"start":["record issue"]}
    # edgeST = {"end": ["issue completion"]}
    count =-1
    for n in matrix:

        net.add_transition(n,count)
        count -=1
    count =1
    for x in Xw_list:
        for w in x[0]:

            net.add_place(count)
            net.add_edge(net.transition_name_to_id(w),count)
            print([net.transition_name_to_id(w),count])
        for w in x[1]:

            net.add_place(count)
            net.add_edge(count,net.transition_name_to_id(w))
            print([count,net.transition_name_to_id(w)])
        count +=1
    net.add_marking(1)
    return net
def combs(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in combs(a[1:]):
        cs += [c, c+[a[0]]]
    return cs
alpha(read_from_file("extension-log.xes"))

mined_model = alpha(read_from_file("extension-log.xes"))

def check_enabled(pn):
    ts = ["record issue", "inspection", "intervention authorization", "action not required", "work mandate", "no concession", "work completion", "issue completion"]
    for t in ts:
        print (pn.is_enabled(pn.transition_name_to_id(t)))
    print("")
#
#
trace = ["record issue", "inspection", "intervention authorization", "work mandate", "work completion", "issue completion"]
for a in trace:
    check_enabled(mined_model)
    mined_model.fire_transition(mined_model.transition_name_to_id(a))


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
