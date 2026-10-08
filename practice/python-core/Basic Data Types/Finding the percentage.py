if __name__ == '__main__':
    n = int(input())
    student_marks = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()
    marks=0
    for i in student_marks[query_name]:
        marks=marks+i
    avg=marks/3
    #in print, % makes the quotation a special character where f denotes float type & .2 denotes that only the first 2 digits after the decimal will be printed
    print("%.2f"%avg)
    
