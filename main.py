
from src.ltasg.transport.bus import Bus
from src.ltasg.transport.taxi import Taxi
from src.ltasg.transport.train import Train
import asyncio
b = Bus("http://datamall2.mytransport.sg/ltaodataservice/", "33AWj1PMQdeNJzBFp+YH0Q==")
t = Taxi("http://datamall2.mytransport.sg/ltaodataservice/", "33AWj1PMQdeNJzBFp+YH0Q==")
tr = Train("http://datamall2.mytransport.sg/ltaodataservice/", "33AWj1PMQdeNJzBFp+YH0Q==")
s = asyncio.run(b.stop_services(bus_stop_code=71111))
print(s)
