import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Global workflow state to accumulate user inputs and determine when the workflow is complete.
workflow_state = {
    "inputs": [],
    "final_output": None,
    "complete": False
}

# HTML template with user input and final output sections.
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Rivet Graph AI Workflow MVP</title>
</head>
<body>
    <h1>AI Workflow Input</h1>
    <div id="input-section">
        <form id="inputForm">
            <input type="text" name="userInput" placeholder="Enter your input" required>
            <button type="submit">Submit</button>
        </form>
    </div>
    <h2>Final Output</h2>
    <div id="output-section">
        <p id="finalOutput"></p>
    </div>
    <script>
        // Handle the form submission asynchronously.
        document.getElementById("inputForm").addEventListener("submit", async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const input = formData.get("userInput");
            const response = await fetch("/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input: input })
            });
            const result = await response.json();
            if (result.complete) {
                // Update the final output section when the workflow is complete.
                document.getElementById("finalOutput").innerText = result.final_output;
                // Optionally hide the input form.
                document.getElementById("inputForm").style.display = "none";
            } else {
                alert("Input received. Please provide the next input if required.");
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_template)

@app.route("/submit", methods=["POST"])
def submit():
    global workflow_state
    data = request.get_json()
    user_input = data.get("input")
    
    # Append the new input.
    workflow_state["inputs"].append(user_input)
    
    # For this MVP, we complete the workflow after 3 inputs.
    if len(workflow_state["inputs"]) >= 3:
        workflow_state["final_output"] = "Final output computed from inputs: " + ", ".join(workflow_state["inputs"])
        workflow_state["complete"] = True
    
    return jsonify({
        "complete": workflow_state["complete"],
        "final_output": workflow_state["final_output"] if workflow_state["complete"] else ""
    })

if __name__ == '__main__':
    # Use the port provided by the hosting platform, defaulting to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
