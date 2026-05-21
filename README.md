
# Parksim Terminal Tycoon

**Parksim Terminal Tycoon** is a feature-rich theme park simulator that runs entirely in your terminal. Build, manage, and optimize your own amusement park using a fast, keyboard-driven interface.

---

## Features

- Build paths, rides, stalls, and toilets
- Manage park finances, guest needs, and flow
- Dynamic guest simulation and park economy
- Fully customizable settings via `constants.py`
- Retro terminal UI with color and character art

---

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (for dependency management and running)

### Installation

1. **Clone the repository:**
2. **Run the game:**
	```sh
	uv run python main.py
	```
	*(Run this command from the project root in your terminal)*

---

## Configuration

You can tweak game parameters by editing the `constants.py` files in the following folders:

- `sim/constants.py` — Park size, guest limits, prices, build costs, and more
- `ui/constants.py` — UI layout and HUD settings

Example settings you can change:

```python
# sim/constants.py
PARK_WIDTH = 80
PARK_HEIGHT = 40
STARTING_CASH = 10000.0
ENTRANCE_FEE = 10.0
# ...and many more
```

---

## Project Structure

- `main.py` — Entry point
- `sim/` — Core simulation logic (guests, park, finance, etc.)
- `ui/` — Terminal UI rendering and colors
- `tests/` — Automated tests

---


