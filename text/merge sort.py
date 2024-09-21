def mergeSort(array):
    if len(array) <= 1:
        return array
    
    midpoint = len(array) // 2
    leftarr = array[:midpoint]
    rightarr = array[midpoint:]
    
    sortedLarr = mergeSort(leftarr)
    sortedRarr = mergeSort(rightarr)

    return merge(sortedLarr, sortedRarr)

def merge(L, R):
    result = []
    i = 0 
    j = 0 

    while i < len(L) and j < len(R):
        if L[i] < R[j]:
            result.append(L[i])
            i += 1
        else:
            result.append(R[j])
            j += 1

    # The above while loop terminates once one of the sub-arrays has put all it's elements into the result list.Meaning, there will still be elements in the other array. 
    # So the result list needs to include the rest of the elements, which are already sorted as they have been built up from sorted 2-length lists. 
    result.extend(L[i:])
    result.extend(R[j:])

    return result

unsortedArr = [3, 7, 6, -10]
sortedArr = mergeSort(unsortedArr)
strSorted = []
for i in range(0, len(unsortedArr)):
    strSorted.append(str(sortedArr[i]))
print("Sorted array:", strSorted)
print(strSorted[1:])