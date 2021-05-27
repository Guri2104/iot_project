# Python3 program to demonstrate working of heapq

from heapq import heapify, heappush, heappop


class Heap:
    def __init__(self, maximum, exclusion_list=None):
        self.max = maximum
        self.__current_size = maximum
        self.__heap = []
        heapify(self.__heap)
        for i in range(1, maximum+1):
            if i in exclusion_list:
                exclusion_list.remove(i)
                continue
            heappush(self.__heap, i)

    def pop_min(self):
        element = heappop(self.__heap)
        self.__current_size -= 1
        return element

    def heap_push(self, element):
        heappush(self.__heap, element)
        self.__current_size += 1

    def get_current_size(self):
        return self.__current_size
