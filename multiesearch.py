# encoding: utf-8
import copy
import rexxl
import singleSearch as ss
import optimal_expression as oe


def check_connect(adjacent, target_set):
    tmp_list = list(target_set)
    o_size = 0
    n_size = 1
    some_set = set()
    new_some_set = {tmp_list[0]}
    while n_size > o_size:
        some_set = copy.copy(new_some_set)
        for x in some_set:
            new_some_set |= set(adjacent[x])
        new_some_set = new_some_set & target_set
        o_size = len(some_set)
        n_size = len(new_some_set)
    if n_size == len(target_set):
        return True
    else:
        return False


def check_satisfied(r_set, related_p, principles):
    for i in range(len(related_p)):
        if principles[i] == 1:
            if not related_p[i] in r_set:
                return False
        elif principles[i] == 0:
            if related_p[i] in r_set:
                return False
    return True


def multisearch_transfer(query_list, adjacent):
    if not query_list:
        return {}, 0
    new_point = query_list[0]
    new_neighbors = set()
    for q in query_list:
        new_neighbors |= set(adjacent[q])
        adjacent.pop(q)
    new_neighbors = new_neighbors - set(query_list)
    for p in adjacent:
        adjacent[p] = list(filter(lambda x: x not in query_list, adjacent[p]))
    for np in new_neighbors:
        adjacent[np].append(new_point)
    adjacent[new_point] = list(new_neighbors)
    return adjacent, new_point


def query_search(related_points, principle, adjacent, method, k):
    if not len(related_points) == len(principle):
        return set()
    in_list = []
    out_list = []
    not_care_list = []
    for i in range(0, len(related_points)):
        if principle[i] == 1:
            in_list.append(related_points[i])
        elif principle[i] == 0:
            out_list.append(related_points[i])
        else:
            not_care_list.append(related_points[i])
    print(in_list)
    if method == 1:  # 超节点 k-truss sfs
        new_adjacent, new_q = multisearch_transfer(in_list, copy.deepcopy(adjacent))
        truss = ss.truss_decomposition(ss.get_edges(copy.deepcopy(new_adjacent)), copy.deepcopy(new_adjacent))
        tcp_index = ss.tcp_index_construction(truss, copy.deepcopy(new_adjacent), ss.get_edges(copy.deepcopy(new_adjacent)))
        proto_result = ss.k_truss_processing(truss, tcp_index, new_adjacent, k, new_q)
        full_result = copy.copy(proto_result)
        for o in out_list:
            if o in full_result:
                return set()
        if full_result:
            full_result.remove(new_q)
            full_result |= set(in_list)
            if check_connect(adjacent, full_result):
                return full_result
            else:
                return set()
        return full_result
    elif method == 2:    # 超节点 k-core sfs
        new_adjacent, new_q = multisearch_transfer(in_list, copy.deepcopy(adjacent))
        proto_result = ss.local_cst_solution(copy.deepcopy(new_adjacent), k, new_q)
        full_result = copy.copy(proto_result)
        print(full_result)
        for o in out_list:
            if o in full_result:
                return set()
        if full_result:
            full_result.remove(new_q)
            full_result |= set(in_list)
            if check_connect(adjacent, full_result):
                return full_result
            else:
                return set()
    elif method == 3:  # filter-search k-core
        new_adjacent = ss.vertex_delete(adjacent, out_list)
        proto_result = ss.m_local_cst_solution(copy.deepcopy(new_adjacent), k, in_list, {})
        full_result = copy.copy(proto_result)
        for o in out_list:
            if o in full_result:
                return set()
        return full_result
    elif method == 4: # on-the-fly k-core
        proto_result = ss.m_local_cst_solution(copy.deepcopy(adjacent), k, in_list, out_list)
        full_result = copy.copy(proto_result)
        return full_result
    elif method == 5:  # k-truss filter-search
        new_adjacent = ss.vertex_delete(adjacent, out_list)
        truss = ss.truss_decomposition(ss.get_edges(copy.deepcopy(new_adjacent)), copy.deepcopy(new_adjacent))
        tcp_index = ss.tcp_index_construction(truss, copy.deepcopy(new_adjacent),
                                              ss.get_edges(copy.deepcopy(new_adjacent)))
        if len(in_list) >= 1:
            proto_result = ss.k_truss_processing(truss, tcp_index, new_adjacent, k, in_list[0])
            full_result = copy.copy(proto_result)
            for i in in_list:
                if i not in full_result:
                    return set()
            return full_result
        else:
            print("ERROR no search object!")
        return set()
    elif method == 6: # k-core sfs
        proto_result = ss.m_local_cst_solution(copy.deepcopy(adjacent), k, in_list, {})
        full_result = copy.copy(proto_result)
        flag = False
        for o in out_list:
            if o in full_result:
                flag = True
                break
        if flag:
            sub_adjacent = ss.get_subgraph(adjacent, full_result)
            new_adjacent = ss.vertex_delete(sub_adjacent, out_list)
            full_result = ss.m_local_cst_solution(copy.deepcopy(new_adjacent), k, in_list, {})
        return full_result
    else:
        return set()


def complex_search(bool_expression, adjacent, method, k):
    rexxl.sInput = bool_expression
    rexxl.getVariable_num()
    rexxl.parseInput()
    rexxl.cal('num')
    related_p = list(map(lambda x: int(x), rexxl.variable))
    print(related_p)
    all_r = []
    simple_prs = oe.get_simplified_expression(rexxl.ornl)
    print(rexxl.ornl)
    print("@^&")
    print(simple_prs)
    v_nums = len(rexxl.variable)
    extracted_simple_prs = oe.extract_common_factor(simple_prs, v_nums)
    # for pr in rexxl.ornl:
    #     pp = bin(pr)[2:].zfill(len(related_p))
    #     num_pp = []
    #     for i in range(0, len(pp)):
    #         num_pp.append(int(pp[i]))
    #     print(num_pp)
    #     result = query_search(related_p, num_pp, adjacent, method, k)
    #     print(result)
    #     if result != set():
    #         all_r.append(result)
    for espr in extracted_simple_prs:
        if espr.type == 1:
            print("!!!")
            print(related_p)
            print(espr.normal_factor)
            result = query_search(related_p, espr.normal_factor, adjacent, method, k)
        else:
            temp_pr = []
            temp_related_p = []
            for x in espr.common_factor:
                temp_pr.append(espr.filter_factor[0][x])
                temp_related_p.append(related_p[x])
            pre_result = query_search(temp_related_p, temp_pr, adjacent, method, k)
            result = []
            temp_other_related_p = []
            for x in related_p:
                if not x in temp_related_p:
                    temp_other_related_p.append(x)
            for pr in pre_result:
                flag = True
                for f in espr.filter_factor:
                    temp_other_pr = []
                    for i in range(len(f)):
                        if not i in espr.common_factor:
                            temp_other_pr.append(f[i])
                    if not check_satisfied(pr, temp_other_related_p, temp_other_pr):
                        flag = False
                        break
                if flag:
                    result.append(pr)
        print(result)
        if result != set():
            all_r.append(result)
    return all_r


def get_gt(gt_filename):
    gt_f = open(gt_filename, "r")
    lines = gt_f.readlines()
    gt_dic = {}
    gt_dic_reverse = {}
    for line in lines:
        if not line.startswith("#"):
            data_str = line.strip("\n").split("\t")
            v = int(data_str[0])
            c = int(data_str[1])
            gt_dic[v] = c
            if c in gt_dic_reverse:
                gt_dic_reverse[c].append(v)
            else:
                gt_dic_reverse[c] = [v]
    return gt_dic, gt_dic_reverse


def correct_measure(result, q, gt_dic, gt_dic_r):
    truth = gt_dic[q]
    true_c = gt_dic_r[truth]
    correct = result & set(true_c)
    if result == set():
        return 0
    pre = len(correct)/len(result)
    rec = len(correct)/len(true_c)
    if not (pre == 0 and rec == 0):
        f_measure = 2*pre*rec/(pre+rec)
    else:
        f_measure = 0
    return f_measure


def correct_measure_with_t(result, true_c):
    correct = result & set(true_c)
    if result == set():
        return 0
    pre = len(correct)/len(result)
    rec = len(correct)/len(true_c)
    if not (pre == 0 and rec == 0):
        f_measure = 2*pre*rec/(pre+rec)
    else:
        f_measure = 0
    return f_measure


def local_modularity(adjacent, result_c):
    local_v = set()
    all_es = ss.get_edges(adjacent)
    for v in result_c:
        local_v.add(v)
        local_v |= set(adjacent[v])
    in_edges = list(filter(lambda x: x[0] in result_c and x[1] in result_c, all_es))
    local_edges = list(filter(lambda x: x[0] in result_c and x[1] in local_v, all_es))
    return len(in_edges)/len(local_edges)


if __name__ == "__main__":
    print("请输入一个社区查询条件：")
    # expr = input()
    a_dic, v_dic = ss.get_graph("football.txt")
    # print(a_dic[98])
    # print(a_dic[117])
    #r = query_search([98, 117, 1], [1, 1, 0], a_dic, 2, 2)

    r = ss.m_local_cst_solution(a_dic, 7, {12, 17}, set())

    # r = complex_search(expr, a_dic, 1, 5)
    print(r)
    #
    # print(local_modularity(a_dic, r[0]))
    #

    # result = ss.label_weighting(a_dic, {12, 17}, {40}, 1, 6)
    # print(result)
    # r = ss.label_weighting_search(a_dic, result, 0.18, {12, 17})
    # print(r)

    gt, gt_r = get_gt("football_gt.txt")
    # print(gt_r)
    print(correct_measure_with_t(r, gt_r[gt[12]]))
    print(local_modularity(a_dic, r))
    # LFR