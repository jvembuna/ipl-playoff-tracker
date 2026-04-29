const state = {
  appState: null,
  qualificationPercentages: null,
  matchProbabilities: {},
};

const standingsBody = document.getElementById("standings-body");
const matchesList = document.getElementById("matches-list");
const simulationCountInput = document.getElementById("simulation-count");
const simulateButton = document.getElementById("simulate-button");

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

function currentQualification(teamId) {
  return state.qualificationPercentages?.[teamId] ?? 0;
}

function renderStandings() {
  if (!state.appState) {
    standingsBody.innerHTML = "";
    return;
  }

  const standings = [...state.appState.standings];
  standings.sort((a, b) => {
    const chanceDelta = currentQualification(b.team_id) - currentQualification(a.team_id);
    if (chanceDelta !== 0) {
      return chanceDelta;
    }
    if (b.points !== a.points) {
      return b.points - a.points;
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
              <span class="team-badge">${row.team_id}</span>
              <span>${row.team_name}</span>
            </div>
          </td>
          <td>${row.played}</td>
          <td>${row.won}</td>
          <td>${row.lost}</td>
          <td>${row.points}</td>
          <td>
            <div class="chance-wrap">
              <div class="chance-meta">
                <span>${percent(chance)}</span>
                <span>${row.team_id}</span>
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
