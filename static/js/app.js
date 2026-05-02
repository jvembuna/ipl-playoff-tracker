const state = {
  appState: null,
  qualificationPercentages: null,
  matchProbabilities: {},
};

const standingsBody = document.getElementById("standings-body");
const matchesList = document.getElementById("matches-list");
const simulationCountInput = document.getElementById("simulation-count");
const simulateButton = document.getElementById("simulate-button");
const historyLegend = document.getElementById("history-legend");
const historyCanvas = document.getElementById("history-chart");

const TEAM_COLORS = {
  PBKS: "#d44a2a",
  RCB: "#caa13d",
  RR: "#2f61c2",
  SRH: "#d85b19",
  GT: "#2f365f",
  CSK: "#f0b11b",
  DC: "#294f95",
  KKR: "#5b3a7d",
  MI: "#3567b7",
  LSG: "#1f8e87",
};

const TEAM_LOGOS = {
  PBKS: "/static/images/teams/pbks.png",
  RCB: "/static/images/teams/rcb.png",
  SRH: "/static/images/teams/srh.png",
  RR: "/static/images/teams/rr.png",
  GT: "/static/images/teams/gt.png",
  CSK: "/static/images/teams/csk.png",
  DC: "/static/images/teams/dc.png",
  KKR: "/static/images/teams/kkr.png",
  MI: "/static/images/teams/mi.png",
  LSG: "/static/images/teams/lsg.png",
};

let historyChart = null;
let highlightedTeamId = null;

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message || "Request failed");
  }
  return payload;
}

function percent(value) {
  return `${Number(value).toFixed(1)}%`;
}

function formatNetRunRate(value) {
  const numeric = Number(value);
  return `${numeric >= 0 ? "+" : ""}${numeric.toFixed(3)}`;
}

function compactDateLabel(value) {
  const [year, month, day] = String(value).split("-");
  if (!year || !month || !day) {
    return value;
  }
  return `${Number(month)}/${Number(day)}`;
}

function currentQualification(teamId) {
  return state.qualificationPercentages?.[teamId] ?? 0;
}

function chartHistoryEntries() {
  const history = [...(state.appState?.qualification_history || [])];
  if (!state.appState || !state.qualificationPercentages) {
    return history;
  }

  const currentEntry = {
    date: state.appState.refreshed_at,
    simulation_count: Number(simulationCountInput.value || window.APP_CONFIG.defaultSimulations),
    qualification_percentages: state.qualificationPercentages,
  };

  const alreadyPresent = history.some((entry) => entry.date === currentEntry.date);
  if (!alreadyPresent) {
    history.push(currentEntry);
  }

  return history;
}

function renderStandings() {
  if (!state.appState) {
    standingsBody.innerHTML = "";
    return;
  }

  const standings = [...state.appState.standings];
  standings.sort((a, b) => {
    if (b.points !== a.points) {
      return b.points - a.points;
    }
    if (b.net_run_rate !== a.net_run_rate) {
      return b.net_run_rate - a.net_run_rate;
    }
    return b.team_id.localeCompare(a.team_id);
  });

  standingsBody.innerHTML = standings
    .map((row) => {
      const chance = currentQualification(row.team_id);
      return `
        <tr>
          <td>
            <div class="team-cell">
              <img
                class="team-logo"
                src="${TEAM_LOGOS[row.team_id] || ""}"
                alt="${row.team_name} logo"
                loading="lazy"
              >
              <span>${row.team_name}</span>
            </div>
          </td>
          <td>${row.played}</td>
          <td>${row.won}</td>
          <td>${row.lost}</td>
          <td>${row.no_result}</td>
          <td>${row.points}</td>
          <td>${formatNetRunRate(row.net_run_rate)}</td>
          <td>
            <div class="chance-wrap">
              <div class="chance-meta">
                <span>${percent(chance)}</span>
              </div>
              <div class="chance-bar">
                <span style="width: ${chance}%"></span>
              </div>
            </div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function sliderProbability(matchId) {
  if (state.matchProbabilities[matchId] === undefined) {
    state.matchProbabilities[matchId] = 0.5;
  }
  return state.matchProbabilities[matchId];
}

function renderMatches() {
  if (!state.appState) {
    matchesList.innerHTML = "";
    return;
  }

  matchesList.innerHTML = state.appState.remaining_matches
    .map((match) => {
      const probability = sliderProbability(match.match_id);
      const teamAPercentage = Math.round(probability * 100);
      const teamBPercentage = 100 - teamAPercentage;
      return `
        <div class="match-card">
          <div class="match-header">
            <span>${match.team_a} vs ${match.team_b}</span>
            <span class="match-id">${match.match_id}</span>
          </div>
          <div class="slider-row">
            <span class="team-side">${match.team_a} ${teamAPercentage}%</span>
            <input
              type="range"
              min="0"
              max="100"
              value="${teamAPercentage}"
              data-match-id="${match.match_id}"
            >
            <span class="team-side">${teamBPercentage}% ${match.team_b}</span>
          </div>
        </div>
      `;
    })
    .join("");

  matchesList.querySelectorAll("input[type='range']").forEach((slider) => {
    slider.addEventListener("input", (event) => {
      const target = event.currentTarget;
      state.matchProbabilities[target.dataset.matchId] = Number(target.value) / 100;
      renderMatches();
    });
  });
}

function renderState() {
  renderStandings();
  renderMatches();
  renderHistoryChart();
}

async function loadState() {
  const payload = await requestJson("/api/state");
  state.appState = payload.state;
  if (!state.qualificationPercentages) {
    state.qualificationPercentages = Object.fromEntries(
      payload.state.standings.map((row) => [row.team_id, 0])
    );
  }
  renderState();
}

function buildHistorySeries() {
  const history = chartHistoryEntries();
  const labels = history.map((entry) => compactDateLabel(entry.date));
  const teamIds = state.appState?.standings.map((row) => row.team_id) || [];
  const datasets = teamIds.map((teamId) => {
    const isHighlighted = highlightedTeamId === teamId;
    const isMuted = highlightedTeamId && highlightedTeamId !== teamId;
    const baseColor = TEAM_COLORS[teamId] || "#5f6b7b";
    return {
      label: teamId,
      data: history.map((entry) => entry.qualification_percentages[teamId] ?? null),
      borderColor: isMuted ? "rgba(95, 107, 123, 0.25)" : baseColor,
      backgroundColor: isMuted ? "rgba(95, 107, 123, 0.15)" : baseColor,
      borderWidth: isHighlighted ? 4 : 2,
      tension: 0.25,
      pointRadius: history.length <= 1 ? 5 : isHighlighted ? 4 : 2,
      pointHoverRadius: history.length <= 1 ? 6 : isHighlighted ? 5 : 3,
    };
  });
  return { labels, datasets };
}

function renderHistoryLegend() {
  const teamIds = state.appState?.standings.map((row) => row.team_id) || [];
  historyLegend.innerHTML = teamIds
    .map((teamId) => {
      const muted = highlightedTeamId && highlightedTeamId !== teamId ? "is-muted" : "";
      const swatchColor = TEAM_COLORS[teamId] || "#5f6b7b";
      return `
        <button type="button" class="${muted}" data-team-id="${teamId}">
          <span class="legend-swatch" style="background:${swatchColor}"></span>
          <span>${teamId}</span>
        </button>
      `;
    })
    .join("");

  historyLegend.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      const nextTeamId = button.dataset.teamId;
      highlightedTeamId = highlightedTeamId === nextTeamId ? null : nextTeamId;
      renderHistoryChart();
    });
  });
}

function renderHistoryChart() {
  if (!state.appState || !window.Chart) {
    return;
  }

  const { labels, datasets } = buildHistorySeries();
  renderHistoryLegend();

  if (historyChart) {
    historyChart.destroy();
  }

  historyChart = new window.Chart(historyCanvas, {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { mode: "index", intersect: false },
      },
      interaction: {
        mode: "nearest",
        intersect: false,
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: {
            callback: (value) => `${value}%`,
          },
        },
      },
    },
  });
}

async function runSimulation({ silent = false } = {}) {
  simulateButton.disabled = true;
  try {
    const payload = await requestJson("/api/simulate", {
      method: "POST",
      body: JSON.stringify({
        simulation_count: simulationCountInput.value,
        match_probabilities: Object.fromEntries(
          Object.entries(state.matchProbabilities).map(([matchId, probability]) => [
            matchId,
            { team_a_win_probability: probability },
          ])
        ),
      }),
    });

    state.qualificationPercentages = payload.qualification_percentages;
    state.matchProbabilities = payload.match_probabilities;
    if (payload.ordered_standings) {
      state.appState.standings = payload.ordered_standings;
    }
    renderState();
  } catch (error) {
    if (!silent) {
      window.alert(error.message);
    }
  } finally {
    simulateButton.disabled = false;
  }
}

simulateButton.addEventListener("click", runSimulation);
loadState()
  .then(() => runSimulation({ silent: true }))
  .catch((error) => window.alert(error.message));
