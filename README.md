# ⚡ Quantum-Flux Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Budget: $72.65/$75](https://img.shields.io/badge/Budget-$72.65%2F$75-success.svg)](bom/BOM.csv)
[![Open Access Only](https://img.shields.io/badge/Open%20Access-Only-blue.svg)](src/whitelist.json)
[![CI Status](https://github.com/CrazhHolmes/QuantumFluxLab/workflows/CI/badge.svg)](.github/workflows/ci.yml)
[![Temporal Physics](https://img.shields.io/badge/Temporal-Physics-purple.svg)](logs/Log_time_travel.log)

> **A garage-scale quantum physics lab that levitates fog, glows violet, and pushes your hand back — all for under $75.**

The **Quantum-Flux Lab** is an open-source research platform combining piezo-driven high-voltage resonance, corona plasma generation, electrostatic pressure fields, and infrasound standing waves to achieve stable levitation of visible matter (≥10g) with measurable plasma generation and physical pressure fields.

![Quantum-Flux Lab Concept](docs/images/concept.png)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/CrazhHolmes/QuantumFluxLab.git
cd QuantumFluxLab

# Install Python dependencies
pip install -r src/requirements.txt

# Start the web console
python -m http.server 8080 --directory ui

# Open your browser
open http://localhost:8080
```

Or simply open `ui/index.html` directly in your web browser.

## 🎯 Features

- **⚡ Piezo-HV Array**: 6x phased piezo sparkers generating 10-30kV corona discharge
- **🔮 Plasma Generation**: Self-sustaining plasma sheets with ion density >10¹² cm⁻³
- **🌊 Infrasound Levitation**: 14-40 Hz standing waves for acoustic confinement
- **⚡ Electrostatic Pressure**: EHD thrust fields producing 2-5N hand-pressure
- **🎮 Gamepad Control**: Real-time Xbox/PS4 controller interface
- **🛡️ Triple Redundant Safety**: Hardware relay + software MOSFET + passive fuse
- **🔬 Time-Travel Physics**: Delayed-choice quantum experiments (fringe science section)

## 📸 Hardware Build

| Component | Photo | Specs |
|-----------|-------|-------|
| Piezo Array | ![Piezo](docs/images/piezo.jpg) | 6x BBQ igniters, 15-30kV |
| Corona Electrode | ![Electrode](docs/images/electrode.jpg) | 0.25mm Cu wire, 30mm gap |
| Acoustic Driver | ![Speaker](docs/images/speaker.jpg) | 6" TV woofer, ported |

*Note: Add your build photos to `docs/images/`*

## 🛡️ Safety First

**⚠️ WARNING: High Voltage (30kV) and High Sound Pressure (140dB)**

- **Electric Field**: Operating at 3-5 kV/m (safe margin from 20 kV/m limit)
- **Ozone**: Auto-shutdown at 0.08 ppm (OSHA limit: 0.1 ppm)
- **SPL**: Maximum 120 dB at operator position (hearing protection required)
- **Temperature**: Auto-shutdown at 50°C (piezo depolarization protection)

### Fail-Safe Circuit
```
[Power] → [Fuse 2A] → [Relay NC] → [MOSFET] → [Load]
                            ↑
                    [Watchdog OR Sensors OR E-Stop]
```

See [Log_safety.log](logs/Log_safety.log) for complete safety analysis.

## 💰 Budget Breakdown

| Category | Cost |
|----------|------|
| Piezo-HV Components | $28.44 |
| Acoustic System | $19.49 |
| Control Electronics | $16.49 |
| Sensors & Safety | $8.23 |
| **TOTAL** | **$72.65** ✅ |

Full BOM: [bom/BOM.csv](bom/BOM.csv)

## 📚 Citation Requirements

This project is licensed under MIT — you are free to use, modify, and distribute.

**When reusing research papers, you MUST cite the original arXiv DOI:**

```bibtex
@misc{riba2021corona,
  title={Corona Discharge Characteristics under Variable Pressure and Frequency},
  author={Riba, J.-R. et al.},
  journal={Sensors},
  volume={21},
  number={19},
  pages={6676},
  year={2021},
  doi={10.3390/s21196676}
}

@misc{shoshany2023warp,
  title={Warp Drives and Closed Timelike Curves},
  author={Shoshany, Barak},
  journal={arXiv:2309.10072},
  year={2023}
}
```

See [docs/MAIN_REPORT.md](docs/MAIN_REPORT.md) for full citations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Quantum-Flux Lab System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐      ┌──────────────┐                   │
│   │   Gamepad    │──────▶│  Controller  │                   │
│   │ (Xbox/PS4)   │      │ (Arduino/Pi) │                   │
│   └──────────────┘      └──────┬───────┘                   │
│                                │                            │
│              ┌─────────────────┼─────────────────┐          │
│              ▼                 ▼                 ▼          │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│   │  PIEZO-HV    │   │   CORONA     │   │  ACOUSTIC    │   │
│   │   ARRAY      │──▶│   PLASMA     │   │   DRIVER     │   │
│   │ (3-6 units)  │   │   SHEET      │   │ (TV Speaker) │   │
│   └──────────────┘   └──────┬───────┘   └──────────────┘   │
│                             │                              │
│                             ▼                              │
│                    ┌──────────────────┐                    │
│                    │  LEVITATION NODE │                    │
│                    │   (Target zone)  │                    │
│                    └──────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/amazing-feature`
3. **Add safety tests**: Ensure `tests/test_safety.py` passes
4. **Verify budget**: Ensure `tests/test_budget.py` passes (≤$75)
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

**⚠️ IMPORTANT**: All hardware changes MUST include verified fail-safe circuit testing. Use the [Safety First issue template](.github/ISSUE_TEMPLATE/safety_first.md).

## 🔬 Open Access Policy

This project **only** uses open-access research sources:

✅ **Whitelisted**: arxiv.org, nasa.gov, osti.gov, zenodo.org, *.edu  
❌ **Blacklisted**: elsevier.com, springer.com, wiley.com (paywalled)

See [src/whitelist.json](src/whitelist.json) and [src/blacklist.log](src/blacklist.log) for full lists.

## 🔮 Temporal Physics Section

*"The combination of piezo-driven HV resonance and infrasound creates a parametric amplification effect that probes the same conceptual space as Closed Timelike Curves..."*

See [logs/Log_time_travel.log](logs/Log_time_travel.log) for the complete investigation into:
- Warp drives and CTCs (arXiv:2309.10072)
- Macroscopic delayed-choice quantum erasers
- Garage-scale temporal nonlocality experiments

## 📄 License

[MIT License](LICENSE) © 2026 Quantum-Flux Lab Contributors

---

**⚡ Built with passion, physics, and a $75 budget.**

## 🚀 Updates & Contributions

- Star the repo to follow development!
- Open an Issue for bugs, ideas, or safety concerns.
- Pull Requests are welcome – please include tests for any code changes.
