import google.generativeai as genai
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = "AIzaSyAuI7ScKduRx-4ECqkjdJJiEkJ-5-lokBc"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def generate_ai_explanation(scenario_name, inputs, results):

    try:
        prompt = f"""
        As an expert in wireless engineering, provide a detailed and user-friendly explanation for the following scenario.
        The explanation should be clear for a student learning about this topic.

        Scenario: {scenario_name}

        User-Provided Inputs:
        {inputs}

        Calculated Results:
        {results}

        Please explain the following:
        1.  A brief overview of what was calculated.
        2.  An explanation of each calculated value and what it represents.
        3.  The formulas that were likely used to derive these results.
        4.  The real-world significance of these results in network design.

        Structure the response clearly using Markdown for headings and bold text for key terms.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI explanation: {str(e)}"


@app.route('/api/wireless', methods=['POST'])
def wireless_comm_system():
    data = request.json
    try:

        f_max = float(data['f_max'])
        bits_per_sample = int(data['bits_per_sample'])
        source_coding_ratio = float(data['source_coding_ratio'])
        channel_coding_rate = float(data['channel_coding_rate'])
        burst_overhead = float(data['burst_overhead'])

        sampling_rate = 2 * f_max
        quantizer_rate = sampling_rate * bits_per_sample
        source_encoder_rate = quantizer_rate * source_coding_ratio
        channel_encoder_rate = source_encoder_rate / channel_coding_rate
        interleaver_rate = channel_encoder_rate
        burst_rate = channel_encoder_rate * (1 + burst_overhead / 100)

        results = {
            "Sampler Output Rate (Hz)": f"{sampling_rate:,.2f}",
            "Quantizer Output Rate (bps)": f"{quantizer_rate:,.2f}",
            "Source Encoder Output Rate (bps)": f"{source_encoder_rate:,.2f}",
            "Channel Encoder Output Rate (bps)": f"{channel_encoder_rate:,.2f}",
            "Interleaver Output Rate (bps)": f"{interleaver_rate:,.2f}",
            "Burst Formatting Rate (bps)": f"{burst_rate:,.2f}"
        }

        ai_explanation = generate_ai_explanation("Wireless Communication System Chain", data, results)
        return jsonify({"results": results, "explanation": ai_explanation})

    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid or missing input: {str(e)}"}), 400


@app.route('/api/ofdm', methods=['POST'])
def ofdm_systems():
    data = request.json
    try:
        num_subcarriers = int(data['num_subcarriers'])
        bits_per_symbol = int(data['bits_per_symbol'])
        symbol_duration = float(data['symbol_duration_us']) * 1e-6
        subcarriers_per_rb = int(data['subcarriers_per_rb'])
        symbols_per_rb = int(data['symbols_per_rb'])
        num_parallel_rb = int(data['num_parallel_rb'])
        bandwidth_mhz = float(data['bandwidth_mhz']) * 1e6

        re_rate = bits_per_symbol / symbol_duration
        ofdm_symbol_rate = re_rate * num_subcarriers
        rb_rate = (subcarriers_per_rb * symbols_per_rb * bits_per_symbol) / (symbols_per_rb * symbol_duration)
        max_capacity = rb_rate * num_parallel_rb
        spectral_efficiency = max_capacity / bandwidth_mhz

        results = {
            "Data Rate per Resource Element (bps)": f"{re_rate:,.2f}",
            "Data Rate per OFDM Symbol (bps)": f"{ofdm_symbol_rate:,.2f}",
            "Data Rate per Resource Block (bps)": f"{rb_rate:,.2f}",
            "Max Capacity with Parallel RBs (bps)": f"{max_capacity:,.2f}",
            "Spectral Efficiency (bps/Hz)": f"{spectral_efficiency:,.2f}"
        }

        ai_explanation = generate_ai_explanation("OFDM System Parameters", data, results)
        return jsonify({"results": results, "explanation": ai_explanation})

    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid or missing input: {str(e)}"}), 400


@app.route('/api/link_budget', methods=['POST'])
def link_budget():
    data = request.json
    try:
        distance = float(data['distance_km']) * 1000
        frequency_mhz = float(data['frequency_mhz']) * 1e6
        tx_power_dbm = float(data['tx_power_dbm'])
        tx_gain_dbi = float(data['tx_gain_dbi'])
        rx_gain_dbi = float(data['rx_gain_dbi'])

        c = 3e8

        fspl_db = 20 * np.log10(distance) + 20 * np.log10(frequency_mhz) + 20 * np.log10(4 * np.pi / c)

        rx_power_dbm = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - fspl_db

        tx_power_watts = 10 ** ((tx_power_dbm - 30) / 10)

        results = {
            "Transmitted Power (Watts)": f"{tx_power_watts:.4f}",
            "Free Space Path Loss (dB)": f"{fspl_db:.2f}",
            "Received Signal Strength (dBm)": f"{rx_power_dbm:.2f}"
        }

        ai_explanation = generate_ai_explanation("Link Budget Calculation", data, results)
        return jsonify({"results": results, "explanation": ai_explanation})

    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid or missing input: {str(e)}"}), 400


@app.route('/api/cellular', methods=['POST'])
def cellular_design():
    data = request.json
    try:
        total_area_sqkm = float(data['total_area_sqkm'])
        cell_radius_km = float(data['cell_radius_km'])
        cluster_size = int(data['cluster_size'])
        channels_per_cell = int(data['channels_per_cell'])

        cell_area = 2.598 * (cell_radius_km ** 2)
        num_cells = int(np.ceil(total_area_sqkm / cell_area))
        num_clusters = int(np.ceil(num_cells / cluster_size))
        total_channels = channels_per_cell * num_cells
        system_capacity = channels_per_cell * cluster_size

        results = {
            "Area per Cell (sq. km)": f"{cell_area:.2f}",
            "Number of Cells Required": f"{num_cells}",
            "Number of Clusters": f"{num_clusters}",
            "Total System Capacity (channels in one frequency reuse cluster)": f"{system_capacity}",
            "Total Channels Across All Cells": f"{total_channels}"
        }

        ai_explanation = generate_ai_explanation("Cellular System Design", data, results)
        return jsonify({"results": results, "explanation": ai_explanation})

    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid or missing input: {str(e)}"}), 400


@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


if __name__ == '__main__':
    app.run(debug=True)
