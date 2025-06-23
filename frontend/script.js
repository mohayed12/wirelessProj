document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'https://wirelessproj.onrender.com/api';

    setupForm('wireless-form', `${API_BASE_URL}/wireless`, [
        'f_max', 'bits_per_sample', 'source_coding_ratio',
        'channel_coding_rate', 'interleaver_depth', 'burst_overhead'
    ]);
    setupForm('ofdm-form', `${API_BASE_URL}/ofdm`, [
        'num_subcarriers', 'bits_per_symbol', 'symbol_duration_us',
        'subcarriers_per_rb', 'symbols_per_rb', 'num_parallel_rb', 'bandwidth_mhz'
    ]);
    setupForm('link-budget-form', `${API_BASE_URL}/link_budget`, [
        'distance_km', 'frequency_mhz', 'tx_power_dbm',
        'tx_gain_dbi', 'rx_gain_dbi'
    ]);
    setupForm('cellular-form', `${API_BASE_URL}/cellular`, [
        'total_area_sqkm', 'cell_radius_km', 'cluster_size', 'channels_per_cell'
    ]);

    function setupForm(formId, apiUrl, fieldIds) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const resultsContainer = document.getElementById(formId.replace('-form', '-results'));
            resultsContainer.style.display = 'block';
            resultsContainer.innerHTML = `
                <div class="d-flex justify-content-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>`;

            const body = {};
            fieldIds.forEach(id => {
                const element = document.getElementById(id);
                if (element) body[id] = element.value;
            });

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                displayResults(resultsContainer, data);

            } catch (error) {
                resultsContainer.innerHTML = `<div class="alert alert-danger" role="alert"><strong>Error:</strong> ${error.message}</div>`;
            }
        });
    }

    function displayResults(container, data) {

        let resultsHtml = '<h5>Numerical Results</h5><ul class="list-group mb-4">';
        for (const [key, value] of Object.entries(data.results)) {
            resultsHtml += `<li class="list-group-item d-flex justify-content-between align-items-center">
                              ${key}
                              <span class="badge bg-primary rounded-pill">${value}</span>
                            </li>`;
        }
        resultsHtml += '</ul>';

        resultsHtml += '<h5>🤖 AI-Generated Explanation</h5>';
        resultsHtml += `<div class="ai-explanation">${marked.parse(data.explanation)}</div>`;

        container.innerHTML = resultsHtml;
    }
});
