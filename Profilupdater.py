
# to use activeMq bridge
import stomp

conn = None




def main():
    print("producing start")




    hosts = [('localhost', 61613)]
    conn = stomp.Connection(hosts)
    conn.start()
    conn.connect('admin', 'admin', wait=True)
    with open(r'C:\Users\Oussama\PycharmProjects\scrape\immoscraping2\immoscraping/agencyurl.txt') as f:
        content = f.readlines()
        for l in range(len(content)):
            url = content[l]
            conn.send(body=url, destination='/queue/scrapy.seloger.agency.profile.queue')
    input("Enter to exit")
    conn.stop()

if __name__ == "__main__":
    # execute only if run as a script

    main()

