from collections import deque
import heapq


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(node, width, height, blocked):
    x, y = node
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in blocked:
            yield (nx, ny)


def reconstruct(came_from, start, goal):
    if goal not in came_from:
        return []
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def bfs(start, goal, width, height, blocked):
    queue = deque([start])
    came_from = {start: start}
    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct(came_from, start, goal)
        for nxt in neighbors(current, width, height, blocked):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)
    return []


def dfs(start, goals, width, height, blocked):
    stack = [start]
    parents = {start: start}
    visited = set()
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        if current in goals:
            return reconstruct(parents, start, current)
        next_nodes = list(neighbors(current, width, height, blocked))
        next_nodes.reverse()
        for nxt in next_nodes:
            if nxt not in parents:
                parents[nxt] = current
            if nxt not in visited:
                stack.append(nxt)
    return []


def greedy_safe(start, goal, width, height, blocked, danger_map):
    heap = [(danger_map.get(start, 0) + manhattan(start, goal), start)]
    came_from = {start: start}
    cost_so_far = {start: 0}
    while heap:
        _, current = heapq.heappop(heap)
        if current == goal:
            return reconstruct(came_from, start, goal)
        for nxt in neighbors(current, width, height, blocked):
            new_cost = cost_so_far[current] + 1 + danger_map.get(nxt, 0)
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + danger_map.get(nxt, 0)
                heapq.heappush(heap, (priority, nxt))
                came_from[nxt] = current
    return []


def a_star(start, goal, width, height, blocked, danger_map=None):
    danger_map = danger_map or {}
    heap = [(0, start)]
    came_from = {start: start}
    cost_so_far = {start: 0}
    while heap:
        _, current = heapq.heappop(heap)
        if current == goal:
            return reconstruct(came_from, start, goal)
        for nxt in neighbors(current, width, height, blocked):
            move_cost = 1 + danger_map.get(nxt, 0)
            new_cost = cost_so_far[current] + move_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + manhattan(nxt, goal)
                heapq.heappush(heap, (priority, nxt))
                came_from[nxt] = current
    return []
