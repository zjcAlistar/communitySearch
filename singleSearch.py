# encoding: utf-8
import copy
import math
from random import sample


def get_graph(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    adjacent_dic = {}
    adjacent_dic_s = {}
    vertices_dic = {}
    for line in lines:
        if not line.startswith("#"):
            edge_str = line.strip("\n").split("\t")
            v1 = int(edge_str[0])
            v2 = int(edge_str[1])
            if v1 in adjacent_dic:
                adjacent_dic_s[v1].add(v2)
            else:
                adjacent_dic_s[v1] = {v2}
            adjacent_dic[v1] = list(adjacent_dic_s[v1])
    for x in adjacent_dic:
        vertices_dic[x] = len(adjacent_dic[x])
    return adjacent_dic, vertices_dic


def get_subgraph(adjacent, vertex_set):
    new_adjacent = {}
    for v in adjacent:
        if v in vertex_set:
            new_adjacent[v] = set(adjacent[v]) & vertex_set
    return new_adjacent


def vertex_delete(adjacent, o_set):
    new_adjacent = copy.deepcopy(adjacent)
    for o in o_set:
        neighbor = new_adjacent.pop(o)
        for n in neighbor:
            if n in new_adjacent.keys():
                new_adjacent[n].remove(o)
    return new_adjacent


def global_cst_solution(adjacent, vertices, k, q):
    queue = [set(vertices.keys())]
    final = []
    while queue:
        c = queue.pop()
        if q not in c:
            continue
        v = sorted(list(c), key=lambda x: vertices[x])
        min_v = v[0]
        tmp_d = vertices.pop(min_v)
        # tmp_d = vertices[min_v]
        # print(min_v, tmp_d)
        # if min_v == q:
        #     tmp_min_v = list(filter(lambda x: vertices[x] == tmp_d and x != q, v))
        #     if tmp_min_v:
        #         min_v = tmp_min_v[0]
        #         tmp_d = vertices.pop(min_v)
        #         print(min_v, tmp_d)
        #     else:
        #         del vertices[min_v]
        # else:
        #     del vertices[min_v]

        if tmp_d >= k:
            final.append(copy.deepcopy(c))
        tmp_v = list(filter(lambda x: x != min_v, v))
        tmp_n = adjacent.pop(min_v)
        for n in tmp_n:
            adjacent[n].remove(min_v)
            vertices[n] -= 1
        if tmp_v:
            candidates = get_connected_components(copy.deepcopy(adjacent), set(tmp_v))
            for candidate in candidates:
                queue.append(candidate)
    return final[-1]


def get_connected_components(adjacent, n_set):
    v_set = copy.copy(n_set)
    o_set = copy.copy(n_set)
    cc = []
    while v_set != set():
        r_set = set()
        tmp_r_set = set()
        tmp_r_set.add(v_set.pop())
        while tmp_r_set-r_set != set():
            delta_set = tmp_r_set - r_set
            for d in delta_set:
                r_set.add(d)
                for n in set(adjacent[d]) & o_set:
                    tmp_r_set.add(n)
        v_set -= r_set
        cc.append(copy.deepcopy(r_set))
    return cc


def local_cst_solution(adjacent, k, q):
    temp_degree_dic = {q: 0}
    min_degree = 0
    community = {q}

    while min_degree < k:
        min_vs = list(dict(filter(lambda x: x[1] == min_degree, temp_degree_dic.items())))
        candidates = set()
        for min_v in min_vs:
            candidates |= set(adjacent[min_v])
        candidates -= community
        select = sorted(list(candidates), key=lambda x: len(community & set(adjacent[x])), reverse=True)
        if select:
            n = select[0]
            community.add(n)
            neighbor_in_c = community & set(adjacent[n])
            for neighbor in neighbor_in_c:
                temp_degree_dic[neighbor] += 1
            temp_degree_dic[n] = len(neighbor_in_c)
            min_degree = sorted(temp_degree_dic.items(), key=lambda x: x[1])[0][1]
        else:
            return set()
    return community


def m_local_cst_solution(adjacent, k, q_set, o_set):
    community = copy.copy(q_set)
    origin_partition = copy.copy(q_set)
    partitions = []
    while origin_partition:
        temp_partition = set()
        s = sample(origin_partition, 1)[0]
        temp_partition.add(s)
        origin_partition.remove(s)
        neighbors = set(adjacent[s])
        new_vs = neighbors & origin_partition
        while new_vs:
            temp_partition |= new_vs
            origin_partition -= new_vs
            for v in new_vs:
                neighbors |= set(adjacent[v])
            neighbors -= temp_partition
            new_vs = neighbors & origin_partition
        partitions.append(temp_partition)
    while True:
        candidates = set()
        candidates_info_dic = {}
        for q in community:
            for n in adjacent[q]:
                if n not in community and n not in o_set:
                    candidates.add(n)
                    candidates_info_dic[n] = {}
                    candidates_info_dic[n][-1] = 0
                    for i in range(len(partitions)):
                        if len(set(adjacent[n]) & partitions[i]) > 0:
                            candidates_info_dic[n][i] = 1
                        else:
                            candidates_info_dic[n][i] = 0
                        candidates_info_dic[n][-1] += candidates_info_dic[n][i]
        part_connects = set(map(lambda x: candidates_info_dic[x][-1], candidates))
        max_parts_connects = max(part_connects)
        new_candidates = set(filter(lambda x: candidates_info_dic[x][-1] == max_parts_connects, candidates))
        if max_parts_connects == 1:
            min_p = len(community)+1
            for p in partitions:
                t = len(p)
                if t < min_p:
                    min_p = t
            temp_new_candidates = set()
            print(min_p)
            for nc in new_candidates:
                for key in candidates_info_dic[nc].keys():
                    # print(partitions[key])
                    if key > -1 and candidates_info_dic[nc][key] > 0 and len(partitions[key]) == min_p:
                        temp_new_candidates.add(nc)
            new_candidates = temp_new_candidates
        commons = {}
        temp_new_candidates = set()
        for nc in new_candidates:
            commons[nc] = len(set(adjacent[nc]) & community)
        max_commons = max(commons.values())
        for nc in new_candidates:
            if commons[nc] == max_commons:
                temp_new_candidates.add(nc)
        new_candidates = temp_new_candidates
        new_candidate_degree = 0
        next_v = -1
        for nc in new_candidates:
            if len(set(adjacent[nc]) - o_set) > new_candidate_degree:
                new_candidate_degree = len(adjacent[nc])
                next_v = nc
        if next_v == -1:
            print("ERROR")
        else:
            community.add(next_v)
            temp_partitions = []
            temp_p = set()
            for i in range(len(partitions)):
                if candidates_info_dic[next_v][i] == 1:
                    temp_p |= partitions[i]
                else:
                    temp_partitions.append(partitions[i])
            temp_p.add(next_v)
            temp_partitions.append(temp_p)
            partitions = temp_partitions

        min_degree = len(community)+1
        for member in community:
            d = len(set(adjacent[member]) & community)
            if d < min_degree:
                min_degree = d
        if min_degree >= k:
            break
    return community


def get_edges(adjacent):
    edges = set()
    for src in adjacent:
        for dst in adjacent[src]:
            if src < dst:
                edges.add((src, dst))
            else:
                edges.add((dst, src))
    return edges


def truss_decomposition(edges, adjacent):
    sup_list = list(map(lambda x: (x, len(set(adjacent[x[0]]) & set(adjacent[x[1]]))), edges))
    sup_list = sorted(sup_list, key=lambda x: x[1])
    sup_dic = dict(sup_list)
    truss_dic = {}
    k = 2
    while sup_list:
        while sup_list[0][1] <= k-2:
            e = sup_list[0][0]
            cn = set(adjacent[e[0]]) & set(adjacent[e[1]])
            for w in cn:
                if e[0] < w:
                    sup_dic[(e[0], w)] -= 1
                else:
                    sup_dic[(w, e[0])] -= 1
                if e[1] < w:
                    sup_dic[(e[1], w)] -= 1
                else:
                    sup_dic[(w, e[1])] -= 1
            truss_dic[e] = k
            sup_dic.pop(e)
            adjacent[e[0]].remove(e[1])
            adjacent[e[1]].remove(e[0])
            sup_list = sorted(sup_dic.items(), key=lambda x: x[1])
            if not sup_list:
                break
        k += 1
    return truss_dic


def tcp_index_construction(t_dic, adjacent, edges):
    vs = list(adjacent.keys())
    t_x_dic = {}
    for v in vs:
        t_x_dic[v] = {}
        temp_edges = list(filter(lambda x: x[0] in adjacent[v] and x[1] in adjacent[v], edges))
        w_dic = {}
        # print(v)
        for (y, z) in temp_edges:
            if v < y:
                e1 = (v, y)
            else:
                e1 = (y, v)
            if v < z:
                e2 = (v, z)
            else:
                e2 = (z, v)
            w_dic[(y, z)] = min(t_dic[(y, z)], t_dic[e1], t_dic[e2])
        if not w_dic.values():
            k_max = 1
        else:
            k_max = max(w_dic.values())
        t_o = list(map(lambda x: {x}, adjacent[v]))
        for k in range(2, k_max+1)[::-1]:
            sk = list(filter(lambda x: w_dic[x] == k, list(w_dic.keys())))
            for (y, z) in sk:
                c1 = list(filter(lambda x: y in x, t_o))
                c2 = list(filter(lambda x: z in x, t_o))
                if len(c1) > 1 or len(c2) > 1:
                    print("error")
                    return t_x_dic
                elif c1[0] != c2[0]:
                    t_o.append(c1[0] | c2[0])
                    t_o.remove(c1[0])
                    t_o.remove(c2[0])
            t_x_dic[v][k] = copy.deepcopy(t_o)
    return t_x_dic


def k_truss_processing(truss, tcp_index, adjacent, k, q):
    visited = set()
    l = -1
    c = []
    for u in adjacent[q]:
        if u < q:
            e = (u, q)
        else:
            e = (q, u)
        if truss[e] >= k and e not in visited:
            que = []
            c.append(set())
            l += 1
            que.append(e)
            while que:
                (x, y) = que.pop()
                if (x, y) not in visited:
                    if k in tcp_index[x]:
                        candi = list(filter(lambda a: y in a, tcp_index[x][k]))
                    else:
                        candi = {y}
                    if len(candi) != 1:
                        print("error")
                        return set()
                    else:
                        vk = candi[0]
                        for z in vk:
                            visited.add((x, z))
                            c[l].add((x, z))
                            if (z, x) not in visited:
                                que.append((z, x))
    edge_result = set()
    for i in range(0, len(c)):
        edge_result |= c[i]
    v_result = set()
    for er in edge_result:
        v_result.add(er[0])
        v_result.add(er[1])
    return v_result


def label_weighting(adjacent, q_set, out_set, decay_factor, iterate_times):
    associated_score_dic = {}
    candidate_set = set()
    for q in q_set:
        associated_score_dic[q] = 1.0
        candidate_set.add(q)
        candidate_set |= set(adjacent[q])
    for o in out_set:
        associated_score_dic[o] = -1.0
        candidate_set.add(o)
        candidate_set |= set(adjacent[o])
    for n in adjacent.keys():
        if n not in q_set and n not in out_set:
            associated_score_dic[n] = 0

    for i in range(iterate_times):
        temp_associated_score_dic = copy.deepcopy(associated_score_dic)
        for c in candidate_set:
            if c not in q_set and c not in out_set:
                voters = set(associated_score_dic.keys()) & set(adjacent[c])
                temp_associated_score_dic[c] = 0
                for v in voters:
                    temp_associated_score_dic[c] += associated_score_dic[v]  # *(1-math.e**(1-len(adjacent[v])))
                temp_associated_score_dic[c] /= len(voters)
                temp_associated_score_dic[c] *= decay_factor
        for key in temp_associated_score_dic.keys():
            candidate_set |= set(adjacent[key])
        associated_score_dic = copy.deepcopy(temp_associated_score_dic)
    return associated_score_dic


def label_weighting_search(adjacent, score_dic, threshold, q_set):
    o_set = set(score_dic.keys())
    temp_community_set = set(filter(lambda x: score_dic[x] >= threshold, o_set))
    cc = get_connected_components(adjacent, temp_community_set)
    print(cc)
    if len(cc) == 1:
        return cc[0]
    else:
        for c in cc:
            if c & q_set == q_set:
                return c
        new_cc = []
        for c in cc:
            if c & q_set != set():
                new_cc.append(c)
        while len(new_cc) > 1:
            candidates = set()
            connect_dic = {}
            for i in range(len(new_cc)):
                for v in new_cc[i]:
                    for n in set(adjacent[v]) & temp_community_set:
                        if n not in (q_set | o_set):
                            candidates.add(n)
                            if n not in connect_dic:
                                connect_dic[n] = [i]
                            else:
                                connect_dic[n].append(i)
            f_c = 0
            max_connects = 0
            connects = []
            for c in candidates:
                if len(connect_dic[c]) > max_connects:
                    max_connects = len(connect_dic[c])
                    f_c = c
                    connects = connect_dic[c]
            if f_c != 0:
                temp_cc = []
                temp_new_c = {f_c}
                for i in range(len(cc)):
                    if i not in connects:
                        temp_cc.append(cc[i])
                    else:
                        temp_new_c |= cc[i]
                        temp_cc.append(temp_new_c)
                new_cc = copy.deepcopy(temp_cc)
            else:
                new_cc = [new_cc[0]]
        return new_cc[0]

    # if len(cc) == 1:
    #     return cc[0]
    # else:
    #
    #     while len(cc) > 1:
    #         candidates = set()
    #         connect_dic = {}
    #         print(cc)
    #         for i in range(len(cc)):
    #             for v in cc[i]:
    #                 # print("!!!")
    #                 # print(v)
    #                 # if v == 0:
    #                 #     print(i)
    #                 #     print(cc)
    #                 # print("???")
    #                 for n in set(adjacent[v]) & temp_community_set:
    #                     if n not in o_set:
    #                         candidates.add(n)
    #                         if n not in connect_dic:
    #                             connect_dic[n] = [i]
    #                         else:
    #                             connect_dic[n].append(i)
    #         f_c = 0
    #         max_connects = 0
    #         connects = []
    #         for c in candidates:
    #             if len(connect_dic[c]) > max_connects:
    #                 max_connects = len(connect_dic[c])
    #                 f_c = c
    #                 connects = connect_dic[c]
    #         temp_cc = []
    #         temp_new_c = {f_c}
    #         for i in range(len(cc)):
    #             if i not in connects:
    #                 temp_cc.append(cc[i])
    #             else:
    #                 temp_new_c |= cc[i]
    #         temp_cc.append(temp_new_c)
    #         cc = copy.deepcopy(temp_cc)
    #     return cc[0]

if __name__ == "__main__":
    a_dic, v_dic = get_graph("football.txt")
    # # r = local_cst_solution(copy.deepcopy(a_dic), 7, 9)
    # # print(r)
    # # print(get_edges(a_dic))
    # trussness = truss_decomposition(get_edges(copy.deepcopy(a_dic)), copy.deepcopy(a_dic))
    # tcp_index_dic = tcp_index_construction(trussness, copy.deepcopy(a_dic), get_edges(copy.deepcopy(a_dic)))
    # print(k_truss_processing(trussness, tcp_index_dic, a_dic, 6, 90))

    # result = label_weighting(a_dic, {1, 2}, {}, 0.5, 6)
    # print(result)
    # print(label_weighting_search(a_dic, result, 0.05, {1, 2}))
    print(a_dic)

