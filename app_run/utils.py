from geopy import distance


def get_distance_in_km(coordinates: list[tuple[float, float]]):
    return round(distance.distance(*coordinates).kilometers, 3)