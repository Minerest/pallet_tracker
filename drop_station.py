import requests
import modals

class Station:

    def __init__(self, station):
        self.station = station
        self.url = "http://127.0.0.1/drop_station"

    def make_the_drop(self, master_batch):

        Session = modals.db.get_session()
        name = Session.query(modals.Picker).filter(modals.MasterBatch.id == master_batch,
                                                   modals.MasterBatch.pickerid == modals.Picker.id)
        post_req = {
            "station": self.station,
            "picker": name,
            "masterid": master_batch
        }
        r = requests.post(url=self.url, data=post_req)
        if r.status_code >= 300:
            print(r.status_code)
            print(self.url)
            print(post_req)


if __name__ == "__main__":
    test_station = Station("Door 37")
    test_station.make_the_drop("$919191919")
