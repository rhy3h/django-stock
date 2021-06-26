def progress_bar(prefix, count, length):
    size = 50
    print("%s[%s%s] %d/%d (%d%%)" % (prefix, '#'*(int)(count / length * size), "."*(size - (int)(count / length * size)), count, length, (count / length * 100)), end='\r')