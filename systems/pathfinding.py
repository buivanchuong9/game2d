from collections import deque
import heapq

def bfs(start, goal, width, height, blocked):
    """
    Tìm đường đi ngắn nhất từ start đến goal bằng thuật toán BFS.
    blocked: tập hợp hoặc mảng 2D chứa các ô bị chặn.
    """
    if not start or not goal:
        return []
    
    queue = deque([start])
    came_from = {start: None}
    
    # Chuyển blocked thành set để tra cứu nhanh nếu nó là list of lists
    if isinstance(blocked, list):
        obstacles = set((x, y) for y, row in enumerate(blocked) for x, val in enumerate(row) if val)
    else:
        obstacles = blocked

    found = False
    while queue:
        current = queue.popleft()
        
        if current == goal:
            found = True
            break
            
        x, y = current
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in obstacles and (nx, ny) not in came_from:
                    came_from[(nx, ny)] = current
                    queue.append((nx, ny))
                    
    if not found:
        return []
        
    # Tái tạo đường đi
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def dfs(start, goal, width, height, blocked):
    """
    Tìm đường đi từ start đến goal bằng thuật toán DFS.
    """
    if not start or not goal:
        return []
    
    stack = [start]
    came_from = {start: None}
    
    if isinstance(blocked, list):
        obstacles = set((x, y) for y, row in enumerate(blocked) for x, val in enumerate(row) if val)
    else:
        obstacles = blocked

    found = False
    while stack:
        current = stack.pop()
        
        if current == goal:
            found = True
            break
            
        x, y = current
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in obstacles and (nx, ny) not in came_from:
                    came_from[(nx, ny)] = current
                    stack.append((nx, ny))
                    
    if not found:
        return []
        
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def heuristic_search(start, goal, width, height, blocked):
    """
    Tìm đường đi từ start đến goal chỉ dùng Heuristic (Greedy Best-First Search).
    """
    if not start or not goal:
        return []
        
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    pq = []
    heapq.heappush(pq, (0, start))
    came_from = {start: None}
    
    if isinstance(blocked, list):
        obstacles = set((x, y) for y, row in enumerate(blocked) for x, val in enumerate(row) if val)
    else:
        obstacles = blocked

    found = False
    while pq:
        _, current = heapq.heappop(pq)
        
        if current == goal:
            found = True
            break
            
        x, y = current
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in obstacles and (nx, ny) not in came_from:
                    came_from[(nx, ny)] = current
                    h = heuristic((nx, ny), goal)
                    heapq.heappush(pq, (h, (nx, ny)))
                    
    if not found:
        return []
        
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def astar(start, goal, width, height, blocked):
    """
    Tìm đường đi ngắn nhất từ start đến goal bằng thuật toán A*.
    """
    if not start or not goal:
        return []
        
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    pq = []
    heapq.heappush(pq, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    if isinstance(blocked, list):
        obstacles = set((x, y) for y, row in enumerate(blocked) for x, val in enumerate(row) if val)
    else:
        obstacles = blocked

    found = False
    while pq:
        _, current = heapq.heappop(pq)
        
        if current == goal:
            found = True
            break
            
        x, y = current
        for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in obstacles:
                    new_cost = cost_so_far[current] + 1
                    if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                        cost_so_far[(nx, ny)] = new_cost
                        priority = new_cost + heuristic((nx, ny), goal)
                        heapq.heappush(pq, (priority, (nx, ny)))
                        came_from[(nx, ny)] = current
                    
    if not found:
        return []
        
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
