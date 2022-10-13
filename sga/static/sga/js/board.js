const user_stories = JSON.parse(
  document.getElementById("user_stories").textContent
);

const us_types = JSON.parse(document.getElementById("us_types").textContent);

const items = user_stories.map(({ id, title }) => ({
  id,
  title,
}));

const activeUsType = us_types[0];

let currentBoards = activeUsType.columns.map((column, index) => ({
  id: `board-${column}`,
  title: column,
  item: getUsByType(activeUsType.id, index),
  dragTo: activeUsType.columns
    .filter((c) => c !== column)
    .map((column) => `board-${column}`),
}));

const kanban = new jKanban({
  element: "#myKanban",
  gutter: "20px",
  widthBoard: "260px",
  dragBoards: false,
  boards: currentBoards,
  dropEl: function (el, target, source, sibling) {
    const usId = el.getAttribute("data-eid").split("-")[1];
    const usTypeColumn = target.parentElement
      .getAttribute("data-id")
      .split("-")[1];
    const usTypeColumnId = activeUsType.columns.indexOf(usTypeColumn);
    updateUsColumn(usId, usTypeColumnId);
  },
});
/**
 * Obtiene todas las US de un tipo y columna
 * @param {number} usTypeId Id del tipo de US
 * @param {number} indexColumn Indice de la columna dentro de columns del tipo de US
 * @returns {Array} Lista de US
 */
function getUsByType(usTypeId, indexColumn) {
  return user_stories
    .filter((us) => us.us_type === usTypeId && us.column === indexColumn)
    .map(({ id, title }) => ({
      id: `us-${id}`,
      title,
    }));
}

/**
 * Funcion que se ejecuta al seleccionar un tipo de US, actualiza el tablero
 */
function filterUs() {
  // Obtener el tipo de US seleccionado
  const usType = document.getElementById("us_type").value;
  const usTypeObj = us_types.find((us) => us.id === parseInt(usType));

  // Actualizar el tablero
  const boards = usTypeObj.columns.map((column, index) => ({
    id: `board-${column}`,
    title: column,
    item: getUsByType(usTypeObj.id, index),
    dragTo: usTypeObj.columns
      .filter((c) => c !== column)
      .map((column) => `board-${column}`),
  }));
  // Eliminar las columnas del tablero actual
  const currentBoardIds = currentBoards.map((board) => board.id);
  currentBoardIds.forEach((boardId) => {
    kanban.removeBoard(boardId);
  });

  // Agregar las columnas del nuevo tablero
  kanban.addBoards(boards);
  currentBoards = boards;
}

async function updateUsColumn(usId, column) {
  const url = `/projects/1/user-stories/${usId}/`;
  const csrftoken = document.cookie
    .split(";")
    .find((row) => row.trim().startsWith("csrftoken="))
    .split("=")[1].trim();

  fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ column }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
