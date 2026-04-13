# Deploy Notes

## Local

```bash
cd SwarmShot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Web Build

Project nay van la `pygame`, nen cach deploy web phu hop nhat la build qua `pygbag`.

```bash
cd SwarmShot
pip install pygbag
python3 -m pygbag main.py
```

Sau khi build, thu muc `build/web/` co the dua len:

- GitHub Pages
- Netlify
- Vercel static hosting

## Product Notes

- Game da co `menu`, `intro`, `pause`, `win`, `lose`
- Co `chapter flow` 4 tang theo cot truyen
- Co `NPC`, `item`, `objective panel`, `minimap`, `BFS/DFS/SAFE/A*`
- Neu muon deploy production tot hon, nen tach asset loading, save system va audio manager thanh module rieng
