
//C:\Users\john_\Documents\dissertation-ai-cost-extraction\client\excel-addin\deltic-excel-addin\src\ai\deltic_ai.js
// WEEK 10
// =========================
// Chat UI helpers




//function appendMessage(sender, text) {
export function appendMessage(sender, text) {
  const box = document.getElementById("messages");
  const div = document.createElement("div");

  // Force text to be a string
  let safeText = "";

  if (typeof text === "string") {
    safeText = text;
  } else if (text && typeof text === "object") {
    safeText = JSON.stringify(text, null, 2);
  } else {
    safeText = String(text);
  }

  div.textContent = sender + ": " + safeText;
  div.style.marginBottom = "6px";
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}



// =================================
// DelticAI chat handler 
//async function onSendMessage() {
export async function onSendMessage() {
    console.log("NEW ONSENDMESSAGE MULTI-TURN");
    // Always read the user input FIRST
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text) return;
    // ------------------------------------------------------------
    // 1. Handle YES/NO confirmation for extrapolation - Week 10 version for just one curve
    /*if (window.pendingExtrapolation) {
        const answer = text.toLowerCase();

        /*if (answer === "yes" || answer === "y") { // redundent section not used in week 10
            appendMessage("DelticAI", "Running extrapolation…");
            runExtrapolationScenario(window.pendingExtrapolation);
            window.pendingExtrapolation = null;
            return;
        }*/
        /*if (answer === "yes" || answer === "y") {

            appendMessage("You", text);
            //chatHistory.push({
            window.chatHistory.push({
                role: "user",
                content: text
            });
            input.value = "";

            appendMessage("DelticAI","Running extrapolation...");
            await runExtrapolationScenario(window.pendingExtrapolation);
            window.pendingExtrapolation = null;
            return;
        }

        /*if (answer === "no" || answer === "n") { // redundent section not used in week 10
            appendMessage("DelticAI", "Okay, I won't run it.");
            window.pendingExtrapolation = null;
            return;
        }*/
        /*if (answer === "no" || answer === "n") {
            appendMessage(
                "DelticAI",
                "No problem. Let me know when you'd like to run the prediction."
            );
            window.pendingExtrapolation = null;
            return;
        }
        appendMessage("DelticAI", "Please answer yes or no.");
        return;
    }*/

    // Week 12 - Unified confirmation listener for all curve actions
    if (window.pendingCurveAction) {
        const answer = text.toLowerCase();

        if (answer === "yes" || answer === "y") {

            appendMessage("You", text);
            window.chatHistory.push({
                role: "user",
                content: text
            });
            input.value = "";

            appendMessage("DelticAI", `Running ${window.pendingCurveAction.action.replace("_", " ")}…`);

            await runCurveAction(window.pendingCurveAction);

            window.pendingCurveAction = null;
            return;
        }

        if (answer === "no" || answer === "n") {
            appendMessage(
                "DelticAI",
                "No problem. Let me know when you'd like me to run the analysis."
            );
            window.pendingCurveAction = null;
            return;
        }

        appendMessage("DelticAI", "Please answer yes or no.");
        return;
    }





    // -------------------------------------- -----------------
    // 2. Normal chat flow
    appendMessage("You", text);
    // Add to chat history
    //chatHistory.push({ role: "user", content: text });
    window.chatHistory.push({ role: "user", content: text });
    // Clear input
    input.value = "";

    // Ensure file_id exists
    if (!window.currentFileId) {
        appendMessage("System", "No file loaded. Please load a dataset first.");
        return;
    }
    try {
        const res = await fetch("http://127.0.0.1:8000/copilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                history: chatHistory,
                message: text,
                file_id: window.currentFileId
            })
        });

        const data = await res.json();

        // Extract natural-language reply safely
        let replyText = data.reply || "(No reply)";

        // If backend accidentally double-encoded JSON
        try {
            const parsed = JSON.parse(replyText);
            replyText = parsed.reply || replyText;
        } catch (_) {}

        // Show AI assistant reply and add to chat history 
        appendMessage("DelticAI", replyText);
        //chatHistory.push({ role: "assistant", content: replyText });
        window.chatHistory.push({ role: "assistant", content: replyText });
        // Detect extrapolation intent
        /*if (data.action === "extrapolate") {
            askForExtrapolationConfirmation(data);
        }*/

        if (data.action === "extrapolate") {
            //askForExtrapolationConfirmation({ // Week 12 modifictaion
            askForCurveConfirmation({
                action: data.action,
                target: data.target,
                attribute: data.attribute,
                group_field: data.group_field
            });
        }
        if (data.action === "summarize") {
          await runSummaryScenario();
          return;
        }
        // Week 12 additional features
        if (data.action === "breakdown") {
            await runBreakdownScenario(data.attribute);
            return;
        }
        if (data.action === "extrapolate") {
            askForCurveConfirmation({
                action: "extrapolate",
                target: data.target,
                attribute: data.attribute,
                group_field: data.group_field
            });
            return;
        }
        if (data.action === "spline_curve") {
            askForCurveConfirmation({
                action: "spline_curve",
                attribute: data.attribute,
                group_field: data.group_field
            });
            return;
        }
        if (data.action === "monotonic_gb") {
            askForCurveConfirmation({
                action: "monotonic_gb",
                attribute: data.attribute,
                group_field: data.group_field
            });
            return;
        }
        if (data.action === "calculus_curve") {
            askForCurveConfirmation({
                action: "calculus_curve",
                attribute: data.attribute,
                group_field: data.group_field
            });
            return;
        } // end of week 12 but see below for full functions
    } catch (e) {
        appendMessage("System", "Backend unreachable: " + e.message);
    }
}



// Old yes/no for curve function from week 10
/*function askForExtrapolationConfirmation(info) {
    appendMessage(
        "DelticAI",
        //"`I can extrapolate ${info.target} using ${info.attribute} grouped by ${info.group_field}. Run it? (yes/no)`
        "Please confirm that I can run the data extrapolation now. Would you like me to proceed? (yes/no)"
    );

    window.pendingExtrapolation = {
        action: info.action,
        target: info.target,
        attribute: info.attribute,
        group_field: info.group_field
    };
}*/

// new version from week 12
function askForCurveConfirmation(info) {
    appendMessage(
        "DelticAI",
        `Please confirm that I can run
         the ${info.action.replace("_", " ")} now. Would you like me to proceed? (yes/no)`
    );

    window.pendingCurveAction = {
        action: info.action,
        target: info.target || "unit_price",
        attribute: info.attribute,
        group_field: info.group_field
    };
}

// week 12 curve assitant
async function runCurveAction(info) {
    if (info.action === "extrapolate") {
        await runExtrapolationScenario(info);
        return;
    }

    if (info.action === "spline_curve") {
        await runSplineCurveScenario(info.attribute, info.group_field);
        return;
    }

    if (info.action === "calculus_curve") {
        await runCalculusCurveScenario(info.attribute, info.group_field);
        return;
    }

    if (info.action === "monotonic_gb") {
        await runMonotonicGBCurveScenario(info.attribute, info.group_field);
        return;
    }

}



async function runExtrapolationScenario(instruction) {
  try {
    console.log("STEP 1");

    const res = await fetch(
      "http://127.0.0.1:8000/analysis/run",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_id: window.currentFileId,
          instruction
        })
      }
    );

    console.log("STEP 2");
    const data = await res.json();
    console.log("STEP 3", data);
    const aiResult = data.result;
    console.log("STEP 4");
    const scenarioIndex =
      await window.getNextScenarioIndex();
      //await getNextScenarioIndex();


    console.log(
      "STEP 5 scenario",
      scenarioIndex
    );

    //await insertScenarioColumns(
    await window.insertScenarioColumns(
      scenarioIndex
    );

    console.log("STEP 6");

    await Excel.run(async (context) => {

      console.log("STEP 7");

      const sheet =
        context.workbook.worksheets
          .getItem("JoinedCostData");

      sheet.load("name");

      await context.sync();

      console.log(
        "STEP 8 sheet found",
        sheet.name
      );

      //await populateExtrapolationBlock(
      await window.populateExtrapolationBlock(
        context,
        aiResult
      );
      console.log("STEP 9");
    });
    console.log("STEP 10");
    appendMessage(
        "DelticAI",
        `Extrapolation complete. ${aiResult.length} predictions written to Scenario ${scenarioIndex}.`
    );

  } catch (e) {

    console.error(
      "RUN EXTRAPOLATION FAILED"
    );
    console.error(e);
    console.error(e.debugInfo);
  }
}



//function resetConversationState() {
export function resetConversationState() {
    console.log("Resetting conversation state due to dataset change");

    // Reset multi-turn memory
    //chatHistory = [];
    window.chatHistory = [];

    // Reset pending extrapolation
    //pendingExtrapolation = null;
    window.pendingExtrapolation = null;
    window.pendingCurveAction  = null;


    // Clear chat UI
    const chat = document.getElementById("chat");
    if (chat) chat.innerHTML = "";

    // Optional: fresh greeting
    appendMessage("DelticAI", "New dataset loaded. How would you like to begin?");
}

async function runSummaryScenario() {
    try {
        appendMessage("DelticAI", "Preparing a full dataset summary…");

        const res = await fetch("http://127.0.0.1:8000/analysis/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                file_id: window.currentFileId,
                instruction: { action: "summarize" }
            })
        });

        const data = await res.json();

        if (data.status !== "success") {
            appendMessage("DelticAI", "Summary failed: " + data.message);
            return;
        }

        // The orchestrator returns:
        // { status: "success", type: "summary", summary: "..." }
        const summaryText = data.summary;

        appendMessage("DelticAI", summaryText);

        // Add to chat history
        window.chatHistory.push({
            role: "assistant",
            content: summaryText
        });

    } catch (e) {
        appendMessage("System", "Summary failed: " + e.message);
    }
}


// ------------------ Week 12 --- additional AI functions -----
async function runBreakdownScenario(attribute) {
    appendMessage("DelticAI", `Preparing a breakdown by '${attribute}'…`);

    const res = await fetch("http://127.0.0.1:8000/analysis/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            file_id: window.currentFileId,
            instruction: {
                action: "breakdown",
                attribute
            }
        })
    });

    const data = await res.json();

    if (data.status !== "success") {
        appendMessage("DelticAI", "Breakdown failed: " + data.message);
        return;
    }

    const rows = data.result;

    // Display each group nicely
    rows.forEach(r => {
        appendMessage(
            "DelticAI",
            `${attribute} = ${r.attribute_value}
            Total rows: ${r.total_rows}
            Zero prices: ${r.zero_prices}
            Mean: ${r.mean_nonzero_price}
            Median: ${r.median_nonzero_price}`
        );
    });

    window.chatHistory.push({
        role: "assistant",
        content: JSON.stringify(rows)
    });
}

async function runSplineCurveScenario(attribute, group_field) {
    try {
        const res = await fetch(
            "http://127.0.0.1:8000/analysis/run",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    file_id: window.currentFileId,
                    instruction: {
                        action: "spline_curve",
                        attribute,
                        group_field
                    }
                })
            }
        );

        const data = await res.json();

        if (data.status === "error") {
            appendMessage("DelticAI", `Spline curve failed: ${data.message}`);
            return;
        }

        const aiResult = data.result;

        const scenarioIndex = await window.getNextScenarioIndex();
        await window.insertScenarioColumns(scenarioIndex);

        await Excel.run(async (context) => {
            const sheet = context.workbook.worksheets.getItem("JoinedCostData");
            await window.populateExtrapolationBlock(context, aiResult);
        });

        appendMessage(
            "DelticAI",
            `Spline curve complete. ${aiResult.length} predictions written to Scenario ${scenarioIndex}.`
        );

    } catch (e) {
        console.error("RUN SPLINE FAILED");
        console.error(e);
        console.error(e.debugInfo);
    }
}


async function runCalculusCurveScenario(attribute, group_field) {
    try {
        const res = await fetch(
            "http://127.0.0.1:8000/analysis/run",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    file_id: window.currentFileId,
                    instruction: {
                        action: "calculus_curve",
                        attribute,
                        group_field
                    }
                })
            }
        );

        const data = await res.json();

        if (data.status === "error") {
            appendMessage("DelticAI", `Calculus curve failed: ${data.message}`);
            return;
        }

        const aiResult = data.result;

        const scenarioIndex = await window.getNextScenarioIndex();
        await window.insertScenarioColumns(scenarioIndex);

        await Excel.run(async (context) => {
            const sheet = context.workbook.worksheets.getItem("JoinedCostData");
            await window.populateExtrapolationBlock(context, aiResult);
        });

        appendMessage(
            "DelticAI",
            `Calculus curve complete. ${aiResult.length} predictions written to Scenario ${scenarioIndex}.`
        );

    } catch (e) {
        console.error("RUN SPLINE FAILED");
        console.error(e);
        console.error(e.debugInfo);
    }
}


async function runMonotonicGBCurveScenario(attribute, group_field) {
    try {

        // Warn the user before running
        appendMessage(
            "DelticAI",
            "Monotonic Gradient Boosting will take far longer to compute than other methods. Starting now..."
        );
        const res = await fetch(
            "http://127.0.0.1:8000/analysis/run",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    file_id: window.currentFileId,
                    instruction: {
                        action: "monotonic_gb",
                        attribute,
                        group_field
                    }
                })
            }
        );

        const data = await res.json();

        if (data.status === "error") {
            appendMessage("DelticAI", `Monotonic GB curve failed: ${data.message}`);
            return;
        }

        const aiResult = data.result;

        const scenarioIndex = await window.getNextScenarioIndex();
        await window.insertScenarioColumns(scenarioIndex);

        await Excel.run(async (context) => {
            const sheet = context.workbook.worksheets.getItem("JoinedCostData");
            await window.populateExtrapolationBlock(context, aiResult);
        });

        appendMessage(
            "DelticAI",
            `Monotonic Gradient Boosting curve complete. ${aiResult.length} predictions written to Scenario ${scenarioIndex}.`
        );

    } catch (e) {
        console.error("RUN MONOTONIC GB FAILED");
        console.error(e);
        console.error(e.debugInfo);
    }
}
