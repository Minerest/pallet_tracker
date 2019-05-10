import requests


class Station:

    def __init__(self, station):
        self.station = station
        self.url = "http://127.0.0.1/drop_station"

    def make_the_drop(self, name, master_batch):
        if name[0] == "$" and name[-1] == "$":
            name = name.strip("$")
        else:
            return

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
    test_station = Station("test")
    test_station.make_the_drop("$EricDiaz$", "$123456792")
