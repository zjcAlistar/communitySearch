import rexxl as rx
import qm
import copy


class SearchItem(object):
    type = 1
    normal_factor = []
    common_factor = []
    filter_factor = []

    def __init__(self, t, para):
        self.type = t
        if t == 1:
            self.normal_factor = para
        else:
            self.common_factor = para[0]
            self.filter_factor = para[1]

    def print_all(self):
        if self.type == 1:
            print(self.normal_factor)
        else:
            print(self.common_factor)
            print(self.filter_factor)
        print("hello")

    pass


def get_simplified_expression(ornl=[]):
    result = qm.qm(ones=ornl)
    result_f = list(map(lambda x: list(map(lambda y: int(y) if y != 'X' else -1, x)), result))
    return result_f


def extract_common_factor(result_list, v_num):
    l = len(result_list)
    count = [0 for i in range(v_num)]
    checked = [0 for i in range(l)]
    for r in result_list:
        for i in range(v_num):
            if r[i] == 1:
                count[i] += 1
    search_list = []
    most_frequent = max(count)
    while most_frequent > 1:
        pos = count.index(most_frequent)
        temp = []
        for i in range(l):
            if result_list[i][pos] == 1 and checked[i] != 1:
                temp.append(copy.copy(result_list[i]))
                for j in range(v_num):
                    if result_list[i][j] == 1:
                        count[j] -= 1
                checked[i] = 1
        commons = []
        for i in range(v_num):
            flag = True
            for t in temp:
                if t[i] != 1:
                    flag = False
            if flag:
                commons.append(i)
        search_list.append(SearchItem(0, (commons, temp)))
        most_frequent = max(count)
    for i in range(l):
        if checked[i] != 1:
            search_list.append(SearchItem(1, copy.copy(result_list[i])))
    return search_list

if __name__ == '__main__':
    a = extract_common_factor([[1, -1, 1, 1], [1, 1, -1, 1], [-1, -1, -1, 0]], 4)
    for x in a:
        x.print_all()
    # rx.myinput()
    # rx.getVariable()
    # rx.parseInput()
    # rx.cal()
    # print(get_simplified_expression(rx.ornl))
    print("end")
