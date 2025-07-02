from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Shared state (in-memory, resets when server restarts)
COUNTER_STATE = {
    'successes': 0,
    'attempts': 0,
    'trackAttempts': True,
    'showButtons': True,
    'label': 'Mounts Dropped:',
    'fontFamily': 'Arial',
    'fontSize': 48,
    'fontColor': '#FF0000',
}

HTML_CONTROL = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OBS Counter Control</title>
    <style>
        body { background: transparent; margin: 0; overflow: hidden; }
        #settings {
            position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            background: rgba(255,255,255,0.95); padding: 10px 20px; border-radius: 8px;
            display: flex; gap: 10px; align-items: center; z-index: 10;
        }
        #counter {
            font-family: var(--font-family, Arial);
            font-size: var(--font-size, 48px);
            color: var(--font-color, #FF0000);
            text-align: center;
            margin-top: 80px;
            user-select: none;
        }
        #buttons {
            display: flex; gap: 8px; justify-content: center;
            margin-top: 8px;
        }
        .btn {
            font-size: 1em;
            padding: 2px 8px;
            border-radius: 5px;
            border: 1px solid #aaa;
            background: #f8f8f8;
            cursor: pointer;
            min-width: 70px;
        }
        .btn-success { color: #176117; font-weight: bold; }
        .btn-attempt { color: #a11a1a; font-weight: bold; }
        .btn:active { background: #e0e0e0; }
        label { font-size: 14px; }
        #settings label { margin-bottom: 0; }
    </style>
</head>
<body>
    <div id="settings">
        <label>Label: <input id="labelText" value="Mounts Dropped:" style="width:120px" onchange="updateDisplay()"></label>
        <label><input type="checkbox" id="trackAttempts" checked onchange="toggleAttempts()"> Track Attempts (X/Y)</label>
        <label>Font:
            <select id="fontFamily" onchange="updateStyle()">
                <option>Arial</option>
                <option>Verdana</option>
                <option>Times New Roman</option>
                <option>Courier New</option>
                <option>Comic Sans MS</option>
                <option>Impact</option>
            </select>
        </label>
        <label>Size:
            <input type="number" id="fontSize" value="48" min="10" max="200" style="width:50px;" onchange="updateStyle()"> px
        </label>
        <label>Color:
            <input type="color" id="fontColor" value="#FF0000" onchange="updateStyle()">
        </label>
        <label><input type="checkbox" id="showButtons" checked onchange="toggleButtons()"> Show Buttons</label>
    </div>
    <div id="counter"></div>
    <div id="buttons"></div>
    <script>
        let state = {};
        function fetchState() {
            fetch('/state').then(r => r.json()).then(s => {
                state = s;
                document.getElementById('labelText').value = s.label;
                document.getElementById('fontFamily').value = s.fontFamily;
                document.getElementById('fontSize').value = s.fontSize;
                document.getElementById('fontColor').value = s.fontColor;
                document.getElementById('trackAttempts').checked = s.trackAttempts;
                document.getElementById('showButtons').checked = s.showButtons;
                updateDisplay();
                updateStyle();
                renderButtons();
            });
        }
        function postState() {
            fetch('/state', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state)
            });
        }
        function updateDisplay() {
            const label = document.getElementById('labelText').value;
            const counter = document.getElementById('counter');
            if (state.trackAttempts) {
                counter.textContent = `${label} ${state.successes}/${state.attempts}`;
            } else {
                counter.textContent = `${label} ${state.successes}`;
            }
        }
        function updateStyle() {
            const fam = document.getElementById('fontFamily').value;
            const size = document.getElementById('fontSize').value + 'px';
            const color = document.getElementById('fontColor').value;
            const counter = document.getElementById('counter');
            counter.style.fontFamily = fam;
            counter.style.fontSize = size;
            counter.style.color = color;
        }
        function renderButtons() {
            const btns = document.getElementById('buttons');
            btns.innerHTML = '';
            if (!state.showButtons) return;
            // Success +
            const btnSuccessPlus = document.createElement('button');
            btnSuccessPlus.textContent = 'Success +';
            btnSuccessPlus.className = 'btn btn-success';
            btnSuccessPlus.onclick = () => {
                state.successes++;
                if (state.trackAttempts) state.attempts++;
                postState();
                updateDisplay();
            };
            btns.appendChild(btnSuccessPlus);
            // Success -
            const btnSuccessMinus = document.createElement('button');
            btnSuccessMinus.textContent = 'Success -';
            btnSuccessMinus.className = 'btn';
            btnSuccessMinus.onclick = () => {
                if (state.successes > 0) state.successes--;
                postState();
                updateDisplay();
            };
            btns.appendChild(btnSuccessMinus);
            if (state.trackAttempts) {
                // Attempt +
                const btnAttemptPlus = document.createElement('button');
                btnAttemptPlus.textContent = 'Attempt +';
                btnAttemptPlus.className = 'btn btn-attempt';
                btnAttemptPlus.onclick = () => {
                    state.attempts++;
                    postState();
                    updateDisplay();
                };
                btns.appendChild(btnAttemptPlus);
                // Attempt -
                const btnAttemptMinus = document.createElement('button');
                btnAttemptMinus.textContent = 'Attempt -';
                btnAttemptMinus.className = 'btn';
                btnAttemptMinus.onclick = () => {
                    if (state.attempts > 0) state.attempts--;
                    postState();
                    updateDisplay();
                };
                btns.appendChild(btnAttemptMinus);
            }
        }
        function toggleAttempts() {
            state.trackAttempts = document.getElementById('trackAttempts').checked;
            postState();
            updateDisplay();
            renderButtons();
        }
        function toggleButtons() {
            state.showButtons = document.getElementById('showButtons').checked;
            postState();
            renderButtons();
        }
        document.getElementById('labelText').addEventListener('input', function() { state.label = this.value; postState(); updateDisplay(); });
        document.getElementById('fontFamily').addEventListener('change', function() { state.fontFamily = this.value; postState(); updateStyle(); });
        document.getElementById('fontSize').addEventListener('change', function() { state.fontSize = this.value; postState(); updateStyle(); });
        document.getElementById('fontColor').addEventListener('change', function() { state.fontColor = this.value; postState(); updateStyle(); });
        // Initial fetch
        fetchState();
    </script>
</body>
</html>
'''

HTML_DISPLAY = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OBS Counter Display</title>
    <style>
        body { background: transparent; margin: 0; overflow: hidden; }
        #counter {
            font-family: var(--font-family, Arial);
            font-size: var(--font-size, 48px);
            color: var(--font-color, #FF0000);
            text-align: center;
            margin-top: 80px;
            user-select: none;
        }
    </style>
</head>
<body>
    <div id="counter"></div>
    <script>
        function fetchState() {
            return fetch('/state').then(r => r.json());
        }
        function updateDisplay(s) {
            const counter = document.getElementById('counter');
            if (s.trackAttempts) {
                counter.textContent = `${s.label} ${s.successes}/${s.attempts}`;
            } else {
                counter.textContent = `${s.label} ${s.successes}`;
            }
            counter.style.fontFamily = s.fontFamily;
            counter.style.fontSize = s.fontSize + 'px';
            counter.style.color = s.fontColor;
        }
        // Poll for changes every 200ms
        setInterval(() => {
            fetchState().then(updateDisplay);
        }, 200);
        // Initial render
        fetchState().then(updateDisplay);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_CONTROL)

@app.route('/display')
def display():
    return render_template_string(HTML_DISPLAY)

@app.route('/state', methods=['GET', 'POST'])
def state():
    global COUNTER_STATE
    if request.method == 'POST':
        COUNTER_STATE.update(request.json)
        return jsonify(success=True)
    return jsonify(COUNTER_STATE)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 