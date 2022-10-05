var user_stories = JSON.parse(
  document.getElementById("user_stories").textContent
);
var us_types = JSON.parse(document.getElementById("us_types").textContent);
const items = user_stories.map(({ id, title }) => ({
  id,
  title,
}));
const activeUsType = us_types[0];
const boards = activeUsType.columns.map((column, index) => ({
  id: `board-${column}`,
  title: column,
  item: getUsByType(activeUsType.id, index),
  dragTo: activeUsType.columns
    .filter((c) => c !== column)
    .map((column) => `board-${column}`),
}));
console.log(boards);
const kanban = new jKanban({
  element: "#myKanban",
  gutter: "20px",
  widthBoard: "260px",
  boards,
  dropEl: function (el, target, source, sibling) {
    const usId = el.getAttribute("data-eid").split("-")[1];
    const usTypeColumn = target.parentElement
      .getAttribute("data-id")
      .split("-")[1];
    const usTypeColumnId = activeUsType.columns.indexOf(usTypeColumn);
    console.log(usId, usTypeColumn, usTypeColumnId);
  },
});
/**
 *
 * @param {number} usTypeId Id del tipo de US
 * @param {*} indexColumn Columna del tipo de US
 * @returns
 */
function getUsByType(usTypeId, indexColumn) {
  // TODO Filtrar por columna del tipo de user story
  return user_stories
    .filter((us) => us.us_type === usTypeId)
    .map(({ id, title }) => ({
      id: `us-${id}`,
      title,
    }));
}
