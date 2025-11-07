class PstrykSchedulerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._selectedHour = null;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity (price_data sensor)');
    }
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  render() {
    if (!this._hass || !this._config.entity) {
      return;
    }

    const entity = this._hass.states[this._config.entity];
    const scheduleEntity = this._hass.states[this._config.schedule_entity || 'sensor.pstryk_scheduler_schedule'];

    if (!entity) {
      this.shadowRoot.innerHTML = `<ha-card><div style="padding: 16px;">Entity not found: ${this._config.entity}</div></ha-card>`;
      return;
    }

    const prices = entity.attributes.hourly_prices || {};
    const schedule = scheduleEntity?.attributes.schedule || {};

    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
        }
        .header {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 16px;
        }
        .chart-container {
          position: relative;
          height: 400px;
          margin-bottom: 16px;
        }
        .bar-chart {
          display: flex;
          align-items: flex-end;
          height: 300px;
          gap: 2px;
          margin-top: 20px;
        }
        .bar-wrapper {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          cursor: pointer;
          position: relative;
        }
        .bar {
          width: 100%;
          background: linear-gradient(to top, #4caf50, #8bc34a);
          border-radius: 4px 4px 0 0;
          transition: all 0.3s ease;
          position: relative;
        }
        .bar:hover {
          opacity: 0.8;
          transform: scaleY(1.05);
        }
        .bar.high-price {
          background: linear-gradient(to top, #f44336, #ff9800);
        }
        .bar.medium-price {
          background: linear-gradient(to top, #ff9800, #ffc107);
        }
        .bar.scheduled {
          border: 3px solid #2196f3;
          box-shadow: 0 0 10px rgba(33, 150, 243, 0.5);
        }
        .bar.current-hour {
          border: 3px solid #9c27b0;
          box-shadow: 0 0 10px rgba(156, 39, 176, 0.5);
        }
        .hour-label {
          font-size: 10px;
          margin-top: 4px;
          text-align: center;
        }
        .price-label {
          font-size: 9px;
          margin-bottom: 2px;
          font-weight: bold;
        }
        .mode-badge {
          position: absolute;
          top: -20px;
          left: 50%;
          transform: translateX(-50%);
          background: #2196f3;
          color: white;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 8px;
          white-space: nowrap;
          z-index: 10;
        }
        .legend {
          display: flex;
          justify-content: center;
          gap: 20px;
          margin-top: 16px;
          font-size: 12px;
        }
        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .legend-color {
          width: 20px;
          height: 20px;
          border-radius: 4px;
        }
        .modal {
          display: none;
          position: fixed;
          z-index: 1000;
          left: 0;
          top: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0,0,0,0.5);
        }
        .modal.show {
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .modal-content {
          background-color: var(--card-background-color, #fff);
          padding: 24px;
          border-radius: 8px;
          max-width: 500px;
          width: 90%;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .modal-header {
          font-size: 20px;
          font-weight: bold;
          margin-bottom: 16px;
        }
        .modal-body {
          margin-bottom: 16px;
        }
        .mode-select {
          width: 100%;
          padding: 12px;
          font-size: 16px;
          border: 1px solid #ccc;
          border-radius: 4px;
          margin-top: 8px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
        }
        .modal-buttons {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }
        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }
        .btn-primary {
          background-color: #2196f3;
          color: white;
        }
        .btn-danger {
          background-color: #f44336;
          color: white;
        }
        .btn-secondary {
          background-color: #757575;
          color: white;
        }
        .info-box {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }
        .info-item {
          background: var(--primary-background-color);
          padding: 12px;
          border-radius: 4px;
          text-align: center;
        }
        .info-label {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        .info-value {
          font-size: 18px;
          font-weight: bold;
          margin-top: 4px;
        }
      </style>

      <ha-card>
        <div class="header">${this._config.title || 'Pstryk Energy Scheduler'}</div>

        <div class="info-box">
          <div class="info-item">
            <div class="info-label">Current Price</div>
            <div class="info-value">${this._formatPrice(entity.attributes.current_price)} €/kWh</div>
          </div>
          <div class="info-item">
            <div class="info-label">Average Price</div>
            <div class="info-value">${this._formatPrice(entity.attributes.average_price)} €/kWh</div>
          </div>
          <div class="info-item">
            <div class="info-label">Min Price</div>
            <div class="info-value">${this._formatPrice(entity.attributes.min_price)} €/kWh</div>
          </div>
          <div class="info-item">
            <div class="info-label">Max Price</div>
            <div class="info-value">${this._formatPrice(entity.attributes.max_price)} €/kWh</div>
          </div>
        </div>

        <div class="chart-container">
          <div class="bar-chart">
            ${this._renderBars(prices, schedule)}
          </div>
        </div>

        <div class="legend">
          <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(to top, #4caf50, #8bc34a);"></div>
            <span>Low Price</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(to top, #ff9800, #ffc107);"></div>
            <span>Medium Price</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="background: linear-gradient(to top, #f44336, #ff9800);"></div>
            <span>High Price</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="border: 3px solid #2196f3;"></div>
            <span>Scheduled</span>
          </div>
          <div class="legend-item">
            <div class="legend-color" style="border: 3px solid #9c27b0;"></div>
            <span>Current Hour</span>
          </div>
        </div>
      </ha-card>

      <div class="modal" id="mode-modal">
        <div class="modal-content">
          <div class="modal-header">Set Mode for Hour</div>
          <div class="modal-body">
            <div id="selected-hour-display"></div>
            <select class="mode-select" id="mode-select">
              <option value="Default">Default</option>
              <option value="Buy">Buy</option>
              <option value="Sell">Sell</option>
              <option value="Sell (All)">Sell (All)</option>
              <option value="Sell (PV Only)">Sell (PV Only)</option>
              <option value="Buy (Charge car)">Buy (Charge car)</option>
              <option value="Buy (Charge car and charge battery)">Buy (Charge car and charge battery)</option>
            </select>
          </div>
          <div class="modal-buttons">
            <button class="btn btn-secondary" id="cancel-btn">Cancel</button>
            <button class="btn btn-danger" id="clear-btn">Clear Schedule</button>
            <button class="btn btn-primary" id="save-btn">Save</button>
          </div>
        </div>
      </div>
    `;

    this._attachEventListeners();
  }

  _renderBars(prices, schedule) {
    const priceEntries = Object.entries(prices).sort((a, b) => a[0].localeCompare(b[0]));
    const priceValues = priceEntries.map(([_, price]) => price);
    const minPrice = Math.min(...priceValues);
    const maxPrice = Math.max(...priceValues);
    const avgPrice = priceValues.reduce((a, b) => a + b, 0) / priceValues.length;

    const currentHour = new Date();
    currentHour.setMinutes(0, 0, 0);
    const currentHourStr = this._formatHourKey(currentHour);

    return priceEntries.map(([hour, price]) => {
      const heightPercent = ((price - minPrice) / (maxPrice - minPrice)) * 100 || 50;

      let priceClass = 'medium-price';
      if (price < avgPrice * 0.8) {
        priceClass = '';
      } else if (price > avgPrice * 1.2) {
        priceClass = 'high-price';
      }

      const isScheduled = schedule[hour] && schedule[hour] !== 'Default';
      const isCurrentHour = hour === currentHourStr;

      const barClasses = ['bar', priceClass];
      if (isScheduled) barClasses.push('scheduled');
      if (isCurrentHour) barClasses.push('current-hour');

      const date = new Date(hour);
      const hourLabel = date.getHours().toString().padStart(2, '0') + ':00';

      let modeBadge = '';
      if (isScheduled) {
        const mode = schedule[hour];
        const shortMode = mode.replace('Buy (Charge car and charge battery)', 'Buy+Car+Batt')
                              .replace('Buy (Charge car)', 'Buy+Car')
                              .replace('Sell (PV Only)', 'Sell PV')
                              .replace('Sell (All)', 'Sell All');
        modeBadge = `<div class="mode-badge">${shortMode}</div>`;
      }

      return `
        <div class="bar-wrapper" data-hour="${hour}">
          ${modeBadge}
          <div class="price-label">${this._formatPrice(price)}€</div>
          <div class="${barClasses.join(' ')}" style="height: ${heightPercent}%;"></div>
          <div class="hour-label">${hourLabel}</div>
        </div>
      `;
    }).join('');
  }

  _formatPrice(price) {
    if (price === null || price === undefined) return 'N/A';
    return parseFloat(price).toFixed(3);
  }

  _formatHourKey(date) {
    return date.toISOString().slice(0, 13) + ':00:00';
  }

  _attachEventListeners() {
    const bars = this.shadowRoot.querySelectorAll('.bar-wrapper');
    const modal = this.shadowRoot.getElementById('mode-modal');
    const saveBtn = this.shadowRoot.getElementById('save-btn');
    const clearBtn = this.shadowRoot.getElementById('clear-btn');
    const cancelBtn = this.shadowRoot.getElementById('cancel-btn');
    const modeSelect = this.shadowRoot.getElementById('mode-select');
    const hourDisplay = this.shadowRoot.getElementById('selected-hour-display');

    bars.forEach(bar => {
      bar.addEventListener('click', (e) => {
        this._selectedHour = bar.dataset.hour;
        const scheduleEntity = this._hass.states[this._config.schedule_entity || 'sensor.pstryk_scheduler_schedule'];
        const schedule = scheduleEntity?.attributes.schedule || {};
        const currentMode = schedule[this._selectedHour] || 'Default';

        modeSelect.value = currentMode;

        const date = new Date(this._selectedHour);
        hourDisplay.textContent = `Hour: ${date.toLocaleString()}`;

        modal.classList.add('show');
      });
    });

    cancelBtn.addEventListener('click', () => {
      modal.classList.remove('show');
    });

    saveBtn.addEventListener('click', () => {
      const mode = modeSelect.value;
      this._hass.callService('pstryk_scheduler', 'set_schedule', {
        hour: this._selectedHour,
        mode: mode
      });
      modal.classList.remove('show');
    });

    clearBtn.addEventListener('click', () => {
      this._hass.callService('pstryk_scheduler', 'clear_schedule', {
        hour: this._selectedHour
      });
      modal.classList.remove('show');
    });

    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('show');
      }
    });
  }

  getCardSize() {
    return 6;
  }
}

customElements.define('pstryk-scheduler-card', PstrykSchedulerCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'pstryk-scheduler-card',
  name: 'Pstryk Scheduler Card',
  description: 'Interactive energy price scheduler with hourly price visualization',
  preview: true,
});
