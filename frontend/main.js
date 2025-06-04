const boardEl = document.getElementById('board');
const boardSize = 5; // same as server

function render(state) {
  boardEl.innerHTML = '';
  boardEl.style.display = 'grid';
  boardEl.style.gridTemplateColumns = `repeat(${boardSize}, 40px)`;
  boardEl.style.gridTemplateRows = `repeat(${boardSize}, 40px)`;
  for (let y = 0; y < boardSize; y++) {
    for (let x = 0; x < boardSize; x++) {
      const cell = document.createElement('div');
      cell.style.width = '40px';
      cell.style.height = '40px';
      cell.style.border = '1px solid #ccc';
      const bot = Object.entries(state).find(([, info]) => info.pos[0] === x && info.pos[1] === y);
      if (bot) {
        cell.textContent = bot[0][0];
        cell.style.background = '#faa';
        cell.title = bot[0] + ' HP: ' + bot[1].hp;
      }
      boardEl.appendChild(cell);
    }
  }
}

async function fetchState() {
  const res = await fetch('http://localhost:8000/state');
  const data = await res.json();
  render(data);
}

setInterval(fetchState, 1000);
fetchState();
