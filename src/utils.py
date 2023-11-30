import heapq


def build_graph(rates: list) -> dict:
    graph = {}
    for rate in rates:
        base_currency, target_currency = rate.name.split("/")

        if base_currency not in graph:
            graph[base_currency] = {}

        if target_currency not in graph:
            graph[target_currency] = {}

        graph[base_currency][target_currency] = rate.rate

        reverse_rate = 1 / rate.rate if rate.rate != 0 else None
        graph[target_currency][base_currency] = reverse_rate

    return graph


def find_shortest_path(graph: dict, start: str, end: str) -> list[str] | None:
    """
    dijkstra's algorithm
    """
    if start not in graph or end not in graph:
        return None

    distances = {currency: float("inf") for currency in graph}
    distances[start] = 1
    priority_queue = [(1, start, [start])]

    visited = set()

    while priority_queue:
        current_rate, current_currency, path = heapq.heappop(priority_queue)

        visited.add(current_currency)

        # if this is the target currency, return the rate and path
        if current_currency == end:
            return path

        # check each neighbour of the current currency
        for neighbour, rate in graph[current_currency].items():
            # calculate the new rate
            new_rate = current_rate * rate

            # if the new rate is lower than the previously known rate, and neighbour not visited,
            # update it and record the path
            if new_rate < distances[neighbour] and neighbour not in visited:
                distances[neighbour] = new_rate
                new_path = [*path, neighbour]
                heapq.heappush(priority_queue, (new_rate, neighbour, new_path))
    return None


def calculate_combined_rate(path: list, graph: dict) -> float:
    rate = 1
    for i in range(len(path) - 1):
        rate *= graph[path[i]][path[i + 1]]

    return rate
