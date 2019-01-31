import json


def split_download_list_to_10000_items():
    courts = open('data/txcourts details.json')
    for id, court in enumerate(courts.readlines()):
        if id % 22917 == 0:
            print(id)
            result_file = open('data/div' + str(int(id / 22917 + 1)) + '.json', 'w')
        result_file.write(court)

if __name__ == '__main__':
    court_file = open('data/txcourts details.json')
    court_infos = []
    for court in court_file.readlines():
        if court.__contains__('Your search found no results. Try broadening your search criteria.'):
            continue
        court_infos.append(json.loads(court))
    court_file.close()

    print(len(court_infos))
    court_file = open('data/txcourts details.json', 'w')
    for case in court_infos:
        court_file.write(json.dumps(case) + '\n')
    court_file.close()

    split_download_list_to_10000_items()
