const api = {
  habits: "/api/habits",
  stats: "/api/stats",
};

const form = document.getElementById("habit-form");
const listEl = document.getElementById("habit-list");
const statsEl = document.getElementById("stats");
const filterEl = document.getElementById("filter");

let habits = [];
let filter = "all";

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message = body.error || "Request failed";
    throw new Error(message);
  }

  return response.json();
}

function applyFilter(items) {
  if (filter === "active") {
    return items.filter((h) => !h.completed_today);
  }
  if (filter === "done") {
    return items.filter((h) => h.completed_today);
  }
  return items;
}

function renderList() {
  listEl.innerHTML = "";
  const filtered = applyFilter(habits);

  if (filtered.length === 0) {
    listEl.innerHTML = "<li class='meta'>Привычек пока нет.</li>";
    return;
  }

  for (const habit of filtered) {
    const li = document.createElement("li");
    li.className = `habit-item ${habit.completed_today ? "completed" : ""}`;
    li.innerHTML = `
      <div class="habit-main">
        <div>
          <strong>${habit.title}</strong>
          <span class="badge">${habit.frequency}</span>
          <div class="meta">Категория: ${habit.category}</div>
        </div>
        <div class="meta">Streak: ${habit.streak} дн.</div>
      </div>
      <div class="controls">
        <button class="secondary" data-action="toggle" data-id="${habit.id}">
          ${habit.completed_today ? "Снять отметку" : "Отметить выполненной"}
        </button>
        <button class="danger" data-action="delete" data-id="${habit.id}">Удалить</button>
      </div>
    `;
    listEl.appendChild(li);
  }
}

function renderStats(stats) {
  statsEl.innerHTML = `
    <div class="stats-grid">
      <div class="stat"><span>Всего привычек</span><b>${stats.total_habits}</b></div>
      <div class="stat"><span>Выполнено сегодня</span><b>${stats.done_today}</b></div>
      <div class="stat"><span>Выполнение, %</span><b>${stats.completion_rate}</b></div>
      <div class="stat"><span>Лучший streak</span><b>${stats.longest_streak}</b></div>
    </div>
  `;
}

async function loadData() {
  habits = await request(api.habits);
  const stats = await request(api.stats);
  renderList();
  renderStats(stats);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = document.getElementById("title").value.trim();
  const category = document.getElementById("category").value.trim();
  const frequency = document.getElementById("frequency").value;

  if (!title) {
    alert("Название привычки обязательно");
    return;
  }

  try {
    await request(api.habits, {
      method: "POST",
      body: JSON.stringify({ title, category, frequency }),
    });
    form.reset();
    await loadData();
  } catch (error) {
    alert(error.message);
  }
});

filterEl.addEventListener("change", () => {
  filter = filterEl.value;
  renderList();
});

listEl.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }

  const id = button.dataset.id;
  const action = button.dataset.action;

  try {
    if (action === "delete") {
      await request(`${api.habits}/${id}`, { method: "DELETE" });
    }

    if (action === "toggle") {
      await request(`${api.habits}/${id}/toggle`, { method: "PATCH" });
    }

    await loadData();
  } catch (error) {
    alert(error.message);
  }
});

loadData().catch((error) => {
  statsEl.innerHTML = `<p class="meta">Ошибка загрузки: ${error.message}</p>`;
});
