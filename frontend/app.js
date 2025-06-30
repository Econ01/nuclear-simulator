document.addEventListener('DOMContentLoaded', () => {
    const yieldSlider = document.getElementById('yield');
    const distanceSlider = document.getElementById('distance');
    const yieldValue = document.getElementById('yield-value');
    const distanceValue = document.getElementById('distance-value');
    const calculateBtn = document.getElementById('calculate-btn');
    const overpressureEl = document.getElementById('overpressure');
    const radiationEl = document.getElementById('radiation');

    // Update slider values
    yieldSlider.addEventListener('input', () => {
        yieldValue.textContent = `${yieldSlider.value} kt`;
    });

    distanceSlider.addEventListener('input', () => {
        distanceValue.textContent = `${distanceSlider.value} m`;
    });

    // Calculate button handler
    calculateBtn.addEventListener('click', async () => {
        const payload = {
            yield: yieldSlider.value,
            distance: distanceSlider.value
        };

        try {
            const response = await fetch('http://localhost:5000/calculate-blast', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            overpressureEl.textContent = `${data.overpressure_psi.toFixed(2)} psi`;
            radiationEl.textContent = `${data.radiation_sv.toFixed(4)} Sv`;
        } catch (error) {
            console.error('Error:', error);
        }
    });
});