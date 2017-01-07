if __name__ == '__main__':
    list = open('list.txt')
    proxies = open('proxies.txt', 'w')

    print("start to format...")
    for item in list.readlines():
        proxy = "http://" + item
        proxies.write(proxy)

    list.close()
    proxies.close()
    print("finished.")