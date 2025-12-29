if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())
    arr = list(arr)
    max = -100
    runner = -100
    for i in range(0, n):
        if arr[i] > max:
            runner = max
            max = arr[i]
        elif arr[i] > runner and arr[i] != max:
            runner = arr[i]
    print(runner)