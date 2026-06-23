/**
 * @typedef {Object} AIExtrapolationResult
 * @property {Array<number|null>} values
 * @property {Array<string>} flags
 * @property {Array<string>} methods
 * @property {Array<number>} confidence
 */

function validateAIResponse(aiResult) {
    if (!Array.isArray(aiResult)) {
        throw new Error("AI result must be an array of prediction objects.");
    }

    for (const item of aiResult) {
        if (typeof item.cost_item_id === "undefined") {
            throw new Error("AI result item missing cost_item_id.");
        }
        if (!("predicted_value" in item)) {
            throw new Error("AI result item missing predicted_value.");
        }
        if (!("flag" in item)) {
            throw new Error("AI result item missing flag.");
        }
        if (!("method" in item)) {
            throw new Error("AI result item missing method.");
        }
        if (!("confidence" in item)) {
            throw new Error("AI result item missing confidence.");
        }
    }

    return true;
}

export async function populateExtrapolationBlock(context, aiResult) {

    const sheet = context.workbook.worksheets.getItem("JoinedCostData");
    sheet.activate();
    await context.sync();

    await Excel.run(async (context) => {
        const sheet =
        context.workbook.worksheets.getItem("JoinedCostData");
        sheet.protection.unprotect();
        await context.sync();
    });

    const table = sheet.tables.getItemAt(0);
   
    const idCol = table.columns.getItem("id").getDataBodyRange();
    idCol.load("values");
    await context.sync();

    const excelIds = idCol.values.flat();
    const idToRow = new Map();

    excelIds.forEach((id, i) => {
        if (id !== null && id !== "") {
            idToRow.set(id, i + 1);
        }
    });

    // Find last 4 columns and load 
    const used = sheet.getUsedRange(true);
    used.load("columnCount");
    await context.sync();
    const lastBlockStart = used.columnCount - 4;

    // Write to ONLY the rows that have predictions
    for (const p of aiResult) {
        const row = idToRow.get(p.cost_item_id);
        if (!row) continue;
        sheet.getCell(row, lastBlockStart).values = [[p.predicted_value]];
        sheet.getCell(row, lastBlockStart + 1).values = [[p.flag]];
        sheet.getCell(row, lastBlockStart + 2).values = [[p.method]];
        sheet.getCell(row, lastBlockStart + 3).values = [[p.confidence]];
    }

    await context.sync();
}
