Office.onReady(() => {
  console.log("Commands runtime ready");
});

/**
 * Called by the ribbon button via ExecuteFunction
 */
function showTaskpane() {
  Office.addin.showAsTaskpane();
}
