from datetime import datetime


class Solution(object):
    def topKFrequent(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        """
        array = {}
        for i in nums:
            if i in array:
                array[i] += 1
            else:
                array[i] = 1
        sorted_array = sorted(array, key=array.get, reverse=True)
        return sorted_array[:k]

        # for i in nums:
        #     print(nums)
        #     x = nums.count(i)
        #     nums = [a for a in nums if a != i]
        #     array.append(x)
        #     print(nums)
        # return array


start_time = datetime.now()
nums = [4,1,-1,2,-1,2,3]
k = 2
s = Solution()
print(s.topKFrequent(nums, k))
print(datetime.now() - start_time)
# k = 1
# print(s.topKFrequent(nums, k))
