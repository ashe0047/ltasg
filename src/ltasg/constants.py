from enum import Enum


DEFAULT_BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice/"


class TransportType(Enum):
    BUS = "bus"
    TRAIN = "mrt"
    TAXI = "taxi"

LTA_SERVICES = {
    "PUBLIC_TRANSPORT_SERVICES": {
        TransportType.BUS: {
            "ARRIVAL": "v3/BusArrival",
            "SERVICES": "BusServices",
            "ROUTES": "BusRoutes",
            "STOPS": "BusStops",
            "PV_BUS_STOPS": "PV/Bus",
            "PV_OD_BUS": "PV/ODBus",
            "PLANNED_BUS_ROUTES": "PlannedBusRoutes",
        },
        TransportType.TRAIN: {
            "PLATFORM_CROWD_DENSITY": {
                "REALTIME": "PCDRealTime",
                "FORECAST": "PCDForecast"
            },
            "SERVICE_ALERTS": "TrainServiceAlerts",
            "FACILITIES_MAINTENANCE": "v2/FacilitiesMaintenance",
            "PV_OD_TRAIN": "PV/ODTrain",
            "PV_TRAIN": "PV/Train",
        },
        TransportType.TAXI: {
            "AVAILABILITY": "Taxi-Availability",
            "STANDS": "TaxiStands",
        }
}}

TRAFFIC_SERVICES = {
    "CARPARK_AVAILABILITY": "CarParkAvailabilityv2",
    "ESTIMATED_TRAVEL_TIMES": "EstTravelTimes",
    "FAULTY_TRAFFIC_LIGHTS": "FaultyTrafficLights",
    "PLANNED_ROAD_OPENINGS": "RoadOpenings",
    "APPROVED_ROAD_WORKS": "RoadWorks",
    "TRAFFIC_IMAGES": "Traffic-Imagesv2",
    "TRAFFIC_INCIDENTS": "TrafficIncidents",
    "TRAFFIC_SPEED_BANDS": "v4/TrafficSpeedBands",
    "VMS": "VMS",
    "TRAFFIC_FLOW": "TrafficFlow",
    "FLOOD_ALERTS": "PubFloodAlerts",
}


OTHER_SERVICES = {
    "BICYCLE_PARKING": "BicycleParkingv2",
    "GEOSPATIAL_WHOLE_ISLAND": "GeospatialWholeIsland",
    "EV_CHARGING_POINTS": "EVChargingPoints",
    "EV_CHARGING_POINTS_BATCH": "EVCBatch",
}