const form = document.getElementById('prediction-form');
const submitButton = document.getElementById('predict-button');
const emptyState = document.getElementById('result-empty');
const resultContent = document.getElementById('result-content');

const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const weekdayNames = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

function populateSelects() {
  const month = document.getElementById('month');
  monthNames.forEach((name, index) => month.add(new Option(name, index + 1, false, index === 5)));

  const hour = document.getElementById('hour');
  for (let i = 0; i < 24; i++) {
    const label = `${String(i).padStart(2, '0')}:00`;
    hour.add(new Option(label, i, false, i === 12));
  }

  const weekday = document.getElementById('weekday');
  weekdayNames.forEach((name, index) => weekday.add(new Option(name, index, false, index === 1)));
}

function bindSliders() {
  ['temperature', 'humidity', 'windspeed'].forEach(id => {
    const slider = document.getElementById(id);
    const output = document.getElementById(`${id}-value`);
    slider.addEventListener('input', () => output.value = Number(slider.value).toFixed(2));
  });
}

function requestPayload() {
  return {
    year: Number(document.getElementById('year').value),
    month: Number(document.getElementById('month').value),
    hour: Number(document.getElementById('hour').value),
    weekday: Number(document.getElementById('weekday').value),
    holiday: document.getElementById('holiday').checked,
    working_day: document.getElementById('working_day').checked,
    weather: document.getElementById('weather').value,
    season: document.getElementById('season').value,
    temperature: Number(document.getElementById('temperature').value),
    humidity: Number(document.getElementById('humidity').value),
    windspeed: Number(document.getElementById('windspeed').value),
  };
}

function setLoading(loading) {
  submitButton.disabled = loading;
  submitButton.querySelector('.button-label').textContent = loading ? 'Calculating forecast...' : 'Predict demand';
}

function renderResult(data) {
  emptyState.classList.add('hidden');
  resultContent.classList.remove('hidden');
  document.getElementById('prediction-number').textContent = data.predicted_rentals.toLocaleString();
  document.getElementById('raw-prediction').textContent = data.raw_prediction.toFixed(2);
  document.getElementById('result-message').textContent = data.message;
  document.getElementById('demand-badge').textContent = `${data.demand_level} demand`;
  const percentage = Math.min(100, Math.max(6, (data.predicted_rentals / 800) * 100));
  document.getElementById('meter-fill').style.width = `${percentage}%`;
}

function renderError(message) {
  emptyState.classList.remove('hidden');
  resultContent.classList.add('hidden');
  emptyState.innerHTML = `<div class="result-icon">!</div><h3>Prediction unavailable</h3><p>${message}</p>`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setLoading(true);
  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(requestPayload()),
    });
    if (!response.ok) throw new Error('The API could not generate a prediction.');
    renderResult(await response.json());
  } catch (error) {
    renderError(error.message || 'Something went wrong.');
  } finally {
    setLoading(false);
  }
});

document.getElementById('reset-button').addEventListener('click', () => {
  form.reset();
  document.getElementById('year').value = '2012';
  document.getElementById('month').value = '6';
  document.getElementById('hour').value = '12';
  document.getElementById('weekday').value = '1';
  document.getElementById('season').value = 'Summer';
  document.getElementById('weather').value = 'Clear';
  document.getElementById('temperature').value = '0.5';
  document.getElementById('humidity').value = '0.5';
  document.getElementById('windspeed').value = '0.2';
  ['temperature', 'humidity', 'windspeed'].forEach(id => {
    document.getElementById(`${id}-value`).value = Number(document.getElementById(id).value).toFixed(2);
  });
  emptyState.innerHTML = '<div class="result-icon">↗</div><h3>Your forecast appears here</h3><p>Choose the conditions and run a prediction to estimate rental demand.</p>';
  emptyState.classList.remove('hidden');
  resultContent.classList.add('hidden');
});

populateSelects();
bindSliders();
