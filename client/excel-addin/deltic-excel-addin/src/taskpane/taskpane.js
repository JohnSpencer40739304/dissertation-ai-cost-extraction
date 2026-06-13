
/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global console, document, Excel, Office */

/* ORIGINAL
Office.onReady((info) => {
  if (info.host === Office.HostType.Excel) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
  }
});

export async function run() {
  try {
    await Excel.run(async (context) => {
      /**
       * Insert your Excel code here
       */
      /*
      const range = context.workbook.getSelectedRange();

      // Read the range address
      range.load("address");

      // Update the fill color
      range.format.fill.color = "yellow";

      await context.sync();
      console.log(`The range address was ${range.address}.`);
    });
  } catch (error) {
    console.error(error);
  }
}
*/

/* global Office */

/* NEW REPLACEMEN */
/*
*Office.onReady((info) => {
*  document.getElementById("sideload-msg").style.display = "none";
*  document.getElementById("app-body").style.display = "block";*

*  if (info.host === Office.HostType.Excel) {
*    document.getElementById("run").onclick = run;
*  }
*});
*/

/*
Office.onReady((info) => {
  if (info.host === Office.HostType.Excel) {
    // Wire the default button to our backend test
    document.getElementById("run").onclick = run;
  }
});
*/

/**
 * Minimal backend test:
 * - Prompts for a file ID
 * - Calls FastAPI: /file/{file_id}/data
 * - Parses JSON
 * - Logs result
 * - Alerts success/failure
 */

/*
async function run() {
  try {
    const fileId = prompt("Enter file ID to load:");
    if (!fileId) {
      alert("No file ID entered.");
      return;
    }

    const url = `http://127.0.0.1:8000/file/${fileId}/data`;
    console.log("Calling backend:", url);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Backend returned status ${response.status}`);
    }

    const data = await response.json();
    console.log("Backend response:", data);

    alert("Data loaded successfully. Check the console for details.");
  } catch (err) {
    console.error("Error calling backend:", err);
    alert("Error calling backend: " + err.message);
  }
}
*/

/* global Office, Excel, console, document */

/* -----------------------------------------
   Week 9 - new initiation  */

Office.onReady(async (info) => {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "block";
    document.getElementById("send-corrections-btn")
    .addEventListener("click", sendCorrections);

    if (info.host === Office.HostType.Excel) {
        await populateFileDropdown();
        document.getElementById("load-file").onclick = loadSelectedFile;
    }
});

// week  9 - added for select table list
const tableSelect = document.getElementById("table-select");
tableSelect.addEventListener("change", () => {
  const selectedIndex = tableSelect.value;
  console.log("User selected table index:", selectedIndex);
});
let BACKEND_TABLE = null;
let BACKEND_ATTRIBUTES = null;
tableSelect.addEventListener("change", () => {
    console.log("Auto-refresh: table_index changed to", tableSelect.value);
    loadSelectedTableOnly();
});

// week 9 add a select, send and extract a file button
const processFileBtn = document.getElementById("process-file-btn");
const hiddenFileInput = document.getElementById("hidden-file-input");

// When user clicks "Process File", open the file picker
processFileBtn.addEventListener("click", () => {
    console.log("Process File clicked — opening file picker");
    hiddenFileInput.click();
});

// When user selects a file, run the full pipeline
hiddenFileInput.addEventListener("change", async () => {
    const file = hiddenFileInput.files[0];
    if (!file) {
        console.warn("No file selected");
        return;
    }
    console.log("User selected file:", file.name);
    await processUploadedFile(file);   // <-- THIS MUST FIRE
});

// Egg timer cursur while running
//function showBusyCursor() {
    //document.body.style.cursor = "wait";
//}
//function hideBusyCursor() {
    //document.body.style.cursor = "default";
//}
function showBusyOverlay() {
    document.getElementById("busy-overlay").style.display = "block";
}

function hideBusyOverlay() {
    document.getElementById("busy-overlay").style.display = "none";
}



// -------------------------------------
// Week 9 - Correction engine configuration
const CORE_FIELDS = [
  "item_description",
  "unit_price",
  "currency",
  "quantity"
];
const LOCKED_CORE_FIELDS = [
  "id",
  "file_id",
  "sheet_name",
  "table_index",
  "row_index",
  "ai_confidence_overall"
];
// Copy of joined table
let ORIGINAL_JOINED_DATA = {};
let ORIGINAL_HEADERS = [];
// ------------------------------


async function populateFileDropdown() {
  const dropdown = document.getElementById("file-select");

  try {
    const response = await fetch("http://localhost:8000/files");
    const files = await response.json();

    dropdown.innerHTML = ""; // clear "Loading..."

    files.forEach(file => {
      const option = document.createElement("option");
      option.value = file.id;
      option.textContent = `${file.id} — ${file.name}`;
      dropdown.appendChild(option);
    });

  } catch (err) {
    console.error("Error loading file list:", err);
    dropdown.innerHTML = "<option>Error loading files</option>";
  }
}




async function loadSelectedFile() {
  const fileId = document.getElementById("file-select").value;
  if (!fileId) {
    console.warn("No file selected");
    return;
  }
  console.log("Loading file:", fileId);
  try {
    const response = await fetch(`http://localhost:8000/file/${fileId}/data`);
    const data = await response.json();
    console.log("Backend returned:", data);
    const table = data.clean_cost_data;
    const table2 = data.clean_cost_data_attributes;

    BACKEND_TABLE = table;
    BACKEND_ATTRIBUTES = table2;

    // week 9 Populate dropdown with select table options (derived from clean_cost_data)
    if (table && table.length > 1) {
        const headers = table[0];
        const idxTableIndex = headers.indexOf("table_index");
        if (idxTableIndex === -1) {
            console.warn("No table_index column found in clean_cost_data");
        } else {
            const seen = new Set();
            // Collect unique table_index values
            for (let i = 1; i < table.length; i++) {
                const row = table[i];
                const tIndex = row[idxTableIndex];
                seen.add(tIndex);
            }
            tableSelect.innerHTML = "";
            // Build dropdown entries
            for (const tIndex of seen) {
                const opt = document.createElement("option");
                // opt.value = index;
                // opt.textContent = `Table ${index + 1}`;
                opt.value = String(tIndex);
                opt.textContent = `Table ${tIndex}`;

                tableSelect.appendChild(opt);
            }
            // Auto-select the lowest table_index
            const first = [...seen][0];
            tableSelect.value = String(first);
        }
    } else {
        // Fallback: single table
        tableSelect.innerHTML = "";
        const opt = document.createElement("option");
        // opt.value = 0;
        // opt.textContent = "Table 1";
        opt.value = "0";
        opt.textContent = "Table 0";
        tableSelect.appendChild(opt);
        tableSelect.value = "0";
    }
    // end of select table section

    if (!table || table.length === 0) {
      console.warn("No clean_cost_data returned");
      return;
    }
    //await writeTableToExcel(table, "CleanCostData");
    await writeTableToExcel(table, "CleanCostData", { selectiveLocking: false });
    if (table2 && table2.length > 0) {
      //await writeTableToExcel(table2, "CleanCostDataAttributes");
      await writeTableToExcel(table2, "CleanCostDataAttributes", { selectiveLocking: false });
    } else {
      console.warn("No clean_cost_data_attributes returned");
    }
    // create joined table using ALL tables of original source
    const expanded = buildExpandedTable(table, table2);
    //await writeTableToExcel(expanded, "JoinedCostData"); // 1 line replaced by 2 below
    storeOriginalJoinedData(expanded);
    await writeTableToExcel(expanded, "JoinedCostData", { selectiveLocking: true });
  } catch (err) {
    console.error("Error loading file:", err);
  }
}


async function loadSelectedTableOnly() {
    if (!BACKEND_TABLE) {
        console.warn("No backend data loaded yet");
        return;
    }
    const selectedTableIndex = Number(tableSelect.value);
    console.log("Refreshing Joined sheet for table_index:", selectedTableIndex);
    const table = BACKEND_TABLE;
    const table2 = BACKEND_ATTRIBUTES;

    // Filter CleanCostData
    const headers = table[0];
    const idxTableIndex = headers.indexOf("table_index");
    const idxId = headers.indexOf("id");
    const filteredTable = [headers];
    for (let i = 1; i < table.length; i++) {
        if (table[i][idxTableIndex] === selectedTableIndex) {
            filteredTable.push(table[i]);
        }
    }

    // Filter attributes
    let filteredAttributes = [];
    if (table2 && table2.length > 0) {
        const attrHeaders = table2[0];
        const idxCostItemId = attrHeaders.indexOf("cost_item_id");
        const allowedIds = new Set(filteredTable.slice(1).map(r => r[idxId]));
        filteredAttributes = [attrHeaders];
        for (let i = 1; i < table2.length; i++) {
            if (allowedIds.has(table2[i][idxCostItemId])) {
                filteredAttributes.push(table2[i]);
            }
        }
    }

    // Rebuild joined sheet only
    const expanded = buildExpandedTable(filteredTable, filteredAttributes);
    storeOriginalJoinedData(expanded);
    await writeTableToExcel(expanded, "JoinedCostData", { selectiveLocking: true });
}





//async function writeTableToExcel(table, sheetName) {
async function writeTableToExcel(table, sheetName, options = {}) {
  const selectiveLocking = options.selectiveLocking || false;
  await Excel.run(async (context) => {

    // Delete old sheet if it exists
    try {
      const oldSheet = context.workbook.worksheets.getItem(sheetName);
      oldSheet.load("name");
      await context.sync();
      oldSheet.delete();
    } catch (e) {}

    const sheet = context.workbook.worksheets.add(sheetName);
    const range = sheet.getRangeByIndexes(0, 0, table.length, table[0].length);
    range.values = table;

    // Convert to Excel Table
    const tableRange = sheet.getRangeByIndexes(0, 0, table.length, table[0].length);
    const excelTable = sheet.tables.add(tableRange, true);
    excelTable.name = sheetName + "_Table";

    // format sheet
    const header = sheet.getRangeByIndexes(0, 0, 1, table[0].length);
    header.format.font.bold = true;
    header.format.fill.color = "#305496";
    header.format.font.color = "white";
    sheet.getUsedRange().format.autofitColumns();
    sheet.freezePanes.freezeRows(1);

    if (selectiveLocking) {

      const lockedColumns = [
        "id",
        "file_id",
        "sheet_name",
        "table_index",
        "row_index",
        "ai_confidence_overall"
      ];

      // Load header row values & lock
      const headerValues = sheet.getRangeByIndexes(0, 0, 1, table[0].length);
      headerValues.load("values");
      await context.sync();
      headerValues.format.protection.locked = true;

      // Unlock all data cells first and then lock specific columns
      const dataRange = sheet.getRangeByIndexes(1, 0, table.length - 1, table[0].length);
      dataRange.format.protection.locked = false;
      lockedColumns.forEach(colName => {
        const colIndex = headerValues.values[0].indexOf(colName);
        if (colIndex !== -1) {
          const colRange = sheet.getRangeByIndexes(1, colIndex, table.length - 1, 1);
          colRange.format.protection.locked = true;
        }
      });
    }

    sheet.protection.protect({
      allowFormatCells: false,
      allowFormatColumns: false,
      allowFormatRows: false,
      allowInsertColumns: selectiveLocking, 
      allowInsertRows: false,
      allowDeleteColumns: false,
      allowDeleteRows: false,
      allowAutoFilter: true,
      allowSort: true,
      allowPivotTables: true
    });

    sheet.activate();
    await context.sync();
  });
}


async function sendCorrections() {
  await Excel.run(async (context) => {

    const sheet = context.workbook.worksheets.getItem("JoinedCostData");
    const usedRange = sheet.getUsedRange();
    usedRange.load("values");
    await context.sync();
    const rows = usedRange.values;
    const headers = rows[0];
    // Identify user-added columns and ignore them
    const extraColumns = headers.filter(h => !ORIGINAL_HEADERS.includes(h));
    const backendCorrections = [];

    for (let r = 1; r < rows.length; r++) {
      const row = rows[r];
      const id = row[0];
      const fileId = row[1];

      for (let c = 0; c < headers.length; c++) {
        const header = headers[c];
        // Skip locked columns
        if (LOCKED_CORE_FIELDS.includes(header)) continue;
        // Skip user-added columns
        if (extraColumns.includes(header)) continue;
        const newValue = row[c];
        const oldValue = ORIGINAL_JOINED_DATA[id][header];
        if (newValue !== oldValue) {

          // Clean cost data core field updates 
          if (CORE_FIELDS.includes(header)) {
            backendCorrections.push({
              source_row_id: id,
              file_id: fileId,
              field_type: "core",
              field_name: header,
              attribute_name: null,
              old_value: oldValue,
              new_value: newValue,
              user: "excel_user"
            });

          // extended attribute field updates 
          } else {
            backendCorrections.push({
              source_row_id: id,
              file_id: fileId,
              field_type: "attribute",
              field_name: null,
              attribute_name: header,
              old_value: oldValue,
              new_value: newValue,
              user: "excel_user"
            });
          }
        }
      }
    }

    if (backendCorrections.length === 0) {
      console.log("No changes detected");
      return;
    }
    console.log("Sending corrections:", backendCorrections);
    await fetch(`http://localhost:8000/corrections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ corrections: backendCorrections })
    });
    console.log("Corrections sent successfully");
  });
}



function storeOriginalJoinedData(expandedTable) {
  ORIGINAL_HEADERS = expandedTable[0];

  for (let i = 1; i < expandedTable.length; i++) {
    const row = expandedTable[i];
    const id = row[0]; // cost_item_id
    ORIGINAL_JOINED_DATA[id] = {};

    ORIGINAL_HEADERS.forEach((header, colIndex) => {
      ORIGINAL_JOINED_DATA[id][header] = row[colIndex];
    });
  }
}


function buildExpandedTable(costData, attributes) {
  // Extract headers from costData
  const costHeaders = costData[0];

  // Build a map: cost_item_id → { attribute_name: attribute_value }
  const attrMap = {};

  for (const row of attributes.slice(1)) { // skip header
    const [id, costItemId, attributeName, attributeValue] = row;
    if (!attrMap[costItemId]) {
      attrMap[costItemId] = {};
    }
    attrMap[costItemId][attributeName] = attributeValue;
  }

  // Collect all unique attribute names
  const attributeNames = new Set();
  for (const row of attributes.slice(1)) {
    attributeNames.add(row[2]); // attribute_name
  }

  const attributeHeaders = Array.from(attributeNames);
  // Build final header row
  const finalHeaders = [...costHeaders, ...attributeHeaders];
  // Build final rows
  const finalRows = [finalHeaders];
  for (const row of costData.slice(1)) { // skip header
    const costItemId = row[0]; // id column
    const attrValues = attrMap[costItemId] || {};
    const expandedRow = [
      ...row,
      ...attributeHeaders.map(name => attrValues[name] || "")
    ];
    finalRows.push(expandedRow);
  }
  return finalRows;
}


async function processUploadedFile(file) {
    //showBusyCursor();
    showBusyOverlay();
    console.log("Pipeline started");
    try {
        const formData = new FormData();
        formData.append("file", file);

        const uploadResp = await fetch("http://localhost:8000/upload-file", {
            method: "POST",
            body: formData
        });
        const uploadData = await uploadResp.json();
        const fileId = uploadData.file_id;
        console.log("Uploaded file_id:", fileId);
        await fetch(`http://localhost:8000/extract-file/${fileId}`, { method: "POST" });
        await fetch(`http://localhost:8000/normalise/${fileId}`, { method: "POST" });
        console.log("Triggering existing load pipeline for file:", fileId);
        await loadSelectedFileById(fileId);
        console.log("Pipeline complete");

    } catch (err) {
        console.error("Pipeline failed:", err);
    } finally {
        //hideBusyCursor();
        hideBusyOverlay();
    }
}


async function loadSelectedFileById(fileId) {
    // Refresh the dropdown so the new file appears
    await populateFileDropdown();

    // Select the new file
    document.getElementById("file-select").value = fileId;

    // Trigger the existing load pipeline
    await loadSelectedFile();
}

