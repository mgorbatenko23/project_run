from geopy import distance


def get_distance_in_km(coordinates: list[tuple[float, float]]):
    return round(distance.distance(*coordinates).kilometers, 2)


def get_distance_to_object(coordinates_1, coordinates_2):
    return round(distance.distance(coordinates_1, coordinates_2).meters, 2)


def get_seconds_between_dates(date_end, date_start):
    time_diff = date_end - date_start
    return int(time_diff.total_seconds())