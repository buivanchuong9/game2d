from collections import deque

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
