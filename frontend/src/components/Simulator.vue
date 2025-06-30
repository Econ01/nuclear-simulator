<!-- frontend/src/components/Simulator.vue -->
<template>
  <div class="simulator-container">
    <div class="control-panel">
      <h2>Nuclear Detonation Parameters</h2>
      
      <div class="input-group">
        <label>Yield (kilotons):</label>
        <input type="range" min="0.1" max="100000" v-model.number="yield_kt">
        <span>{{ yield_kt }} kt</span>
      </div>
      
      <div class="input-group">
        <label>Distance from Ground Zero (meters):</label>
        <input type="number" v-model.number="distance">
      </div>
      
      <button @click="calculateEffects">Calculate Effects</button>
    </div>

    <div class="results" v-if="results">
      <h3>Blast Effects</h3>
      <div class="result-card">
        <h4>Overpressure</h4>
        <p>{{ results.overpressure_kpa.toFixed(1) }} kPa</p>
        <p class="effect-description">
          {{ getOverpressureEffect(results.overpressure_kpa) }}
        </p>
      </div>
      
      <div class="result-card">
        <h4>Thermal Radiation</h4>
        <p>{{ results.thermal_cal_per_cm2.toFixed(1) }} cal/cm²</p>
        <p class="effect-description">
          {{ getThermalEffect(results.thermal_cal_per_cm2) }}
        </p>
      </div>
      
      <div class="result-card">
        <h4>Radiation Dose</h4>
        <p>{{ results.radiation_sv.toFixed(2) }} Sv</p>
        <p class="effect-description">
          {{ getRadiationEffect(results.radiation_sv) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      yield_kt: 100,
      distance: 1000,
      results: null
    }
  },
  methods: {
    async calculateEffects() {
      try {
        const response = await fetch('http://localhost:5000/api/calculate-blast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            yield: this.yield_kt,
            distance: this.distance
          })
        });
        
        this.results = await response.json();
      } catch (error) {
        console.error('Calculation error:', error);
      }
    },
    getOverpressureEffect(pressure) {
      if (pressure > 500) return "All structures destroyed";
      if (pressure > 200) return "Reinforced concrete buildings destroyed";
      if (pressure > 50) return "Residential buildings collapse";
      if (pressure > 20) return "Glass windows shatter";
      return "Minimal structural damage";
    },
    getThermalEffect(energy) {
      if (energy > 100) return "3rd degree burns, spontaneous ignition of materials";
      if (energy > 25) return "2nd degree burns, clothing ignites";
      if (energy > 10) return "1st degree burns, flammable materials ignite";
      return "Sunburn-like effects";
    },
    getRadiationEffect(dose) {
      if (dose > 10) return "100% fatal within 48 hours";
      if (dose > 5) return "50% fatal within 30 days";
      if (dose > 1) return "Radiation sickness, increased cancer risk";
      return "Minimal acute effects";
    }
  }
}
</script>

<style scoped>
.simulator-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: rgba(30, 40, 60, 0.85);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.input-group {
  margin-bottom: 1.5rem;
}

.result-card {
  background: rgba(0, 20, 40, 0.7);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.effect-description {
  font-style: italic;
  color: #ff9e80;
}
</style>