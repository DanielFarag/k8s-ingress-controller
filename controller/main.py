from db import DB
from k8s import K8S


def main():
    db = DB("storage/database.sqlite")
    
    k8s = K8S()
    
    k8s.createCrd()

    k8s.configureNginx(db.all())

    for event in k8s.stream():
        print(event['action'])
        if event['action'] == 'ADDED':
            db.insert(event['data'])
        elif event['action'] == 'DELETED':
            db.delete(event['data']["id"])
        elif event['action'] == 'MODIFIED':
            db.update(event['data'])
        k8s.configureNginx(db.all())
        print(db.all())
if __name__ == '__main__':
    main()